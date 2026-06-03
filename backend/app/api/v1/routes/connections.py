"""Social connection endpoints (scoped to the active workspace)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import WorkspaceContext, get_current_active_user, get_workspace_ctx, require_workspace_role
from app.core.database import get_db
from app.models.enums import WorkspaceRole
from app.models.user import User
from app.repositories.platform import ConnectionRepository
from app.schemas.connection import ConnectionConnect, ConnectionRead
from app.services import connection as connection_service

router = APIRouter(prefix="/connections", tags=["connections"])


@router.get("", response_model=list[ConnectionRead])
async def list_connections(
    db: AsyncSession = Depends(get_db), ctx: WorkspaceContext = Depends(get_workspace_ctx)
):
    return await ConnectionRepository(db).list_for_workspace(ctx.id)


@router.post("/{platform_id}/connect", response_model=ConnectionRead)
async def connect(
    platform_id: str,
    payload: ConnectionConnect,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.editor)),
):
    return await connection_service.connect(db, ctx.workspace, platform_id, payload, user)


@router.post("/{platform_id}/reconnect", response_model=ConnectionRead)
async def reconnect(
    platform_id: str,
    payload: ConnectionConnect,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.editor)),
):
    return await connection_service.connect(db, ctx.workspace, platform_id, payload, user)


@router.post("/{platform_id}/disconnect", response_model=ConnectionRead)
async def disconnect(
    platform_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(require_workspace_role(WorkspaceRole.editor)),
):
    return await connection_service.disconnect(db, ctx.workspace, platform_id)
