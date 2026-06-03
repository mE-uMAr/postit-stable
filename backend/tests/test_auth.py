"""Auth flow: register, login, me, refresh, RBAC."""

from __future__ import annotations

import pytest


async def _register(client, email: str):
    return await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Test User", "email": email, "password": "supersecret1"},
    )


@pytest.mark.asyncio
async def test_register_login_me(client, unique_email):
    res = await _register(client, unique_email)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["user"]["email"] == unique_email
    assert body["tokens"]["access_token"]

    login = await client.post(
        "/api/v1/auth/login", json={"email": unique_email, "password": "supersecret1"}
    )
    assert login.status_code == 200
    token = login.json()["tokens"]["access_token"]

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == unique_email


@pytest.mark.asyncio
async def test_duplicate_email_conflict(client, unique_email):
    await _register(client, unique_email)
    dup = await _register(client, unique_email)
    assert dup.status_code == 409


@pytest.mark.asyncio
async def test_refresh_rotation(client, unique_email):
    reg = await _register(client, unique_email)
    refresh = reg.json()["tokens"]["refresh_token"]
    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert res.status_code == 200
    assert res.json()["access_token"]

    # Old refresh token is now revoked (reuse detection).
    reuse = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert reuse.status_code == 401


@pytest.mark.asyncio
async def test_protected_requires_auth(client):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_admin_requires_superuser(client, unique_email):
    reg = await _register(client, unique_email)
    token = reg.json()["tokens"]["access_token"]
    res = await client.get("/api/v1/admin/metrics", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
