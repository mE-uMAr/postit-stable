"""Admin (superuser) schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import SubscriptionStatus
from app.schemas.common import ORMModel
from app.schemas.user import UserRead


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None
    full_name: str | None = None


class AdminUserRead(UserRead):
    workspace_count: int = 0


class AdminWorkspaceRead(ORMModel):
    id: uuid.UUID
    name: str
    slug: str
    owner_id: uuid.UUID
    created_at: datetime
    member_count: int = 0
    post_count: int = 0
    plan_name: str | None = None


class AdminSubscriptionRead(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    workspace_name: str
    plan_name: str
    status: SubscriptionStatus
    billing_cycle: str
    mrr_cents: int
    current_period_end: datetime | None = None


class AdminSubscriptionOverride(BaseModel):
    plan_id: uuid.UUID
    status: SubscriptionStatus | None = None


class AdminMetrics(BaseModel):
    total_users: int
    active_users: int
    new_users_30d: int
    total_workspaces: int
    active_workspaces: int
    total_posts: int
    posts_published: int
    paying_subscriptions: int
    mrr_cents: int
    arr_cents: int
    plan_distribution: dict[str, int]


class AuditLogRead(ORMModel):
    id: uuid.UUID
    actor_id: uuid.UUID | None = None
    workspace_id: uuid.UUID | None = None
    action: str
    target_type: str | None = None
    target_id: str | None = None
    meta: dict | None = None
    ip: str | None = None
    created_at: datetime
