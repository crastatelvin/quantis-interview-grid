from __future__ import annotations

from typing import Optional

import redis

from backend.app.config import settings


class SessionCache:
    def __init__(self) -> None:
        self._client = None
        try:
            self._client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            self._client.ping()
        except Exception:
            self._client = None

    def available(self) -> bool:
        return self._client is not None

    def get(self, session_id: str) -> Optional[str]:
        if not self._client:
            return None
        try:
            return self._client.get(f"session:{session_id}")
        except Exception:
            return None

    def set(self, session_id: str, payload: str, ttl_seconds: int) -> None:
        if not self._client:
            return
        try:
            self._client.setex(f"session:{session_id}", ttl_seconds, payload)
        except Exception:
            return

    def delete(self, session_id: str) -> None:
        if not self._client:
            return
        try:
            self._client.delete(f"session:{session_id}")
        except Exception:
            return

