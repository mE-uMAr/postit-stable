"""Generic async repository with the common CRUD surface."""

from __future__ import annotations

from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, id_: Any) -> ModelT | None:
        return await self.db.get(self.model, id_)

    async def list(
        self,
        *whereclauses: Any,
        order_by: Any = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ModelT]:
        stmt: Select = select(self.model)
        if whereclauses:
            stmt = stmt.where(*whereclauses)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return (await self.db.execute(stmt)).scalars().all()

    async def find_one(self, *whereclauses: Any) -> ModelT | None:
        stmt = select(self.model).where(*whereclauses).limit(1)
        return (await self.db.execute(stmt)).scalars().first()

    async def count(self, *whereclauses: Any) -> int:
        stmt = select(func.count()).select_from(self.model)
        if whereclauses:
            stmt = stmt.where(*whereclauses)
        return int((await self.db.execute(stmt)).scalar_one())

    def add(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        return obj

    async def create(self, **kwargs: Any) -> ModelT:
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    async def flush(self) -> None:
        await self.db.flush()
