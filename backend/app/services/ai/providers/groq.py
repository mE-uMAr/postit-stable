"""Groq provider — OpenAI-compatible API with a different base URL/model."""

from __future__ import annotations

from app.core.config import settings
from app.services.ai.providers.openai import OpenAIProvider


class GroqProvider(OpenAIProvider):
    name = "groq"
    default_base_url = "https://api.groq.com/openai/v1"
    default_model = "llama-3.3-70b-versatile"

    def _base_url(self) -> str:
        # Honour an explicit override, else Groq's endpoint (not OpenAI's).
        return (settings.AI_BASE_URL or self.default_base_url).rstrip("/")
