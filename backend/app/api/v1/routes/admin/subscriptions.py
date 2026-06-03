"""Admin subscription management."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.pagination import Page, PageParams
from app.models.user import User
from app.repositories.billing import PlanRepository, SubscriptionRepository
from app.schemas.admin import AdminSubscriptionOverride, AdminSubscriptionRead
from app.schemas.common import Message
from app.services import admin as admin_service
from app.services.audit import record_audit

router = APIRouter(prefix="/subscriptions", tags=["admin"])


@router.get("", response_model=Page[AdminSubscriptionRead])
async def list_subscriptions(params: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    rows, total = await admin_service.list_subscriptions(db, params.offset, params.limit)
    items = [AdminSubscriptionRead(**r) for r in rows]
    return Page.create(items, total, params)


@router.post("/{subscription_id}/override", response_model=Message)
async def override_subscription(
    subscription_id: uuid.UUID,
    payload: AdminSubscriptionOverride,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_user),
):
    sub = await SubscriptionRepository(db).get(subscription_id)
    if sub is None:
        raise NotFoundError("Subscription not found.", code="subscription_not_found")
    plan = await PlanRepository(db).get(payload.plan_id)
    if plan is None:
        raise NotFoundError("Plan not found.", code="plan_not_found")
    sub.plan_id = plan.id
    if payload.status is not None:
        sub.status = payload.status
    await db.flush()
    await record_audit(
        db,
        action="admin.subscription.override",
        actor_id=admin.id,
        target_type="subscription",
        target_id=str(subscription_id),
        meta={"plan": plan.code},
    )
    return Message(message=f"Subscription moved to {plan.name}.")
