"""Billing - plans, subscriptions, invoices, payment methods, usage counters."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.types import GUID, JSONType
from app.models.enums import BillingCycle, InvoiceStatus, SubscriptionStatus
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Plan(UUIDPKMixin, TimestampMixin, Base):
    """Admin-managed plan. Annual price derives from the monthly price + discount."""

    __tablename__ = "plans"

    code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_monthly_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    annual_discount_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    max_connections: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    max_ai_posts_monthly: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_seats: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    features: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    paddle_product_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    paddle_price_monthly_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    paddle_price_annual_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    @property
    def price_annual_cents(self) -> int:
        """Total yearly price after the configured discount, in cents."""
        yearly = self.price_monthly_cents * 12
        return round(yearly * (100 - self.annual_discount_percent) / 100)

    @property
    def is_unlimited_ai(self) -> bool:
        return self.max_ai_posts_monthly < 0


class Subscription(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("plans.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, native_enum=False, length=20),
        default=SubscriptionStatus.active,
        nullable=False,
    )
    billing_cycle: Mapped[BillingCycle] = mapped_column(
        Enum(BillingCycle, native_enum=False, length=12),
        default=BillingCycle.monthly,
        nullable=False,
    )
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    paddle_customer_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    paddle_subscription_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)


class Invoice(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "invoices"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amount_due_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    amount_paid_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, native_enum=False, length=20),
        default=InvoiceStatus.open,
        nullable=False,
    )
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hosted_invoice_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    paddle_transaction_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)


class PaymentMethod(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "payment_methods"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    brand: Mapped[str] = mapped_column(String(40), default="card", nullable=False)
    last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    exp_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    exp_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    paddle_payment_method_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


class UsageCounter(UUIDPKMixin, TimestampMixin, Base):
    """Per-workspace monthly usage for plan-limit enforcement."""

    __tablename__ = "usage_counters"
    __table_args__ = (UniqueConstraint("workspace_id", "period", name="uq_usage_ws_period"),)

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # "YYYY-MM"
    ai_posts_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    posts_published: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
