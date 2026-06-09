"""Connection - a workspace's linked social account on a platform."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.types import GUID, JSONType
from app.models.enums import ConnectionStatus
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Connection(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "connections"
    __table_args__ = (Index("ix_conn_ws_platform", "workspace_id", "platform_id"),)

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    platform_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("platforms.id", ondelete="RESTRICT"), nullable=False
    )
    external_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    handle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_text: Mapped[str | None] = mapped_column(String(4), nullable=True)

    status: Mapped[ConnectionStatus] = mapped_column(
        Enum(ConnectionStatus, native_enum=False, length=20),
        default=ConnectionStatus.disconnected,
        nullable=False,
    )

    # Stored encrypted (see app.core.security.encrypt_secret).
    access_token: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[list | None] = mapped_column(JSONType, nullable=True)

    connected_by: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
