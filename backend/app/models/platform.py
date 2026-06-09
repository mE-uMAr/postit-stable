"""Platform catalog - one row per social network (admin-toggleable)."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Platform(TimestampMixin, Base):
    __tablename__ = "platforms"

    # slug PK, e.g. "x", "linkedin"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    color: Mapped[str] = mapped_column(String(16), default="#16151A", nullable=False)
    requires_media: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_video: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    char_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    supports_longform: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
