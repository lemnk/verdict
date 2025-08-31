import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.models.upload import DocumentUploadResponse, DocumentStatusResponse, DocumentStatus
from app.db.database import get_db
from app.db.models import Document

router = APIRouter()
security = HTTPBearer()

# Configuration
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
UPLOAD_DIR = Path("uploads")
ALLOWED_MIME_TYPES = ["application/pdf"]
ALLOWED_EXTENSIONS = [".pdf"]

def validate_pdf_file(file: UploadFile) -> None:
    """Validate PDF file type and size"""
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file extension. Only .pdf files are allowed"
        )

def save_uploaded_file(file: UploadFile) -> tuple[str, str]:
    """Save uploaded file and return UUID filename and file path"""
    # Generate unique filename
    file_uuid = str(uuid.uuid4())
    filename = f"{file_uuid}.pdf"
    file_path = UPLOAD_DIR / filename
    
    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save file: {str(e)}"
        )
    
    return file_uuid, str(file_path)

@router.post("/", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Upload legal document for processing"""
    # Validate file
    validate_pdf_file(file)
    
    # Save file to disk
    file_uuid, file_path = save_uploaded_file(file)
    
    # Create document record in database
    try:
        document = Document(
            id=uuid.UUID(file_uuid),
            filename=file.filename,
            file_path=file_path,
            status="uploaded"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception as e:
        # Clean up file if database insert fails
        try:
            os.remove(file_path)
        except:
            pass
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save document metadata: {str(e)}"
        )
    
    return DocumentUploadResponse(
        id=document.id,
        status=DocumentStatus.UPLOADED
    )

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get processing status of uploaded document"""
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    
    document = db.query(Document).filter(Document.id == doc_uuid).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # TODO: Implement actual progress tracking
    progress = 50 if document.status == "processing" else 100
    
    return DocumentStatusResponse(
        document_id=document.id,
        status=DocumentStatus(document.status),
        progress=progress
    )