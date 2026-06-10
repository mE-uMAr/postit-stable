"""Admin view of each platform's OAuth callback URLs + credential status.

Lets a superuser copy the exact Redirect / Uninstall (deauthorize) / Delete callback
URLs to paste into each platform's developer console.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import OAUTH_PLATFORMS, settings

router = APIRouter(prefix="/integrations", tags=["admin"])


@router.get("")
async def list_integrations() -> dict:
    return {
        "public_api_url": settings.PUBLIC_API_URL,
        "webhook_verify_token": settings.OAUTH_WEBHOOK_VERIFY_TOKEN,
        "platforms": [settings.platform_oauth_config(pid) for pid in OAUTH_PLATFORMS],
    }
