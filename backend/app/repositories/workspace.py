"""Workspace + membership repositories."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.enums import MembershipStatus, WorkspaceRole
from app.models.membership import Membership
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    model = Workspace

    async def get_by_slug(self, slug: str) -> Workspace | None:
        return await self.find_one(Workspace.slug == slug)


class MembershipRepository(BaseRepository[Membership]):
    model = Membership

    async def get_membership(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> Membership | None:
        return await self.find_one(
            Membership.workspace_id == workspace_id, Membership.user_id == user_id
        )

    async def list_for_user(self, user_id: uuid.UUID) -> list[tuple[Membership, Workspace]]:
        stmt = (
            select(Membership, Workspace)
            .join(Workspace, Workspace.id == Membership.workspace_id)
            .where(
                Membership.user_id == user_id,
                Membership.status == MembershipStatus.active,
                Workspace.deleted_at.is_(None),
            )
            .order_by(Workspace.created_at.asc())
        )
        return [(m, w) for m, w in (await self.db.execute(stmt)).all()]

    async def list_members(self, workspace_id: uuid.UUID) -> list[tuple[Membership, User | None]]:
        stmt = (
            select(Membership, User)
            .outerjoin(User, User.id == Membership.user_id)
            .where(Membership.workspace_id == workspace_id)
            .order_by(Membership.created_at.asc())
        )
        return [(m, u) for m, u in (await self.db.execute(stmt)).all()]

    async def count_active(self, workspace_id: uuid.UUID) -> int:
        return await self.count(
            Membership.workspace_id == workspace_id,
            Membership.status == MembershipStatus.active,
        )

    async def add_owner(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> Membership:
        return await self.create(
            workspace_id=workspace_id,
            user_id=user_id,
            role=WorkspaceRole.owner,
            status=MembershipStatus.active,
        )
