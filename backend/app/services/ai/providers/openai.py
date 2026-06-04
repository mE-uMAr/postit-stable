"""OpenAI-compatible Chat Completions provider.

Works for OpenAI directly and for any OpenAI-compatible gateway via ``AI_BASE_URL``
(used by :class:`app.services.ai.providers.groq.GroqProvider`).
"""

from __future__ import annotations

import httpx

from app.core.config import settings
from app.services.ai.base import LLMProvider, ProviderError


class OpenAIProvider(LLMProvider):
    name = "openai"
    default_base_url = "https://api.openai.com/v1"
    default_model = "gpt-4o-mini"

    def _base_url(self) -> str:
        return (settings.AI_BASE_URL or self.default_base_url).rstrip("/")

    async def generate(
        self, *, system: str, prompt: str, max_tokens: int, temperature: float = 0.7
    ) -> str:
        model = settings.AI_MODEL or self.default_model
        try:
            async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                res = await client.post(
                    f"{self._base_url()}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.AI_API_KEY or ''}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                    },
                )
            res.raise_for_status()
            data = res.json()
            text = (data["choices"][0]["message"]["content"] or "").strip()
            if not text:
                raise ProviderError(f"{self.name} returned no text.")
            return text
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise ProviderError(f"{self.name} request failed: {exc}") from exc
