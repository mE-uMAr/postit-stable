"""Authentication: registration, login, JWT issuance & refresh rotation."""

from __future__ import annotations

from datetime import datetime, timezone

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthError, ConflictError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    refresh_token_expiry,
    sha256,
    verify_password,
)
from app.models.user import User
from app.repositories.user import RefreshTokenRepository, UserRepository
from app.repositories.workspace import MembershipRepository
from app.schemas.token import TokenPair
from app.services import workspace as workspace_service


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def register(
    db: AsyncSession, *, full_name: str, email: str, password: str, workspace_name: str | None
) -> User:
    users = UserRepository(db)
    email = email.lower().strip()
    if await users.get_by_email(email):
        raise ConflictError("An account with that email already exists.", code="email_taken")

    user = await users.create(
        full_name=full_name.strip(),
        email=email,
        hashed_password=hash_password(password),
        is_verified=False,
    )
    await workspace_service.create_workspace(db, user, workspace_name or f"{full_name}'s Workspace")
    return user


async def authenticate(db: AsyncSession, *, email: str, password: str) -> User:
    users = UserRepository(db)
    user = await users.get_by_email(email.lower().strip())
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Incorrect email or password.", code="invalid_credentials")
    if not user.is_active:
        raise AuthError("This account is disabled.", code="account_disabled")
    user.last_login_at = _now()
    return user


async def issue_tokens(
    db: AsyncSession, user: User, *, user_agent: str | None = None, ip: str | None = None
) -> TokenPair:
    extra = {"is_superuser": user.is_superuser}
    access, _ = create_access_token(str(user.id), extra=extra)
    refresh, jti = create_refresh_token(str(user.id))

    tokens = RefreshTokenRepository(db)
    await tokens.create(
        user_id=user.id,
        token_hash=sha256(jti),
        expires_at=refresh_token_expiry(),
        user_agent=(user_agent or "")[:255] or None,
        ip=(ip or "")[:64] or None,
    )
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_TTL_MINUTES * 60,
    )


async def refresh_tokens(
    db: AsyncSession, refresh_token: str, *, user_agent: str | None = None, ip: str | None = None
) -> TokenPair:
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid or expired refresh token.", code="invalid_refresh") from exc

    user_id = payload["sub"]
    jti = payload["jti"]
    tokens = RefreshTokenRepository(db)
    record = await tokens.get_by_hash(sha256(jti))

    if record is None or not record.is_active:
        # Token reuse / unknown token: defensively revoke the whole family.
        if record is not None:
            await tokens.revoke_all_for_user(record.user_id, _now())
        raise AuthError("Refresh token is no longer valid.", code="refresh_reuse")

    users = UserRepository(db)
    user = await users.get(user_id)
    if user is None or not user.is_active:
        raise AuthError("Account unavailable.", code="account_unavailable")

    # Rotate: issue a new pair and revoke the old record.
    new_pair = await issue_tokens(db, user, user_agent=user_agent, ip=ip)
    new_payload = decode_token(new_pair.refresh_token, expected_type="refresh")
    record.revoked_at = _now()
    record.replaced_by = sha256(new_payload["jti"])
    return new_pair


async def logout(db: AsyncSession, refresh_token: str | None) -> None:
    if not refresh_token:
        return
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except jwt.PyJWTError:
        return
    record = await RefreshTokenRepository(db).get_by_hash(sha256(payload["jti"]))
    if record and record.is_active:
        record.revoked_at = _now()


async def change_password(
    db: AsyncSession, user: User, *, current_password: str, new_password: str
) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise AuthError("Current password is incorrect.", code="invalid_password")
    user.hashed_password = hash_password(new_password)
    # Revoke all sessions on password change.
    await RefreshTokenRepository(db).revoke_all_for_user(user.id, _now())


async def get_primary_workspace_id(db: AsyncSession, user: User):
    memberships = await MembershipRepository(db).list_for_user(user.id)
    return memberships[0][1].id if memberships else None
