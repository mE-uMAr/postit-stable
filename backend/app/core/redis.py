"""Redis client with a graceful in-memory fallback.

When ``REDIS_URL`` is unset (or Redis is unreachable), an in-process backend is used
so the app runs in any environment. The interface used by cache / rate-limit / denylist
is the small subset below.
"""

from __future__ import annotations

import time
from typing import Protocol

from app.core.config import settings
from app.core.logging import logger


class KVBackend(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl: int | None = None) -> None: ...
    async def delete(self, *keys: str) -> None: ...
    async def incr(self, key: str, ttl: int) -> int: ...
    async def exists(self, key: str) -> bool: ...
    async def ping(self) -> bool: ...


class InMemoryBackend:
    """Best-effort single-process KV with TTL. Not for multi-worker production."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float | None]] = {}

    def _expired(self, key: str) -> bool:
        item = self._store.get(key)
        if item is None:
            return True
        _, exp = item
        if exp is not None and exp < time.monotonic():
            self._store.pop(key, None)
            return True
        return False

    async def get(self, key: str) -> str | None:
        if self._expired(key):
            return None
        return self._store[key][0]

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        exp = time.monotonic() + ttl if ttl else None
        self._store[key] = (value, exp)

    async def delete(self, *keys: str) -> None:
        for k in keys:
            self._store.pop(k, None)

    async def incr(self, key: str, ttl: int) -> int:
        current = 0 if self._expired(key) else int(self._store[key][0])
        current += 1
        exp = self._store[key][1] if (key in self._store and not self._expired(key)) else None
        if exp is None:
            exp = time.monotonic() + ttl
        self._store[key] = (str(current), exp)
        return current

    async def exists(self, key: str) -> bool:
        return not self._expired(key)

    async def ping(self) -> bool:
        return True


class RedisBackend:
    def __init__(self, client) -> None:  # noqa: ANN001
        self._c = client

    async def get(self, key: str) -> str | None:
        return await self._c.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        await self._c.set(key, value, ex=ttl)

    async def delete(self, *keys: str) -> None:
        if keys:
            await self._c.delete(*keys)

    async def incr(self, key: str, ttl: int) -> int:
        value = await self._c.incr(key)
        if value == 1:
            await self._c.expire(key, ttl)
        return int(value)

    async def exists(self, key: str) -> bool:
        return bool(await self._c.exists(key))

    async def ping(self) -> bool:
        try:
            return bool(await self._c.ping())
        except Exception:
            return False


_backend: KVBackend | None = None


async def init_kv() -> KVBackend:
    """Initialise the KV backend at startup; called from the app lifespan."""
    global _backend
    if _backend is not None:
        return _backend
    if settings.REDIS_URL:
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            backend = RedisBackend(client)
            if await backend.ping():
                logger.info("Connected to Redis")
                _backend = backend
                return _backend
            logger.warning("Redis ping failed; using in-memory KV fallback")
        except Exception as exc:  # pragma: no cover
            logger.warning("Redis unavailable (%s); using in-memory KV fallback", exc)
    _backend = InMemoryBackend()
    return _backend


def get_kv() -> KVBackend:
    global _backend
    if _backend is None:
        _backend = InMemoryBackend()
    return _backend
