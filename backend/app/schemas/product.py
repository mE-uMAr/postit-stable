"""Schemas for the Alibaba / AliExpress product import feature.

These normalise the two very different affiliate-API payloads into a single shape
the compose UI can consume (title, price, images, optional video, affiliate link).
"""

from __future__ import annotations

from pydantic import BaseModel


class ProductSource(BaseModel):
    id: str            # "alibaba" | "aliexpress"
    name: str
    configured: bool


class ProductCard(BaseModel):
    """A lightweight search-result tile."""

    source: str
    product_id: str
    title: str
    price: str | None = None        # display string, native currency
    currency: str | None = None
    image: str | None = None
    url: str | None = None          # canonical product page (used to fetch detail)


class ProductSearchResult(BaseModel):
    items: list[ProductCard]
    page: int
    has_more: bool = False


class ProductDetail(BaseModel):
    """Everything needed to drop a product into a post."""

    source: str
    product_id: str
    title: str
    description: str = ""            # plain text, HTML stripped
    price: str | None = None
    currency: str | None = None
    images: list[str] = []
    video_url: str | None = None
    affiliate_link: str | None = None
    url: str | None = None
