"""Workspace schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import WorkspaceRole
from app.schemas.common import ORMModel


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    logo_text: str | None = Field(default=None, max_length=4)
    settings: dict | None = None


class WorkspaceRead(ORMModel):
    id: uuid.UUID
    name: str
    slug: str
    logo_text: str
    owner_id: uuid.UUID
    settings: dict
    created_at: datetime


class WorkspaceMembershipRead(WorkspaceRead):
    """Workspace plus the caller's role in it."""

    role: WorkspaceRole
