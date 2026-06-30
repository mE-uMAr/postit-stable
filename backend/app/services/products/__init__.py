"""Product-import service: dispatches to the Alibaba / AliExpress clients."""

from __future__ import annotations

from app.schemas.product import ProductDetail, ProductSearchResult, ProductSource
from app.services.products.alibaba import AlibabaClient
from app.services.products.aliexpress import AliExpressClient
from app.services.products.base import ProductError

_CLIENTS = {
    "alibaba": AlibabaClient,
    "aliexpress": AliExpressClient,
}


def _client(source: str):
    cls = _CLIENTS.get(source)
    if cls is None:
        raise ProductError(f"Unknown product source '{source}'.")
    return cls()


def list_sources() -> list[ProductSource]:
    out: list[ProductSource] = []
    for source, cls in _CLIENTS.items():
        c = cls()
        out.append(ProductSource(id=source, name=c.name, configured=c.configured))
    return out


async def search(source: str, keyword: str, page: int = 1, size: int = 20) -> ProductSearchResult:
    items, has_more = await _client(source).search(keyword, page=page, size=size)
    return ProductSearchResult(items=items, page=page, has_more=has_more)


async def detail(source: str, url: str) -> ProductDetail:
    return await _client(source).detail(url)


__all__ = ["ProductError", "list_sources", "search", "detail"]
