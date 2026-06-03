"""Thin async wrapper around the Stripe SDK.

Every call degrades gracefully: when no test key is configured the gateway reports
``enabled == False`` and mutating calls raise ``ServiceUnavailableError`` so the rest of
the app keeps working without Stripe.
"""

from __future__ import annotations

from typing import Any

import anyio

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError
from app.core.logging import logger

try:  # pragma: no cover - import guard
    import stripe
except Exception:  # pragma: no cover
    stripe = None  # type: ignore[assignment]


def enabled() -> bool:
    return settings.stripe_enabled and stripe is not None


def _require():  # noqa: ANN202
    if not enabled():
        raise ServiceUnavailableError(
            "Stripe is not configured. Set STRIPE_SECRET_KEY (test mode) to enable billing.",
            code="stripe_disabled",
        )
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


async def _call(fn, /, *args, **kwargs):  # noqa: ANN001, ANN202
    return await anyio.to_thread.run_sync(lambda: fn(*args, **kwargs))


async def ensure_plan_prices(plan) -> dict[str, str]:  # noqa: ANN001
    """Create/refresh the Stripe Product + monthly & annual Prices for a plan."""
    s = _require()
    product_id = plan.stripe_product_id
    if not product_id:
        product = await _call(
            s.Product.create, name=plan.name, metadata={"plan_code": plan.code}
        )
        product_id = product["id"]

    monthly = await _call(
        s.Price.create,
        product=product_id,
        unit_amount=plan.price_monthly_cents,
        currency=plan.currency,
        recurring={"interval": "month"},
        metadata={"plan_code": plan.code, "cycle": "monthly"},
    )
    annual = await _call(
        s.Price.create,
        product=product_id,
        unit_amount=plan.price_annual_cents,
        currency=plan.currency,
        recurring={"interval": "year"},
        metadata={"plan_code": plan.code, "cycle": "annual"},
    )
    return {
        "product_id": product_id,
        "price_monthly_id": monthly["id"],
        "price_annual_id": annual["id"],
    }


async def ensure_customer(email: str, name: str, metadata: dict[str, Any]) -> str:
    s = _require()
    customer = await _call(s.Customer.create, email=email, name=name, metadata=metadata)
    return customer["id"]


async def create_checkout_session(
    *, customer_id: str, price_id: str, success_url: str, cancel_url: str, metadata: dict[str, Any]
) -> dict[str, Any]:
    s = _require()
    return await _call(
        s.checkout.Session.create,
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
        subscription_data={"metadata": metadata},
    )


async def create_portal_session(*, customer_id: str, return_url: str) -> dict[str, Any]:
    s = _require()
    return await _call(s.billing_portal.Session.create, customer=customer_id, return_url=return_url)


def construct_event(payload: bytes, sig_header: str) -> Any:
    s = _require()
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.warning("STRIPE_WEBHOOK_SECRET unset; skipping signature verification")
        import json

        return json.loads(payload)
    return s.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
