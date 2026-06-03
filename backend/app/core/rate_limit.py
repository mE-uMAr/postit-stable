"""Fixed-window rate limiting over the KV backend."""

from __future__ import annotations

import time

from app.core.config import settings
from app.core.redis import get_kv


async def check_rate_limit(identifier: str, limit: int | None = None, window: int = 60) -> tuple[bool, int]:
    """Return ``(allowed, remaining)`` for ``identifier`` in the current window."""
    if not settings.RATE_LIMIT_ENABLED:
        return True, limit or settings.RATE_LIMIT_PER_MINUTE
    limit = limit or settings.RATE_LIMIT_PER_MINUTE
    window_id = int(time.time()) // window
    key = f"ratelimit:{identifier}:{window_id}"
    count = await get_kv().incr(key, ttl=window)
    remaining = max(0, limit - count)
    return count <= limit, remaining
