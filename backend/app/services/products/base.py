"""Shared helpers for the product-import providers (Alibaba / AliExpress)."""

from __future__ import annotations

import re
from html import unescape

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t]*\n[ \t]*")
_MULTI_NL_RE = re.compile(r"\n{3,}")


class ProductError(Exception):
    """Raised when a product API call fails; the message is user-safe."""


def fix_image_url(url: str | None) -> str | None:
    """Normalise CDN URLs: add scheme to protocol-relative ones, force https."""
    if not url:
        return None
    url = url.strip()
    if url.startswith("//"):
        url = "https:" + url
    if url.startswith("http://"):
        url = "https://" + url[len("http://") :]
    if not url.startswith("https://"):
        return None
    return url


def strip_html(text: str | None) -> str:
    """Turn an HTML product description into clean, paragraphed plain text."""
    if not text:
        return ""
    text = unescape(text)
    # Treat block-level breaks as newlines before dropping the rest of the tags.
    text = re.sub(r"(?i)<\s*(br|/p|/div|/li|/h[1-6])\s*/?>", "\n", text)
    text = re.sub(r"(?i)<\s*li[^>]*>", "• ", text)
    text = _TAG_RE.sub("", text)
    text = _WS_RE.sub("\n", text)
    text = _MULTI_NL_RE.sub("\n\n", text)
    return text.strip()


def dedupe_keep_order(urls: list[str | None]) -> list[str]:
    """Drop blanks/dupes while preserving order (first image stays first)."""
    seen: set[str] = set()
    out: list[str] = []
    for raw in urls:
        u = fix_image_url(raw)
        if u and u not in seen:
            seen.add(u)
            out.append(u)
    return out
