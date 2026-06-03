"""Post create -> generate -> publish flow."""

from __future__ import annotations

import pytest


async def _auth(client, email):
    reg = await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Poster", "email": email, "password": "supersecret1"},
    )
    return {"Authorization": f"Bearer {reg.json()['tokens']['access_token']}"}


@pytest.mark.asyncio
async def test_post_lifecycle(client, unique_email):
    headers = await _auth(client, unique_email)

    created = await client.post(
        "/api/v1/posts",
        headers=headers,
        json={"body": "Launching our spring collection today, lighter and brighter."},
    )
    assert created.status_code == 201, created.text
    post_id = created.json()["id"]

    gen = await client.post(
        f"/api/v1/posts/{post_id}/generate",
        headers=headers,
        json={"platforms": ["x", "linkedin", "threads"]},
    )
    assert gen.status_code == 200, gen.text
    targets = gen.json()["targets"]
    assert len(targets) == 3
    assert all(t["content"] for t in targets)

    published = await client.post(f"/api/v1/posts/{post_id}/publish", headers=headers)
    assert published.status_code == 200
    assert published.json()["status"] == "published"

    listing = await client.get("/api/v1/posts?status=published", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1


@pytest.mark.asyncio
async def test_generate_requires_eligible_platform(client, unique_email):
    headers = await _auth(client, unique_email)
    created = await client.post(
        "/api/v1/posts", headers=headers, json={"body": "A text-only post."}
    )
    post_id = created.json()["id"]
    # Instagram requires media -> not eligible -> 422
    res = await client.post(
        f"/api/v1/posts/{post_id}/generate", headers=headers, json={"platforms": ["instagram"]}
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_platforms_endpoint(client):
    res = await client.get("/api/v1/platforms")
    assert res.status_code == 200
    assert len(res.json()) == 9
