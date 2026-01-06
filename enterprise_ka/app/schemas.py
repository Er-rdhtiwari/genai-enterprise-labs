from typing import Literal

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)
    prompt_template: str | None = Field(
        default=None,
        description="Optional prompt template name. Falls back to server default when not provided."
    )
    debug_prompt: bool = Field(
        default=False,
        description="If true, returns the rendered system/user prompts for comparison."
    )

class Citation(BaseModel):
    doc_id: str
    chunk_id: str
    score: float

class GuardrailEvent(BaseModel):
    category: str
    action: Literal["block", "warn", "info"]
    detail: str

class PromptTrace(BaseModel):
    template: str
    version: str
    description: str
    system_prompt: str | None = None
    user_prompt: str | None = None

class AskResponse(BaseModel):
    request_id: str
    answer: str
    citations: list[Citation]
    latency_ms: int
    prompt: PromptTrace | None = None
    guardrails: list[GuardrailEvent] = Field(default_factory=list)
