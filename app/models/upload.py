from pydantic import BaseModel
from enum import Enum
from uuid import UUID

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentUploadResponse(BaseModel):
    id: UUID
    status: DocumentStatus

class DocumentStatusResponse(BaseModel):
    document_id: UUID
    status: DocumentStatus
    progress: int