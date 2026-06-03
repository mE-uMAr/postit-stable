"""User + refresh-token repositories."""

from __future__ import annotations

from sqlalchemy import select

from app.models.auth import RefreshToken
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        return await self.find_one(User.email == email.lower().strip())


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return await self.find_one(RefreshToken.token_hash == token_hash)

    async def revoke_all_for_user(self, user_id, when) -> None:  # noqa: ANN001
        rows = (
            await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
                )
            )
        ).scalars().all()
        for r in rows:
            r.revoked_at = when
