"""Real OAuth2 authorization + publishing for social platform connections.

Replaces the previous mock connect/publish. Each provider declares its
authorize/token endpoints, scopes and PKCE needs, and implements account
lookup + publishing against the platform's live API.
"""

from app.services.oauth.registry import get_oauth_provider, oauth_supported

__all__ = ["get_oauth_provider", "oauth_supported"]
