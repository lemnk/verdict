import hashlib
import json
import redis
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from decimal import Decimal
import logging

from app.models.rag import AnswerRequest, AnswerResponse, Citation, RetrievalItem
from app.db.database import get_db
from app.db.models import QueryLog, User
from app.utils.retrieval import retrieve_topk, trim_context_to_token_budget
from app.utils.prompting import build_prompt
from app.utils.llm import chat_complete
from app.utils.embedding import generate_embedding

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Redis configuration
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
CACHE_TTL = 600  # 10 minutes

def get_user_from_token(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    """Extract user from JWT token"""
    # TODO: Implement proper JWT validation
    # For now, return a mock user
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user

def generate_cache_key(user_id: int, query: str, k: int, model: str) -> str:
    """Generate cache key from request parameters"""
    cache_data = f"{user_id}:{query}:{k}:{model or 'default'}"
    return hashlib.sha256(cache_data.encode()).hexdigest()

def get_cached_response(cache_key: str) -> AnswerResponse:
    """Retrieve cached response from Redis"""
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            cached_dict = json.loads(cached_data)
            # Convert cost back to Decimal
            cached_dict['cost_usd'] = Decimal(str(cached_dict['cost_usd']))
            return AnswerResponse(**cached_dict)
    except Exception as e:
        logger.warning(f"Error retrieving cached response: {str(e)}")
    return None

def cache_response(cache_key: str, response: AnswerResponse):
    """Cache response in Redis"""
    try:
        # Convert Decimal to string for JSON serialization
        response_dict = response.dict()
        response_dict['cost_usd'] = str(response_dict['cost_usd'])
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(response_dict))
        logger.info(f"Cached response with key: {cache_key[:16]}...")
    except Exception as e:
        logger.warning(f"Error caching response: {str(e)}")

def log_query_metrics(
    user_id: int,
    query: str,
    provider: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
    cost_usd: Decimal,
    latency_ms: float,
    cached: bool,
    db: Session
):
    """Log query metrics to database"""
    try:
        query_log = QueryLog(
            user_id=user_id,
            query=query,
            provider=provider,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            latency_ms=int(latency_ms),
            cached=cached
        )
        db.add(query_log)
        db.commit()
        logger.info(f"Logged query metrics: {tokens_in}+{tokens_out} tokens, ${cost_usd}")
    except Exception as e:
        logger.error(f"Error logging query metrics: {str(e)}")
        db.rollback()

@router.post("/ask", response_model=AnswerResponse)
async def ask_legal_question(
    request: AnswerRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Ask a legal question using RAG system"""
    
    # Get user from token
    user = get_user_from_token(credentials, db)
    
    # Generate cache key
    cache_key = generate_cache_key(user.id, request.query, request.k, request.model)
    
    # Check cache first
    cached_response = get_cached_response(cache_key)
    if cached_response:
        cached_response.cached = True
        logger.info(f"Returning cached response for query: {request.query[:50]}...")
        return cached_response
    
    try:
        # Retrieve top-k chunks
        retrieval_items = retrieve_topk(request.query, request.k, db)
        if not retrieval_items:
            raise HTTPException(status_code=404, detail="No relevant documents found")
        
        # Trim context to token budget
        budgeted_items = trim_context_to_token_budget(
            retrieval_items, 
            request.max_context_tokens, 
            request.model or "gpt-4o-mini"
        )
        
        if not budgeted_items:
            raise HTTPException(status_code=400, detail="Context too large for token budget")
        
        # Build prompt
        prompt = build_prompt(request.query, budgeted_items)
        
        # Get LLM response
        llm_response = chat_complete(prompt, request.model)
        
        # Construct citations preserving item order
        citations = []
        for i, item in enumerate(budgeted_items):
            citation = Citation(
                doc_id=item.doc_id,
                chunk_index=item.chunk_index,
                snippet=item.snippet,
                score=item.score
            )
            citations.append(citation)
        
        # Build response
        response = AnswerResponse(
            answer=llm_response["text"],
            citations=citations,
            provider=llm_response["provider"],
            model=llm_response["model"],
            tokens_in=llm_response["tokens_in"],
            tokens_out=llm_response["tokens_out"],
            cost_usd=Decimal(str(llm_response["cost_usd"])),
            latency_ms=llm_response["latency_ms"],
            cached=False
        )
        
        # Cache response
        cache_response(cache_key, response)
        
        # Log metrics
        log_query_metrics(
            user.id,
            request.query,
            response.provider,
            response.model,
            response.tokens_in,
            response.tokens_out,
            response.cost_usd,
            response.latency_ms,
            False,
            db
        )
        
        logger.info(f"Generated RAG response for query: {request.query[:50]}... with {len(citations)} citations")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in RAG inference: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG inference failed: {str(e)}")