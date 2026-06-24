"""Social account connections via real platform OAuth2.

`start_authorization` builds the platform consent URL (signed state + PKCE where
required); `complete_callback` exchanges the returned code for tokens, looks up
the account, and stores the (encrypted) tokens on the connection.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError_
from app.core.security import encrypt_secret, generate_opaque_token
from app.models.connection import Connection
from app.models.enums import ConnectionStatus
from app.models.platform import Platform
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.platform import ConnectionRepository, PlatformRepository
from app.services import usage as usage_service
from app.services.oauth import get_oauth_provider, oauth_supported
from app.services.oauth.base import OAuthError
from app.services.oauth.state import (
    make_pkce_pair,
    pop_verifier,
    sign_state,
    store_verifier,
    verify_state,
)


async def _get_platform(db: AsyncSession, platform_id: str) -> Platform:
    platform = await PlatformRepository(db).get(platform_id)
    if platform is None or not platform.is_active:
        raise NotFoundError("Unknown platform.", code="platform_not_found")
    return platform


async def start_authorization(
    db: AsyncSession, workspace: Workspace, platform_id: str, user: User
) -> str:
    """Validate + return the platform's OAuth consent URL to redirect the user to."""
    await _get_platform(db, platform_id)
    if not oauth_supported(platform_id):
        raise ValidationError_("This platform isn't available for connection.", code="oauth_unsupported")

    provider = get_oauth_provider(platform_id)
    if not provider.configured:
        raise ValidationError_(
            f"{platform_id} OAuth isn't configured on the server.", code="oauth_not_configured"
        )

    # Enforce the plan's connection limit before sending the user off to consent.
    existing = await ConnectionRepository(db).get_for_platform(workspace.id, platform_id)
    if existing is None or existing.status != ConnectionStatus.connected:
        await usage_service.enforce_connection_limit(db, workspace.id)

    nonce = generate_opaque_token(16)
    state = sign_state(
        workspace_id=str(workspace.id), user_id=str(user.id), platform_id=platform_id, nonce=nonce
    )
    code_challenge = None
    if provider.use_pkce:
        verifier, code_challenge = make_pkce_pair()
        await store_verifier(nonce, verifier)
    return provider.authorize_url_for(state, code_challenge)


async def complete_callback(db: AsyncSession, platform_id: str, code: str, state: str) -> Connection:
    """Handle the provider redirect: verify state, exchange code, store tokens."""
    try:
        claims = verify_state(state)
    except jwt.PyJWTError as exc:
        raise ValidationError_("Invalid or expired authorization state.", code="bad_state") from exc
    if claims.get("plat") != platform_id:
        raise ValidationError_("Authorization state platform mismatch.", code="bad_state")

    workspace_id = uuid.UUID(claims["ws"])
    user_id = uuid.UUID(claims["uid"])
    provider = get_oauth_provider(platform_id)

    verifier = await pop_verifier(claims["nonce"]) if provider.use_pkce else None
    try:
        token = await provider.exchange_code(code, verifier)
        account = await provider.fetch_account(token)
    except OAuthError as exc:
        raise ValidationError_(str(exc), code="oauth_failed") from exc

    # Facebook (and similar) publish with a page token rather than the user token.
    publish_token = account.publish_token or token.access_token
    expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=token.expires_in)
        if token.expires_in
        else None
    )

    repo = ConnectionRepository(db)
    conn = await repo.get_for_platform(workspace_id, platform_id)
    fields = dict(
        external_account_id=account.external_account_id,
        handle=account.handle,
        display_name=account.display_name,
        status=ConnectionStatus.connected,
        access_token=encrypt_secret(publish_token),
        refresh_token=encrypt_secret(token.refresh_token),
        token_expires_at=expires_at,
        scopes=token.scopes,
        connected_by=user_id,
    )
    if conn is None:
        conn = await repo.create(workspace_id=workspace_id, platform_id=platform_id, **fields)
    else:
        for key, value in fields.items():
            setattr(conn, key, value)
        await db.flush()
    return conn


async def disconnect(db: AsyncSession, workspace: Workspace, platform_id: str) -> Connection:
    repo = ConnectionRepository(db)
    conn = await repo.get_for_platform(workspace.id, platform_id)
    if conn is None:
        raise NotFoundError("No connection for that platform.", code="connection_not_found")
    conn.status = ConnectionStatus.disconnected
    conn.access_token = None
    conn.refresh_token = None
    conn.token_expires_at = None
    await db.flush()
    return conn
