import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Path as FastAPIPath
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.models.chunk import ParseResult
from app.db.database import get_db
from app.db.models import Document, DocumentChunk
from app.utils.parser import extract_chunks_from_pdf
from app.utils.embedding import embed_chunks
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/{doc_id}", response_model=ParseResult)
async def parse_document(
    doc_id: str = FastAPIPath(..., description="Document UUID to parse"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Parse uploaded PDF document into chunks and generate embeddings"""
    
    # Validate UUID format
    try:
        document_uuid = uuid.UUID(doc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    
    # Get document from database
    document = db.query(Document).filter(Document.id == document_uuid).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if document file exists
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")
    
    # Check if document is already parsed
    existing_chunks = db.query(DocumentChunk).filter(DocumentChunk.doc_id == document_uuid).count()
    if existing_chunks > 0:
        raise HTTPException(status_code=409, detail="Document already parsed")
    
    try:
        # Extract chunks from PDF
        chunks = extract_chunks_from_pdf(str(file_path))
        if not chunks:
            raise HTTPException(status_code=422, detail="No text content extracted from PDF")
        
        # Generate embeddings for chunks
        embeddings = embed_chunks(chunks)
        if len(embeddings) != len(chunks):
            raise HTTPException(status_code=500, detail="Embedding generation failed")
        
        # Store chunks and embeddings in database
        chunk_objects = []
        for i, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_obj = DocumentChunk(
                doc_id=document_uuid,
                chunk_index=i,
                content=chunk_content,
                embedding=embedding
            )
            chunk_objects.append(chunk_obj)
        
        # Bulk insert chunks
        db.add_all(chunk_objects)
        
        # Update document status
        document.status = "parsed"
        
        # Commit transaction
        db.commit()
        
        logger.info(f"Successfully parsed document {doc_id} into {len(chunks)} chunks")
        
        return ParseResult(
            doc_id=document_uuid,
            chunks_indexed=len(chunks),
            total_chunks=len(chunks),
            status="completed"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Rollback on error
        db.rollback()
        logger.error(f"Error parsing document {doc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document parsing failed: {str(e)}")

@router.get("/{doc_id}/chunks")
async def get_document_chunks(
    doc_id: str = FastAPIPath(..., description="Document UUID to retrieve chunks for"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Retrieve all chunks for a parsed document"""
    
    # Validate UUID format
    try:
        document_uuid = uuid.UUID(doc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    
    # Get document chunks
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.doc_id == document_uuid
    ).order_by(DocumentChunk.chunk_index).all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for document")
    
    # Return chunk data
    return {
        "doc_id": doc_id,
        "chunks": [
            {
                "id": str(chunk.id),
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "embedding_length": len(chunk.embedding) if chunk.embedding else 0
            }
            for chunk in chunks
        ],
        "total_chunks": len(chunks)
    }