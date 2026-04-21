from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
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


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class InterviewRunModel(Base):
    __tablename__ = "interview_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    interview_type: Mapped[str] = mapped_column(String(32), nullable=False)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    final_score: Mapped[int] = mapped_column(nullable=False, default=0)
    report_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    transcript_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

