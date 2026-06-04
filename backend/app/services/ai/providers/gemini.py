"""Google Gemini provider (Generative Language API)."""

from __future__ import annotations

import httpx

from app.core.config import settings
from app.services.ai.base import LLMProvider, ProviderError

_DEFAULT_BASE = "https://generativelanguage.googleapis.com/v1beta"
_DEFAULT_MODEL = "gemini-1.5-flash"


class GeminiProvider(LLMProvider):
    name = "gemini"

    async def generate(
        self, *, system: str, prompt: str, max_tokens: int, temperature: float = 0.7
    ) -> str:
        base = (settings.AI_BASE_URL or _DEFAULT_BASE).rstrip("/")
        model = settings.AI_MODEL or _DEFAULT_MODEL
        try:
            async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                res = await client.post(
                    f"{base}/models/{model}:generateContent",
                    params={"key": settings.AI_API_KEY or ""},
                    json={
                        "systemInstruction": {"parts": [{"text": system}]},
                        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "maxOutputTokens": max_tokens,
                            "temperature": temperature,
                        },
                    },
                )
            res.raise_for_status()
            data = res.json()
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts).strip()
            if not text:
                raise ProviderError("Gemini returned no text.")
            return text
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise ProviderError(f"Gemini request failed: {exc}") from exc
