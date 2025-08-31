from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

class RetrievalItem(BaseModel):
    doc_id: UUID
    chunk_index: int
    score: float
    snippet: str

class AnswerRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(default=5, ge=1, le=20)
    max_context_tokens: int = Field(default=2000, ge=100, le=8000)
    model: Optional[str] = Field(default=None, max_length=50)

class Citation(BaseModel):
    doc_id: UUID
    chunk_index: int
    snippet: str
    score: float

class AnswerResponse(BaseModel):
    answer: str
    citations: List[Citation]
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: Decimal
    latency_ms: float
    cached: bool