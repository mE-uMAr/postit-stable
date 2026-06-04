"""Async wrapper around the Paddle Billing REST API (httpx).

Paddle is a Merchant of Record. Checkout uses a server-created *transaction* that the
frontend opens with the Paddle.js overlay; subscription/payment state arrives via signed
webhooks. The gateway degrades gracefully: when no API key is configured, ``enabled`` is
False and mutating calls raise ``ServiceUnavailableError`` so the rest of the app runs.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError
from app.core.logging import logger


def enabled() -> bool:
    return settings.paddle_enabled


def _require() -> str:
    if not enabled():
        raise ServiceUnavailableError(
            "Paddle is not configured. Set PADDLE_API_KEY (sandbox) to enable billing.",
            code="paddle_disabled",
        )
    return settings.PADDLE_API_KEY  # type: ignore[return-value]


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_require()}",
        "Content-Type": "application/json",
    }


async def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{settings.paddle_api_base}{path}"
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.request(method, url, headers=_headers(), json=payload)
    if res.status_code >= 400:
        logger.warning("Paddle API %s %s -> %s: %s", method, path, res.status_code, res.text[:500])
        raise ServiceUnavailableError(
            f"Paddle API error ({res.status_code}).", code="paddle_api_error"
        )
    return res.json().get("data", {})


# --------------------------------------------------------------------------- #
# Products & prices
# --------------------------------------------------------------------------- #
async def ensure_plan_prices(plan) -> dict[str, str]:  # noqa: ANN001
    """Create/refresh the Paddle Product + monthly & annual Prices for a plan."""
    product_id = plan.paddle_product_id
    if not product_id:
        product = await _request(
            "POST",
            "/products",
            {
                "name": plan.name,
                "tax_category": "standard",
                "custom_data": {"plan_code": plan.code},
            },
        )
        product_id = product["id"]

    currency = (plan.currency or settings.PADDLE_CURRENCY).upper()

    monthly = await _request(
        "POST",
        "/prices",
        {
            "description": f"{plan.name} (monthly)",
            "product_id": product_id,
            "unit_price": {"amount": str(plan.price_monthly_cents), "currency_code": currency},
            "billing_cycle": {"interval": "month", "frequency": 1},
            "tax_mode": "account_setting",
            "custom_data": {"plan_code": plan.code, "cycle": "monthly"},
        },
    )
    annual = await _request(
        "POST",
        "/prices",
        {
            "description": f"{plan.name} (annual)",
            "product_id": product_id,
            "unit_price": {"amount": str(plan.price_annual_cents), "currency_code": currency},
            "billing_cycle": {"interval": "year", "frequency": 1},
            "tax_mode": "account_setting",
            "custom_data": {"plan_code": plan.code, "cycle": "annual"},
        },
    )
    return {
        "product_id": product_id,
        "price_monthly_id": monthly["id"],
        "price_annual_id": annual["id"],
    }


# --------------------------------------------------------------------------- #
# Customers
# --------------------------------------------------------------------------- #
async def ensure_customer(email: str, name: str) -> str:
    """Return a Paddle customer id, creating one or reusing the existing email."""
    _require()
    # Reuse an existing customer with this email if present.
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(
            f"{settings.paddle_api_base}/customers",
            headers=_headers(),
            params={"email": email},
        )
    if res.status_code < 400:
        existing = res.json().get("data", [])
        if existing:
            return existing[0]["id"]

    created = await _request("POST", "/customers", {"email": email, "name": name})
    return created["id"]


# --------------------------------------------------------------------------- #
# Checkout (transaction) & portal
# --------------------------------------------------------------------------- #
async def create_transaction(
    *, customer_id: str, price_id: str, custom_data: dict[str, Any]
) -> dict[str, Any]:
    return await _request(
        "POST",
        "/transactions",
        {
            "items": [{"price_id": price_id, "quantity": 1}],
            "customer_id": customer_id,
            "custom_data": custom_data,
            "collection_mode": "automatic",
        },
    )


async def create_portal_session(*, customer_id: str) -> str:
    data = await _request("POST", f"/customers/{customer_id}/portal-sessions", {})
    return data.get("urls", {}).get("general", {}).get("overview", "")


# --------------------------------------------------------------------------- #
# Webhook signature verification
# --------------------------------------------------------------------------- #
def verify_and_parse(payload: bytes, signature_header: str | None) -> dict[str, Any]:
    """Verify the ``Paddle-Signature`` header (HMAC-SHA256) and return the event JSON.

    Header format: ``ts=1700000000;h1=<hex hmac of "{ts}:{raw_body}">``.
    """
    _require()
    secret = settings.PADDLE_WEBHOOK_SECRET
    if not secret:
        logger.warning("PADDLE_WEBHOOK_SECRET unset; skipping webhook signature verification")
        return json.loads(payload)

    parts = dict(p.split("=", 1) for p in (signature_header or "").split(";") if "=" in p)
    ts, h1 = parts.get("ts"), parts.get("h1")
    if not ts or not h1:
        raise ServiceUnavailableError("Malformed Paddle-Signature header.", code="bad_signature")

    expected = hmac.new(secret.encode(), f"{ts}:{payload.decode()}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, h1):
        raise ServiceUnavailableError("Webhook signature mismatch.", code="bad_signature")
    return json.loads(payload)
