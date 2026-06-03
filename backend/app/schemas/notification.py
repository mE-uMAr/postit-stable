"""Notification schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import NotificationType
from app.schemas.common import ORMModel


class NotificationPrefRead(ORMModel):
    published: bool
    failed: bool
    weekly: bool
    suggestions: bool


class NotificationPrefUpdate(BaseModel):
    published: bool | None = None
    failed: bool | None = None
    weekly: bool | None = None
    suggestions: bool | None = None


class NotificationRead(ORMModel):
    id: uuid.UUID
    type: NotificationType
    title: str
    body: str | None = None
    read_at: datetime | None = None
    created_at: datetime
