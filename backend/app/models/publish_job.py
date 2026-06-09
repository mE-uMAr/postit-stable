"""Publish job - outbox row representing intent to publish a post.

No scheduler runs yet; this is the durable contract a future worker drains.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.types import GUID
from app.models.enums import PublishJobStatus
from app.models.mixins import TimestampMixin, UUIDPKMixin


class PublishJob(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "publish_jobs"

    post_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("posts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[PublishJobStatus] = mapped_column(
        Enum(PublishJobStatus, native_enum=False, length=16),
        default=PublishJobStatus.pending,
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    run_after: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
