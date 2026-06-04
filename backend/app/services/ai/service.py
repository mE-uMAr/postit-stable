"""High-level AI surface used by the rest of the app.

Provider-agnostic: builds platform-aware prompts, calls the configured provider,
and *always* degrades gracefully to the deterministic rewriter so generation
never hard-fails (offline, missing key, provider outage…).
"""

from __future__ import annotations

import uuid
from datetime import datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.models.analytics import AnalyticsDaily
from app.models.brand_voice import BrandVoice
from app.models.platform import Platform
from app.services.ai.registry import get_provider
from app.services.rewrite import rewrite_for

# Canonical posting hours (UTC) used when proposing schedule slots.
_GOOD_HOURS = [time(9, 0), time(14, 0), time(11, 30)]
_WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class AIService:
    @property
    def enabled(self) -> bool:
        """True when a real (non-mock) provider is active."""
        return get_provider().name != "mock"

    @property
    def provider_name(self) -> str:
        return get_provider().name

    def _system(self, brand_voice: BrandVoice | None) -> str:
        lines = [
            "You are a senior social media copywriter who makes one idea sound native",
            "on each platform. Return ONLY the post text — no preamble, no quotes, no labels.",
        ]
        if brand_voice:
            if brand_voice.tone:
                lines.append(f"Brand tone: {brand_voice.tone}.")
            if brand_voice.guidelines:
                lines.append(f"Brand guidelines: {brand_voice.guidelines}")
            if brand_voice.words_to_avoid:
                lines.append("Never use these words: " + ", ".join(brand_voice.words_to_avoid) + ".")
        return " ".join(lines)

    def _prompt(self, platform: Platform, body: str, tone: str) -> str:
        rules: list[str] = []
        if platform.char_limit:
            rules.append(f"Keep it under {platform.char_limit} characters.")
        if platform.supports_longform:
            rules.append("Long-form is welcome; structure it with short paragraphs.")
        if platform.id in ("instagram", "tiktok", "threads"):
            rules.append("Casual, lowercase-friendly, a few relevant emoji and 2–3 hashtags.")
        if platform.id == "linkedin":
            rules.append("Professional and warm; a hook first line, then value.")
        if platform.id == "x":
            rules.append("Punchy; one strong line; up to 3 hashtags.")
        rule_text = (" " + " ".join(rules)) if rules else ""
        return (
            f"Rewrite this post natively for {platform.name}.{rule_text}\n"
            f"Desired tone: {tone}.\n\n"
            f"Original post:\n{body}"
        )

    async def generate_variant(
        self,
        *,
        platform: Platform,
        body: str,
        tone: str,
        brand_voice: BrandVoice | None = None,
    ) -> str:
        body = (body or "").strip()
        if not body:
            return ""
        provider = get_provider()
        if provider.name == "mock":
            return rewrite_for(platform.id, body, tone)
        try:
            text = await provider.generate(
                system=self._system(brand_voice),
                prompt=self._prompt(platform, body, tone),
                max_tokens=settings.AI_MAX_TOKENS,
            )
            text = text.strip().strip('"')
            if not text:
                raise ValueError("empty completion")
            if platform.char_limit and len(text) > platform.char_limit:
                text = text[: platform.char_limit].rstrip()
            return text
        except Exception:  # noqa: BLE001 - any provider failure → deterministic fallback
            logger.warning(
                "AI provider '%s' failed; using deterministic rewrite", provider.name, exc_info=True
            )
            return rewrite_for(platform.id, body, tone)

    async def suggest_best_times(
        self, db: AsyncSession, workspace_id: uuid.UUID, *, count: int = 3
    ) -> list[dict]:
        """Heuristic best-time suggestions from the workspace's engagement history."""
        since = datetime.now(timezone.utc).date() - timedelta(days=60)
        stmt = (
            select(AnalyticsDaily.date, func.sum(AnalyticsDaily.engagements))
            .where(AnalyticsDaily.workspace_id == workspace_id, AnalyticsDaily.date >= since)
            .group_by(AnalyticsDaily.date)
        )
        rows = (await db.execute(stmt)).all()

        # Average engagement per weekday (0=Mon … 6=Sun).
        totals: dict[int, list[int]] = {}
        for d, eng in rows:
            totals.setdefault(d.weekday(), []).append(int(eng or 0))
        ranked = sorted(
            totals.items(), key=lambda kv: sum(kv[1]) / len(kv[1]), reverse=True
        )
        best_weekdays = [wd for wd, _ in ranked[:count]] or [1, 3, 4]  # Tue/Thu/Fri default

        today = datetime.now(timezone.utc)
        out: list[dict] = []
        for i, wd in enumerate(best_weekdays[:count]):
            days_ahead = (wd - today.weekday()) % 7 or 7
            day = (today + timedelta(days=days_ahead)).date()
            slot = datetime.combine(day, _GOOD_HOURS[i % len(_GOOD_HOURS)], tzinfo=timezone.utc)
            out.append(
                {
                    "datetime": slot.isoformat(),
                    "label": f"{_WEEKDAY_NAMES[wd]} {slot.strftime('%H:%M')}",
                    "reason": f"{_WEEKDAY_NAMES[wd]} drives the most engagement for this workspace.",
                }
            )
        return out

    async def get_brand_voice(self, db: AsyncSession, workspace_id: uuid.UUID) -> BrandVoice | None:
        stmt = select(BrandVoice).where(BrandVoice.workspace_id == workspace_id).limit(1)
        return (await db.execute(stmt)).scalars().first()


ai_service = AIService()
