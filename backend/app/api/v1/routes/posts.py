"""Post endpoints (scoped to the active workspace)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    WorkspaceContext,
    get_current_active_user,
    get_workspace_ctx,
    require_workspace_role,
)
from app.core.database import get_db
from app.core.pagination import Page, PageParams, paginate
from app.models.enums import PostStatus, WorkspaceRole
from app.models.user import User
from app.repositories.post import PostRepository
from app.schemas.common import Message
from app.schemas.post import (
    GenerateRequest,
    PostCreate,
    PostRead,
    PostUpdate,
    ScheduleRequest,
    TargetRead,
    TargetUpdate,
)
from app.services import post as post_service

router = APIRouter(prefix="/posts", tags=["posts"])

_editor = require_workspace_role(WorkspaceRole.editor)


@router.get("", response_model=Page[PostRead])
async def list_posts(
    status: PostStatus | None = Query(default=None),
    q: str | None = Query(default=None, max_length=160),
    params: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(get_workspace_ctx),
):
    stmt = PostRepository(db).list_stmt(ctx.id, status, q)
    rows, total = await paginate(db, stmt, params)
    items = [PostRead.model_validate(p) for p in rows]
    return Page.create(items, total, params)


@router.post("", response_model=PostRead, status_code=201)
async def create_post(
    payload: PostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
    ctx: WorkspaceContext = Depends(_editor),
):
    post = await post_service.create_post(db, ctx.workspace, user, payload)
    return PostRead.model_validate(post)


@router.get("/{post_id}", response_model=PostRead)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(get_workspace_ctx),
):
    post = await post_service.get_post_or_404(db, post_id, ctx.id)
    return PostRead.model_validate(post)


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: uuid.UUID,
    payload: PostUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(_editor),
):
    post = await post_service.get_post_or_404(db, post_id, ctx.id)
    post = await post_service.update_post(db, post, payload)
    return PostRead.model_validate(post)


@router.delete("/{post_id}", response_model=Message)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(_editor),
):
    post = await post_service.get_post_or_404(db, post_id, ctx.id)
    await post_service.delete_post(db, post)
    return Message(message="Post deleted.")


@router.post("/{post_id}/generate", response_model=PostRead)
async def generate(
    post_id: uuid.UUID,
    payload: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(_editor),
):
    post = await post_service.get_post_or_404(db, post_id, ctx.id)
    post = await post_service.generate(db, post, payload.platforms)
    return PostRead.model_validate(post)


@router.put("/{post_id}/targets/{platform_id}", response_model=TargetRead)
async def update_target(
    post_id: uuid.UUID,
    platform_id: str,
    payload: TargetUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(_editor),
):
    post = await post_service.get_post_or_404(db, post_id, ctx.id)
    return await post_service.update_target(db, post, platform_id, payload.content)


@router.post("/{post_id}/targets/{platform_id}/regenerate", response_model=TargetRead)
async def regenerate_target(
    post_id: uuid.UUID,
    platform_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(_editor),
):
    post = await post_service.get_post_or_404(db, post_id, ctx.id)
    return await post_service.regenerate_target(db, post, platform_id)


@router.post("/{post_id}/schedule", response_model=PostRead)
async def schedule_post(
    post_id: uuid.UUID,
    payload: ScheduleRequest,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(_editor),
):
    post = await post_service.get_post_or_404(db, post_id, ctx.id)
    post = await post_service.schedule(db, post, payload.scheduled_at)
    return PostRead.model_validate(post)


@router.post("/{post_id}/publish", response_model=PostRead)
async def publish_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: WorkspaceContext = Depends(_editor),
):
    post = await post_service.get_post_or_404(db, post_id, ctx.id)
    post = await post_service.publish(db, post)
    return PostRead.model_validate(post)
