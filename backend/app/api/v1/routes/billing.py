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
from app.core.exceptions import AppError, BillingError
from app.core.logging import logger
from app.models.enums import WorkspaceRole
from app.models.user import User
from app.repositories.billing import InvoiceRepository, PaymentMethodRepository
from app.schemas.common import Message
from app.schemas.subscription import (
    CheckoutRequest,
    InvoiceRead,
    PaddleCheckout,
    PaymentMethodRead,
    PortalSession,
)
from app.services import billing as billing_service
from app.services import paddle_gateway

router = APIRouter(prefix="/billing", tags=["billing"])

_admin = require_workspace_role(WorkspaceRole.admin)


@router.post("/checkout", response_model=PaddleCheckout)
async def create_checkout(
    payload: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    ctx: WorkspaceContext = Depends(_admin),
):
    """Create a Paddle transaction; the frontend opens it with the Paddle.js overlay."""
    result = await billing_service.create_checkout(
        db, ctx.workspace, user, plan_id=payload.plan_id, cycle=payload.billing_cycle
    )
    return PaddleCheckout(**result)


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
async def paddle_webhook(
    request: Request, paddle_signature: str | None = Header(default=None, alias="Paddle-Signature")
):
    """Paddle webhook — unauthenticated, signature-verified. Uses its own DB session."""
    payload = await request.body()
    try:
        event = paddle_gateway.verify_and_parse(payload, paddle_signature)
    except AppError:
        raise
    except Exception as exc:  # parse failure
        logger.warning("Paddle webhook verification failed: %s", exc)
        raise BillingError("Invalid webhook payload.", code="bad_webhook") from exc

    async with SessionLocal() as db:
        await billing_service.handle_webhook_event(db, event)
        await db.commit()
    return Message(message="ok")
