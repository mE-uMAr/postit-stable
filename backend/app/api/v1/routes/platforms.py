"""Public platform catalog (cached)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get, cache_set
from app.core.database import get_db
from app.repositories.platform import PlatformRepository
from app.schemas.platform import PlatformRead

router = APIRouter(prefix="/platforms", tags=["platforms"])

_CACHE_KEY = "platforms:active"


@router.get("", response_model=list[PlatformRead])
async def list_platforms(db: AsyncSession = Depends(get_db)):
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    platforms = await PlatformRepository(db).list_active()
    data = [PlatformRead.model_validate(p).model_dump() for p in platforms]
    await cache_set(_CACHE_KEY, data, ttl=300)
    return data
