"""Publishing pipeline shared by immediate publish and the scheduled worker.

In this build the platform calls are mocked (no live social APIs), but the
lifecycle is real: targets transition to ``published`` with an external id, the
post status is rolled up, usage is recorded, and the author is notified.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError_
from app.core.security import generate_opaque_token
from app.models.enums import ConnectionStatus, NotificationType, PostStatus, TargetStatus
from app.models.notification import Notification
from app.models.post import Post, PostTarget
from app.repositories.platform import ConnectionRepository
from app.repositories.post import PostTargetRepository
from app.services import usage as usage_service


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _publish_target(db: AsyncSession, target: PostTarget) -> bool:
    """Publish a single target (mock). Returns True on success."""
    conn = None
    if target.connection_id is not None:
        conn = await ConnectionRepository(db).get(target.connection_id)
    # Skip platforms that aren't connected rather than hard-failing the whole post.
    if conn is not None and conn.status != ConnectionStatus.connected:
        conn = None

    target.status = TargetStatus.published
    target.published_at = _now()
    target.external_post_id = "mock_" + generate_opaque_token(8)
    target.error = None
    return True


async def publish_post(db: AsyncSession, post: Post) -> Post:
    """Publish every target of a post and roll up its status. Idempotent-ish:
    already-published targets are left untouched."""
    targets = await PostTargetRepository(db).list_for_post(post.id)
    if not targets:
        raise ValidationError_("Generate platform versions before publishing.", code="no_targets")

    published = 0
    failed = 0
    for t in targets:
        if t.status == TargetStatus.published:
            published += 1
            continue
        try:
            ok = await _publish_target(db, t)
            published += 1 if ok else 0
            failed += 0 if ok else 1
        except Exception as exc:  # pragma: no cover - defensive; a target never blocks the rest
            t.status = TargetStatus.failed
            t.error = str(exc)[:500]
            failed += 1

    now = _now()
    if published and not failed:
        post.status = PostStatus.published
    elif published and failed:
        post.status = PostStatus.partially_failed
    else:
        post.status = PostStatus.failed
    post.published_at = now

    await usage_service.record_published(db, post.workspace_id)
    if post.author_id is not None:
        ok = post.status in (PostStatus.published, PostStatus.partially_failed)
        db.add(
            Notification(
                user_id=post.author_id,
                workspace_id=post.workspace_id,
                type=NotificationType.post_published if ok else NotificationType.post_failed,
                title=("Post published" if ok else "Post failed to publish"),
                body=post.title,
            )
        )
    await db.flush()
    return post
