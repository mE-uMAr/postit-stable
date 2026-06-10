"""Site CMS, password reset, AI fallback, and error-log admin view."""

from __future__ import annotations

import pytest

from app.core.database import SessionLocal
from app.models.error_log import ErrorLog
from app.repositories.user import UserRepository


async def _register(client, email: str) -> dict:
    res = await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Feat User", "email": email, "password": "supersecret1"},
    )
    return res.json()


async def _promote_superuser(email: str) -> None:
    async with SessionLocal() as db:
        user = await UserRepository(db).get_by_email(email)
        user.is_superuser = True
        await db.commit()


# ---------------------------------------------------------------- site CMS ----
@pytest.mark.asyncio
async def test_public_site_content_has_defaults(client):
    res = await client.get("/api/v1/site/content")
    assert res.status_code == 200
    data = res.json()
    assert "hero" in data and data["hero"]["title"]
    assert isinstance(data["features"], list)


@pytest.mark.asyncio
async def test_site_edit_requires_superuser(client, unique_email):
    reg = await _register(client, unique_email)
    token = reg["tokens"]["access_token"]
    res = await client.put(
        "/api/v1/admin/site",
        json={"announcement": {"enabled": False, "text": "hi"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_superuser_can_edit_site(client, unique_email):
    reg = await _register(client, unique_email)
    await _promote_superuser(unique_email)
    token = reg["tokens"]["access_token"]
    res = await client.put(
        "/api/v1/admin/site",
        json={"announcement": {"enabled": False, "text": "Edited banner"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["announcement"]["text"] == "Edited banner"


# -------------------------------------------------------- password reset ----
@pytest.mark.asyncio
async def test_password_reset_flow(client, unique_email):
    await _register(client, unique_email)

    forgot = await client.post("/api/v1/auth/forgot", json={"email": unique_email})
    assert forgot.status_code == 200
    token = forgot.json()["reset_token"]  # surfaced outside production
    assert token

    reset = await client.post(
        "/api/v1/auth/reset", json={"token": token, "new_password": "brandnewpass1"}
    )
    assert reset.status_code == 200

    # Old password rejected, new password works.
    old = await client.post(
        "/api/v1/auth/login", json={"email": unique_email, "password": "supersecret1"}
    )
    assert old.status_code == 401
    new = await client.post(
        "/api/v1/auth/login", json={"email": unique_email, "password": "brandnewpass1"}
    )
    assert new.status_code == 200


@pytest.mark.asyncio
async def test_forgot_unknown_email_is_silent(client):
    res = await client.post("/api/v1/auth/forgot", json={"email": "no-such-user@maildomain.com"})
    assert res.status_code == 200
    assert res.json()["reset_token"] is None


# ------------------------------------------------------------- AI fallback ----
@pytest.mark.asyncio
async def test_ai_defaults_to_mock_provider():
    from app.services.ai import ai_service, get_provider

    assert get_provider().name == "mock"
    assert ai_service.enabled is False


# -------------------------------------------------------- platform webhooks ----
@pytest.mark.asyncio
async def test_webhook_verification_handshake(client):
    from app.core.config import settings

    ok = await client.get(
        "/api/v1/webhooks/threads/deauthorize",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": settings.OAUTH_WEBHOOK_VERIFY_TOKEN,
            "hub.challenge": "CH123",
        },
    )
    assert ok.status_code == 200 and ok.text == "CH123"

    bad = await client.get(
        "/api/v1/webhooks/threads/deauthorize",
        params={"hub.mode": "subscribe", "hub.verify_token": "nope", "hub.challenge": "x"},
    )
    assert bad.status_code == 403


@pytest.mark.asyncio
async def test_webhook_deauthorize_and_delete(client):
    deauth = await client.post("/api/v1/webhooks/threads/deauthorize", json={"user_id": "123"})
    assert deauth.status_code == 200 and deauth.json()["success"] is True

    delete = await client.post("/api/v1/webhooks/facebook/delete", json={"user_id": "123"})
    assert delete.status_code == 200
    body = delete.json()
    assert body["confirmation_code"] and body["url"].endswith(body["confirmation_code"])

    unknown = await client.post("/api/v1/webhooks/madeup/deauthorize", json={})
    assert unknown.status_code == 404


# ----------------------------------------------------------- error log view ----
@pytest.mark.asyncio
async def test_admin_error_log_lists_entries(client, unique_email):
    reg = await _register(client, unique_email)
    await _promote_superuser(unique_email)
    token = reg["tokens"]["access_token"]

    async with SessionLocal() as db:
        db.add(ErrorLog(status_code=500, error_code="boom", message="kaboom", path="/x", method="GET"))
        await db.commit()

    res = await client.get(
        "/api/v1/admin/errors", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert any(item["message"] == "kaboom" for item in res.json()["items"])
