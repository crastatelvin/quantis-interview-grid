from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from backend.app.config import settings


class GroqClient:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1") if settings.groq_api_key else None

    def available(self) -> bool:
        return self.client is not None

    def chat_text(self, prompt: str) -> str:
        if not self.client:
            return ""
        try:
            resp = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception:
            return ""

    def chat_json(self, prompt: str, fallback: dict[str, Any]) -> dict[str, Any]:
        text = self.chat_text(prompt)
        if not text:
            return fallback
        try:
            return json.loads(text)
        except Exception:
            return fallback

