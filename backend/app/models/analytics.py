"""Analytics — raw per-target metrics + pre-aggregated daily rollup."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.types import GUID
from app.models.mixins import UUIDPKMixin


class PostMetric(UUIDPKMixin, Base):
    """Raw metric snapshots for a target (drill-down)."""

    __tablename__ = "post_metrics"
    __table_args__ = (Index("ix_metric_target_captured", "post_target_id", "captured_at"),)

    post_target_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("post_targets.id", ondelete="CASCADE"), nullable=False
    )
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reach: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shares: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AnalyticsDaily(UUIDPKMixin, Base):
    """Pre-aggregated per-workspace, per-platform, per-day rollup for dashboards."""

    __tablename__ = "analytics_daily"
    __table_args__ = (
        UniqueConstraint("workspace_id", "platform_id", "date", name="uq_daily_ws_pf_date"),
        Index("ix_daily_ws_date", "workspace_id", "date"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    platform_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("platforms.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    reach: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    engagements: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    posts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
