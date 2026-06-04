"""Editable site content / feature flags — the admin's control-plane for the
public marketing site. One row per top-level content section (key/value JSON)."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.types import JSONType
from app.models.mixins import TimestampMixin


class SiteSetting(TimestampMixin, Base):
    __tablename__ = "site_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[dict | list] = mapped_column(JSONType, nullable=False)
