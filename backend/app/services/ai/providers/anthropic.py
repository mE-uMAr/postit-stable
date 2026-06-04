"""Anthropic Claude provider (Messages API)."""

from __future__ import annotations

import httpx

from app.core.config import settings
from app.services.ai.base import LLMProvider, ProviderError

_DEFAULT_MODEL = "claude-sonnet-4-6"


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    async def generate(
        self, *, system: str, prompt: str, max_tokens: int, temperature: float = 0.7
    ) -> str:
        base = (settings.AI_BASE_URL or "https://api.anthropic.com").rstrip("/")
        model = settings.AI_MODEL or _DEFAULT_MODEL
        try:
            async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                res = await client.post(
                    f"{base}/v1/messages",
                    headers={
                        "x-api-key": settings.AI_API_KEY or "",
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": model,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "system": system,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
            res.raise_for_status()
            data = res.json()
            parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
            text = "".join(parts).strip()
            if not text:
                raise ProviderError("Anthropic returned no text.")
            return text
        except httpx.HTTPError as exc:
            raise ProviderError(f"Anthropic request failed: {exc}") from exc
