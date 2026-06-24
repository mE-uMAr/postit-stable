"""Concrete OAuth providers + publishers, one class per platform.

Media is streamed to the platform at publish time and never stored. Platforms
that accept a binary upload (X, LinkedIn, Facebook, YouTube, TikTok, WordPress)
get the bytes directly; Instagram/Threads require a hosted media URL, which this
direct-upload mode doesn't provide, so they publish text only and refuse media
with a clear message.
"""

from __future__ import annotations

from urllib.parse import urlencode

import httpx

from app.services.oauth.base import (
    AccountInfo,
    MediaRef,
    OAuthError,
    OAuthProvider,
    TokenResult,
)

_TIMEOUT = 120.0
_GRAPH = "https://graph.facebook.com/v21.0"


def _first(media: list[MediaRef] | None, kind: str | None = None) -> MediaRef | None:
    for m in media or []:
        if kind is None or m.kind == kind:
            return m
    return None


# --------------------------------------------------------------------------- #
# X (Twitter) — OAuth2 + PKCE; binary media upload
# --------------------------------------------------------------------------- #
class XProvider(OAuthProvider):
    platform_id = "x"
    authorize_url = "https://twitter.com/i/oauth2/authorize"
    token_url = "https://api.twitter.com/2/oauth2/token"
    scopes = ["tweet.read", "tweet.write", "users.read", "media.write", "offline.access"]
    use_pkce = True
    token_auth_basic = True

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        data = (await self._get_json("https://api.twitter.com/2/users/me", token=token.access_token)).get("data", {})
        return AccountInfo(
            external_account_id=data.get("id"),
            handle=f"@{data['username']}" if data.get("username") else None,
            display_name=data.get("name"),
        )

    async def _upload_media(self, access_token: str, m: MediaRef) -> str:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                "https://upload.twitter.com/1.1/media/upload.json",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"media": (m.filename, m.data, m.content_type)},
            )
        if resp.status_code >= 400:
            raise OAuthError(f"X media upload failed: {resp.text[:300]}")
        return resp.json()["media_id_string"]

    async def publish(self, *, access_token, external_account_id=None, text, title=None, media=None) -> str:
        body: dict = {"text": text}
        if media:
            body["media"] = {"media_ids": [await self._upload_media(access_token, m) for m in media]}
        out = await self._post_json("https://api.twitter.com/2/tweets", token=access_token, json=body)
        tweet_id = (out.get("data") or {}).get("id")
        if not tweet_id:
            raise OAuthError(f"X publish returned no id: {out}")
        return tweet_id


# --------------------------------------------------------------------------- #
# LinkedIn — member share (text + optional binary image)
# --------------------------------------------------------------------------- #
class LinkedInProvider(OAuthProvider):
    platform_id = "linkedin"
    authorize_url = "https://www.linkedin.com/oauth/v2/authorization"
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    scopes = ["openid", "profile", "w_member_social"]

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        me = await self._get_json("https://api.linkedin.com/v2/userinfo", token=token.access_token)
        return AccountInfo(external_account_id=me.get("sub"), handle=me.get("name"), display_name=me.get("name"))

    async def _register_image(self, access_token: str, owner: str, m: MediaRef) -> str:
        reg = await self._post_json(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            token=access_token,
            json={
                "registerUploadRequest": {
                    "owner": owner,
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "serviceRelationships": [
                        {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
                    ],
                }
            },
        )
        value = reg["value"]
        asset = value["asset"]
        upload_url = value["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            up = await client.put(
                upload_url, content=m.data, headers={"Authorization": f"Bearer {access_token}"}
            )
        if up.status_code >= 400:
            raise OAuthError(f"LinkedIn image upload failed: {up.text[:200]}")
        return asset

    async def publish(self, *, access_token, external_account_id=None, text, title=None, media=None) -> str:
        if not external_account_id:
            raise OAuthError("LinkedIn connection missing member id; reconnect the account.")
        owner = f"urn:li:person:{external_account_id}"
        share: dict = {"shareCommentary": {"text": text}, "shareMediaCategory": "NONE"}
        img = _first(media, "image")
        if img:
            asset = await self._register_image(access_token, owner, img)
            share["shareMediaCategory"] = "IMAGE"
            share["media"] = [{"status": "READY", "media": asset}]
        body = {
            "author": owner,
            "lifecycleState": "PUBLISHED",
            "specificContent": {"com.linkedin.ugc.ShareContent": share},
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
# Facebook Pages — binary photo/video upload
# --------------------------------------------------------------------------- #
class FacebookProvider(OAuthProvider):
    platform_id = "facebook"
    authorize_url = "https://www.facebook.com/v21.0/dialog/oauth"
    token_url = f"{_GRAPH}/oauth/access_token"
    scopes = ["pages_manage_posts", "pages_read_engagement", "pages_show_list", "public_profile"]
    scope_separator = ","

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        data = (await self._get_json(f"{_GRAPH}/me/accounts", token=token.access_token)).get("data", [])
        if not data:
            raise OAuthError("No Facebook Page found (need pages_show_list + a Page).")
        page = data[0]
        return AccountInfo(
            external_account_id=page.get("id"),
            handle=page.get("name"),
            display_name=page.get("name"),
            publish_token=page.get("access_token"),
        )

    async def publish(self, *, access_token, external_account_id=None, text, title=None, media=None) -> str:
        img = _first(media, "image")
        vid = _first(media, "video")
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            if vid:
                resp = await client.post(
                    f"{_GRAPH}/{external_account_id}/videos",
                    data={"description": text, "access_token": access_token},
                    files={"source": (vid.filename, vid.data, vid.content_type)},
                )
            elif img:
                resp = await client.post(
                    f"{_GRAPH}/{external_account_id}/photos",
                    data={"message": text, "access_token": access_token},
                    files={"source": (img.filename, img.data, img.content_type)},
                )
            else:
                resp = await client.post(
                    f"{_GRAPH}/{external_account_id}/feed",
                    data={"message": text, "access_token": access_token},
                )
        if resp.status_code >= 400:
            raise OAuthError(f"Facebook publish failed: {resp.text[:300]}")
        out = resp.json()
        return out.get("id") or out.get("post_id") or "facebook_ok"


# --------------------------------------------------------------------------- #
# Threads — text only here (media needs a hosted URL, unavailable in direct mode)
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

    async def publish(self, *, access_token, external_account_id=None, text, title=None, media=None) -> str:
        if media:
            raise OAuthError("Threads media needs a hosted URL — not supported in direct-upload mode.")
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
# Instagram — requires hosted media URL (unavailable here)
# --------------------------------------------------------------------------- #
class InstagramProvider(OAuthProvider):
    platform_id = "instagram"
    authorize_url = "https://www.facebook.com/v21.0/dialog/oauth"
    token_url = f"{_GRAPH}/oauth/access_token"
    scopes = ["instagram_basic", "instagram_content_publish", "pages_show_list"]
    scope_separator = ","
    can_publish_text = False
    unsupported_reason = (
        "Instagram needs hosted media (its API fetches by URL), which direct-upload mode doesn't provide."
    )


# --------------------------------------------------------------------------- #
# Google base (Blogger / YouTube)
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
        return AccountInfo(external_account_id=blog.get("id"), handle=blog.get("name"), display_name=blog.get("name"))

    async def publish(self, *, access_token, external_account_id=None, text, title=None, media=None) -> str:
        # Blogger has no media-upload API; post text only.
        out = await self._post_json(
            f"https://www.googleapis.com/blogger/v3/blogs/{external_account_id}/posts",
            token=access_token,
            json={"title": title or "New post", "content": text},
        )
        return out.get("id", "blogger_ok")


class YouTubeProvider(_GoogleProvider):
    platform_id = "youtube"
    scopes = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly",
    ]
    can_publish_text = False
    unsupported_reason = "YouTube needs a video — add a video to the post."

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        data = await self._get_json(
            "https://www.googleapis.com/youtube/v3/channels", token=token.access_token,
            params={"part": "snippet", "mine": "true"},
        )
        items = data.get("items", [])
        if not items:
            return AccountInfo()
        title = (items[0].get("snippet") or {}).get("title")
        return AccountInfo(external_account_id=items[0].get("id"), handle=title, display_name=title)

    async def publish(self, *, access_token, external_account_id=None, text, title=None, media=None) -> str:
        vid = _first(media, "video")
        if not vid:
            raise OAuthError(self.unsupported_reason)
        metadata = {
            "snippet": {"title": (title or text or "Untitled")[:100], "description": text},
            "status": {"privacyStatus": "public"},
        }
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            init = await client.post(
                "https://www.googleapis.com/upload/youtube/v3/videos",
                params={"uploadType": "resumable", "part": "snippet,status"},
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Upload-Content-Type": vid.content_type,
                },
                json=metadata,
            )
            if init.status_code >= 400:
                raise OAuthError(f"YouTube init failed: {init.text[:300]}")
            upload_url = init.headers.get("location")
            if not upload_url:
                raise OAuthError("YouTube init returned no upload URL.")
            up = await client.put(upload_url, content=vid.data, headers={"Content-Type": vid.content_type})
        if up.status_code >= 400:
            raise OAuthError(f"YouTube upload failed: {up.text[:300]}")
        return up.json().get("id", "youtube_ok")


# --------------------------------------------------------------------------- #
# WordPress.com — binary media upload then embed
# --------------------------------------------------------------------------- #
class WordPressProvider(OAuthProvider):
    platform_id = "wordpress"
    authorize_url = "https://public-api.wordpress.com/oauth2/authorize"
    token_url = "https://public-api.wordpress.com/oauth2/token"
    scopes = ["global"]

    async def fetch_account(self, token: TokenResult) -> AccountInfo:
        blog_id = token.raw.get("blog_id")
        blog_url = token.raw.get("blog_url")
        return AccountInfo(
            external_account_id=str(blog_id) if blog_id else None, handle=blog_url, display_name=blog_url
        )

    async def publish(self, *, access_token, external_account_id=None, text, title=None, media=None) -> str:
        content = text
        site = external_account_id
        for m in media or []:
            if m.kind != "image":
                continue
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                up = await client.post(
                    f"https://public-api.wordpress.com/rest/v1.1/sites/{site}/media/new",
                    headers={"Authorization": f"Bearer {access_token}"},
                    files={"media[]": (m.filename, m.data, m.content_type)},
                )
            if up.status_code < 400:
                urls = [x.get("URL") for x in up.json().get("media", []) if x.get("URL")]
                for u in urls:
                    content += f'<p><img src="{u}" /></p>'
        out = await self._post_json(
            f"https://public-api.wordpress.com/rest/v1.1/sites/{site}/posts/new",
            token=access_token,
            json={"title": title or "New post", "content": content},
        )
        return str(out.get("ID") or "wordpress_ok")


# --------------------------------------------------------------------------- #
# TikTok — video only, binary FILE_UPLOAD
# --------------------------------------------------------------------------- #
class TikTokProvider(OAuthProvider):
    platform_id = "tiktok"
    authorize_url = "https://www.tiktok.com/v2/auth/authorize/"
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    scopes = ["user.info.basic", "video.publish"]
    scope_separator = ","
    can_publish_text = False
    unsupported_reason = "TikTok needs a video — add a video to the post."

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

    async def publish(self, *, access_token, external_account_id=None, text, title=None, media=None) -> str:
        vid = _first(media, "video")
        if not vid:
            raise OAuthError(self.unsupported_reason)
        size = len(vid.data)
        init = await self._post_json(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            token=access_token,
            json={
                "post_info": {"title": text[:150], "privacy_level": "SELF_ONLY"},
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": size,
                    "chunk_size": size,
                    "total_chunk_count": 1,
                },
            },
        )
        data = init.get("data") or {}
        upload_url = data.get("upload_url")
        if not upload_url:
            raise OAuthError(f"TikTok init returned no upload URL: {init}")
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            up = await client.put(
                upload_url,
                content=vid.data,
                headers={
                    "Content-Type": vid.content_type,
                    "Content-Range": f"bytes 0-{size - 1}/{size}",
                },
            )
        if up.status_code >= 400:
            raise OAuthError(f"TikTok upload failed: {up.text[:300]}")
        return data.get("publish_id", "tiktok_ok")
