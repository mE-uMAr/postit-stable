"""Admin plan CRUD (name, monthly price, annual discount, limits, features)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import Message
from app.schemas.plan import PlanCreate, PlanRead, PlanUpdate
from app.services import plan as plan_service
from app.services.audit import record_audit

router = APIRouter(prefix="/plans", tags=["admin"])


@router.get("", response_model=list[PlanRead])
async def list_plans(db: AsyncSession = Depends(get_db)):
    return await plan_service.list_all_plans(db)


@router.post("", response_model=PlanRead, status_code=201)
async def create_plan(
    payload: PlanCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_user),
):
    plan = await plan_service.create_plan(db, payload)
    await record_audit(
        db, action="admin.plan.created", actor_id=admin.id, target_type="plan", target_id=str(plan.id)
    )
    return plan


@router.patch("/{plan_id}", response_model=PlanRead)
async def update_plan(
    plan_id: uuid.UUID,
    payload: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_user),
):
    plan = await plan_service.update_plan(db, plan_id, payload)
    await record_audit(
        db, action="admin.plan.updated", actor_id=admin.id, target_type="plan", target_id=str(plan_id)
    )
    return plan


@router.delete("/{plan_id}", response_model=Message)
async def delete_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_user),
):
    await plan_service.delete_plan(db, plan_id)
    await record_audit(
        db, action="admin.plan.archived", actor_id=admin.id, target_type="plan", target_id=str(plan_id)
    )
    return Message(message="Plan archived.")
