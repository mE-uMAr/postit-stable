"""Analytics schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class MetricDelta(BaseModel):
    value: str
    label: str
    direction: str = "up"  # up | down | flat


class AnalyticsOverview(BaseModel):
    total_reach: int
    engagement_rate: float
    posts_published: int
    reach_delta: MetricDelta
    engagement_delta: MetricDelta
    posts_delta: MetricDelta


class TrendPoint(BaseModel):
    label: str
    date: date
    value: int


class PlatformBreakdown(BaseModel):
    platform_id: str
    name: str
    color: str
    value: int          # reach
    percent: int        # share of total reach


class AnalyticsResponse(BaseModel):
    range_days: int
    overview: AnalyticsOverview
    trend: list[TrendPoint]
    by_platform: list[PlatformBreakdown]


class BestTimeSuggestion(BaseModel):
    datetime: str       # ISO-8601 suggested slot
    label: str          # e.g. "Tuesday 14:00"
    reason: str
