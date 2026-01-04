from pydantic import BaseModel, Field
from typing import List, Optional

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)

class Citation(BaseModel):
    doc_id: str
    chunk_id: str
    score: float

class AskResponse(BaseModel):
    request_id: str
    answer: str
    citations: List[Citation]
    latency_ms: int
