"""Billing repositories — plans, subscriptions, invoices, payment methods, usage."""

from __future__ import annotations

import uuid

from app.models.billing import Invoice, PaymentMethod, Plan, Subscription, UsageCounter
from app.repositories.base import BaseRepository


class PlanRepository(BaseRepository[Plan]):
    model = Plan

    async def get_by_code(self, code: str) -> Plan | None:
        return await self.find_one(Plan.code == code)

    async def list_public(self) -> list[Plan]:
        return list(
            await self.list(
                Plan.is_active.is_(True),
                Plan.is_public.is_(True),
                order_by=Plan.sort_order.asc(),
            )
        )

    async def list_all(self) -> list[Plan]:
        return list(await self.list(order_by=Plan.sort_order.asc()))


class SubscriptionRepository(BaseRepository[Subscription]):
    model = Subscription

    async def get_for_workspace(self, workspace_id: uuid.UUID) -> Subscription | None:
        return await self.find_one(Subscription.workspace_id == workspace_id)

    async def get_by_paddle_subscription(self, sub_id: str) -> Subscription | None:
        return await self.find_one(Subscription.paddle_subscription_id == sub_id)

    async def get_by_paddle_customer(self, customer_id: str) -> Subscription | None:
        return await self.find_one(Subscription.paddle_customer_id == customer_id)


class InvoiceRepository(BaseRepository[Invoice]):
    model = Invoice

    async def list_for_workspace(self, workspace_id: uuid.UUID, limit: int = 20) -> list[Invoice]:
        return list(
            await self.list(
                Invoice.workspace_id == workspace_id,
                order_by=Invoice.created_at.desc(),
                limit=limit,
            )
        )


class PaymentMethodRepository(BaseRepository[PaymentMethod]):
    model = PaymentMethod

    async def list_for_workspace(self, workspace_id: uuid.UUID) -> list[PaymentMethod]:
        return list(await self.list(PaymentMethod.workspace_id == workspace_id))


class UsageRepository(BaseRepository[UsageCounter]):
    model = UsageCounter

    async def get_or_create(self, workspace_id: uuid.UUID, period: str) -> UsageCounter:
        existing = await self.find_one(
            UsageCounter.workspace_id == workspace_id, UsageCounter.period == period
        )
        if existing:
            return existing
        return await self.create(workspace_id=workspace_id, period=period)
