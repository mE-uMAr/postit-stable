"""Team membership management (invite, role change, removal)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, PermissionError_, ValidationError_
from app.models.enums import MembershipStatus, WorkspaceRole
from app.models.membership import Membership
from app.repositories.user import UserRepository
from app.repositories.workspace import MembershipRepository
from app.schemas.membership import MemberInvite
from app.services import usage as usage_service


async def list_members(db: AsyncSession, workspace_id: uuid.UUID) -> list[dict]:
    rows = await MembershipRepository(db).list_members(workspace_id)
    out: list[dict] = []
    for membership, user in rows:
        name = user.full_name if user else (membership.invited_email or "Invited member")
        email = user.email if user else (membership.invited_email or "")
        avatar = user.initials if user else (email[:2].upper() if email else "??")
        out.append(
            {
                "id": membership.id,
                "role": membership.role,
                "status": membership.status,
                "name": name,
                "email": email,
                "avatar": avatar,
            }
        )
    return out


async def invite_member(
    db: AsyncSession, workspace_id: uuid.UUID, data: MemberInvite
) -> Membership:
    await usage_service.enforce_seat_limit(db, workspace_id)
    repo = MembershipRepository(db)
    users = UserRepository(db)

    existing_user = await users.get_by_email(data.email)
    if existing_user:
        if await repo.get_membership(workspace_id, existing_user.id):
            raise ConflictError("That user is already a member.", code="already_member")
        return await repo.create(
            workspace_id=workspace_id,
            user_id=existing_user.id,
            role=data.role,
            status=MembershipStatus.active,
        )
    # Invite a not-yet-registered user (pending).
    return await repo.create(
        workspace_id=workspace_id,
        invited_email=data.email,
        role=data.role,
        status=MembershipStatus.invited,
    )


async def update_role(
    db: AsyncSession, workspace_id: uuid.UUID, membership_id: uuid.UUID, role: WorkspaceRole
) -> Membership:
    repo = MembershipRepository(db)
    membership = await repo.get(membership_id)
    if membership is None or membership.workspace_id != workspace_id:
        raise NotFoundError("Member not found.", code="member_not_found")
    if membership.role == WorkspaceRole.owner and role != WorkspaceRole.owner:
        raise ValidationError_("Transfer ownership before demoting the owner.", code="owner_demote")
    membership.role = role
    await db.flush()
    return membership


async def remove_member(
    db: AsyncSession, workspace_id: uuid.UUID, membership_id: uuid.UUID
) -> None:
    repo = MembershipRepository(db)
    membership = await repo.get(membership_id)
    if membership is None or membership.workspace_id != workspace_id:
        raise NotFoundError("Member not found.", code="member_not_found")
    if membership.role == WorkspaceRole.owner:
        raise PermissionError_("The workspace owner can't be removed.", code="owner_remove")
    await repo.delete(membership)
