"""Plan schemas (admin-managed; annual price derived from discount)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, computed_field

from app.schemas.common import ORMModel


class PlanBase(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=80)
    description: str | None = None
    price_monthly_cents: int = Field(ge=0)
    currency: str = "usd"
    annual_discount_percent: int = Field(default=0, ge=0, le=100)
    max_connections: int = Field(default=3, ge=-1)
    max_ai_posts_monthly: int = Field(default=10, ge=-1)  # -1 = unlimited
    max_seats: int = Field(default=1, ge=1)
    features: list[str] = Field(default_factory=list)
    is_active: bool = True
    is_public: bool = True
    sort_order: int = 0


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price_monthly_cents: int | None = Field(default=None, ge=0)
    annual_discount_percent: int | None = Field(default=None, ge=0, le=100)
    max_connections: int | None = Field(default=None, ge=-1)
    max_ai_posts_monthly: int | None = Field(default=None, ge=-1)
    max_seats: int | None = Field(default=None, ge=1)
    features: list[str] | None = None
    is_active: bool | None = None
    is_public: bool | None = None
    sort_order: int | None = None


class PlanRead(ORMModel):
    id: uuid.UUID
    code: str
    name: str
    description: str | None = None
    price_monthly_cents: int
    currency: str
    annual_discount_percent: int
    max_connections: int
    max_ai_posts_monthly: int
    max_seats: int
    features: list
    is_active: bool
    is_public: bool
    sort_order: int
    stripe_price_monthly_id: str | None = None
    stripe_price_annual_id: str | None = None
    created_at: datetime

    @computed_field
    @property
    def price_annual_cents(self) -> int:
        yearly = self.price_monthly_cents * 12
        return round(yearly * (100 - self.annual_discount_percent) / 100)
