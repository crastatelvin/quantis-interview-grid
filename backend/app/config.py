from __future__ import annotations

import os
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_ROOT / ".env", override=True)


@dataclass(frozen=True)
class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    cors_origins: list[str] = field(
        default_factory=lambda: [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
    )
    session_ttl_minutes: int = int(os.getenv("SESSION_TTL_MINUTES", "120"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./quantis_interview_grid.db",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    jwt_secret: str = os.getenv("JWT_SECRET", "change_me")
    jwt_expire_hours: int = int(os.getenv("JWT_EXPIRE_HOURS", "72"))


settings = Settings()

