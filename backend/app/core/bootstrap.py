"""Deploy-time database bootstrap: run migrations (and optionally the core seed)
when the app boots, coordinated across instances with a DB advisory lock.

Enabled via RUN_MIGRATIONS_ON_STARTUP / RUN_SEED_ON_STARTUP so local dev and tests
(which manage their own schema) are unaffected.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import bindparam, text

from app.core.config import settings
from app.core.database import engine
from app.core.logging import logger

# Backend root (contains alembic.ini + alembic/), resolved from this file so it
# works regardless of the process working directory.
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_LOCK_NAME = "postit_db_bootstrap"


def _alembic_config() -> Config:
    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    return cfg


def _run_upgrade() -> None:
    # Alembic's env.py drives the async engine via asyncio.run(), which can't run
    # inside an already-running loop — so this is invoked in a worker thread.
    command.upgrade(_alembic_config(), "head")


async def _migrate_and_seed() -> None:
    await asyncio.to_thread(_run_upgrade)
    logger.info("DB migrations applied (alembic upgrade head)")
    if settings.RUN_SEED_ON_STARTUP:
        from app.db.seed import run as seed_run

        await seed_run(core=True, demo=False)
        logger.info("Core seed applied")


async def bootstrap_database() -> None:
    """Apply migrations (+ core seed) on startup. No-op unless enabled."""
    if not settings.RUN_MIGRATIONS_ON_STARTUP:
        return
    if settings.is_sqlite:
        await _migrate_and_seed()
        return
    # MySQL: serialize across workers/instances so a first deploy can't race.
    # Every instance still runs it, but alembic-at-head and the seed are no-ops.
    async with engine.connect() as conn:
        got = await conn.execute(
            text("SELECT GET_LOCK(:name, 120)").bindparams(bindparam("name", _LOCK_NAME))
        )
        if got.scalar() != 1:
            logger.warning("DB bootstrap lock not acquired; proceeding (idempotent)")
        try:
            await _migrate_and_seed()
        finally:
            await conn.execute(
                text("SELECT RELEASE_LOCK(:name)").bindparams(bindparam("name", _LOCK_NAME))
            )
