"""Admin server-error log listing."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.pagination import Page, PageParams, paginate
from app.models.error_log import ErrorLog
from app.schemas.admin import ErrorLogRead

router = APIRouter(prefix="/errors", tags=["admin"])


@router.get("", response_model=Page[ErrorLogRead])
async def list_errors(
    status_code: int | None = Query(default=None),
    params: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ErrorLog)
    if status_code is not None:
        stmt = stmt.where(ErrorLog.status_code == status_code)
    stmt = stmt.order_by(ErrorLog.created_at.desc())
    rows, total = await paginate(db, stmt, params)
    return Page.create([ErrorLogRead.model_validate(r) for r in rows], total, params)
