"""Superuser admin API — every route requires `is_superuser`."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_superuser
from app.api.v1.routes.admin import (
    analytics,
    audit,
    plans,
    platforms,
    subscriptions,
    users,
    workspaces,
)

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_superuser)],
)

admin_router.include_router(analytics.router)
admin_router.include_router(users.router)
admin_router.include_router(workspaces.router)
admin_router.include_router(subscriptions.router)
admin_router.include_router(plans.router)
admin_router.include_router(platforms.router)
admin_router.include_router(audit.router)
