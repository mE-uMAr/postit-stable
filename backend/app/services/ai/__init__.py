"""Pluggable AI service. Swap providers via the ``AI_*`` settings.

    from app.services.ai import ai_service
    text = await ai_service.generate_variant(platform=p, body="...", tone="Bold")
"""

from app.services.ai.base import LLMProvider, ProviderError
from app.services.ai.registry import available_providers, get_provider
from app.services.ai.service import AIService, ai_service

__all__ = [
    "ai_service",
    "AIService",
    "LLMProvider",
    "ProviderError",
    "get_provider",
    "available_providers",
]
