"""Liveness + readiness probes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_kv
from app.services.ai import ai_service

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "service": settings.PROJECT_NAME, "env": settings.ENVIRONMENT}


@router.get("/readyz")
async def readyz(db: AsyncSession = Depends(get_db)) -> dict:
    db_ok = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    kv_ok = await get_kv().ping()
    ready = db_ok
    return {
        "ready": ready,
        "checks": {
            "database": db_ok,
            "kv": kv_ok,
            "paddle": settings.paddle_enabled,
            "ai": {"enabled": ai_service.enabled, "provider": ai_service.provider_name},
        },
    }
