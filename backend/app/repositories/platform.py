"""Platform + connection repositories."""

from __future__ import annotations

import uuid

from app.models.connection import Connection
from app.models.enums import ConnectionStatus
from app.models.platform import Platform
from app.repositories.base import BaseRepository


class PlatformRepository(BaseRepository[Platform]):
    model = Platform

    async def list_active(self) -> list[Platform]:
        return list(
            await self.list(Platform.is_active.is_(True), order_by=Platform.sort_order.asc())
        )

    async def list_all(self) -> list[Platform]:
        return list(await self.list(order_by=Platform.sort_order.asc()))


class ConnectionRepository(BaseRepository[Connection]):
    model = Connection

    async def list_for_workspace(self, workspace_id: uuid.UUID) -> list[Connection]:
        return list(
            await self.list(
                Connection.workspace_id == workspace_id,
                order_by=Connection.created_at.asc(),
            )
        )

    async def get_for_platform(
        self, workspace_id: uuid.UUID, platform_id: str
    ) -> Connection | None:
        return await self.find_one(
            Connection.workspace_id == workspace_id,
            Connection.platform_id == platform_id,
        )

    async def count_connected(self, workspace_id: uuid.UUID) -> int:
        return await self.count(
            Connection.workspace_id == workspace_id,
            Connection.status == ConnectionStatus.connected,
        )
