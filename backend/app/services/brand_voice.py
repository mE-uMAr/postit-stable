"""Brand voice get/update."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand_voice import BrandVoice
from app.repositories.misc import BrandVoiceRepository
from app.schemas.brand_voice import BrandVoiceUpdate


async def get_brand_voice(db: AsyncSession, workspace_id: uuid.UUID) -> BrandVoice:
    repo = BrandVoiceRepository(db)
    voice = await repo.get_for_workspace(workspace_id)
    if voice is None:
        voice = await repo.create(workspace_id=workspace_id)
    return voice


async def update_brand_voice(
    db: AsyncSession, workspace_id: uuid.UUID, data: BrandVoiceUpdate
) -> BrandVoice:
    voice = await get_brand_voice(db, workspace_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(voice, key, value)
    await db.flush()
    return voice
