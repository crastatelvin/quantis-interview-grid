from __future__ import annotations

import json
import random
import time
from typing import Any

from openai import OpenAI

from backend.app.config import settings


class GroqClient:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1") if settings.groq_api_key else None
        self.failure_count = 0
        self.circuit_open_until = 0.0

    def available(self) -> bool:
        return self.client is not None

    def chat_text(self, prompt: str) -> str:
        if not self.client:
            return ""
        now = time.time()
        if self.circuit_open_until > now:
            return ""
        for attempt in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=settings.groq_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    timeout=30,
                )
                self.failure_count = 0
                self.circuit_open_until = 0.0
                return (resp.choices[0].message.content or "").strip()
            except Exception:
                self.failure_count += 1
                sleep_s = min(2.5, (0.4 * (2**attempt)) + random.random() * 0.2)
                time.sleep(sleep_s)
        if self.failure_count >= 5:
            self.circuit_open_until = time.time() + 60
        return ""

    def chat_json(self, prompt: str, fallback: dict[str, Any]) -> dict[str, Any]:
        text = self.chat_text(prompt)
        if not text:
            return fallback
        try:
            return json.loads(text)
        except Exception:
            return fallback

