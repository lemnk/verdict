import math
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.models.rag import RetrievalItem
from app.db.models import DocumentChunk
from app.utils.embedding import embed_chunks, cosine_similarity

logger = logging.getLogger(__name__)

def retrieve_topk(query: str, k: int, db: Session) -> List[RetrievalItem]:
    """Retrieve top-k chunks for a query using vector similarity"""
    try:
        # Generate query embedding
        query_embeddings = embed_chunks([query])
        if not query_embeddings:
            logger.error("Failed to generate query embedding")
            return []
        
        query_embedding = query_embeddings[0]
        
        # Get all chunks with embeddings from database
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.embedding.isnot(None)
        ).all()
        
        if not chunks:
            logger.warning("No chunks with embeddings found in database")
            return []
        
        # Calculate similarities and create retrieval items
        retrieval_items = []
        for chunk in chunks:
            if chunk.embedding:
                similarity = cosine_similarity(query_embedding, chunk.embedding)
                
                # Create snippet around chunk content (300-400 chars)
                content = chunk.content
                snippet_length = min(350, len(content))
                start = max(0, (len(content) - snippet_length) // 2)
                snippet = content[start:start + snippet_length]
                
                # Add ellipsis if truncated
                if start > 0:
                    snippet = "..." + snippet
                if start + snippet_length < len(content):
                    snippet = snippet + "..."
                
                retrieval_items.append(RetrievalItem(
                    doc_id=chunk.doc_id,
                    chunk_index=chunk.chunk_index,
                    score=similarity,
                    snippet=snippet
                ))
        
        # Sort by score (descending) and return top-k
        retrieval_items.sort(key=lambda x: x.score, reverse=True)
        top_items = retrieval_items[:k]
        
        logger.info(f"Retrieved {len(top_items)} chunks for query: {query[:50]}...")
        return top_items
        
    except Exception as e:
        logger.error(f"Error in retrieve_topk: {str(e)}")
        return []

def trim_context_to_token_budget(items: List[RetrievalItem], budget_tokens: int, model: str) -> List[RetrievalItem]:
    """Trim context to fit within token budget"""
    if not items:
        return []
    
    # Estimate tokens: approximately 4 characters per token
    chars_per_token = 4
    
    budgeted_items = []
    current_tokens = 0
    
    for item in items:
        # Estimate tokens for this item
        item_tokens = math.ceil(len(item.snippet) / chars_per_token)
        
        # Check if adding this item would exceed budget
        if current_tokens + item_tokens <= budget_tokens:
            budgeted_items.append(item)
            current_tokens += item_tokens
        else:
            # Try to fit a truncated version if it's the first item
            if not budgeted_items and item_tokens <= budget_tokens:
                # Truncate the snippet to fit budget
                max_chars = budget_tokens * chars_per_token
                truncated_snippet = item.snippet[:max_chars] + "..."
                truncated_item = RetrievalItem(
                    doc_id=item.doc_id,
                    chunk_index=item.chunk_index,
                    score=item.score,
                    snippet=truncated_snippet
                )
                budgeted_items.append(truncated_item)
            break
    
    logger.info(f"Trimmed context from {len(items)} to {len(budgeted_items)} items, using {current_tokens}/{budget_tokens} tokens")
    return budgeted_items