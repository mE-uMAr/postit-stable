"""Admin audit-log listing."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.pagination import Page, PageParams, paginate
from app.models.audit_log import AuditLog
from app.schemas.admin import AuditLogRead

router = APIRouter(prefix="/audit", tags=["admin"])


@router.get("", response_model=Page[AuditLogRead])
async def list_audit(
    action: str | None = Query(default=None),
    workspace_id: uuid.UUID | None = Query(default=None),
    params: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AuditLog)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if workspace_id:
        stmt = stmt.where(AuditLog.workspace_id == workspace_id)
    stmt = stmt.order_by(AuditLog.created_at.desc())
    rows, total = await paginate(db, stmt, params)
    return Page.create([AuditLogRead.model_validate(r) for r in rows], total, params)
