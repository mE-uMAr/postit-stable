"""Repositories for notifications, brand voice, audit logs, analytics."""

from __future__ import annotations

import uuid

from app.models.analytics import AnalyticsDaily
from app.models.audit_log import AuditLog
from app.models.brand_voice import BrandVoice
from app.models.notification import Notification, NotificationPreference
from app.repositories.base import BaseRepository


class NotificationPrefRepository(BaseRepository[NotificationPreference]):
    model = NotificationPreference

    async def get_or_create(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> NotificationPreference:
        existing = await self.find_one(
            NotificationPreference.user_id == user_id,
            NotificationPreference.workspace_id == workspace_id,
        )
        if existing:
            return existing
        return await self.create(user_id=user_id, workspace_id=workspace_id)


class NotificationRepository(BaseRepository[Notification]):
    model = Notification

    async def list_for_user(self, user_id: uuid.UUID, limit: int = 30) -> list[Notification]:
        return list(
            await self.list(
                Notification.user_id == user_id,
                order_by=Notification.created_at.desc(),
                limit=limit,
            )
        )


class BrandVoiceRepository(BaseRepository[BrandVoice]):
    model = BrandVoice

    async def get_for_workspace(self, workspace_id: uuid.UUID) -> BrandVoice | None:
        return await self.find_one(BrandVoice.workspace_id == workspace_id)


class AuditRepository(BaseRepository[AuditLog]):
    model = AuditLog


class AnalyticsDailyRepository(BaseRepository[AnalyticsDaily]):
    model = AnalyticsDaily
