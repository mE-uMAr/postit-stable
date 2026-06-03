"""Subscription + billing schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import BillingCycle, InvoiceStatus, SubscriptionStatus
from app.schemas.common import ORMModel
from app.schemas.plan import PlanRead


class SubscriptionRead(ORMModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    plan_id: uuid.UUID
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    trial_end: datetime | None = None
    cancel_at_period_end: bool


class SubscriptionDetail(SubscriptionRead):
    plan: PlanRead


class CheckoutRequest(BaseModel):
    plan_id: uuid.UUID
    billing_cycle: BillingCycle = BillingCycle.monthly
    success_url: str | None = None
    cancel_url: str | None = None


class CheckoutSession(BaseModel):
    url: str
    session_id: str | None = None


class PortalSession(BaseModel):
    url: str


class InvoiceRead(ORMModel):
    id: uuid.UUID
    number: str | None = None
    amount_due_cents: int
    amount_paid_cents: int
    currency: str
    status: InvoiceStatus
    period_start: datetime | None = None
    period_end: datetime | None = None
    hosted_invoice_url: str | None = None
    created_at: datetime


class PaymentMethodRead(ORMModel):
    id: uuid.UUID
    brand: str
    last4: str | None = None
    exp_month: int | None = None
    exp_year: int | None = None
    is_default: bool


class UsageRead(BaseModel):
    period: str
    ai_posts_used: int
    ai_posts_limit: int
    posts_published: int
    connections_used: int
    connections_limit: int
    seats_used: int
    seats_limit: int
