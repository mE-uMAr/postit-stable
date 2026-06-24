"""Connection schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ConnectionStatus
from app.schemas.common import ORMModel


class ConnectionRead(ORMModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    platform_id: str
    handle: str | None = None
    display_name: str | None = None
    avatar_text: str | None = None
    status: ConnectionStatus
    token_expires_at: datetime | None = None
    created_at: datetime


class AuthorizeResponse(BaseModel):
    """The platform consent URL the client should redirect the browser to."""

    authorize_url: str
