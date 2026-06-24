"""Base OAuth2 provider: standard authorization-code flow + publishing hooks.

Most platforms share the same authorize/token mechanics; subclasses override the
URLs/scopes and implement ``fetch_account`` and ``publish_text`` against their
live API. Anything provider-specific (HTTP Basic token auth, extra token-response
fields like a page token) is handled via small overridable hooks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlencode

import httpx

from app.core.config import settings

_HTTP_TIMEOUT = 25.0


class OAuthError(Exception):
    """Raised when an OAuth or publish step fails; message is user-safe-ish."""


@dataclass
class TokenResult:
    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None  # seconds until access-token expiry
    scopes: list[str] | None = None
    raw: dict = field(default_factory=dict)  # full token response for provider hooks


@dataclass
class MediaRef:
    """A piece of media to attach to a post (streamed at publish time, not stored)."""

    kind: str  # "image" | "video"
    content_type: str
    data: bytes  # raw bytes — uploaded directly to the platform
    filename: str = "upload"


@dataclass
class AccountInfo:
    external_account_id: str | None = None
    handle: str | None = None
    display_name: str | None = None
    # Optional publishing token/target that differs from the user token
    # (e.g. a Facebook Page access token + page id). Stored on the connection.
    publish_token: str | None = None


class OAuthProvider:
    platform_id: str = ""
    authorize_url: str = ""
    token_url: str = ""
    scopes: list[str] = []
    scope_separator: str = " "
    use_pkce: bool = False
    token_auth_basic: bool = False  # send client creds via HTTP Basic (e.g. X)
    extra_authorize_params: dict[str, str] = {}
    # Capability: can this platform accept a plain-text post? (IG/TikTok/YT can't)
    can_publish_text: bool = True
    unsupported_reason: str = ""

    def __init__(self) -> None:
        self.client_id, self.client_secret = settings.platform_credentials(self.platform_id)

    # --- config helpers ---------------------------------------------------- #
    @property
    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    @property
    def redirect_uri(self) -> str:
        return settings.oauth_redirect_uri(self.platform_id)

    # --- authorize --------------------------------------------------------- #
    def authorize_url_for(self, state: str, code_challenge: str | None) -> str:
        params: dict[str, str] = {
            "client_id": self.client_id or "",
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scope_separator.join(self.scopes),
            "state": state,
            **self.extra_authorize_params,
        }
        if self.use_pkce and code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        return f"{self.authorize_url}?{urlencode(params)}"

    # --- token exchange ---------------------------------------------------- #
    def _token_data(self, code: str, code_verifier: str | None) -> dict[str, str]:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id or "",
        }
        if not self.token_auth_basic:
            data["client_secret"] = self.client_secret or ""
        if self.use_pkce and code_verifier:
            data["code_verifier"] = code_verifier
        return data

    async def exchange_code(self, code: str, code_verifier: str | None) -> TokenResult:
        auth = (
            (self.client_id or "", self.client_secret or "") if self.token_auth_basic else None
        )
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.post(
                self.token_url,
                data=self._token_data(code, code_verifier),
                headers={"Accept": "application/json"},
                auth=auth,
            )
        if resp.status_code >= 400:
            raise OAuthError(f"{self.platform_id} token exchange failed: {resp.text[:300]}")
        payload = resp.json()
        if "access_token" not in payload:
            raise OAuthError(f"{self.platform_id} token response missing access_token")
        scope_val = payload.get("scope")
        scopes = scope_val.split() if isinstance(scope_val, str) else None
        return TokenResult(
            access_token=payload["access_token"],
            refresh_token=payload.get("refresh_token"),
            expires_in=payload.get("expires_in"),
            scopes=scopes,
            raw=payload,
        )

    # --- account + publish (override per platform) ------------------------- #
    async def fetch_account(self, token: TokenResult) -> AccountInfo:  # noqa: ARG002
        return AccountInfo()

    async def publish(
        self,
        *,
        access_token: str,
        external_account_id: str | None,
        text: str,
        title: str | None = None,
        media: list[MediaRef] | None = None,
    ) -> str:
        raise OAuthError(
            self.unsupported_reason
            or f"Publishing is not supported for {self.platform_id} in this build."
        )

    # --- shared http helpers ---------------------------------------------- #
    @staticmethod
    async def _get_json(url: str, *, token: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.get(
                url, headers={"Authorization": f"Bearer {token}"}, params=params
            )
        if resp.status_code >= 400:
            raise OAuthError(f"GET {url} failed: {resp.text[:300]}")
        return resp.json()

    @staticmethod
    async def _post_json(url: str, *, token: str | None, json: dict, headers: dict | None = None) -> dict:
        h = {"Content-Type": "application/json"}
        if token:
            h["Authorization"] = f"Bearer {token}"
        if headers:
            h.update(headers)
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.post(url, json=json, headers=h)
        if resp.status_code >= 400:
            raise OAuthError(f"POST {url} failed: {resp.text[:300]}")
        return resp.json() if resp.content else {}
