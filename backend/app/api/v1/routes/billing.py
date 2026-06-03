"""Billing endpoints: checkout, portal, invoices, payment methods, webhook."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    WorkspaceContext,
    get_current_active_user,
    get_workspace_ctx,
    require_workspace_role,
)
from app.core.database import SessionLocal, get_db
from app.core.exceptions import BillingError
from app.core.logging import logger
from app.models.enums import WorkspaceRole
from app.models.user import User
from app.repositories.billing import InvoiceRepository, PaymentMethodRepository
from app.schemas.common import Message
from app.schemas.subscription import (
    CheckoutRequest,
    CheckoutSession,
    InvoiceRead,
    PaymentMethodRead,
    PortalSession,
)
from app.services import billing as billing_service
from app.services import stripe_gateway

router = APIRouter(prefix="/billing", tags=["billing"])

_admin = require_workspace_role(WorkspaceRole.admin)


@router.post("/checkout", response_model=CheckoutSession)
async def create_checkout(
    payload: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    ctx: WorkspaceContext = Depends(_admin),
):
    result = await billing_service.create_checkout(
        db,
        ctx.workspace,
        user,
        plan_id=payload.plan_id,
        cycle=payload.billing_cycle,
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
    )
    return CheckoutSession(**result)


@router.post("/portal", response_model=PortalSession)
async def create_portal(
    db: AsyncSession = Depends(get_db), ctx: WorkspaceContext = Depends(_admin)
):
    return PortalSession(**await billing_service.create_portal(db, ctx.workspace))


@router.get("/invoices", response_model=list[InvoiceRead])
async def list_invoices(
    db: AsyncSession = Depends(get_db), ctx: WorkspaceContext = Depends(get_workspace_ctx)
):
    return await InvoiceRepository(db).list_for_workspace(ctx.id)


@router.get("/payment-methods", response_model=list[PaymentMethodRead])
async def list_payment_methods(
    db: AsyncSession = Depends(get_db), ctx: WorkspaceContext = Depends(get_workspace_ctx)
):
    return await PaymentMethodRepository(db).list_for_workspace(ctx.id)


@router.post("/webhook", response_model=Message, include_in_schema=False)
async def stripe_webhook(
    request: Request, stripe_signature: str | None = Header(default=None, alias="Stripe-Signature")
):
    """Stripe webhook — unauthenticated, signature-verified. Uses its own DB session."""
    payload = await request.body()
    try:
        event = stripe_gateway.construct_event(payload, stripe_signature or "")
    except BillingError:
        raise
    except Exception as exc:  # signature / parse failure
        logger.warning("Stripe webhook verification failed: %s", exc)
        raise BillingError("Invalid webhook signature.", code="bad_signature") from exc

    event_dict = event if isinstance(event, dict) else event.to_dict()
    async with SessionLocal() as db:
        await billing_service.handle_webhook_event(db, event_dict)
        await db.commit()
    return Message(message="ok")
