"""Shared FastAPI dependencies: auth, current user, workspace context, RBAC."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import jwt
from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthError, NotFoundError, PermissionError_
from app.core.security import decode_token
from app.models.enums import ROLE_RANK, WorkspaceRole
from app.models.membership import Membership
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.user import UserRepository
from app.repositories.workspace import MembershipRepository, WorkspaceRepository

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> User:
    if creds is None or not creds.credentials:
        raise AuthError("Authentication required.", code="missing_token")
    try:
        payload = decode_token(creds.credentials, expected_type="access")
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Access token expired.", code="token_expired") from exc
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid access token.", code="invalid_token") from exc

    user = await UserRepository(db).get(payload["sub"])
    if user is None or user.deleted_at is not None:
        raise AuthError("User no longer exists.", code="user_not_found")
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise PermissionError_("Your account is disabled.", code="account_disabled")
    return user


async def require_superuser(user: User = Depends(get_current_active_user)) -> User:
    if not user.is_superuser:
        raise PermissionError_("Administrator access required.", code="not_superuser")
    return user


@dataclass
class WorkspaceContext:
    workspace: Workspace
    membership: Membership
    role: WorkspaceRole

    @property
    def id(self) -> uuid.UUID:
        return self.workspace.id


async def get_workspace_ctx(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-Id"),
) -> WorkspaceContext:
    """Resolve the active workspace from the ``X-Workspace-Id`` header.

    Falls back to the caller's first workspace when the header is absent.
    """
    members = MembershipRepository(db)
    workspaces = WorkspaceRepository(db)

    if x_workspace_id:
        try:
            ws_id = uuid.UUID(x_workspace_id)
        except ValueError as exc:
            raise NotFoundError("Invalid workspace id.", code="bad_workspace") from exc
        membership = await members.get_membership(ws_id, user.id)
        if membership is None:
            raise PermissionError_("You're not a member of that workspace.", code="not_member")
        workspace = await workspaces.get(ws_id)
    else:
        owned = await members.list_for_user(user.id)
        if not owned:
            raise NotFoundError("You don't belong to any workspace yet.", code="no_workspace")
        membership, workspace = owned[0]

    if workspace is None or workspace.deleted_at is not None:
        raise NotFoundError("Workspace not found.", code="workspace_not_found")
    return WorkspaceContext(workspace=workspace, membership=membership, role=membership.role)


def require_workspace_role(minimum: WorkspaceRole):
    """Dependency factory enforcing a minimum workspace role."""

    async def _checker(ctx: WorkspaceContext = Depends(get_workspace_ctx)) -> WorkspaceContext:
        if ROLE_RANK[ctx.role] < ROLE_RANK[minimum]:
            raise PermissionError_(
                f"This action requires the {minimum.value} role or higher.",
                code="insufficient_role",
            )
        return ctx

    return _checker


def client_meta(request: Request) -> dict[str, str | None]:
    return {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
