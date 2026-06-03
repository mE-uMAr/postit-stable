"""Analytics aggregation over the pre-computed daily rollup."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsDaily
from app.models.platform import Platform
from app.schemas.analytics import (
    AnalyticsOverview,
    AnalyticsResponse,
    MetricDelta,
    PlatformBreakdown,
    TrendPoint,
)


def _today() -> date:
    return datetime.now(timezone.utc).date()


async def _window_totals(
    db: AsyncSession, workspace_id: uuid.UUID, start: date, end: date
) -> tuple[int, int, int]:
    stmt = select(
        func.coalesce(func.sum(AnalyticsDaily.reach), 0),
        func.coalesce(func.sum(AnalyticsDaily.impressions), 0),
        func.coalesce(func.sum(AnalyticsDaily.engagements), 0),
    ).where(
        AnalyticsDaily.workspace_id == workspace_id,
        AnalyticsDaily.date >= start,
        AnalyticsDaily.date < end,
    )
    reach, impressions, engagements = (await db.execute(stmt)).one()
    return int(reach), int(impressions), int(engagements)


def _humanize(n: int) -> str:
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


async def get_analytics(
    db: AsyncSession, workspace_id: uuid.UUID, range_days: int = 30
) -> AnalyticsResponse:
    end = _today() + timedelta(days=1)
    start = end - timedelta(days=range_days)
    prev_start = start - timedelta(days=range_days)

    reach, impressions, engagements = await _window_totals(db, workspace_id, start, end)
    prev_reach, prev_impr, _ = await _window_totals(db, workspace_id, prev_start, start)

    posts_published = int(
        (
            await db.execute(
                select(func.coalesce(func.sum(AnalyticsDaily.posts_count), 0)).where(
                    AnalyticsDaily.workspace_id == workspace_id,
                    AnalyticsDaily.date >= start,
                    AnalyticsDaily.date < end,
                )
            )
        ).scalar_one()
    )

    engagement_rate = round(engagements / impressions * 100, 1) if impressions else 0.0
    reach_change = round((reach - prev_reach) / prev_reach * 100, 1) if prev_reach else 0.0

    overview = AnalyticsOverview(
        total_reach=reach,
        engagement_rate=engagement_rate,
        posts_published=posts_published,
        reach_delta=MetricDelta(
            value=f"{'+' if reach_change >= 0 else ''}{reach_change}%",
            label="vs last period",
            direction="up" if reach_change >= 0 else "down",
        ),
        engagement_delta=MetricDelta(value=f"{engagement_rate}%", label="engagement", direction="up"),
        posts_delta=MetricDelta(value=str(posts_published), label="published", direction="up"),
    )

    # Trend: bucket the range into ~7 segments by reach.
    buckets = 7
    seg = max(1, range_days // buckets)
    daily = (
        await db.execute(
            select(AnalyticsDaily.date, func.sum(AnalyticsDaily.reach))
            .where(
                AnalyticsDaily.workspace_id == workspace_id,
                AnalyticsDaily.date >= start,
                AnalyticsDaily.date < end,
            )
            .group_by(AnalyticsDaily.date)
        )
    ).all()
    by_date = {d: int(r) for d, r in daily}
    trend: list[TrendPoint] = []
    for i in range(buckets):
        b_start = start + timedelta(days=i * seg)
        b_end = b_start + timedelta(days=seg)
        total = sum(v for d, v in by_date.items() if b_start <= d < b_end)
        trend.append(TrendPoint(label=f"Wk {i + 1}", date=b_start, value=total))

    # By platform.
    rows = (
        await db.execute(
            select(AnalyticsDaily.platform_id, func.sum(AnalyticsDaily.reach))
            .where(
                AnalyticsDaily.workspace_id == workspace_id,
                AnalyticsDaily.date >= start,
                AnalyticsDaily.date < end,
            )
            .group_by(AnalyticsDaily.platform_id)
            .order_by(func.sum(AnalyticsDaily.reach).desc())
        )
    ).all()
    platforms = {p.id: p for p in (await db.execute(select(Platform))).scalars().all()}
    total_reach = sum(int(r) for _, r in rows) or 1
    by_platform = [
        PlatformBreakdown(
            platform_id=pid,
            name=platforms[pid].name if pid in platforms else pid,
            color=platforms[pid].color if pid in platforms else "#888",
            value=int(r),
            percent=round(int(r) / total_reach * 100),
        )
        for pid, r in rows
    ]

    return AnalyticsResponse(
        range_days=range_days, overview=overview, trend=trend, by_platform=by_platform
    )
