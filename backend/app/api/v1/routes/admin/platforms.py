"""Admin platform catalog management."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_delete
from app.core.database import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.platform import PlatformRepository
from app.schemas.platform import PlatformCreate, PlatformRead, PlatformUpdate

router = APIRouter(prefix="/platforms", tags=["admin"])


@router.get("", response_model=list[PlatformRead])
async def list_platforms(db: AsyncSession = Depends(get_db)):
    return await PlatformRepository(db).list_all()


@router.post("", response_model=PlatformRead, status_code=201)
async def create_platform(payload: PlatformCreate, db: AsyncSession = Depends(get_db)):
    repo = PlatformRepository(db)
    if await repo.get(payload.id):
        raise ConflictError("A platform with that id already exists.", code="platform_exists")
    platform = await repo.create(**payload.model_dump())
    await cache_delete("platforms:active")
    return platform


@router.patch("/{platform_id}", response_model=PlatformRead)
async def update_platform(
    platform_id: str, payload: PlatformUpdate, db: AsyncSession = Depends(get_db)
):
    repo = PlatformRepository(db)
    platform = await repo.get(platform_id)
    if platform is None:
        raise NotFoundError("Platform not found.", code="platform_not_found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(platform, key, value)
    await db.flush()
    await cache_delete("platforms:active")
    return platform
