from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select

from backend.app.db import SessionLocal
from backend.app.models import InterviewSessionModel
from backend.app.schemas import Session


class SessionRepository:
    def cleanup_expired(self) -> None:
        with SessionLocal() as db:
            db.execute(delete(InterviewSessionModel).where(InterviewSessionModel.expires_at <= datetime.now(timezone.utc)))
            db.commit()

    def save(self, session_id: str, data: Session, raw_jd: str = "") -> None:
        with SessionLocal() as db:
            existing = db.get(InterviewSessionModel, session_id)
            if not existing:
                existing = InterviewSessionModel(session_id=session_id, created_at=data.created_at, expires_at=data.expires_at, interview_type=data.interview_type, jd_analysis=data.jd_analysis, questions=data.questions, answers=data.answers, evaluations=data.evaluations, raw_jd=raw_jd)
                db.add(existing)
            else:
                existing.created_at = data.created_at
                existing.expires_at = data.expires_at
                existing.interview_type = data.interview_type
                existing.jd_analysis = data.jd_analysis
                existing.questions = data.questions
                existing.answers = data.answers
                existing.evaluations = data.evaluations
                if raw_jd:
                    existing.raw_jd = raw_jd
            db.commit()

    def get(self, session_id: str) -> Session | None:
        with SessionLocal() as db:
            row = db.get(InterviewSessionModel, session_id)
            if not row:
                return None
            return Session(
                created_at=row.created_at,
                expires_at=row.expires_at,
                jd_analysis=row.jd_analysis,
                interview_type=row.interview_type,
                questions=row.questions,
                answers=row.answers or [],
                evaluations=row.evaluations or [],
            )

    def exists(self, session_id: str) -> bool:
        with SessionLocal() as db:
            return db.execute(select(InterviewSessionModel.session_id).where(InterviewSessionModel.session_id == session_id)).scalar_one_or_none() is not None

