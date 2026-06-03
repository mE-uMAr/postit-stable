"""Social account connections (mock OAuth)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.connection import Connection
from app.models.enums import ConnectionStatus
from app.models.platform import Platform
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.platform import ConnectionRepository, PlatformRepository
from app.schemas.connection import ConnectionConnect
from app.services import usage as usage_service


async def _get_platform(db: AsyncSession, platform_id: str) -> Platform:
    platform = await PlatformRepository(db).get(platform_id)
    if platform is None or not platform.is_active:
        raise NotFoundError("Unknown platform.", code="platform_not_found")
    return platform


async def connect(
    db: AsyncSession,
    workspace: Workspace,
    platform_id: str,
    data: ConnectionConnect,
    user: User,
) -> Connection:
    platform = await _get_platform(db, platform_id)
    repo = ConnectionRepository(db)
    existing = await repo.get_for_platform(workspace.id, platform_id)

    if existing is None or existing.status != ConnectionStatus.connected:
        await usage_service.enforce_connection_limit(db, workspace.id)

    handle = data.handle or f"@{workspace.slug}"
    display_name = data.display_name or workspace.name
    if existing is None:
        existing = await repo.create(
            workspace_id=workspace.id,
            platform_id=platform_id,
            handle=handle,
            display_name=display_name,
            avatar_text=workspace.logo_text,
            external_account_id=data.external_account_id,
            status=ConnectionStatus.connected,
            connected_by=user.id,
        )
    else:
        existing.status = ConnectionStatus.connected
        existing.handle = handle
        existing.display_name = display_name
        existing.connected_by = user.id
        await db.flush()
    return existing


async def disconnect(db: AsyncSession, workspace: Workspace, platform_id: str) -> Connection:
    repo = ConnectionRepository(db)
    conn = await repo.get_for_platform(workspace.id, platform_id)
    if conn is None:
        raise NotFoundError("No connection for that platform.", code="connection_not_found")
    conn.status = ConnectionStatus.disconnected
    conn.handle = None
    conn.access_token = None
    conn.refresh_token = None
    await db.flush()
    return conn
