"""Brand voice — per-workspace default tone + guidelines for the rewrite engine."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPKMixin


class BrandVoice(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "brand_voices"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    tone: Mapped[str] = mapped_column(String(40), default="Match my brand", nullable=False)
    guidelines: Mapped[str | None] = mapped_column(Text, nullable=True)
    words_to_avoid: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
