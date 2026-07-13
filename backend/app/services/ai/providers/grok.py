"""Grok provider (xAI) - OpenAI-compatible API with a different base URL/model."""

from __future__ import annotations

from app.core.config import settings
from app.services.ai.providers.openai import OpenAIProvider


class GrokProvider(OpenAIProvider):
    name = "grok"
    default_base_url = "https://api.x.ai/v1"
    default_model = "grok-beta"

    def _base_url(self) -> str:
        # Honour an explicit override, else Grok's endpoint (not OpenAI's).
        return (settings.AI_BASE_URL or self.default_base_url).rstrip("/")
