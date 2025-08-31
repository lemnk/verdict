from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer

from app.models.upload import DocumentUploadResponse, DocumentStatus
from app.utils.pdf_parser import parse_pdf_document

router = APIRouter()
security = HTTPBearer()

@router.post("/document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload legal document for processing"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # TODO: Implement actual file storage and processing
    document_id = "doc_123"
    
    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status=DocumentStatus.UPLOADED,
        message="Document uploaded successfully"
    )

@router.get("/document/{document_id}/status")
async def get_document_status(
    document_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get processing status of uploaded document"""
    # TODO: Implement actual status checking
    return {
        "document_id": document_id,
        "status": DocumentStatus.PROCESSING,
        "progress": 50
    }