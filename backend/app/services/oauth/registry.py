"""Maps a platform id to its OAuth provider implementation."""

from __future__ import annotations

from app.services.oauth.base import OAuthProvider
from app.services.oauth.providers import (
    BloggerProvider,
    FacebookProvider,
    InstagramProvider,
    LinkedInProvider,
    ThreadsProvider,
    TikTokProvider,
    WordPressProvider,
    XProvider,
    YouTubeProvider,
)

_REGISTRY: dict[str, type[OAuthProvider]] = {
    "x": XProvider,
    "linkedin": LinkedInProvider,
    "facebook": FacebookProvider,
    "threads": ThreadsProvider,
    "instagram": InstagramProvider,
    "blogger": BloggerProvider,
    "youtube": YouTubeProvider,
    "wordpress": WordPressProvider,
    "tiktok": TikTokProvider,
}


def oauth_supported(platform_id: str) -> bool:
    return platform_id in _REGISTRY


def get_oauth_provider(platform_id: str) -> OAuthProvider:
    cls = _REGISTRY.get(platform_id)
    if cls is None:
        raise KeyError(f"No OAuth provider for platform '{platform_id}'")
    return cls()
