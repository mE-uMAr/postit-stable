"""Post (the idea/campaign) and its per-platform targets (variants)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import GUID, JSONType
from app.models.enums import PostStatus, TargetStatus
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPKMixin


class Post(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "posts"
    __table_args__ = (
        Index("ix_posts_ws_status", "workspace_id", "status"),
        Index("ix_posts_ws_scheduled", "workspace_id", "scheduled_at"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(160), default="Untitled draft", nullable=False)
    body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    tone: Mapped[str] = mapped_column(String(40), default="Match my brand", nullable=False)
    media: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)

    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, native_enum=False, length=20),
        default=PostStatus.draft,
        nullable=False,
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Optimistic concurrency.
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    targets: Mapped[list["PostTarget"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PostTarget(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "post_targets"
    __table_args__ = (UniqueConstraint("post_id", "platform_id", name="uq_target_post_platform"),)

    post_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("posts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    platform_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("platforms.id", ondelete="RESTRICT"), nullable=False
    )
    connection_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("connections.id", ondelete="SET NULL"), nullable=True
    )

    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[TargetStatus] = mapped_column(
        Enum(TargetStatus, native_enum=False, length=20),
        default=TargetStatus.pending,
        nullable=False,
    )
    external_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    post: Mapped["Post"] = relationship(back_populates="targets")
