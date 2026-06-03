"""Post + target repositories."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.enums import PostStatus
from app.models.post import Post, PostTarget
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    model = Post

    def list_stmt(self, workspace_id: uuid.UUID, status: PostStatus | None = None):
        stmt = select(Post).where(
            Post.workspace_id == workspace_id, Post.deleted_at.is_(None)
        )
        if status is not None:
            stmt = stmt.where(Post.status == status)
        return stmt.order_by(Post.created_at.desc())

    async def get_in_workspace(self, post_id: uuid.UUID, workspace_id: uuid.UUID) -> Post | None:
        return await self.find_one(
            Post.id == post_id,
            Post.workspace_id == workspace_id,
            Post.deleted_at.is_(None),
        )


class PostTargetRepository(BaseRepository[PostTarget]):
    model = PostTarget

    async def list_for_post(self, post_id: uuid.UUID) -> list[PostTarget]:
        return list(await self.list(PostTarget.post_id == post_id))

    async def get_for_platform(
        self, post_id: uuid.UUID, platform_id: str
    ) -> PostTarget | None:
        return await self.find_one(
            PostTarget.post_id == post_id, PostTarget.platform_id == platform_id
        )
