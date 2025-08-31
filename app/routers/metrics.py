from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional
import logging

from app.db.database import get_db
from app.db.models import User, QueryLog
from app.lib.auth import get_user_from_token

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

def require_admin(user: User) -> None:
    """Check if user has admin role"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

@router.get("/summary")
async def get_metrics_summary(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get aggregated metrics summary"""
    user = get_user_from_token(credentials, db)
    require_admin(user)
    
    try:
        # Total queries and cache hit rate
        total_queries = db.query(func.count(QueryLog.id)).scalar() or 0
        
        if total_queries > 0:
            cache_hits = db.query(func.count(QueryLog.id)).filter(QueryLog.cached == True).scalar() or 0
            cache_hit_rate = (cache_hits / total_queries) * 100
        else:
            cache_hit_rate = 0.0
        
        # Average cost
        avg_cost_result = db.query(func.avg(QueryLog.cost_usd)).scalar()
        avg_cost_usd = float(avg_cost_result) if avg_cost_result else 0.0
        
        # Percentile latencies using window functions
        latency_query = text("""
            SELECT 
                percentile_cont(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50_latency_ms,
                percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency_ms
            FROM query_logs
        """)
        latency_result = db.execute(latency_query).fetchone()
        p50_latency_ms = int(latency_result.p50_latency_ms) if latency_result.p50_latency_ms else 0
        p95_latency_ms = int(latency_result.p95_latency_ms) if latency_result.p95_latency_ms else 0
        
        # Metrics by model
        model_metrics_query = text("""
            SELECT 
                model,
                COUNT(*) as n,
                AVG(cost_usd) as avg_cost_usd,
                percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency_ms
            FROM query_logs 
            GROUP BY model 
            ORDER BY n DESC
        """)
        model_metrics = db.execute(model_metrics_query).fetchall()
        
        by_model = [
            {
                "model": row.model,
                "n": row.n,
                "avg_cost_usd": float(row.avg_cost_usd) if row.avg_cost_usd else 0.0,
                "p95_latency_ms": int(row.p95_latency_ms) if row.p95_latency_ms else 0
            }
            for row in model_metrics
        ]
        
        # Last 24 hours hourly breakdown
        hourly_metrics_query = text("""
            SELECT 
                DATE_TRUNC('hour', created_at) as ts_hour,
                COUNT(*) as n,
                AVG(cost_usd) as avg_cost_usd,
                AVG(latency_ms) as avg_latency_ms
            FROM query_logs 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            GROUP BY DATE_TRUNC('hour', created_at)
            ORDER BY ts_hour DESC
        """)
        hourly_metrics = db.execute(hourly_metrics_query).fetchall()
        
        last_24h = [
            {
                "ts_hour": row.ts_hour.isoformat() if row.ts_hour else None,
                "n": row.n,
                "avg_cost_usd": float(row.avg_cost_usd) if row.avg_cost_usd else 0.0,
                "avg_latency_ms": float(row.avg_latency_ms) if row.avg_latency_ms else 0.0
            }
            for row in hourly_metrics
        ]
        
        return {
            "total_queries": total_queries,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "avg_cost_usd": round(avg_cost_usd, 6),
            "p50_latency_ms": p50_latency_ms,
            "p95_latency_ms": p95_latency_ms,
            "by_model": by_model,
            "last_24h": last_24h
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@router.get("/recent")
async def get_recent_queries(
    limit: int = Query(default=100, ge=1, le=1000),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get recent query logs with pagination"""
    user = get_user_from_token(credentials, db)
    require_admin(user)
    
    try:
        # Get recent queries with user info
        recent_queries_query = text("""
            SELECT 
                ql.id,
                ql.user_id,
                u.name as user_name,
                ql.query,
                ql.provider,
                ql.model,
                ql.tokens_in,
                ql.tokens_out,
                ql.cost_usd,
                ql.latency_ms,
                ql.created_at,
                ql.cached
            FROM query_logs ql
            LEFT JOIN users u ON ql.user_id = u.id
            ORDER BY ql.created_at DESC
            LIMIT :limit
        """)
        
        recent_queries = db.execute(recent_queries_query, {"limit": limit}).fetchall()
        
        return {
            "items": [
                {
                    "id": str(row.id),
                    "user_id": row.user_id,
                    "user_name": row.user_name,
                    "query": row.query,
                    "provider": row.provider,
                    "model": row.model,
                    "tokens_in": row.tokens_in,
                    "tokens_out": row.tokens_out,
                    "cost_usd": str(row.cost_usd),
                    "latency_ms": row.latency_ms,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "cached": row.cached
                }
                for row in recent_queries
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting recent queries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recent queries")