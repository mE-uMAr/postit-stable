"""Seed data for Postit.

Idempotent - safe to run repeatedly. Two layers:

* **core** - platforms, plans, editable site content, and the superadmin. Always
  needed (production included).
* **demo** - the "Maple & Co" sample workspace for demos/local dev.

Usage::

    python -m app.db.seed            # core + demo (default)
    python -m app.db.seed --core     # core only (production bootstrap)
    python -m app.db.seed --demo     # demo only
    python -m app.db.seed --all      # both, explicit
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import logger, setup_logging
from app.core.security import generate_opaque_token, hash_password
from app.db.base import create_all
from app.models.analytics import AnalyticsDaily
from app.models.billing import Subscription
from app.models.brand_voice import BrandVoice
from app.models.connection import Connection
from app.models.enums import (
    ConnectionStatus,
    MembershipStatus,
    PostStatus,
    PublishJobStatus,
    SubscriptionStatus,
    TargetStatus,
    WorkspaceRole,
)
from app.models.membership import Membership
from app.models.platform import Platform
from app.models.post import Post, PostTarget
from app.models.publish_job import PublishJob
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.billing import PlanRepository
from app.repositories.user import UserRepository
from app.repositories.workspace import WorkspaceRepository
from app.services import site as site_service
from app.services.rewrite import rewrite_for

PLATFORMS = [
    {"id": "x", "name": "X", "color": "#16151A", "char_limit": 280, "sort_order": 0},
    {"id": "linkedin", "name": "LinkedIn", "color": "#0A66C2", "char_limit": 3000, "sort_order": 1},
    {"id": "instagram", "name": "Instagram", "color": "#E1306C", "requires_media": True, "sort_order": 2},
    {"id": "threads", "name": "Threads", "color": "#16151A", "char_limit": 500, "sort_order": 3},
    {"id": "facebook", "name": "Facebook", "color": "#1877F2", "sort_order": 4},
    {"id": "tiktok", "name": "TikTok", "color": "#00BCD4", "requires_video": True, "sort_order": 5},
    {"id": "youtube", "name": "YouTube", "color": "#FF0000", "requires_video": True, "sort_order": 6},
    {"id": "wordpress", "name": "WordPress", "color": "#21759B", "supports_longform": True, "sort_order": 7},
    {"id": "blogger", "name": "Blogger", "color": "#FF5722", "supports_longform": True, "sort_order": 8},
]

PLANS = [
    {
        "code": "free", "name": "Free", "description": "For getting started.",
        "price_monthly_cents": 0, "annual_discount_percent": 0,
        "max_connections": 3, "max_ai_posts_monthly": 10, "max_seats": 1,
        "features": ["3 connected accounts", "10 AI posts / month", "Basic scheduling", "1 workspace"],
        "sort_order": 0,
    },
    {
        "code": "pro", "name": "Pro", "description": "For creators and founders.",
        "price_monthly_cents": 1900, "annual_discount_percent": 20,
        "max_connections": 9, "max_ai_posts_monthly": -1, "max_seats": 1,
        "features": ["All 9 platforms", "Unlimited AI rewrites", "Calendar, queue & best-time", "Brand voice & analytics"],
        "sort_order": 1,
    },
    {
        "code": "team", "name": "Team", "description": "For social teams.",
        "price_monthly_cents": 4900, "annual_discount_percent": 20,
        "max_connections": 9, "max_ai_posts_monthly": -1, "max_seats": 5,
        "features": ["Everything in Pro", "5 seats & roles", "Approval workflows", "Shared brand voices"],
        "sort_order": 2,
    },
]

CONNECTIONS = [
    ("x", ConnectionStatus.connected, "@maplehome"),
    ("linkedin", ConnectionStatus.connected, "Maple & Co"),
    ("instagram", ConnectionStatus.connected, "maple.home"),
    ("threads", ConnectionStatus.connected, "maple.home"),
    ("facebook", ConnectionStatus.connected, "Maple & Co Home"),
    ("youtube", ConnectionStatus.expired, "Maple & Co"),
    ("tiktok", ConnectionStatus.disconnected, None),
    ("wordpress", ConnectionStatus.connected, "maple.blog"),
    ("blogger", ConnectionStatus.disconnected, None),
]

TEAM = [
    ("Devon Okafor", "devon@maple.co", WorkspaceRole.editor),
    ("Sana Kapoor", "sana@maple.co", WorkspaceRole.editor),
    ("Theo Marsh", "theo@maple.co", WorkspaceRole.viewer),
]

# (body, platform_ids, status, day_offset) - offset is days from today:
# negative = already published, positive = scheduled into the future.
POSTS = [
    ("Five small ways to refresh a room for spring", ["x", "linkedin", "wordpress"], PostStatus.published, -6),
    ("We hit 4,000 happy customers this week 🎉", ["x", "instagram", "threads", "facebook", "linkedin"], PostStatus.published, -2),
    ("Launching our spring collection - lighter materials and a brighter palette", ["x", "linkedin", "instagram", "threads"], PostStatus.scheduled, 1),
    ("Behind the scenes: how we photograph a new collection", ["instagram", "threads"], PostStatus.scheduled, 3),
    ("Customer spotlight: the Alvarez family kitchen", ["linkedin", "facebook"], PostStatus.scheduled, 5),
    ("Weekend sale teaser - 48 hours only", ["x", "threads", "facebook"], PostStatus.scheduled, 8),
]

# 30-day reach weights per platform (mirrors the frontend's by-platform split).
REACH_WEIGHTS = {"instagram": 1600, "x": 1100, "linkedin": 800, "threads": 460, "facebook": 250}


async def seed_platforms(db) -> None:  # noqa: ANN001
    existing = {p.id for p in (await db.execute(select(Platform))).scalars().all()}
    for spec in PLATFORMS:
        if spec["id"] not in existing:
            db.add(Platform(**spec))
    await db.flush()


async def seed_plans(db) -> None:  # noqa: ANN001
    repo = PlanRepository(db)
    for spec in PLANS:
        if await repo.get_by_code(spec["code"]) is None:
            db.add(repo.model(**spec))
    await db.flush()


async def seed_superadmin(db) -> User:  # noqa: ANN001
    users = UserRepository(db)
    admin = await users.get_by_email(settings.SEED_SUPERADMIN_EMAIL)
    if admin is None:
        admin = await users.create(
            full_name="Postit Admin",
            email=settings.SEED_SUPERADMIN_EMAIL.lower(),
            hashed_password=hash_password(settings.SEED_SUPERADMIN_PASSWORD),
            is_superuser=True,
            is_verified=True,
        )
    return admin


async def seed_demo(db) -> None:  # noqa: ANN001
    users = UserRepository(db)
    workspaces = WorkspaceRepository(db)

    if await workspaces.get_by_slug("maple-co") is not None:
        return  # already seeded

    owner = await users.get_by_email(settings.SEED_DEMO_EMAIL)
    if owner is None:
        owner = await users.create(
            full_name="Rina Alvarez",
            email=settings.SEED_DEMO_EMAIL.lower(),
            hashed_password=hash_password(settings.SEED_DEMO_PASSWORD),
            is_verified=True,
        )

    workspace = await workspaces.create(
        name="Maple & Co", slug="maple-co", logo_text="M", owner_id=owner.id
    )
    db.add(Membership(workspace_id=workspace.id, user_id=owner.id, role=WorkspaceRole.owner, status=MembershipStatus.active))

    # Brand voice.
    db.add(
        BrandVoice(
            workspace_id=workspace.id,
            tone="Match my brand",
            guidelines=(
                "Warm but confident. Plain-spoken, short sentences, verbs over adjectives. "
                "We're a home-goods brand that values craft and calm."
            ),
            words_to_avoid=["cheap", "hustle", "game-changer", "synergy"],
        )
    )

    # Pro subscription.
    pro = await PlanRepository(db).get_by_code("pro")
    now = datetime.now(timezone.utc)
    db.add(
        Subscription(
            workspace_id=workspace.id,
            plan_id=pro.id,
            status=SubscriptionStatus.active,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
        )
    )

    # Team members.
    for name, email, role in TEAM:
        member = await users.get_by_email(email)
        if member is None:
            member = await users.create(
                full_name=name, email=email, hashed_password=hash_password("password123"), is_verified=True
            )
        db.add(Membership(workspace_id=workspace.id, user_id=member.id, role=role, status=MembershipStatus.active))

    # Connections.
    for platform_id, status, handle in CONNECTIONS:
        db.add(
            Connection(
                workspace_id=workspace.id,
                platform_id=platform_id,
                status=status,
                handle=handle,
                display_name=workspace.name if handle else None,
                avatar_text="M" if handle else None,
                connected_by=owner.id if status != ConnectionStatus.disconnected else None,
            )
        )

    # Posts + targets.
    for body, platform_ids, status, day_offset in POSTS:
        is_published = status == PostStatus.published
        when = now + timedelta(days=day_offset)
        post = Post(
            workspace_id=workspace.id,
            author_id=owner.id,
            title=body[:48],
            body=body,
            tone="Match my brand",
            status=status,
            scheduled_at=None if is_published else when,
            published_at=when if is_published else None,
        )
        db.add(post)
        await db.flush()
        for pid in platform_ids:
            db.add(
                PostTarget(
                    post_id=post.id,
                    platform_id=pid,
                    content=rewrite_for(pid, body, "Match my brand"),
                    status=TargetStatus.published if is_published else TargetStatus.scheduled,
                    published_at=when if is_published else None,
                )
            )
        # Scheduled posts get a live outbox job so the worker would publish them.
        if not is_published:
            db.add(
                PublishJob(
                    post_id=post.id,
                    status=PublishJobStatus.pending,
                    run_after=when,
                    idempotency_key=generate_opaque_token(16),
                )
            )

    # Analytics - 60 days of daily rollup per platform.
    today = now.date()
    for day_offset in range(60):
        day = today - timedelta(days=day_offset)
        wobble = 0.7 + (day_offset % 7) * 0.09  # weekly seasonality
        for platform_id, base in REACH_WEIGHTS.items():
            reach = int(base * wobble)
            impressions = int(reach * 1.4)
            engagements = int(impressions * 0.047)
            db.add(
                AnalyticsDaily(
                    workspace_id=workspace.id,
                    platform_id=platform_id,
                    date=day,
                    reach=reach,
                    impressions=impressions,
                    engagements=engagements,
                    posts_count=1 if day_offset % 4 == 0 and platform_id == "instagram" else 0,
                )
            )

    await db.flush()


async def seed_core(db) -> None:  # noqa: ANN001
    """Foundational, production-safe data."""
    await seed_platforms(db)
    await seed_plans(db)
    await site_service.seed_defaults(db)
    await seed_superadmin(db)


async def run(*, core: bool = True, demo: bool = True) -> None:
    setup_logging()
    await create_all()
    async with SessionLocal() as db:
        if core:
            await seed_core(db)
        if demo:
            # Demo depends on platforms + plans; (re)seed them idempotently.
            await seed_platforms(db)
            await seed_plans(db)
            await seed_demo(db)
        await db.commit()
    logger.info(
        "Seed complete (core=%s, demo=%s). Superadmin=%s",
        core,
        demo,
        settings.SEED_SUPERADMIN_EMAIL,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the Postit database.")
    parser.add_argument("--core", action="store_true", help="seed core data only")
    parser.add_argument("--demo", action="store_true", help="seed the demo workspace only")
    parser.add_argument("--all", action="store_true", help="seed core + demo (default)")
    args = parser.parse_args()

    none_chosen = not (args.core or args.demo or args.all)
    core = args.all or args.core or none_chosen
    demo = args.all or args.demo or none_chosen
    asyncio.run(run(core=core, demo=demo))


if __name__ == "__main__":
    main()
