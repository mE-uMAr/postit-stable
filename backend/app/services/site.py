"""Site content control-plane.

The public marketing site reads from :func:`get_content`; superadmins edit it via
the admin API. Stored as one ``site_settings`` row per top-level section, merged
over :data:`DEFAULT_CONTENT` so a fresh install always renders.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.site_setting import SiteSetting

DEFAULT_CONTENT: dict = {
    "announcement": {
        "enabled": True,
        "text": "Postit is live - write once, post natively everywhere.",
        "href": "/signup",
    },
    "hero": {
        "eyebrow": "AI social publishing",
        "title": "Write once. Sound native on every platform.",
        "subtitle": "Postit turns one idea into nine on-brand posts - then schedules, "
        "publishes, and measures them from a single calm workspace.",
        "primary_cta": {"label": "Start free", "href": "/signup"},
        "secondary_cta": {"label": "See how it works", "href": "#how"},
    },
    "logos": ["Northwind", "Lumen", "Foundry", "Maple & Co", "Beacon", "Driftwood"],
    "features": [
        {
            "icon": "compose",
            "title": "One composer, nine native posts",
            "body": "Draft once. Postit rewrites for X, LinkedIn, Instagram, Threads and more - "
            "respecting each platform's voice and limits.",
        },
        {
            "icon": "calendar",
            "title": "Calendar & best-time scheduling",
            "body": "Drag to reschedule, and let AI suggest the slots your audience actually shows up for.",
        },
        {
            "icon": "analytics",
            "title": "Analytics that mean something",
            "body": "Reach, engagement and growth across every platform - rolled up, not scattered.",
        },
        {
            "icon": "shield",
            "title": "Brand voice, enforced",
            "body": "Set tone, guidelines and words to avoid once; every generation stays on-brand.",
        },
    ],
    "testimonials": [
        {
            "quote": "Postit cut our posting time by 80%. One draft, every channel, all on-brand.",
            "name": "Rina Alvarez",
            "role": "Founder, Maple & Co",
        },
        {
            "quote": "The best-time suggestions are uncanny. Our reach is up and we barely touch the queue.",
            "name": "Devon Okafor",
            "role": "Head of Growth, Lumen",
        },
        {
            "quote": "Finally, analytics I can act on without exporting five dashboards.",
            "name": "Sana Kapoor",
            "role": "Social Lead, Foundry",
        },
    ],
    "faq": [
        {
            "q": "Which platforms does Postit support?",
            "a": "X, LinkedIn, Instagram, Threads, Facebook, TikTok, YouTube, WordPress and Blogger.",
        },
        {
            "q": "Do I need my own AI key?",
            "a": "No. Postit works out of the box; teams can plug in their own provider (Claude, "
            "OpenAI, Groq, Gemini) for fully custom generation.",
        },
        {
            "q": "Can I schedule and auto-publish?",
            "a": "Yes - schedule a post and our worker publishes it at the right moment.",
        },
    ],
    "flags": {
        "social_auth": False,   # Google/Apple buttons on auth pages
        "show_pricing": True,
    },
    # Pricing model is admin-controlled: "plan" (subscription tiers from /subscriptions/plans)
    # or "usage" (pay-as-you-go rates below). Rates are in cents.
    "pricing": {
        "model": "plan",          # "plan" | "usage"
        "currency": "USD",
        "headline": "Start free. Upgrade when it pays for itself.",
        "subhead": "Simple pricing that scales with how much you publish.",
        "rates": {
            "per_post_cents": 25,            # each scheduled/published post
            "per_ai_generation_cents": 10,   # each AI rewrite/generation
            "per_manual_post_cents": 5,      # manual post creation + media upload
        },
        "usage_note": "No subscription. You only pay for what you publish, billed monthly.",
    },
}

# Sections a superuser may edit through the admin API.
EDITABLE_KEYS = set(DEFAULT_CONTENT.keys())


async def get_content(db: AsyncSession) -> dict:
    try:
        rows = (await db.execute(select(SiteSetting))).scalars().all()
    except SQLAlchemyError:
        # The public marketing site must render even if the DB is unreachable.
        # Roll back so the request-scoped session closes cleanly (the get_db
        # dependency would otherwise re-raise on its trailing commit), and serve
        # the built-in defaults.
        await db.rollback()
        logger.warning("site.get_content: DB unavailable, serving default content")
        return dict(DEFAULT_CONTENT)
    stored = {r.key: r.value for r in rows}
    return {key: stored.get(key, default) for key, default in DEFAULT_CONTENT.items()}


async def set_content(db: AsyncSession, data: dict) -> dict:
    for key, value in data.items():
        if key not in EDITABLE_KEYS:
            continue
        row = await db.get(SiteSetting, key)
        if row is None:
            db.add(SiteSetting(key=key, value=value))
        else:
            row.value = value
    await db.flush()
    return await get_content(db)


async def seed_defaults(db: AsyncSession) -> None:
    """Idempotently persist the default content (called from seed_core)."""
    existing = set((await db.execute(select(SiteSetting.key))).scalars().all())
    for key, value in DEFAULT_CONTENT.items():
        if key not in existing:
            db.add(SiteSetting(key=key, value=value))
    await db.flush()
