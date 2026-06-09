"""In-process publish worker - drains the ``publish_jobs`` outbox.

Started from the FastAPI lifespan when ``SCHEDULER_ENABLED`` is true. Polls for
due jobs (``pending`` with ``run_after <= now``), claims each atomically, and
publishes via :func:`app.services.publish.publish_post`, with bounded retries.

For a single API process this is sufficient. When running multiple web workers,
run the API with ``SCHEDULER_ENABLED=false`` and start exactly one process with
it enabled (or split this into a dedicated worker entrypoint).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import logger
from app.models.enums import PublishJobStatus
from app.models.post import Post
from app.models.publish_job import PublishJob
from app.services import publish as publish_service


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _claim(db, job_id) -> bool:  # noqa: ANN001
    """Atomically move a job pending→running. Returns True if we own it."""
    res = await db.execute(
        update(PublishJob)
        .where(PublishJob.id == job_id, PublishJob.status == PublishJobStatus.pending)
        .values(status=PublishJobStatus.running, attempts=PublishJob.attempts + 1)
    )
    await db.commit()
    return res.rowcount == 1


async def _process_due_jobs() -> int:
    """Process all currently-due jobs. Returns the count handled."""
    handled = 0
    async with SessionLocal() as db:
        stmt = (
            select(PublishJob.id)
            .where(
                PublishJob.status == PublishJobStatus.pending,
                (PublishJob.run_after.is_(None)) | (PublishJob.run_after <= _now()),
            )
            .order_by(PublishJob.run_after.asc())
            .limit(50)
        )
        due_ids = [row[0] for row in (await db.execute(stmt)).all()]

    for job_id in due_ids:
        async with SessionLocal() as db:
            if not await _claim(db, job_id):
                continue  # another tick/worker grabbed it
            job = await db.get(PublishJob, job_id)
            try:
                post = await db.get(Post, job.post_id)
                if post is None or post.deleted_at is not None:
                    job.status = PublishJobStatus.failed
                    job.last_error = "Post no longer exists."
                else:
                    await publish_service.publish_post(db, post)
                    job.status = PublishJobStatus.succeeded
                    job.last_error = None
                await db.commit()
                handled += 1
            except Exception as exc:  # noqa: BLE001 - retry/backoff, never crash the loop
                await db.rollback()
                job = await db.get(PublishJob, job_id)
                job.last_error = str(exc)[:500]
                if job.attempts >= settings.SCHEDULER_MAX_ATTEMPTS:
                    job.status = PublishJobStatus.failed
                    logger.error("Publish job %s failed permanently: %s", job_id, exc)
                else:
                    # Exponential backoff, then make it due again.
                    job.status = PublishJobStatus.pending
                    job.run_after = _now() + timedelta(seconds=30 * job.attempts)
                    logger.warning("Publish job %s retry %s: %s", job_id, job.attempts, exc)
                await db.commit()
    return handled


async def run_scheduler(stop: asyncio.Event) -> None:
    """Poll loop. Exits when ``stop`` is set."""
    logger.info("Publish scheduler started (poll=%ss)", settings.SCHEDULER_POLL_SECONDS)
    while not stop.is_set():
        try:
            await _process_due_jobs()
        except Exception:  # noqa: BLE001 - the loop must survive transient errors
            logger.exception("Scheduler tick failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=settings.SCHEDULER_POLL_SECONDS)
        except asyncio.TimeoutError:
            pass
    logger.info("Publish scheduler stopped")
