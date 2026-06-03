"""Notification preferences + log."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.notification import NotificationPreference
from app.repositories.misc import NotificationPrefRepository, NotificationRepository
from app.schemas.notification import NotificationPrefUpdate


async def get_preferences(
    db: AsyncSession, user_id: uuid.UUID, workspace_id: uuid.UUID
) -> NotificationPreference:
    return await NotificationPrefRepository(db).get_or_create(user_id, workspace_id)


async def update_preferences(
    db: AsyncSession, user_id: uuid.UUID, workspace_id: uuid.UUID, data: NotificationPrefUpdate
) -> NotificationPreference:
    pref = await NotificationPrefRepository(db).get_or_create(user_id, workspace_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(pref, key, value)
    await db.flush()
    return pref


async def list_notifications(db: AsyncSession, user_id: uuid.UUID):
    return await NotificationRepository(db).list_for_user(user_id)


async def mark_read(db: AsyncSession, user_id: uuid.UUID, notification_id: uuid.UUID):
    repo = NotificationRepository(db)
    notif = await repo.get(notification_id)
    if notif is None or notif.user_id != user_id:
        raise NotFoundError("Notification not found.", code="notification_not_found")
    notif.read_at = datetime.now(timezone.utc)
    await db.flush()
    return notif
