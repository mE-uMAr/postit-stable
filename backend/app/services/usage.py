"""Plan-limit enforcement + usage accounting."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BillingError
from app.models.billing import Plan
from app.repositories.billing import PlanRepository, SubscriptionRepository, UsageRepository
from app.repositories.platform import ConnectionRepository
from app.repositories.workspace import MembershipRepository


def current_period() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


async def get_active_plan(db: AsyncSession, workspace_id: uuid.UUID) -> Plan:
    sub = await SubscriptionRepository(db).get_for_workspace(workspace_id)
    plans = PlanRepository(db)
    if sub is not None:
        plan = await plans.get(sub.plan_id)
        if plan is not None:
            return plan
    free = await plans.get_by_code("free")
    if free is None:
        raise BillingError("No plan is configured for this workspace.", code="no_plan")
    return free


async def consume_ai_generation(db: AsyncSession, workspace_id: uuid.UUID) -> None:
    plan = await get_active_plan(db, workspace_id)
    counter = await UsageRepository(db).get_or_create(workspace_id, current_period())
    if plan.max_ai_posts_monthly >= 0 and counter.ai_posts_used >= plan.max_ai_posts_monthly:
        raise BillingError(
            f"You've used all {plan.max_ai_posts_monthly} AI generations on the {plan.name} plan "
            "this month. Upgrade to generate more.",
            code="ai_limit_reached",
        )
    counter.ai_posts_used += 1
    await db.flush()


async def record_published(db: AsyncSession, workspace_id: uuid.UUID) -> None:
    counter = await UsageRepository(db).get_or_create(workspace_id, current_period())
    counter.posts_published += 1
    await db.flush()


async def enforce_connection_limit(db: AsyncSession, workspace_id: uuid.UUID) -> None:
    plan = await get_active_plan(db, workspace_id)
    if plan.max_connections < 0:
        return
    connected = await ConnectionRepository(db).count_connected(workspace_id)
    if connected >= plan.max_connections:
        raise BillingError(
            f"The {plan.name} plan allows {plan.max_connections} connected accounts. "
            "Upgrade to connect more.",
            code="connection_limit_reached",
        )


async def enforce_seat_limit(db: AsyncSession, workspace_id: uuid.UUID) -> None:
    plan = await get_active_plan(db, workspace_id)
    if plan.max_seats < 0:
        return
    seats = await MembershipRepository(db).count_active(workspace_id)
    if seats >= plan.max_seats:
        raise BillingError(
            f"The {plan.name} plan includes {plan.max_seats} seats. Upgrade to invite more.",
            code="seat_limit_reached",
        )


async def get_usage_summary(db: AsyncSession, workspace_id: uuid.UUID) -> dict:
    plan = await get_active_plan(db, workspace_id)
    counter = await UsageRepository(db).get_or_create(workspace_id, current_period())
    connections = await ConnectionRepository(db).count_connected(workspace_id)
    seats = await MembershipRepository(db).count_active(workspace_id)
    return {
        "period": counter.period,
        "ai_posts_used": counter.ai_posts_used,
        "ai_posts_limit": plan.max_ai_posts_monthly,
        "posts_published": counter.posts_published,
        "connections_used": connections,
        "connections_limit": plan.max_connections,
        "seats_used": seats,
        "seats_limit": plan.max_seats,
    }
