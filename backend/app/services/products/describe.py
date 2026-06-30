"""Optional AI product-description generation.

The AliExpress affiliate API doesn't return a rich description, so (like the
original plugin's Groq call) we synthesise one from the title using whatever AI
provider is configured. Always degrades to a simple fallback — never raises.
"""

from __future__ import annotations

from app.core.logging import logger
from app.services.ai.registry import get_provider

_SYSTEM = (
    "You are an e-commerce copywriter. Write a concise, engaging product description "
    "(2-4 short sentences) suitable for a social post. Return only the description."
)


async def generate_description(title: str, *, source: str) -> str:
    fallback = f"{title} — available now via {source}."
    provider = get_provider()
    if provider.name == "mock":
        return fallback
    try:
        text = await provider.generate(
            system=_SYSTEM,
            prompt=f"Product title: {title}\n\nWrite the description.",
            max_tokens=220,
        )
        text = text.strip().strip('"')
        return text or fallback
    except Exception:  # noqa: BLE001 - any provider failure → deterministic fallback
        logger.warning("AI description failed for product import; using fallback", exc_info=True)
        return fallback
