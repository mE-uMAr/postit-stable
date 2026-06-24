"""Platform OAuth callbacks: deauthorize (uninstall) + data-deletion requests.

These are the public, server-to-server callback URLs you paste into each platform's
developer console (e.g. the Threads/Facebook/Instagram "Uninstall" and "Delete"
callbacks). They authenticate via the Meta-style ``signed_request`` (verified with the
platform's client secret) when present, audit-log the event, and best-effort revoke the
matching connection. No user session is involved.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import client_meta
from app.core.config import OAUTH_PLATFORMS, settings
from app.core.database import get_db
from app.core.exceptions import NotFoundError, PermissionError_
from app.core.security import generate_opaque_token
from app.models.connection import Connection
from app.models.enums import ConnectionStatus
from app.services.audit import record_audit

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _b64url_decode(segment: str) -> bytes:
    return base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))


def parse_signed_request(signed_request: str, secret: str | None) -> dict | None:
    """Decode a Meta ``signed_request`` and verify it against the app secret."""
    try:
        sig_b64, payload_b64 = signed_request.split(".", 1)
        payload = json.loads(_b64url_decode(payload_b64))
    except (ValueError, binascii.Error, json.JSONDecodeError):
        return None
    if secret:
        expected = hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).digest()
        try:
            given = _b64url_decode(sig_b64)
        except binascii.Error:
            return None
        if not hmac.compare_digest(expected, given):
            return None
    return payload


def _ensure_known_platform(platform_id: str) -> None:
    if platform_id not in OAUTH_PLATFORMS:
        raise NotFoundError("Unknown platform.", code="platform_not_found")


async def _extract_external_id(platform_id: str, request: Request) -> str | None:
    """Pull the platform user id from a signed_request (Meta) or JSON/form body."""
    signed: str | None = None
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001 - empty/invalid body
            body = None
        if isinstance(body, dict):
            signed = body.get("signed_request")
            if not signed:
                return str(body.get("user_id") or body.get("external_account_id") or "") or None
    else:
        try:
            form = await request.form()
            signed = form.get("signed_request")  # type: ignore[assignment]
        except Exception:  # noqa: BLE001
            signed = None
    if signed:
        _, secret = settings.platform_credentials(platform_id)
        data = parse_signed_request(str(signed), secret)
        if data:
            return str(data.get("user_id") or data.get("user") or "") or None
    return None


async def _revoke_by_external_id(db: AsyncSession, platform_id: str, external_id: str | None) -> int:
    if not external_id:
        return 0
    rows = (
        await db.execute(
            select(Connection).where(
                Connection.platform_id == platform_id,
                Connection.external_account_id == external_id,
            )
        )
    ).scalars().all()
    for conn in rows:
        conn.status = ConnectionStatus.revoked
        conn.access_token = None
        conn.refresh_token = None
    return len(rows)


# --------------------------------------------------------------------------- #
# Webhook subscription verification (Meta GET handshake)
# --------------------------------------------------------------------------- #
@router.get("/{platform_id}", response_class=PlainTextResponse)
@router.get("/{platform_id}/deauthorize", response_class=PlainTextResponse)
@router.get("/{platform_id}/delete", response_class=PlainTextResponse)
async def verify_subscription(
    platform_id: str,
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
):
    """Meta webhook GET handshake — echo hub.challenge when the verify token matches.

    This is the URL to paste into a platform's **Webhooks** product:
    ``https://<api>/api/v1/webhooks/<platform>`` with the verify token set to
    ``OAUTH_WEBHOOK_VERIFY_TOKEN``.
    """
    _ensure_known_platform(platform_id)
    if hub_mode == "subscribe" and hub_verify_token == settings.OAUTH_WEBHOOK_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge or "")
    raise PermissionError_("Invalid verify token.", code="bad_verify_token")


@router.post("/{platform_id}")
async def receive_webhook(
    platform_id: str, request: Request, db: AsyncSession = Depends(get_db)
):
    """Receive webhook event notifications (signature-verified when possible)."""
    _ensure_known_platform(platform_id)
    raw = await request.body()
    _, secret = settings.platform_credentials(platform_id)
    sig = request.headers.get("x-hub-signature-256", "")
    if secret and sig.startswith("sha256="):
        expected = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig.split("=", 1)[1]):
            raise PermissionError_("Invalid signature.", code="bad_signature")
    await record_audit(
        db,
        action="platform.webhook",
        target_type="platform",
        target_id=platform_id,
        meta={"bytes": len(raw)},
        **client_meta(request),
    )
    return {"received": True}


# --------------------------------------------------------------------------- #
# Deauthorize (uninstall) callback
# --------------------------------------------------------------------------- #
@router.post("/{platform_id}/deauthorize")
async def deauthorize(
    platform_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _ensure_known_platform(platform_id)
    external_id = await _extract_external_id(platform_id, request)
    revoked = await _revoke_by_external_id(db, platform_id, external_id)
    await record_audit(
        db,
        action="platform.deauthorized",
        target_type="platform",
        target_id=platform_id,
        meta={"external_id": external_id, "connections_revoked": revoked},
        **client_meta(request),
    )
    return {"success": True}


# --------------------------------------------------------------------------- #
# Data-deletion request callback
# --------------------------------------------------------------------------- #
@router.post("/{platform_id}/delete")
async def request_deletion(
    platform_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge a data-deletion request.

    Returns the JSON shape Meta requires: a status URL the user can check plus a
    confirmation code. We revoke connections and record the request for follow-up.
    """
    _ensure_known_platform(platform_id)
    external_id = await _extract_external_id(platform_id, request)
    code = generate_opaque_token(12)
    revoked = await _revoke_by_external_id(db, platform_id, external_id)
    await record_audit(
        db,
        action="platform.deletion_requested",
        target_type="platform",
        target_id=platform_id,
        meta={"external_id": external_id, "confirmation_code": code, "connections_revoked": revoked},
        **client_meta(request),
    )
    return {
        "url": f"{settings._api_base}/webhooks/{platform_id}/delete/status?code={code}",
        "confirmation_code": code,
    }


@router.get("/{platform_id}/delete/status")
async def deletion_status(platform_id: str, code: str = Query(...)):
    """Public status page a user can hit to confirm their deletion request."""
    _ensure_known_platform(platform_id)
    return {
        "platform": platform_id,
        "confirmation_code": code,
        "status": "received",
        "message": "Your data-deletion request has been received and connections were revoked.",
    }
