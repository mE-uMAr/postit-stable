"""Offset/limit pagination helpers."""

from __future__ import annotations

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PageParams:
    """FastAPI dependency for ``?page=&size=``."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="1-based page number"),
        size: int = Query(20, ge=1, le=100, description="Items per page"),
    ) -> None:
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, params: PageParams) -> "Page[T]":
        pages = (total + params.size - 1) // params.size if params.size else 0
        return cls(items=items, total=total, page=params.page, size=params.size, pages=pages)


async def paginate(db: AsyncSession, stmt: Select, params: PageParams) -> tuple[list, int]:
    """Execute ``stmt`` with limit/offset and return ``(rows, total)``."""
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = (await db.execute(count_stmt)).scalar_one()
    rows = (await db.execute(stmt.offset(params.offset).limit(params.limit))).scalars().all()
    return list(rows), int(total)
