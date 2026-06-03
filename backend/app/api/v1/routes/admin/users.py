"""Admin user management."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.exceptions import ValidationError_
from app.core.pagination import Page, PageParams
from app.models.user import User
from app.schemas.admin import AdminUserRead, AdminUserUpdate
from app.schemas.common import Message
from app.services import admin as admin_service
from app.services.audit import record_audit

router = APIRouter(prefix="/users", tags=["admin"])


@router.get("", response_model=Page[AdminUserRead])
async def list_users(
    q: str | None = Query(default=None),
    params: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await admin_service.list_users(db, q, params.offset, params.limit)
    items = [
        AdminUserRead(**AdminUserRead.model_validate(u).model_dump() | {"workspace_count": wc})
        for u, wc in rows
    ]
    return Page.create(items, total, params)


@router.get("/{user_id}", response_model=AdminUserRead)
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await admin_service.get_user(db, user_id)


@router.patch("/{user_id}", response_model=AdminUserRead)
async def update_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_user),
):
    user = await admin_service.get_user(db, user_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    await db.flush()
    await record_audit(
        db, action="admin.user.updated", actor_id=admin.id, target_type="user", target_id=str(user_id)
    )
    return user


@router.delete("/{user_id}", response_model=Message)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_user),
):
    if user_id == admin.id:
        raise ValidationError_("You can't delete your own account here.", code="self_delete")
    user = await admin_service.get_user(db, user_id)
    user.deleted_at = datetime.now(timezone.utc)
    user.is_active = False
    await record_audit(
        db, action="admin.user.deleted", actor_id=admin.id, target_type="user", target_id=str(user_id)
    )
    return Message(message="User deleted.")
