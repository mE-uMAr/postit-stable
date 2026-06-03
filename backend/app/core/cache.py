"""Tiny JSON cache helper over the KV backend (read-path caching)."""

from __future__ import annotations

import orjson
from typing import Any

from app.core.redis import get_kv

_PREFIX = "cache:"


async def cache_get(key: str) -> Any | None:
    raw = await get_kv().get(_PREFIX + key)
    if raw is None:
        return None
    try:
        return orjson.loads(raw)
    except orjson.JSONDecodeError:
        return None


async def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    await get_kv().set(_PREFIX + key, orjson.dumps(value).decode(), ttl=ttl)


async def cache_delete(*keys: str) -> None:
    await get_kv().delete(*[_PREFIX + k for k in keys])
