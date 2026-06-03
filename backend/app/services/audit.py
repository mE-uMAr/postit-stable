"""Audit logging helper."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def record_audit(
    db: AsyncSession,
    *,
    action: str,
    actor_id: uuid.UUID | None = None,
    workspace_id: uuid.UUID | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    meta: dict[str, Any] | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        action=action,
        actor_id=actor_id,
        workspace_id=workspace_id,
        target_type=target_type,
        target_id=target_id,
        meta=meta,
        ip=ip,
        user_agent=user_agent,
    )
    db.add(entry)
    await db.flush()
    return entry
