"""Notification preference + log endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import WorkspaceContext, get_current_active_user, get_workspace_ctx
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import Message
from app.schemas.notification import (
    NotificationPrefRead,
    NotificationPrefUpdate,
    NotificationRead,
)
from app.services import notification as notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/preferences", response_model=NotificationPrefRead)
async def get_preferences(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    ctx: WorkspaceContext = Depends(get_workspace_ctx),
):
    return await notification_service.get_preferences(db, user.id, ctx.id)


@router.patch("/preferences", response_model=NotificationPrefRead)
async def update_preferences(
    payload: NotificationPrefUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    ctx: WorkspaceContext = Depends(get_workspace_ctx),
):
    return await notification_service.update_preferences(db, user.id, ctx.id, payload)


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_active_user)
):
    return await notification_service.list_notifications(db, user.id)


@router.post("/{notification_id}/read", response_model=Message)
async def mark_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    await notification_service.mark_read(db, user.id, notification_id)
    return Message(message="Marked as read.")
