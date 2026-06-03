"""Analytics endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import WorkspaceContext, get_workspace_ctx
from app.core.database import get_db
from app.schemas.analytics import AnalyticsResponse
from app.services import analytics as analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    range_days: int = Query(default=30, ge=1, le=365, alias="range"),
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(get_workspace_ctx),
):
    return await analytics_service.get_analytics(db, ctx.id, range_days)
