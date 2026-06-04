"""Admin site-content editor (superuser-only via the admin router)."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_delete
from app.core.database import get_db
from app.services import site as site_service

router = APIRouter(prefix="/site", tags=["admin"])


@router.get("")
async def get_site(db: AsyncSession = Depends(get_db)) -> dict:
    return await site_service.get_content(db)


@router.put("")
async def update_site(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    content = await site_service.set_content(db, payload)
    await cache_delete("site:content")
    return content
