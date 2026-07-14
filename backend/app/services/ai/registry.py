"""Provider selection driven by settings (``AI_PROVIDER`` / ``AI_API_KEY``)."""

from __future__ import annotations

from app.core.config import settings
from app.core.logging import logger
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


def _guess_provider_from_key(api_key: str) -> str | None:
    """Infer the provider name from well-known API key prefixes.

    Groq  → ``gsk_…``  |  Anthropic → ``sk-ant-…``
    OpenAI → ``sk-…``  |  Grok (xAI) → ``xai-…``
    """
    key = api_key.strip()
    if key.startswith("gsk_"):
        return "groq"
    if key.startswith("sk-ant-"):
        return "anthropic"
    if key.startswith("sk-"):
        return "openai"
    if key.startswith("xai-"):
        return "grok"
    return None


def get_provider() -> LLMProvider:
    """Return the configured provider, or the mock when AI is off/unconfigured.

    A real provider requires both ``AI_ENABLED`` and an ``AI_API_KEY``; otherwise
    the deterministic mock is used so the app always works offline.

    When ``AI_PROVIDER`` is left at the default ``mock`` *but* an ``AI_API_KEY``
    is present, the provider is auto-detected from the key prefix so operators
    don't have to remember to set both variables.
    """
    if not settings.AI_ENABLED:
        return MockProvider()

    name = (settings.AI_PROVIDER or "mock").lower()

    # Auto-detect: API key is set but provider wasn't explicitly configured.
    if name == "mock" and settings.AI_API_KEY:
        guessed = _guess_provider_from_key(settings.AI_API_KEY)
        if guessed:
            logger.info(
                "AI_PROVIDER is 'mock' but AI_API_KEY looks like %s — auto-selecting provider",
                guessed,
            )
            name = guessed

    cls = _REGISTRY.get(name, MockProvider)
    if cls is MockProvider or name == "mock":
        return MockProvider()
    if not settings.AI_API_KEY:
        return MockProvider()
    return cls()


def available_providers() -> list[str]:
    return list(_REGISTRY.keys())

