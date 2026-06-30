"""Social connection endpoints — real platform OAuth (scoped to the workspace).

Flow: the client POSTs to `/authorize` to get the platform consent URL and sends
the browser there; the platform redirects back to the public `/callback`, which
stores the tokens and bounces the user to the app's Connections page.
"""

from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    WorkspaceContext,
    get_current_active_user,
    get_workspace_ctx,
    require_workspace_role,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.models.enums import WorkspaceRole
from app.models.user import User
from app.repositories.platform import ConnectionRepository
from app.schemas.connection import AuthorizeResponse, ConnectionRead
from app.services import connection as connection_service

router = APIRouter(prefix="/connections", tags=["connections"])


def _connections_redirect(**params: str) -> RedirectResponse:
    base = f"{settings.FRONTEND_URL.rstrip('/')}/app/connections"
    return RedirectResponse(f"{base}?{urlencode(params)}", status_code=303)


@router.get("", response_model=list[ConnectionRead])
async def list_connections(
    db: AsyncSession = Depends(get_db), ctx: WorkspaceContext = Depends(get_workspace_ctx)
):
    return await ConnectionRepository(db).list_for_workspace(ctx.id)


@router.post("/{platform_id}/authorize", response_model=AuthorizeResponse)
async def authorize(
    platform_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.editor)),
):
    """Return the platform OAuth consent URL for the client to redirect to."""
    url = await connection_service.start_authorization(db, ctx.workspace, platform_id, user)
    return AuthorizeResponse(authorize_url=url)


# Back-compat aliases: the Connections UI POSTs /connect for a fresh account and
# /reconnect for an expired one. Both start the same OAuth authorization flow.
@router.post("/{platform_id}/connect", response_model=AuthorizeResponse)
@router.post("/{platform_id}/reconnect", response_model=AuthorizeResponse)
async def reconnect(
    platform_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.editor)),
):
    url = await connection_service.start_authorization(db, ctx.workspace, platform_id, user)
    return AuthorizeResponse(authorize_url=url)


@router.get("/{platform_id}/callback")
async def oauth_callback(
    platform_id: str,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Public OAuth redirect target. Stores tokens, then bounces to the app."""
    if error:
        return _connections_redirect(platform=platform_id, error=error_description or error)
    if not code or not state:
        return _connections_redirect(platform=platform_id, error="missing_code")
    try:
        await connection_service.complete_callback(db, platform_id, code, state)
    except Exception as exc:  # noqa: BLE001 - surface a clean message to the UI
        logger.warning("OAuth callback failed for %s: %s", platform_id, exc, exc_info=True)
        msg = getattr(exc, "message", None) or "connection_failed"
        return _connections_redirect(platform=platform_id, error=str(msg))
    return _connections_redirect(platform=platform_id, connected="1")


@router.post("/{platform_id}/disconnect", response_model=ConnectionRead)
async def disconnect(
    platform_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.editor)),
):
    return await connection_service.disconnect(db, ctx.workspace, platform_id)
