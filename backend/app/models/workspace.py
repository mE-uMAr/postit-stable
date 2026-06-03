"""Workspace — the tenant boundary for posts, connections, billing."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.types import GUID, JSONType
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPKMixin


class Workspace(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True, nullable=False)
    logo_text: Mapped[str] = mapped_column(String(4), default="W", nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    settings: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)
