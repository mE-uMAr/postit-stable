"""Membership / team schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import MembershipStatus, WorkspaceRole
from app.schemas.common import ORMModel


class MemberInvite(BaseModel):
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.editor


class MemberRoleUpdate(BaseModel):
    role: WorkspaceRole


class MemberRead(ORMModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID | None = None
    invited_email: str | None = None
    role: WorkspaceRole
    status: MembershipStatus
    created_at: datetime
    # Enriched from the related user when available.
    name: str | None = None
    email: str | None = None
    avatar: str | None = None


class MemberWithUser(BaseModel):
    id: uuid.UUID
    role: WorkspaceRole
    status: MembershipStatus
    name: str
    email: str
    avatar: str = Field(default="")
