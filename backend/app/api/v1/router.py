"""Aggregate the v1 API."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import (
    analytics,
    auth,
    billing,
    brand_voice,
    connections,
    members,
    notifications,
    platforms,
    posts,
    products,
    site,
    subscriptions,
    users,
    webhooks,
    workspaces,
)
from app.api.v1.routes.admin import admin_router

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(workspaces.router)
api_router.include_router(members.router)
api_router.include_router(platforms.router)
api_router.include_router(connections.router)
api_router.include_router(posts.router)
api_router.include_router(products.router)
api_router.include_router(analytics.router)
api_router.include_router(subscriptions.router)
api_router.include_router(billing.router)
api_router.include_router(notifications.router)
api_router.include_router(brand_voice.router)
api_router.include_router(site.router)
api_router.include_router(webhooks.router)
api_router.include_router(admin_router)
