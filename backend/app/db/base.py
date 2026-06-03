"""Schema bootstrap helpers (used by tests and the seed script)."""

from __future__ import annotations

from app.core.database import Base, engine
from app.models import *  # noqa: F401,F403  (register all tables on Base.metadata)


async def create_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
