from pydantic import BaseModel
from typing import List

class SearchQuery(BaseModel):
    query: str
    filters: dict = {}

class PrecedentResult(BaseModel):
    id: str
    title: str
    court: str
    year: int
    summary: str
    relevance_score: float

class SearchResponse(BaseModel):
    query: str
    results: List[PrecedentResult]
    total_count: int