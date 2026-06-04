"""Post + target schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import PostStatus, TargetStatus
from app.schemas.common import ORMModel


class MediaItem(BaseModel):
    type: str = Field(pattern="^(image|video)$")
    id: str | None = None


class PostCreate(BaseModel):
    body: str = Field(default="", max_length=20000)
    title: str | None = Field(default=None, max_length=160)
    tone: str = Field(default="Match my brand", max_length=40)
    media: list[MediaItem] = Field(default_factory=list)


class PostUpdate(BaseModel):
    body: str | None = Field(default=None, max_length=20000)
    title: str | None = Field(default=None, max_length=160)
    tone: str | None = Field(default=None, max_length=40)
    media: list[MediaItem] | None = None
    # Optional optimistic-concurrency guard; when present must match the server version.
    version: int | None = Field(default=None, ge=0)


class GenerateRequest(BaseModel):
    """Generate native variants for the given platforms."""

    platforms: list[str] = Field(min_length=1)


class TargetUpdate(BaseModel):
    content: str = Field(max_length=20000)


class ScheduleRequest(BaseModel):
    scheduled_at: datetime


class TargetRead(ORMModel):
    id: uuid.UUID
    post_id: uuid.UUID
    platform_id: str
    connection_id: uuid.UUID | None = None
    content: str
    edited: bool
    status: TargetStatus
    external_post_id: str | None = None
    error: str | None = None
    published_at: datetime | None = None


class PostRead(ORMModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    author_id: uuid.UUID | None = None
    title: str
    body: str
    tone: str
    media: list
    status: PostStatus
    version: int = 1
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    targets: list[TargetRead] = Field(default_factory=list)
