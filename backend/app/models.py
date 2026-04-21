from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db import Base


class InterviewSessionModel(Base):
    __tablename__ = "interview_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    interview_type: Mapped[str] = mapped_column(String(32), nullable=False)
    jd_analysis: Mapped[dict] = mapped_column(JSON, nullable=False)
    questions: Mapped[list] = mapped_column(JSON, nullable=False)
    answers: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    evaluations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    raw_jd: Mapped[str] = mapped_column(Text, nullable=False, default="")

