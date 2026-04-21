from __future__ import annotations

import logging
import time
from io import BytesIO
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pypdf import PdfReader

from backend.app.config import settings
from backend.app.db import Base, engine
from backend.app.repositories.session_repository import SessionRepository
from backend.app.schemas import EvaluateRequest, ReportRequest, SetupRequest
from backend.app.services.auth_service import AuthService
from backend.app.services.ai_client import GroqClient
from backend.app.services.cache import SessionCache
from backend.app.services.history_service import HistoryService
from backend.app.services.interview_service import InterviewService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("quantis.api")
request_counter = Counter("api_requests_total", "API request count", ["method", "path", "status"])
request_latency = Histogram("api_request_latency_seconds", "API request latency", ["method", "path"])
obs_state = {"requests_total": 0, "errors_total": 0, "latency_samples": []}

app = FastAPI(title="Quantis Interview Grid API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_methods=["*"], allow_headers=["*"])

Base.metadata.create_all(bind=engine)
auth_service = AuthService()
history_service = HistoryService()
service = InterviewService(
    ai_client=GroqClient(),
    session_repository=SessionRepository(),
    session_cache=SessionCache(),
)


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    obs_state["requests_total"] += 1
    if response.status_code >= 400:
        obs_state["errors_total"] += 1
    samples = obs_state["latency_samples"]
    samples.append(elapsed * 1000)
    if len(samples) > 500:
        del samples[: len(samples) - 500]
    request_counter.labels(request.method, request.url.path, str(response.status_code)).inc()
    request_latency.labels(request.method, request.url.path).observe(elapsed)
    response.headers["X-Request-Latency-Ms"] = f"{elapsed*1000:.2f}"
    return response


def _bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return auth.replace("Bearer ", "", 1).strip()


def _current_user_id(request: Request) -> str:
    try:
        payload = auth_service.decode_token(_bearer_token(request))
        return str(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "quantis-interview-grid-api"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/auth/register")
def register(body: dict) -> dict[str, Any]:
    email = str(body.get("email", "")).strip()
    password = str(body.get("password", "")).strip()
    if "@" not in email or len(password) < 8:
        raise HTTPException(status_code=400, detail="Invalid email or password too short")
    try:
        user = auth_service.register(email, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"user": user}


@app.post("/auth/login")
def login(body: dict) -> dict[str, Any]:
    email = str(body.get("email", "")).strip()
    password = str(body.get("password", "")).strip()
    try:
        token = auth_service.login(email, password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return {"access_token": token, "token_type": "bearer"}


@app.get("/history")
def history(request: Request) -> dict[str, Any]:
    uid = _current_user_id(request)
    return {"runs": history_service.list_runs(uid)}


@app.get("/history/{run_id}")
def history_detail(run_id: str, request: Request) -> dict[str, Any]:
    uid = _current_user_id(request)
    run = history_service.get_run(uid, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/observability/summary")
def observability_summary(request: Request) -> dict[str, Any]:
    _current_user_id(request)
    samples = obs_state["latency_samples"] or [0]
    sorted_samples = sorted(samples)
    p95_idx = min(len(sorted_samples) - 1, int(len(sorted_samples) * 0.95))
    error_rate = (obs_state["errors_total"] / max(1, obs_state["requests_total"])) * 100
    return {
        "requests_total": obs_state["requests_total"],
        "errors_total": obs_state["errors_total"],
        "error_rate_pct": round(error_rate, 2),
        "latency_ms": {
            "avg": round(sum(samples) / max(1, len(samples)), 2),
            "p95": round(sorted_samples[p95_idx], 2),
            "latest": round(samples[-1], 2),
        },
    }


@app.post("/setup")
def setup_interview(body: SetupRequest, request: Request) -> dict[str, Any]:
    logger.info("setup interview type=%s", body.interview_type)
    return service.setup(body.jd_text, body.interview_type, body.session_id)


@app.post("/evaluate")
def evaluate(body: EvaluateRequest, request: Request) -> dict[str, Any]:
    logger.info("evaluate session=%s q=%s", body.session_id, body.question_index)
    if not service.has_session(body.session_id):
        raise HTTPException(status_code=404, detail="Session not found or expired")
    result = service.evaluate(body.session_id, body.question_index, body.answer)
    if result is None:
        raise HTTPException(status_code=400, detail="Question index out of bounds")
    return result


@app.post("/report")
def report(body: ReportRequest, request: Request) -> dict[str, Any]:
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
    try:
        uid = _current_user_id(request)
        history_service.save_run(
            user_id=uid,
            session_id=body.session_id,
            interview_type=result.get("interview_type", "unknown"),
            role_title=result.get("role_title", "Unknown"),
            final_score=int(result.get("final_score", 0)),
            report_json=result,
            transcript_json=body.transcript or [],
        )
    except HTTPException:
        pass
    return result


@app.post("/resume-gap-analysis")
async def resume_gap_analysis(request: Request, jd_text: str = Form(...), resume_file: UploadFile = File(...)) -> dict[str, Any]:
    _current_user_id(request)
    content = await resume_file.read()
    text = ""
    filename = (resume_file.filename or "").lower()
    if filename.endswith(".pdf"):
        try:
            reader = PdfReader(BytesIO(content))
            text = "\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception:
            text = ""
    else:
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception:
            text = ""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract resume text")
    return service.resume_jd_gap(text, jd_text)

