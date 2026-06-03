"""Workspace provisioning + access helpers."""

from __future__ import annotations

import re
import secrets
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand_voice import BrandVoice
from app.models.enums import SubscriptionStatus
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.billing import PlanRepository, SubscriptionRepository
from app.repositories.workspace import MembershipRepository, WorkspaceRepository


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "workspace"


async def _unique_slug(repo: WorkspaceRepository, name: str) -> str:
    base = _slugify(name)
    slug = base
    while await repo.get_by_slug(slug) is not None:
        slug = f"{base}-{secrets.token_hex(2)}"
    return slug


async def create_workspace(db: AsyncSession, owner: User, name: str) -> Workspace:
    ws_repo = WorkspaceRepository(db)
    members = MembershipRepository(db)

    slug = await _unique_slug(ws_repo, name)
    workspace = await ws_repo.create(
        name=name,
        slug=slug,
        logo_text=name.strip()[:1].upper() or "W",
        owner_id=owner.id,
    )
    await members.add_owner(workspace.id, owner.id)

    # Default brand voice.
    db.add(BrandVoice(workspace_id=workspace.id))

    # Subscribe to the default Free plan if one is seeded.
    plans = PlanRepository(db)
    subs = SubscriptionRepository(db)
    free = await plans.get_by_code("free")
    if free is not None:
        await subs.create(
            workspace_id=workspace.id,
            plan_id=free.id,
            status=SubscriptionStatus.active,
        )

    await db.flush()
    return workspace


async def get_user_role(db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID) -> str | None:
    membership = await MembershipRepository(db).get_membership(workspace_id, user_id)
    return membership.role if membership else None
