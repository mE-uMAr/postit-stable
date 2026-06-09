"""Billing orchestration: Paddle checkout (transaction), portal, and webhook sync."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BillingError, NotFoundError
from app.models.billing import Invoice, Subscription
from app.models.enums import BillingCycle, InvoiceStatus, SubscriptionStatus
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.billing import InvoiceRepository, PlanRepository, SubscriptionRepository
from app.services import paddle_gateway
from app.services import plan as plan_service


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


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
) -> dict[str, Any]:
    plan = await plan_service.get_plan(db, plan_id)
    if plan.price_monthly_cents <= 0:
        raise BillingError("That plan is free - no checkout required.", code="plan_is_free")

    # Ensure the plan has Paddle prices.
    if not plan.paddle_price_monthly_id or not plan.paddle_price_annual_id:
        ids = await paddle_gateway.ensure_plan_prices(plan)
        plan.paddle_product_id = ids["product_id"]
        plan.paddle_price_monthly_id = ids["price_monthly_id"]
        plan.paddle_price_annual_id = ids["price_annual_id"]
        await db.flush()

    price_id = (
        plan.paddle_price_annual_id if cycle == BillingCycle.annual else plan.paddle_price_monthly_id
    )

    sub = await get_or_create_subscription(db, workspace)
    if not sub.paddle_customer_id:
        sub.paddle_customer_id = await paddle_gateway.ensure_customer(user.email, workspace.name)
        await db.flush()

    txn = await paddle_gateway.create_transaction(
        customer_id=sub.paddle_customer_id,
        price_id=price_id,
        custom_data={
            "workspace_id": str(workspace.id),
            "plan_id": str(plan.id),
            "cycle": cycle.value,
        },
    )
    return {
        "transaction_id": txn["id"],
        "client_token": settings.PADDLE_CLIENT_TOKEN,
        "environment": settings.PADDLE_ENVIRONMENT,
    }


async def create_portal(db: AsyncSession, workspace: Workspace) -> dict[str, Any]:
    sub = await SubscriptionRepository(db).get_for_workspace(workspace.id)
    if sub is None or not sub.paddle_customer_id:
        raise BillingError("No billing account yet - start a subscription first.", code="no_customer")
    url = await paddle_gateway.create_portal_session(customer_id=sub.paddle_customer_id)
    if not url:
        raise BillingError("Couldn't open the billing portal.", code="portal_failed")
    return {"url": url}


# --------------------------------------------------------------------------- #
# Webhook handling (Paddle Billing events)
# --------------------------------------------------------------------------- #
_STATUS_MAP = {
    "active": SubscriptionStatus.active,
    "trialing": SubscriptionStatus.trialing,
    "past_due": SubscriptionStatus.past_due,
    "paused": SubscriptionStatus.past_due,
    "canceled": SubscriptionStatus.canceled,
}


async def handle_webhook_event(db: AsyncSession, event: dict[str, Any]) -> None:
    event_type = event.get("event_type", "")
    data = event.get("data", {}) or {}

    if event_type == "subscription.canceled":
        await _on_subscription_canceled(db, data)
    elif event_type.startswith("subscription."):
        await _on_subscription_sync(db, data)
    elif event_type == "transaction.completed":
        await _on_transaction_completed(db, data)


async def _resolve_subscription(
    db: AsyncSession, *, custom_data: dict, customer_id: str | None
) -> Subscription | None:
    repo = SubscriptionRepository(db)
    ws_id = custom_data.get("workspace_id")
    if ws_id:
        try:
            sub = await repo.get_for_workspace(uuid.UUID(ws_id))
            if sub:
                return sub
        except ValueError:
            pass
    if customer_id:
        return await repo.get_by_paddle_customer(customer_id)
    return None


async def _match_plan_by_price(db: AsyncSession, price_id: str | None):  # noqa: ANN201
    if not price_id:
        return None, None
    for plan in await PlanRepository(db).list_all():
        if plan.paddle_price_monthly_id == price_id:
            return plan, BillingCycle.monthly
        if plan.paddle_price_annual_id == price_id:
            return plan, BillingCycle.annual
    return None, None


async def _on_subscription_sync(db: AsyncSession, data: dict) -> None:
    repo = SubscriptionRepository(db)
    custom_data = data.get("custom_data") or {}
    sub = await repo.get_by_paddle_subscription(data.get("id", "")) or await _resolve_subscription(
        db, custom_data=custom_data, customer_id=data.get("customer_id")
    )
    if sub is None:
        return

    sub.paddle_subscription_id = data.get("id") or sub.paddle_subscription_id
    sub.paddle_customer_id = data.get("customer_id") or sub.paddle_customer_id
    sub.status = _STATUS_MAP.get(data.get("status", ""), sub.status)

    period = data.get("current_billing_period") or {}
    sub.current_period_start = _parse_dt(period.get("starts_at")) or sub.current_period_start
    sub.current_period_end = _parse_dt(period.get("ends_at")) or sub.current_period_end

    scheduled = data.get("scheduled_change") or {}
    sub.cancel_at_period_end = scheduled.get("action") == "cancel"

    # Resolve plan + cycle from custom_data, else from the subscription's price item.
    plan_id = custom_data.get("plan_id")
    cycle = custom_data.get("cycle")
    if plan_id:
        try:
            sub.plan_id = uuid.UUID(plan_id)
        except ValueError:
            pass
    else:
        items = data.get("items") or []
        price_id = items[0].get("price", {}).get("id") if items else None
        plan, matched_cycle = await _match_plan_by_price(db, price_id)
        if plan:
            sub.plan_id = plan.id
            cycle = cycle or (matched_cycle.value if matched_cycle else None)
    if cycle in (BillingCycle.monthly.value, BillingCycle.annual.value):
        sub.billing_cycle = BillingCycle(cycle)

    await db.flush()


async def _on_subscription_canceled(db: AsyncSession, data: dict) -> None:
    sub = await SubscriptionRepository(db).get_by_paddle_subscription(data.get("id", ""))
    if sub is None:
        return
    sub.status = SubscriptionStatus.canceled
    free = await PlanRepository(db).get_by_code("free")
    if free is not None:
        sub.plan_id = free.id
    await db.flush()


async def _on_transaction_completed(db: AsyncSession, data: dict) -> None:
    sub = await _resolve_subscription(
        db, custom_data=data.get("custom_data") or {}, customer_id=data.get("customer_id")
    )
    if sub is None:
        return
    repo = InvoiceRepository(db)
    txn_id = data.get("id")
    existing = await repo.find_one(Invoice.paddle_transaction_id == txn_id)
    totals = (data.get("details") or {}).get("totals") or {}
    grand_total = int(totals.get("grand_total") or 0)
    currency = (data.get("currency_code") or "USD").lower()[:3]

    if existing:
        existing.status = InvoiceStatus.paid
        existing.amount_paid_cents = grand_total
    else:
        await repo.create(
            workspace_id=sub.workspace_id,
            number=data.get("invoice_number"),
            amount_due_cents=grand_total,
            amount_paid_cents=grand_total,
            currency=currency,
            status=InvoiceStatus.paid,
            paddle_transaction_id=txn_id,
        )
    await db.flush()


async def get_subscription_with_plan(db: AsyncSession, workspace: Workspace):
    sub = await get_or_create_subscription(db, workspace)
    plan = await PlanRepository(db).get(sub.plan_id)
    if plan is None:
        raise NotFoundError("Plan not found for subscription.", code="plan_missing")
    return sub, plan
