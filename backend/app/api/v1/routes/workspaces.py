"""Workspace endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    WorkspaceContext,
    get_current_active_user,
    get_workspace_ctx,
    require_workspace_role,
)
from app.core.database import get_db
from app.core.exceptions import NotFoundError, PermissionError_
from app.models.enums import WorkspaceRole
from app.models.user import User
from app.repositories.workspace import MembershipRepository, WorkspaceRepository
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceMembershipRead,
    WorkspaceRead,
    WorkspaceUpdate,
)
from app.services import workspace as workspace_service

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceMembershipRead])
async def list_my_workspaces(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_active_user)
):
    rows = await MembershipRepository(db).list_for_user(user.id)
    return [
        WorkspaceMembershipRead(**WorkspaceRead.model_validate(ws).model_dump(), role=m.role)
        for m, ws in rows
    ]


@router.post("", response_model=WorkspaceMembershipRead, status_code=201)
async def create_workspace(
    payload: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    ws = await workspace_service.create_workspace(db, user, payload.name)
    return WorkspaceMembershipRead(
        **WorkspaceRead.model_validate(ws).model_dump(), role=WorkspaceRole.owner
    )


@router.get("/current", response_model=WorkspaceMembershipRead)
async def current_workspace(ctx: WorkspaceContext = Depends(get_workspace_ctx)):
    return WorkspaceMembershipRead(
        **WorkspaceRead.model_validate(ctx.workspace).model_dump(), role=ctx.role
    )


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    workspace_id: uuid.UUID,
    payload: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.admin)),
):
    if ctx.workspace.id != workspace_id:
        raise PermissionError_("You can only edit the active workspace.", code="workspace_mismatch")
    ws = await WorkspaceRepository(db).get(workspace_id)
    if ws is None:
        raise NotFoundError("Workspace not found.", code="workspace_not_found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(ws, key, value)
    await db.flush()
    return ws
