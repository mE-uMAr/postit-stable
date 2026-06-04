"""LLM provider contract.

Adding a new provider = implement :class:`LLMProvider.generate` and register the
class in :mod:`app.services.ai.registry`. Everything else (prompting, fallback,
char-limit trimming) lives in :class:`app.services.ai.service.AIService`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderError(Exception):
    """Raised when a provider call fails; the service falls back to the mock."""


class LLMProvider(ABC):
    #: stable identifier, also the value of ``AI_PROVIDER``
    name: str = "base"

    @abstractmethod
    async def generate(
        self, *, system: str, prompt: str, max_tokens: int, temperature: float = 0.7
    ) -> str:
        """Return the model's completion text. Raise :class:`ProviderError` on failure."""
        raise NotImplementedError
