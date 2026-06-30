"""Product-import endpoints (Alibaba / AliExpress) used by the composer.

Search/detail return a normalised product shape; the media proxy streams a remote
CDN image or video back through our origin so the browser can pull the bytes into
the post without CORS issues. The proxy is host-allowlisted to prevent SSRF.
"""

from __future__ import annotations

from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError_
from app.models.user import User
from app.schemas.product import ProductDetail, ProductSearchResult, ProductSource
from app.services import products as product_service
from app.services.products import ProductError

router = APIRouter(prefix="/products", tags=["products"])

_SOURCES = {"alibaba", "aliexpress"}
# CDN/host suffixes the media proxy is allowed to fetch from (SSRF guard).
_MEDIA_HOST_SUFFIXES = (
    ".alicdn.com",
    ".aliexpress.com",
    ".aliexpress-media.com",
    ".alibaba.com",
    ".alibabacdn.com",
    ".alibabausercontent.com",
    # Alibaba-group media/video CDNs (AliExpress product videos live here).
    ".taobao.com",
    ".tbcdn.cn",
    ".mmcdn.cn",
)
_MEDIA_MAX_BYTES = 60 * 1024 * 1024  # 60 MB ceiling for a single asset


def _require_source(source: str) -> str:
    if source not in _SOURCES:
        raise NotFoundError("Unknown product source.")
    return source


@router.get("/sources", response_model=list[ProductSource])
async def sources(_: User = Depends(get_current_active_user)) -> list[ProductSource]:
    return product_service.list_sources()


@router.get("/{source}/search", response_model=ProductSearchResult)
async def search(
    source: str,
    q: str = Query(min_length=1, max_length=200),
    page: int = Query(default=1, ge=1, le=100),
    size: int = Query(default=20, ge=1, le=50),
    _: User = Depends(get_current_active_user),
) -> ProductSearchResult:
    _require_source(source)
    try:
        return await product_service.search(source, q, page=page, size=size)
    except ProductError as exc:
        raise ValidationError_(str(exc), code="product_error") from exc


@router.get("/{source}/detail", response_model=ProductDetail)
async def detail(
    source: str,
    url: str = Query(min_length=4, max_length=2048),
    _: User = Depends(get_current_active_user),
) -> ProductDetail:
    _require_source(source)
    try:
        return await product_service.detail(source, url)
    except ProductError as exc:
        raise ValidationError_(str(exc), code="product_error") from exc


def _media_host_allowed(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return bool(host) and any(host == s.lstrip(".") or host.endswith(s) for s in _MEDIA_HOST_SUFFIXES)


@router.get("/media")
async def media(
    url: str = Query(min_length=8, max_length=2048),
    _: User = Depends(get_current_active_user),
) -> StreamingResponse:
    """Stream a product image/video from an allowlisted CDN back through our origin."""
    if not url.lower().startswith("https://") or not _media_host_allowed(url):
        raise ValidationError_("That media URL isn't allowed.", code="media_not_allowed")

    client = httpx.AsyncClient(timeout=settings.PRODUCT_IMPORT_TIMEOUT, follow_redirects=True)
    try:
        upstream = await client.send(client.build_request("GET", url), stream=True)
    except httpx.HTTPError as exc:
        await client.aclose()
        raise ValidationError_("Couldn't fetch that media.", code="media_fetch_failed") from exc
    if upstream.status_code >= 400:
        await upstream.aclose()
        await client.aclose()
        raise ValidationError_("Media not found at that URL.", code="media_fetch_failed")

    content_type = upstream.headers.get("content-type", "application/octet-stream")
    if not (content_type.startswith("image/") or content_type.startswith("video/")):
        await upstream.aclose()
        await client.aclose()
        raise ValidationError_("That URL isn't an image or video.", code="media_not_media")

    async def _stream():
        sent = 0
        try:
            async for chunk in upstream.aiter_bytes():
                sent += len(chunk)
                if sent > _MEDIA_MAX_BYTES:
                    break
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(_stream(), media_type=content_type)
