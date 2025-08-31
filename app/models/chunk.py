from pydantic import BaseModel
from typing import List
from uuid import UUID

class ChunkResponse(BaseModel):
    id: UUID
    chunk_index: int
    content: str
    embedding_length: int

class ParseResult(BaseModel):
    doc_id: UUID
    chunks_indexed: int
    total_chunks: int
    status: str