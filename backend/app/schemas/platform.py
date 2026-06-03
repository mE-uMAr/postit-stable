"""Platform schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PlatformRead(ORMModel):
    id: str
    name: str
    color: str
    requires_media: bool
    requires_video: bool
    char_limit: int | None = None
    supports_longform: bool
    is_active: bool
    sort_order: int


class PlatformCreate(BaseModel):
    id: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=64)
    color: str = "#16151A"
    requires_media: bool = False
    requires_video: bool = False
    char_limit: int | None = None
    supports_longform: bool = False
    is_active: bool = True
    sort_order: int = 0


class PlatformUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    requires_media: bool | None = None
    requires_video: bool | None = None
    char_limit: int | None = None
    supports_longform: bool | None = None
    is_active: bool | None = None
    sort_order: int | None = None
