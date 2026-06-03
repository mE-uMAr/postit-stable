"""Brand voice endpoints (scoped to the active workspace)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import WorkspaceContext, get_workspace_ctx, require_workspace_role
from app.core.database import get_db
from app.models.enums import WorkspaceRole
from app.schemas.brand_voice import BrandVoiceRead, BrandVoiceUpdate
from app.services import brand_voice as brand_voice_service

router = APIRouter(prefix="/brand-voice", tags=["brand-voice"])


@router.get("", response_model=BrandVoiceRead)
async def get_brand_voice(
    db: AsyncSession = Depends(get_db), ctx: WorkspaceContext = Depends(get_workspace_ctx)
):
    return await brand_voice_service.get_brand_voice(db, ctx.id)


@router.put("", response_model=BrandVoiceRead)
async def update_brand_voice(
    payload: BrandVoiceUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.admin)),
):
    return await brand_voice_service.update_brand_voice(db, ctx.id, payload)
