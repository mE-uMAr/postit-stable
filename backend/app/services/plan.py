"""Plan management (admin) + Paddle price synchronisation."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.billing import Plan
from app.repositories.billing import PlanRepository
from app.schemas.plan import PlanCreate, PlanUpdate
from app.services import paddle_gateway


async def list_public_plans(db: AsyncSession) -> list[Plan]:
    return await PlanRepository(db).list_public()


async def list_all_plans(db: AsyncSession) -> list[Plan]:
    return await PlanRepository(db).list_all()


async def get_plan(db: AsyncSession, plan_id: uuid.UUID) -> Plan:
    plan = await PlanRepository(db).get(plan_id)
    if plan is None:
        raise NotFoundError("Plan not found.", code="plan_not_found")
    return plan


async def _sync_paddle(db: AsyncSession, plan: Plan) -> None:
    """Provision Paddle Product + Prices if Paddle is enabled (best-effort)."""
    if not paddle_gateway.enabled() or plan.price_monthly_cents <= 0:
        return
    ids = await paddle_gateway.ensure_plan_prices(plan)
    plan.paddle_product_id = ids["product_id"]
    plan.paddle_price_monthly_id = ids["price_monthly_id"]
    plan.paddle_price_annual_id = ids["price_annual_id"]
    await db.flush()


async def create_plan(db: AsyncSession, data: PlanCreate) -> Plan:
    repo = PlanRepository(db)
    if await repo.get_by_code(data.code):
        raise ConflictError("A plan with that code already exists.", code="plan_code_taken")
    plan = await repo.create(**data.model_dump())
    await _sync_paddle(db, plan)
    return plan


async def update_plan(db: AsyncSession, plan_id: uuid.UUID, data: PlanUpdate) -> Plan:
    plan = await get_plan(db, plan_id)
    changes = data.model_dump(exclude_unset=True)
    price_changed = (
        "price_monthly_cents" in changes or "annual_discount_percent" in changes
    )
    for key, value in changes.items():
        setattr(plan, key, value)
    await db.flush()
    if price_changed:
        # Prices are immutable in Paddle; create fresh ones to reflect the new amount.
        plan.paddle_price_monthly_id = None
        plan.paddle_price_annual_id = None
        await _sync_paddle(db, plan)
    return plan


async def delete_plan(db: AsyncSession, plan_id: uuid.UUID) -> None:
    plan = await get_plan(db, plan_id)
    # Soft-disable rather than hard delete to preserve subscription references.
    plan.is_active = False
    plan.is_public = False
    await db.flush()
