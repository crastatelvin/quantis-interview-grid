from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import desc, select

from backend.app.db import SessionLocal
from backend.app.models import InterviewRunModel


class HistoryService:
    def save_run(
        self,
        user_id: str,
        session_id: str,
        interview_type: str,
        role_title: str,
        final_score: int,
        report_json: dict,
        transcript_json: list,
    ) -> None:
        with SessionLocal() as db:
            run = InterviewRunModel(
                id=f"run_{uuid4().hex[:16]}",
                user_id=user_id,
                session_id=session_id,
                interview_type=interview_type,
                role_title=role_title,
                final_score=final_score,
                report_json=report_json,
                transcript_json=transcript_json,
                created_at=datetime.now(timezone.utc),
            )
            db.add(run)
            db.commit()

    def list_runs(self, user_id: str, limit: int = 20) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(
                select(InterviewRunModel)
                .where(InterviewRunModel.user_id == user_id)
                .order_by(desc(InterviewRunModel.created_at))
                .limit(limit)
            ).scalars()
            return [
                {
                    "id": r.id,
                    "session_id": r.session_id,
                    "interview_type": r.interview_type,
                    "role_title": r.role_title,
                    "final_score": r.final_score,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]

    def get_run(self, user_id: str, run_id: str) -> dict | None:
        with SessionLocal() as db:
            row = db.execute(
                select(InterviewRunModel)
                .where(InterviewRunModel.user_id == user_id)
                .where(InterviewRunModel.id == run_id)
            ).scalar_one_or_none()
            if not row:
                return None
            return {
                "id": row.id,
                "session_id": row.session_id,
                "interview_type": row.interview_type,
                "role_title": row.role_title,
                "final_score": row.final_score,
                "report": row.report_json,
                "transcript": row.transcript_json,
                "created_at": row.created_at.isoformat(),
            }

