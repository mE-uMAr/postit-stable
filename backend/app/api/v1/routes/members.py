"""Team / membership endpoints (scoped to the active workspace)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import WorkspaceContext, get_workspace_ctx, require_workspace_role
from app.core.database import get_db
from app.models.enums import WorkspaceRole
from app.schemas.common import Message
from app.schemas.membership import MemberInvite, MemberRoleUpdate, MemberWithUser
from app.services import membership as membership_service

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=list[MemberWithUser])
async def list_members(
    db: AsyncSession = Depends(get_db), ctx: WorkspaceContext = Depends(get_workspace_ctx)
):
    return await membership_service.list_members(db, ctx.id)


@router.post("", response_model=Message, status_code=201)
async def invite_member(
    payload: MemberInvite,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.admin)),
):
    await membership_service.invite_member(db, ctx.id, payload)
    return Message(message=f"Invitation sent to {payload.email}.")


@router.patch("/{membership_id}", response_model=Message)
async def update_role(
    membership_id: uuid.UUID,
    payload: MemberRoleUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.admin)),
):
    await membership_service.update_role(db, ctx.id, membership_id, payload.role)
    return Message(message="Role updated.")


@router.delete("/{membership_id}", response_model=Message)
async def remove_member(
    membership_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.admin)),
):
    await membership_service.remove_member(db, ctx.id, membership_id)
    return Message(message="Member removed.")
