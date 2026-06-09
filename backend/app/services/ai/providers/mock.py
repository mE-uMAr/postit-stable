"""Deterministic offline provider - the default and the universal fallback."""

from __future__ import annotations

from app.services.ai.base import LLMProvider


class MockProvider(LLMProvider):
    name = "mock"

    async def generate(
        self, *, system: str, prompt: str, max_tokens: int, temperature: float = 0.7
    ) -> str:
        # The service short-circuits to the heuristic rewriter for the mock
        # provider, so this is only a safety net if called directly.
        return prompt.strip()
