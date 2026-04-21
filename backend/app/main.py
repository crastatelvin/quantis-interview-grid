from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.db import Base, engine
from backend.app.repositories.session_repository import SessionRepository
from backend.app.schemas import EvaluateRequest, ReportRequest, SetupRequest
from backend.app.services.ai_client import GroqClient
from backend.app.services.cache import SessionCache
from backend.app.services.interview_service import InterviewService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("quantis.api")

app = FastAPI(title="Quantis Interview Grid API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_methods=["*"], allow_headers=["*"])

Base.metadata.create_all(bind=engine)
service = InterviewService(
    ai_client=GroqClient(),
    session_repository=SessionRepository(),
    session_cache=SessionCache(),
)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "quantis-interview-grid-api"}


@app.post("/setup")
def setup_interview(body: SetupRequest) -> dict[str, Any]:
    logger.info("setup interview type=%s", body.interview_type)
    return service.setup(body.jd_text, body.interview_type, body.session_id)


@app.post("/evaluate")
def evaluate(body: EvaluateRequest) -> dict[str, Any]:
    logger.info("evaluate session=%s q=%s", body.session_id, body.question_index)
    if not service.has_session(body.session_id):
        raise HTTPException(status_code=404, detail="Session not found or expired")
    result = service.evaluate(body.session_id, body.question_index, body.answer)
    if result is None:
        raise HTTPException(status_code=400, detail="Question index out of bounds")
    return result


@app.post("/report")
def report(body: ReportRequest) -> dict[str, Any]:
    logger.info("report session=%s", body.session_id)
    if not service.has_session(body.session_id):
        raise HTTPException(status_code=404, detail="Session not found or expired")
    result = service.report(body.session_id)
    if result is None:
        raise HTTPException(status_code=400, detail="No evaluations found")
    if result.get("incomplete"):
        raise HTTPException(
            status_code=400,
            detail=f"Interview incomplete: answered {result['answered']} of {result['total']} questions.",
        )
    return result

