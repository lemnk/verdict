from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from app.models.search import SearchQuery, SearchResponse, PrecedentResult
from app.db.database import get_db
from app.db.models import Document, DocumentChunk
from app.utils.embedding import generate_embedding, cosine_similarity

router = APIRouter()
security = HTTPBearer()

@router.post("/precedents", response_model=SearchResponse)
async def search_legal_precedents(
    query: SearchQuery,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Search for legal precedents using RAG system"""
    try:
        # Generate query embedding
        query_embedding = generate_embedding(query.query)
        
        # Get all chunks with embeddings
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.embedding.isnot(None)
        ).all()
        
        if not chunks:
            return SearchResponse(
                query=query.query,
                results=[],
                total_count=0
            )
        
        # Calculate similarities and create results
        results = []
        for chunk in chunks:
            if chunk.embedding:
                similarity = cosine_similarity(query_embedding, chunk.embedding)
                
                # Get document info
                document = db.query(Document).filter(Document.id == chunk.doc_id).first()
                
                result = PrecedentResult(
                    id=str(chunk.id),
                    title=document.filename if document else f"Document {chunk.doc_id}",
                    court="Unknown Court",  # Placeholder
                    year=2024,  # Placeholder
                    summary=chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    relevance_score=similarity
                )
                results.append(result)
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        top_results = results[:10]  # Limit to top 10
        
        return SearchResponse(
            query=query.query,
            results=top_results,
            total_count=len(top_results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/precedents/suggest")
async def get_search_suggestions(
    q: str = Query(..., min_length=2),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get search suggestions based on partial query"""
    # Basic suggestions - could be enhanced with actual document content analysis
    suggestions = [
        "contract law",
        "criminal procedure", 
        "constitutional rights",
        "property law",
        "tort law",
        "family law",
        "corporate law",
        "tax law"
    ]
    
    # Filter suggestions based on query
    filtered_suggestions = [s for s in suggestions if q.lower() in s.lower()]
    
    return {"suggestions": filtered_suggestions[:5]}