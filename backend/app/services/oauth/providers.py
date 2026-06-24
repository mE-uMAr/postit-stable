"""Concrete OAuth providers + publishers, one class per platform.

Endpoints/scopes follow each platform's current documented OAuth2 + publishing
API. Text-capable networks (X, LinkedIn, Facebook Pages, Threads, WordPress,
Blogger) implement ``publish_text``; media-first networks (Instagram, TikTok,
YouTube) authenticate for real but refuse text-only posts with a clear reason
rather than faking success.
"""

from __future__ import annotations

from urllib.parse import urlencode

import httpx

from app.services.oauth.base import AccountInfo, OAuthError, OAuthProvider, TokenResult

_TIMEOUT = 25.0
_GRAPH = "https://graph.facebook.com/v21.0"


# --------------------------------------------------------------------------- #
# X (Twitter) — OAuth2 + PKCE, HTTP Basic token auth
# --------------------------------------------------------------------------- #
class XProvider(OAuthProvider):
    platform_id = "x"
    authorize_url = "https://twitter.com/i/oauth2/authorize"
    token_url = "https://api.twitter.com/2/oauth2/token"
    scopes = ["tweet.read", "tweet.write", "users.read", "offline.access"]
    use_pkce = True
    token_auth_basic = True

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        data = (await self._get_json("https://api.twitter.com/2/users/me", token=token.access_token)).get("data", {})
        return AccountInfo(
            external_account_id=data.get("id"),
            handle=f"@{data['username']}" if data.get("username") else None,
            display_name=data.get("name"),
        )

    async def publish_text(self, *, access_token, external_account_id=None, text, title=None) -> str:
        out = await self._post_json("https://api.twitter.com/2/tweets", token=access_token, json={"text": text})
        tweet_id = (out.get("data") or {}).get("id")
        if not tweet_id:
            raise OAuthError(f"X publish returned no id: {out}")
        return tweet_id


# --------------------------------------------------------------------------- #
# LinkedIn — OAuth2 (OpenID Connect), member share
# --------------------------------------------------------------------------- #
class LinkedInProvider(OAuthProvider):
    platform_id = "linkedin"
    authorize_url = "https://www.linkedin.com/oauth/v2/authorization"
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    scopes = ["openid", "profile", "w_member_social"]

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        me = await self._get_json("https://api.linkedin.com/v2/userinfo", token=token.access_token)
        return AccountInfo(
            external_account_id=me.get("sub"),
            handle=me.get("name"),
            display_name=me.get("name"),
        )

    async def publish_text(self, *, access_token, external_account_id=None, text, title=None) -> str:
        if not external_account_id:
            raise OAuthError("LinkedIn connection missing member id; reconnect the account.")
        body = {
            "author": f"urn:li:person:{external_account_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        out = await self._post_json(
            "https://api.linkedin.com/v2/ugcPosts",
            token=access_token,
            json=body,
            headers={"X-Restli-Protocol-Version": "2.0.0"},
        )
        return out.get("id") or "linkedin_ok"


# --------------------------------------------------------------------------- #
# Facebook Pages — publish to the first managed Page
# --------------------------------------------------------------------------- #
class FacebookProvider(OAuthProvider):
    platform_id = "facebook"
    authorize_url = "https://www.facebook.com/v21.0/dialog/oauth"
    token_url = f"{_GRAPH}/oauth/access_token"
    scopes = ["pages_manage_posts", "pages_read_engagement", "pages_show_list", "public_profile"]
    scope_separator = ","

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        # Exchange for the first Page the user manages; publish with the Page token.
        data = (await self._get_json(f"{_GRAPH}/me/accounts", token=token.access_token)).get("data", [])
        if not data:
            raise OAuthError("No Facebook Page found for this account (need pages_show_list + a Page).")
        page = data[0]
        return AccountInfo(
            external_account_id=page.get("id"),
            handle=page.get("name"),
            display_name=page.get("name"),
            publish_token=page.get("access_token"),
        )

    async def publish_text(self, *, access_token, external_account_id=None, text, title=None) -> str:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{_GRAPH}/{external_account_id}/feed",
                data={"message": text, "access_token": access_token},
            )
        if resp.status_code >= 400:
            raise OAuthError(f"Facebook publish failed: {resp.text[:300]}")
        return resp.json().get("id", "facebook_ok")


# --------------------------------------------------------------------------- #
# Threads — Meta Threads API, two-step create + publish
# --------------------------------------------------------------------------- #
class ThreadsProvider(OAuthProvider):
    platform_id = "threads"
    authorize_url = "https://threads.net/oauth/authorize"
    token_url = "https://graph.threads.net/oauth/access_token"
    scopes = ["threads_basic", "threads_content_publish"]
    scope_separator = ","

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        me = await self._get_json(
            "https://graph.threads.net/v1.0/me", token=token.access_token, params={"fields": "id,username"}
        )
        return AccountInfo(
            external_account_id=me.get("id"),
            handle=f"@{me['username']}" if me.get("username") else None,
            display_name=me.get("username"),
        )

    async def publish_text(self, *, access_token, external_account_id=None, text, title=None) -> str:
        base = f"https://graph.threads.net/v1.0/{external_account_id}"
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            create = await client.post(
                f"{base}/threads",
                data={"media_type": "TEXT", "text": text, "access_token": access_token},
            )
            if create.status_code >= 400:
                raise OAuthError(f"Threads create failed: {create.text[:300]}")
            creation_id = create.json().get("id")
            pub = await client.post(
                f"{base}/threads_publish",
                data={"creation_id": creation_id, "access_token": access_token},
            )
        if pub.status_code >= 400:
            raise OAuthError(f"Threads publish failed: {pub.text[:300]}")
        return pub.json().get("id", "threads_ok")


# --------------------------------------------------------------------------- #
# Instagram — authenticates for real; text-only posts are not allowed by the API
# --------------------------------------------------------------------------- #
class InstagramProvider(OAuthProvider):
    platform_id = "instagram"
    authorize_url = "https://www.facebook.com/v21.0/dialog/oauth"
    token_url = f"{_GRAPH}/oauth/access_token"
    scopes = ["instagram_basic", "instagram_content_publish", "pages_show_list"]
    scope_separator = ","
    can_publish_text = False
    unsupported_reason = "Instagram requires an image or video; text-only posts can't be published."

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        pages = (await self._get_json(f"{_GRAPH}/me/accounts", token=token.access_token)).get("data", [])
        for page in pages:
            info = await self._get_json(
                f"{_GRAPH}/{page['id']}", token=token.access_token,
                params={"fields": "instagram_business_account{id,username}"},
            )
            iga = info.get("instagram_business_account")
            if iga:
                return AccountInfo(
                    external_account_id=iga.get("id"),
                    handle=f"@{iga['username']}" if iga.get("username") else None,
                    display_name=iga.get("username"),
                )
        raise OAuthError("No Instagram Business account linked to a Facebook Page was found.")


# --------------------------------------------------------------------------- #
# Google base (Blogger / YouTube) — offline access for refresh tokens
# --------------------------------------------------------------------------- #
class _GoogleProvider(OAuthProvider):
    authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    extra_authorize_params = {"access_type": "offline", "prompt": "consent"}


class BloggerProvider(_GoogleProvider):
    platform_id = "blogger"
    scopes = ["https://www.googleapis.com/auth/blogger"]

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        blogs = (
            await self._get_json("https://www.googleapis.com/blogger/v3/users/self/blogs", token=token.access_token)
        ).get("items", [])
        if not blogs:
            raise OAuthError("No Blogger blog found for this Google account.")
        blog = blogs[0]
        return AccountInfo(
            external_account_id=blog.get("id"), handle=blog.get("name"), display_name=blog.get("name")
        )

    async def publish_text(self, *, access_token, external_account_id=None, text, title=None) -> str:
        out = await self._post_json(
            f"https://www.googleapis.com/blogger/v3/blogs/{external_account_id}/posts",
            token=access_token,
            json={"title": title or "New post", "content": text},
        )
        return out.get("id", "blogger_ok")


class YouTubeProvider(_GoogleProvider):
    platform_id = "youtube"
    scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
    can_publish_text = False
    unsupported_reason = "YouTube publishing requires a video upload; text posts aren't supported."

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        data = await self._get_json(
            "https://www.googleapis.com/youtube/v3/channels", token=token.access_token,
            params={"part": "snippet", "mine": "true"},
        )
        items = data.get("items", [])
        if not items:
            return AccountInfo()
        ch = items[0]
        title = (ch.get("snippet") or {}).get("title")
        return AccountInfo(external_account_id=ch.get("id"), handle=title, display_name=title)


# --------------------------------------------------------------------------- #
# WordPress.com
# --------------------------------------------------------------------------- #
class WordPressProvider(OAuthProvider):
    platform_id = "wordpress"
    authorize_url = "https://public-api.wordpress.com/oauth2/authorize"
    token_url = "https://public-api.wordpress.com/oauth2/token"
    scopes = ["global"]

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        # The token response carries the selected blog id/url.
        blog_id = token.raw.get("blog_id")
        blog_url = token.raw.get("blog_url")
        return AccountInfo(
            external_account_id=str(blog_id) if blog_id else None,
            handle=blog_url,
            display_name=blog_url,
        )

    async def publish_text(self, *, access_token, external_account_id=None, text, title=None) -> str:
        out = await self._post_json(
            f"https://public-api.wordpress.com/rest/v1.1/sites/{external_account_id}/posts/new",
            token=access_token,
            json={"title": title or "New post", "content": text},
        )
        return str(out.get("ID") or "wordpress_ok")


# --------------------------------------------------------------------------- #
# TikTok — authenticates for real; posting requires a video
# --------------------------------------------------------------------------- #
class TikTokProvider(OAuthProvider):
    platform_id = "tiktok"
    authorize_url = "https://www.tiktok.com/v2/auth/authorize/"
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    scopes = ["user.info.basic", "video.publish"]
    scope_separator = ","
    can_publish_text = False
    unsupported_reason = "TikTok requires a video; text-only posts can't be published."

    # TikTok uses `client_key` instead of `client_id`.
    def authorize_url_for(self, state: str, code_challenge: str | None) -> str:
        params = {
            "client_key": self.client_id or "",
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scope_separator.join(self.scopes),
            "state": state,
        }
        return f"{self.authorize_url}?{urlencode(params)}"

    def _token_data(self, code: str, code_verifier: str | None) -> dict[str, str]:
        return {
            "client_key": self.client_id or "",
            "client_secret": self.client_secret or "",
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        data = (
            await self._get_json(
                "https://open.tiktokapis.com/v2/user/info/", token=token.access_token,
                params={"fields": "open_id,display_name"},
            )
        ).get("data", {}).get("user", {})
        return AccountInfo(
            external_account_id=data.get("open_id"),
            handle=data.get("display_name"),
            display_name=data.get("display_name"),
        )
