"""Post lifecycle: create, generate variants, edit, schedule, publish."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError_
from app.core.security import generate_opaque_token
from app.models.enums import ConnectionStatus, PostStatus, PublishJobStatus, TargetStatus
from app.models.platform import Platform
from app.models.post import Post, PostTarget
from app.models.publish_job import PublishJob
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.platform import ConnectionRepository, PlatformRepository
from app.repositories.post import PostRepository, PostTargetRepository
from app.schemas.post import PostCreate, PostUpdate
from app.services import publish as publish_service
from app.services import usage as usage_service
from app.services.ai import ai_service
from app.services.rewrite import title_for


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _reload_for_response(db: AsyncSession, post: Post) -> Post:
    """Make a post safe to serialize after a write.

    A flush expires server-side columns (``updated_at`` onupdate) and targets
    added by FK aren't reflected on the relationship — refresh both so Pydantic
    never triggers lazy IO outside the async greenlet.
    """
    await db.refresh(post)  # reload columns (clears expired updated_at)
    await db.refresh(post, attribute_names=["targets"])  # load/refresh relationship
    return post


def eligibility(platform: Platform, *, has_media: bool, has_video: bool, char_count: int) -> dict:
    if platform.requires_video and not has_video:
        return {"ok": False, "reason": "Needs a video — disabled for this post."}
    if platform.requires_media and not has_media:
        return {"ok": False, "reason": f"{platform.name} requires an image or video."}
    if platform.char_limit and char_count > platform.char_limit:
        return {"ok": True, "warn": f"Over {platform.char_limit} characters — Postit will trim."}
    return {"ok": True}


async def create_post(db: AsyncSession, workspace: Workspace, author: User, data: PostCreate) -> Post:
    posts = PostRepository(db)
    post = await posts.create(
        workspace_id=workspace.id,
        author_id=author.id,
        body=data.body,
        title=data.title or title_for(data.body),
        tone=data.tone,
        media=[m.model_dump() for m in data.media],
        status=PostStatus.draft,
    )
    return await _reload_for_response(db, post)


async def update_post(db: AsyncSession, post: Post, data: PostUpdate) -> Post:
    # Optimistic concurrency: reject edits made against a stale version.
    if data.version is not None and data.version != post.version:
        raise ConflictError(
            "This post was changed in another tab or by a teammate. Reload and try again.",
            code="stale_version",
        )
    if data.body is not None:
        post.body = data.body
    if data.title is not None:
        post.title = data.title
    if data.tone is not None:
        post.tone = data.tone
    if data.media is not None:
        post.media = [m.model_dump() for m in data.media]
    post.version += 1
    await db.flush()
    return await _reload_for_response(db, post)


async def delete_post(db: AsyncSession, post: Post) -> None:
    post.deleted_at = _now()
    await db.flush()


async def generate(db: AsyncSession, post: Post, platform_ids: list[str]) -> Post:
    """(Re)generate native variants for the selected, eligible platforms."""
    platforms = {p.id: p for p in await PlatformRepository(db).list_active()}
    has_media = bool(post.media)
    has_video = any((m or {}).get("type") == "video" for m in post.media)
    char_count = len(post.body)

    selected = [platforms[pid] for pid in platform_ids if pid in platforms]
    eligible = [p for p in selected if eligibility(p, has_media=has_media, has_video=has_video, char_count=char_count)["ok"]]
    if not eligible:
        raise ValidationError_("No eligible platforms selected for this post.", code="no_eligible_platforms")

    # Enforce the workspace's monthly AI generation limit.
    await usage_service.consume_ai_generation(db, post.workspace_id)

    targets_repo = PostTargetRepository(db)
    conns = ConnectionRepository(db)
    brand_voice = await ai_service.get_brand_voice(db, post.workspace_id)

    existing = {t.platform_id: t for t in await targets_repo.list_for_post(post.id)}
    keep_ids = {p.id for p in eligible}

    # Drop targets no longer selected.
    for pid, target in existing.items():
        if pid not in keep_ids:
            await targets_repo.delete(target)

    for platform in eligible:
        content = await ai_service.generate_variant(
            platform=platform, body=post.body, tone=post.tone, brand_voice=brand_voice
        )
        connection = await conns.get_for_platform(post.workspace_id, platform.id)
        connection_id = (
            connection.id if connection and connection.status == ConnectionStatus.connected else None
        )
        target = existing.get(platform.id)
        if target is None:
            db.add(
                PostTarget(
                    post_id=post.id,
                    platform_id=platform.id,
                    connection_id=connection_id,
                    content=content,
                    edited=False,
                    status=TargetStatus.pending,
                )
            )
        else:
            target.content = content
            target.edited = False
            target.connection_id = connection_id
            target.status = TargetStatus.pending

    post.status = PostStatus.ready
    await db.flush()
    return await _reload_for_response(db, post)


async def update_target(db: AsyncSession, post: Post, platform_id: str, content: str) -> PostTarget:
    target = await PostTargetRepository(db).get_for_platform(post.id, platform_id)
    if target is None:
        raise NotFoundError("No variant for that platform.", code="target_not_found")
    target.content = content
    target.edited = True
    await db.flush()
    return target


async def regenerate_target(db: AsyncSession, post: Post, platform_id: str) -> PostTarget:
    target = await PostTargetRepository(db).get_for_platform(post.id, platform_id)
    if target is None:
        raise NotFoundError("No variant for that platform.", code="target_not_found")
    platform = await PlatformRepository(db).get(platform_id)
    if platform is None:
        raise NotFoundError("Unknown platform.", code="platform_not_found")
    brand_voice = await ai_service.get_brand_voice(db, post.workspace_id)
    target.content = await ai_service.generate_variant(
        platform=platform, body=post.body, tone=post.tone, brand_voice=brand_voice
    )
    target.edited = False
    await db.flush()
    return target


async def schedule(db: AsyncSession, post: Post, scheduled_at: datetime) -> Post:
    """Queue a post for publishing at ``scheduled_at`` via the outbox.

    The in-process worker (:mod:`app.worker.scheduler`) drains due jobs and calls
    :func:`app.services.publish.publish_post`.
    """
    targets = await PostTargetRepository(db).list_for_post(post.id)
    if not targets:
        raise ValidationError_("Generate platform versions before scheduling.", code="no_targets")

    post.scheduled_at = scheduled_at
    post.status = PostStatus.scheduled
    for t in targets:
        t.status = TargetStatus.scheduled

    # One live outbox job per post; refresh an existing pending one on reschedule.
    existing = await _pending_job_for_post(db, post.id)
    if existing is not None:
        existing.run_after = scheduled_at
        existing.status = PublishJobStatus.pending
        existing.last_error = None
    else:
        db.add(
            PublishJob(
                post_id=post.id,
                status=PublishJobStatus.pending,
                run_after=scheduled_at,
                idempotency_key=generate_opaque_token(16),
            )
        )
    await db.flush()
    return await _reload_for_response(db, post)


async def _pending_job_for_post(db: AsyncSession, post_id: uuid.UUID) -> PublishJob | None:
    from sqlalchemy import select

    stmt = (
        select(PublishJob)
        .where(
            PublishJob.post_id == post_id,
            PublishJob.status.in_([PublishJobStatus.pending, PublishJobStatus.running]),
        )
        .limit(1)
    )
    return (await db.execute(stmt)).scalars().first()


async def publish(db: AsyncSession, post: Post) -> Post:
    """Publish immediately (synchronous) and record a completed outbox job."""
    post = await publish_service.publish_post(db, post)
    db.add(
        PublishJob(
            post_id=post.id,
            status=PublishJobStatus.succeeded,
            run_after=_now(),
            idempotency_key=generate_opaque_token(16),
        )
    )
    await db.flush()
    return await _reload_for_response(db, post)


async def get_post_or_404(db: AsyncSession, post_id: uuid.UUID, workspace_id: uuid.UUID) -> Post:
    post = await PostRepository(db).get_in_workspace(post_id, workspace_id)
    if post is None:
        raise NotFoundError("Post not found.", code="post_not_found")
    return post
