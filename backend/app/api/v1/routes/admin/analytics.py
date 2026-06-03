"""Admin platform-wide metrics."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.admin import AdminMetrics
from app.services import admin as admin_service

router = APIRouter(tags=["admin"])


@router.get("/metrics", response_model=AdminMetrics)
async def metrics(db: AsyncSession = Depends(get_db)):
    return await admin_service.get_metrics(db)
