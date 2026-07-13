"""Provider selection driven by settings (``AI_PROVIDER`` / ``AI_API_KEY``)."""

from __future__ import annotations

from app.core.config import settings
from app.services.ai.base import LLMProvider
from app.services.ai.providers.anthropic import AnthropicProvider
from app.services.ai.providers.gemini import GeminiProvider
from app.services.ai.providers.groq import GroqProvider
from app.services.ai.providers.grok import GrokProvider
from app.services.ai.providers.mock import MockProvider
from app.services.ai.providers.openai import OpenAIProvider

_REGISTRY: dict[str, type[LLMProvider]] = {
    "mock": MockProvider,
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "groq": GroqProvider,
    "grok": GrokProvider,
    "gork": GrokProvider,
    "gemini": GeminiProvider,
}


def get_provider() -> LLMProvider:
    """Return the configured provider, or the mock when AI is off/unconfigured.

    A real provider requires both ``AI_ENABLED`` and an ``AI_API_KEY``; otherwise
    the deterministic mock is used so the app always works offline.
    """
    if not settings.AI_ENABLED:
        return MockProvider()
    name = (settings.AI_PROVIDER or "mock").lower()
    cls = _REGISTRY.get(name, MockProvider)
    if cls is MockProvider or name == "mock":
        return MockProvider()
    if not settings.AI_API_KEY:
        return MockProvider()
    return cls()


def available_providers() -> list[str]:
    return list(_REGISTRY.keys())
