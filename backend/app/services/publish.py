"""Publishing pipeline shared by immediate publish and the scheduled worker.

Each target is published to the live platform API using the workspace's stored
(encrypted) OAuth token. Targets transition to ``published`` with the real
external post id, the post status is rolled up, usage is recorded, and the
author is notified.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError_
from app.core.security import decrypt_secret
from app.models.enums import ConnectionStatus, NotificationType, PostStatus, TargetStatus
from app.models.notification import Notification
from app.models.post import Post, PostTarget
from app.repositories.platform import ConnectionRepository
from app.repositories.post import PostTargetRepository
from app.services import usage as usage_service
from app.services.oauth import get_oauth_provider, oauth_supported
from app.services.oauth.base import MediaRef, OAuthError


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _publish_target(
    db: AsyncSession, target: PostTarget, post: Post, media: list[MediaRef]
) -> bool:
    """Publish a single target to its live platform. Returns True on success.

    Raises on any failure so the caller marks just this target failed.
    """
    conn = None
    if target.connection_id is not None:
        conn = await ConnectionRepository(db).get(target.connection_id)
    if conn is None or conn.status != ConnectionStatus.connected:
        raise OAuthError("Account isn't connected for this platform — connect it and retry.")
    if not oauth_supported(target.platform_id):
        raise OAuthError(f"{target.platform_id} publishing isn't available.")

    provider = get_oauth_provider(target.platform_id)
    if not provider.can_publish_text and not media:
        raise OAuthError(provider.unsupported_reason)

    access_token = decrypt_secret(conn.access_token)
    if not access_token:
        raise OAuthError("Stored credentials are missing or invalid — reconnect the account.")

    external_id = await provider.publish(
        access_token=access_token,
        external_account_id=conn.external_account_id,
        text=target.content,
        title=post.title,
        media=media,
    )
    target.status = TargetStatus.published
    target.published_at = _now()
    target.external_post_id = external_id
    target.error = None
    return True


async def publish_post(
    db: AsyncSession, post: Post, media: list[MediaRef] | None = None
) -> Post:
    """Publish every target of a post and roll up its status. Idempotent-ish:
    already-published targets are left untouched.

    ``media`` is streamed straight to the platforms (nothing is stored); the
    scheduled worker passes none, so scheduled posts are text-only.
    """
    targets = await PostTargetRepository(db).list_for_post(post.id)
    if not targets:
        raise ValidationError_("Generate platform versions before publishing.", code="no_targets")

    media = media or []
    published = 0
    failed = 0
    for t in targets:
        if t.status == TargetStatus.published:
            published += 1
            continue
        try:
            ok = await _publish_target(db, t, post, media)
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
