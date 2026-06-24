"""Admin (superuser) aggregation + management helpers."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.billing import Plan, Subscription
from app.models.enums import BillingCycle, SubscriptionStatus
from app.models.membership import Membership
from app.models.post import Post
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.admin import AdminMetrics


async def _scalar(db: AsyncSession, stmt) -> int:  # noqa: ANN001
    return int((await db.execute(stmt)).scalar_one())


async def get_metrics(db: AsyncSession) -> AdminMetrics:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=30)

    total_users = await _scalar(db, select(func.count()).select_from(User).where(User.deleted_at.is_(None)))
    active_users = await _scalar(
        db, select(func.count()).select_from(User).where(User.is_active.is_(True), User.deleted_at.is_(None))
    )
    new_users_30d = await _scalar(
        db, select(func.count()).select_from(User).where(User.created_at >= cutoff)
    )
    total_workspaces = await _scalar(
        db, select(func.count()).select_from(Workspace).where(Workspace.deleted_at.is_(None))
    )
    active_workspaces = total_workspaces
    total_posts = await _scalar(
        db, select(func.count()).select_from(Post).where(Post.deleted_at.is_(None))
    )
    posts_published = await _scalar(
        db, select(func.count()).select_from(Post).where(Post.status == "published")
    )

    # MRR across active, paid subscriptions.
    rows = (
        await db.execute(
            select(Subscription, Plan)
            .join(Plan, Plan.id == Subscription.plan_id)
            .where(Subscription.status == SubscriptionStatus.active)
        )
    ).all()
    mrr = 0
    paying = 0
    distribution: dict[str, int] = {}
    for sub, plan in rows:
        distribution[plan.name] = distribution.get(plan.name, 0) + 1
        if plan.price_monthly_cents <= 0:
            continue
        paying += 1
        if sub.billing_cycle == BillingCycle.annual:
            mrr += round(plan.price_annual_cents / 12)
        else:
            mrr += plan.price_monthly_cents

    return AdminMetrics(
        total_users=total_users,
        active_users=active_users,
        new_users_30d=new_users_30d,
        total_workspaces=total_workspaces,
        active_workspaces=active_workspaces,
        total_posts=total_posts,
        posts_published=posts_published,
        paying_subscriptions=paying,
        mrr_cents=mrr,
        arr_cents=mrr * 12,
        plan_distribution=distribution,
    )


async def list_users(db: AsyncSession, q: str | None, offset: int, limit: int) -> tuple[list, int]:
    stmt = select(User).where(User.deleted_at.is_(None))
    count_stmt = select(func.count()).select_from(User).where(User.deleted_at.is_(None))
    if q:
        like = f"%{q.lower()}%"
        cond = func.lower(User.email).like(like) | func.lower(User.full_name).like(like)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)
    users = (await db.execute(stmt)).scalars().all()
    total = int((await db.execute(count_stmt)).scalar_one())

    # Workspace counts for the whole page in one grouped query (avoids N+1).
    user_ids = [u.id for u in users]
    counts: dict = {}
    if user_ids:
        rows = await db.execute(
            select(Membership.user_id, func.count())
            .where(Membership.user_id.in_(user_ids))
            .group_by(Membership.user_id)
        )
        counts = {uid: int(c) for uid, c in rows.all()}
    enriched = [(u, counts.get(u.id, 0)) for u in users]
    return enriched, total


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User:
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise NotFoundError("User not found.", code="user_not_found")
    return user


async def list_workspaces(db: AsyncSession, offset: int, limit: int) -> tuple[list, int]:
    total = await _scalar(
        db, select(func.count()).select_from(Workspace).where(Workspace.deleted_at.is_(None))
    )
    rows = (
        await db.execute(
            select(Workspace)
            .where(Workspace.deleted_at.is_(None))
            .order_by(Workspace.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    ).scalars().all()
    # Enrich the whole page with a fixed number of grouped queries (avoids N+1:
    # previously 3 queries per workspace row).
    ws_ids = [ws.id for ws in rows]
    member_counts: dict = {}
    post_counts: dict = {}
    plan_names: dict = {}
    if ws_ids:
        m_rows = await db.execute(
            select(Membership.workspace_id, func.count())
            .where(Membership.workspace_id.in_(ws_ids))
            .group_by(Membership.workspace_id)
        )
        member_counts = {wid: int(c) for wid, c in m_rows.all()}

        p_rows = await db.execute(
            select(Post.workspace_id, func.count())
            .where(Post.workspace_id.in_(ws_ids), Post.deleted_at.is_(None))
            .group_by(Post.workspace_id)
        )
        post_counts = {wid: int(c) for wid, c in p_rows.all()}

        s_rows = await db.execute(
            select(Subscription.workspace_id, Plan.name).join(Plan, Plan.id == Subscription.plan_id)
            .where(Subscription.workspace_id.in_(ws_ids))
        )
        plan_names = {wid: name for wid, name in s_rows.all()}

    out = [
        {
            "workspace": ws,
            "member_count": member_counts.get(ws.id, 0),
            "post_count": post_counts.get(ws.id, 0),
            "plan_name": plan_names.get(ws.id),
        }
        for ws in rows
    ]
    return out, total


async def list_subscriptions(db: AsyncSession, offset: int, limit: int) -> tuple[list, int]:
    total = await _scalar(db, select(func.count()).select_from(Subscription))
    rows = (
        await db.execute(
            select(Subscription, Plan, Workspace)
            .join(Plan, Plan.id == Subscription.plan_id)
            .join(Workspace, Workspace.id == Subscription.workspace_id)
            .order_by(Subscription.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    ).all()
    out = []
    for sub, plan, ws in rows:
        if plan.price_monthly_cents <= 0:
            mrr = 0
        elif sub.billing_cycle == BillingCycle.annual:
            mrr = round(plan.price_annual_cents / 12)
        else:
            mrr = plan.price_monthly_cents
        out.append(
            {
                "id": sub.id,
                "workspace_id": ws.id,
                "workspace_name": ws.name,
                "plan_name": plan.name,
                "status": sub.status,
                "billing_cycle": sub.billing_cycle.value,
                "mrr_cents": mrr,
                "current_period_end": sub.current_period_end,
            }
        )
    return out, total
