"""User profile updates."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdate


async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
    changes = data.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(user, key, value)
    await db.flush()
    return user
