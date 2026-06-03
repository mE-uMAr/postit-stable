"""Admin workspace listing."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.pagination import Page, PageParams
from app.schemas.admin import AdminWorkspaceRead
from app.schemas.workspace import WorkspaceRead
from app.services import admin as admin_service

router = APIRouter(prefix="/workspaces", tags=["admin"])


@router.get("", response_model=Page[AdminWorkspaceRead])
async def list_workspaces(params: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    rows, total = await admin_service.list_workspaces(db, params.offset, params.limit)
    items = [
        AdminWorkspaceRead(
            **WorkspaceRead.model_validate(r["workspace"]).model_dump(
                include={"id", "name", "slug", "owner_id", "created_at"}
            ),
            member_count=r["member_count"],
            post_count=r["post_count"],
            plan_name=r["plan_name"],
        )
        for r in rows
    ]
    return Page.create(items, total, params)
