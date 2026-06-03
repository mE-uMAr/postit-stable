"""Billing orchestration: checkout, portal, and Stripe webhook sync."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BillingError, NotFoundError
from app.models.billing import Invoice, Subscription
from app.models.enums import BillingCycle, InvoiceStatus, SubscriptionStatus
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.billing import (
    InvoiceRepository,
    PlanRepository,
    SubscriptionRepository,
)
from app.services import plan as plan_service
from app.services import stripe_gateway


def _ts(value: int | None) -> datetime | None:
    return datetime.fromtimestamp(value, tz=timezone.utc) if value else None


async def get_or_create_subscription(db: AsyncSession, workspace: Workspace) -> Subscription:
    repo = SubscriptionRepository(db)
    sub = await repo.get_for_workspace(workspace.id)
    if sub is not None:
        return sub
    free = await PlanRepository(db).get_by_code("free")
    if free is None:
        raise BillingError("No default plan configured.", code="no_default_plan")
    return await repo.create(
        workspace_id=workspace.id, plan_id=free.id, status=SubscriptionStatus.active
    )


async def create_checkout(
    db: AsyncSession,
    workspace: Workspace,
    user: User,
    *,
    plan_id: uuid.UUID,
    cycle: BillingCycle,
    success_url: str | None,
    cancel_url: str | None,
) -> dict[str, Any]:
    plan = await plan_service.get_plan(db, plan_id)
    if plan.price_monthly_cents <= 0:
        raise BillingError("That plan is free — no checkout required.", code="plan_is_free")

    # Make sure the plan has Stripe prices.
    if not plan.stripe_price_monthly_id or not plan.stripe_price_annual_id:
        ids = await stripe_gateway.ensure_plan_prices(plan)
        plan.stripe_product_id = ids["product_id"]
        plan.stripe_price_monthly_id = ids["price_monthly_id"]
        plan.stripe_price_annual_id = ids["price_annual_id"]
        await db.flush()

    price_id = (
        plan.stripe_price_annual_id
        if cycle == BillingCycle.annual
        else plan.stripe_price_monthly_id
    )

    sub = await get_or_create_subscription(db, workspace)
    if not sub.stripe_customer_id:
        sub.stripe_customer_id = await stripe_gateway.ensure_customer(
            email=user.email,
            name=workspace.name,
            metadata={"workspace_id": str(workspace.id)},
        )
        await db.flush()

    base = settings.FRONTEND_URL.rstrip("/")
    session = await stripe_gateway.create_checkout_session(
        customer_id=sub.stripe_customer_id,
        price_id=price_id,
        success_url=success_url or f"{base}/app/settings?billing=success",
        cancel_url=cancel_url or f"{base}/app/settings?billing=cancelled",
        metadata={
            "workspace_id": str(workspace.id),
            "plan_id": str(plan.id),
            "cycle": cycle.value,
        },
    )
    return {"url": session["url"], "session_id": session.get("id")}


async def create_portal(db: AsyncSession, workspace: Workspace) -> dict[str, Any]:
    sub = await SubscriptionRepository(db).get_for_workspace(workspace.id)
    if sub is None or not sub.stripe_customer_id:
        raise BillingError("No billing account yet — start a subscription first.", code="no_customer")
    base = settings.FRONTEND_URL.rstrip("/")
    session = await stripe_gateway.create_portal_session(
        customer_id=sub.stripe_customer_id, return_url=f"{base}/app/settings"
    )
    return {"url": session["url"]}


# --------------------------------------------------------------------------- #
# Webhook handling
# --------------------------------------------------------------------------- #
async def handle_webhook_event(db: AsyncSession, event: dict[str, Any]) -> None:
    event_type = event.get("type", "")
    obj = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        await _on_checkout_completed(db, obj)
    elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
        await _on_subscription_updated(db, obj)
    elif event_type == "customer.subscription.deleted":
        await _on_subscription_deleted(db, obj)
    elif event_type in ("invoice.paid", "invoice.payment_succeeded", "invoice.payment_failed"):
        await _on_invoice(db, obj, paid=event_type != "invoice.payment_failed")


async def _resolve_subscription(db: AsyncSession, *, customer: str | None, metadata: dict) -> Subscription | None:
    repo = SubscriptionRepository(db)
    ws_id = metadata.get("workspace_id")
    if ws_id:
        try:
            sub = await repo.get_for_workspace(uuid.UUID(ws_id))
            if sub:
                return sub
        except ValueError:
            pass
    if customer:
        return await repo.get_by_stripe_customer(customer)
    return None


async def _on_checkout_completed(db: AsyncSession, obj: dict) -> None:
    metadata = obj.get("metadata", {}) or {}
    sub = await _resolve_subscription(db, customer=obj.get("customer"), metadata=metadata)
    if sub is None:
        return
    sub.stripe_customer_id = obj.get("customer") or sub.stripe_customer_id
    sub.stripe_subscription_id = obj.get("subscription") or sub.stripe_subscription_id
    plan_id = metadata.get("plan_id")
    if plan_id:
        try:
            sub.plan_id = uuid.UUID(plan_id)
        except ValueError:
            pass
    cycle = metadata.get("cycle")
    if cycle in (BillingCycle.monthly, BillingCycle.annual):
        sub.billing_cycle = BillingCycle(cycle)
    sub.status = SubscriptionStatus.active
    await db.flush()


_STATUS_MAP = {
    "active": SubscriptionStatus.active,
    "trialing": SubscriptionStatus.trialing,
    "past_due": SubscriptionStatus.past_due,
    "canceled": SubscriptionStatus.canceled,
    "unpaid": SubscriptionStatus.past_due,
    "incomplete": SubscriptionStatus.incomplete,
    "incomplete_expired": SubscriptionStatus.canceled,
}


async def _on_subscription_updated(db: AsyncSession, obj: dict) -> None:
    repo = SubscriptionRepository(db)
    sub = await repo.get_by_stripe_subscription(obj.get("id")) or await _resolve_subscription(
        db, customer=obj.get("customer"), metadata=obj.get("metadata", {}) or {}
    )
    if sub is None:
        return
    sub.stripe_subscription_id = obj.get("id") or sub.stripe_subscription_id
    sub.status = _STATUS_MAP.get(obj.get("status", ""), sub.status)
    sub.current_period_start = _ts(obj.get("current_period_start")) or sub.current_period_start
    sub.current_period_end = _ts(obj.get("current_period_end")) or sub.current_period_end
    sub.cancel_at_period_end = bool(obj.get("cancel_at_period_end"))
    await db.flush()


async def _on_subscription_deleted(db: AsyncSession, obj: dict) -> None:
    repo = SubscriptionRepository(db)
    sub = await repo.get_by_stripe_subscription(obj.get("id"))
    if sub is None:
        return
    sub.status = SubscriptionStatus.canceled
    free = await PlanRepository(db).get_by_code("free")
    if free is not None:
        sub.plan_id = free.id
    await db.flush()


async def _on_invoice(db: AsyncSession, obj: dict, *, paid: bool) -> None:
    sub = await _resolve_subscription(
        db, customer=obj.get("customer"), metadata=obj.get("metadata", {}) or {}
    )
    if sub is None:
        return
    repo = InvoiceRepository(db)
    existing = await repo.find_one(Invoice.stripe_invoice_id == obj.get("id"))
    status = InvoiceStatus.paid if paid else InvoiceStatus.open
    if existing:
        existing.status = status
        existing.amount_paid_cents = obj.get("amount_paid", existing.amount_paid_cents)
    else:
        await repo.create(
            workspace_id=sub.workspace_id,
            number=obj.get("number"),
            amount_due_cents=obj.get("amount_due", 0),
            amount_paid_cents=obj.get("amount_paid", 0),
            currency=obj.get("currency", "usd"),
            status=status,
            hosted_invoice_url=obj.get("hosted_invoice_url"),
            stripe_invoice_id=obj.get("id"),
        )
    await db.flush()


async def get_subscription_with_plan(db: AsyncSession, workspace: Workspace):
    sub = await get_or_create_subscription(db, workspace)
    plan = await PlanRepository(db).get(sub.plan_id)
    if plan is None:
        raise NotFoundError("Plan not found for subscription.", code="plan_missing")
    return sub, plan
