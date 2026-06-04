"""Scheduled publishing: the outbox worker drains due jobs idempotently."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.worker.scheduler import _process_due_jobs


async def _register(client, email: str) -> str:
    res = await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Sched User", "email": email, "password": "supersecret1"},
    )
    return res.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_scheduled_post_publishes_via_worker(client, unique_email):
    token = await _register(client, unique_email)
    h = {"Authorization": f"Bearer {token}"}

    post = (await client.post("/api/v1/posts", json={"body": "Spring is here"}, headers=h)).json()
    pid = post["id"]
    await client.post(f"/api/v1/posts/{pid}/generate", json={"platforms": ["x", "linkedin"]}, headers=h)

    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    sched = await client.post(f"/api/v1/posts/{pid}/schedule", json={"scheduled_at": past}, headers=h)
    assert sched.status_code == 200
    assert sched.json()["status"] == "scheduled"

    # The worker should now pick up the due job and publish it.
    handled = await _process_due_jobs()
    assert handled >= 1

    refreshed = (await client.get(f"/api/v1/posts/{pid}", headers=h)).json()
    assert refreshed["status"] == "published"
    assert all(t["status"] == "published" for t in refreshed["targets"])

    # Idempotent: a second drain does nothing (job already succeeded).
    assert await _process_due_jobs() == 0


@pytest.mark.asyncio
async def test_optimistic_concurrency_conflict(client, unique_email):
    token = await _register(client, unique_email)
    h = {"Authorization": f"Bearer {token}"}
    post = (await client.post("/api/v1/posts", json={"body": "v1 body"}, headers=h)).json()
    pid = post["id"]
    assert post["version"] == 1

    # Stale version is rejected.
    stale = await client.patch(f"/api/v1/posts/{pid}", json={"body": "x", "version": 99}, headers=h)
    assert stale.status_code == 409
    assert stale.json()["error"]["code"] == "stale_version"

    # Correct version succeeds.
    ok = await client.patch(f"/api/v1/posts/{pid}", json={"body": "x", "version": 1}, headers=h)
    assert ok.status_code == 200
    assert ok.json()["version"] == 2
