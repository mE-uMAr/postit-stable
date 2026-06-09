"""Public site content (no auth) - consumed by the marketing landing page."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get, cache_set
from app.core.database import get_db
from app.services import site as site_service

router = APIRouter(prefix="/site", tags=["site"])

_CACHE_KEY = "site:content"
_CACHE_TTL = 60


@router.get("/content")
async def get_site_content(db: AsyncSession = Depends(get_db)) -> dict:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    content = await site_service.get_content(db)
    await cache_set(_CACHE_KEY, content, _CACHE_TTL)
    return content
