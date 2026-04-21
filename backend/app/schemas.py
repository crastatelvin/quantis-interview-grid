from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


class SetupRequest(BaseModel):
    jd_text: str = Field(min_length=30)
    interview_type: Literal["technical", "behavioral", "product", "leadership", "hr"] = "behavioral"
    session_id: str | None = None


class EvaluateRequest(BaseModel):
    session_id: str
    question_index: int = Field(ge=0)
    answer: str = Field(min_length=10)


class ReportRequest(BaseModel):
    session_id: str
    transcript: list[dict] | None = None


class Session(BaseModel):
    created_at: datetime
    expires_at: datetime
    jd_analysis: Dict[str, Any]
    interview_type: str
    questions: list[str]
    answers: list[str] = Field(default_factory=list)
    evaluations: list[Dict[str, Any]] = Field(default_factory=list)

