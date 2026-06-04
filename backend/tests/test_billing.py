"""Plan catalog + Paddle-disabled billing path + admin plan CRUD."""

from __future__ import annotations

import pytest


async def _register(client, email):
    reg = await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Biller", "email": email, "password": "supersecret1"},
    )
    return reg.json()


@pytest.mark.asyncio
async def test_plans_listed(client):
    res = await client.get("/api/v1/subscriptions/plans")
    assert res.status_code == 200
    codes = {p["code"] for p in res.json()}
    assert {"free", "pro", "team"} <= codes


@pytest.mark.asyncio
async def test_annual_price_derivation(client):
    res = await client.get("/api/v1/subscriptions/plans")
    pro = next(p for p in res.json() if p["code"] == "pro")
    # 1900 * 12 = 22800, minus 20% = 18240.
    assert pro["price_annual_cents"] == 18240


@pytest.mark.asyncio
async def test_default_subscription_is_free(client, unique_email):
    data = await _register(client, unique_email)
    headers = {"Authorization": f"Bearer {data['tokens']['access_token']}"}
    res = await client.get("/api/v1/subscriptions/current", headers=headers)
    assert res.status_code == 200
    assert res.json()["plan"]["code"] == "free"


@pytest.mark.asyncio
async def test_checkout_disabled_without_paddle(client, unique_email):
    data = await _register(client, unique_email)
    headers = {"Authorization": f"Bearer {data['tokens']['access_token']}"}
    plans = (await client.get("/api/v1/subscriptions/plans")).json()
    pro_id = next(p["id"] for p in plans if p["code"] == "pro")
    res = await client.post(
        "/api/v1/billing/checkout", headers=headers, json={"plan_id": pro_id, "billing_cycle": "monthly"}
    )
    # Paddle not configured in tests -> 503.
    assert res.status_code == 503


@pytest.mark.asyncio
async def test_usage_limit_free_plan(client, unique_email):
    """Free plan allows 10 AI generations/month; the 11th is blocked."""
    data = await _register(client, unique_email)
    headers = {"Authorization": f"Bearer {data['tokens']['access_token']}"}
    body = {"body": "Spring is here, lighter materials and a brighter palette today."}
    post_id = (await client.post("/api/v1/posts", headers=headers, json=body)).json()["id"]

    last_status = None
    for _ in range(11):
        res = await client.post(
            f"/api/v1/posts/{post_id}/generate", headers=headers, json={"platforms": ["x"]}
        )
        last_status = res.status_code
    assert last_status == 402  # billing limit reached
