"""Subscription + plan catalog + usage endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import WorkspaceContext, get_workspace_ctx
from app.core.database import get_db
from app.schemas.plan import PlanRead
from app.schemas.subscription import SubscriptionDetail, UsageRead
from app.services import billing as billing_service
from app.services import plan as plan_service
from app.services import usage as usage_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans", response_model=list[PlanRead])
async def list_plans(db: AsyncSession = Depends(get_db)):
    return await plan_service.list_public_plans(db)


@router.get("/current", response_model=SubscriptionDetail)
async def current_subscription(
    db: AsyncSession = Depends(get_db), ctx: WorkspaceContext = Depends(get_workspace_ctx)
):
    sub, plan = await billing_service.get_subscription_with_plan(db, ctx.workspace)
    detail = SubscriptionDetail.model_validate(sub).model_dump()
    detail["plan"] = PlanRead.model_validate(plan)
    return detail


@router.get("/usage", response_model=UsageRead)
async def current_usage(
    db: AsyncSession = Depends(get_db), ctx: WorkspaceContext = Depends(get_workspace_ctx)
):
    return await usage_service.get_usage_summary(db, ctx.id)
