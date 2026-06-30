"""AliExpress Affiliate Open Platform client.

Ported from the AliProds WordPress plugin: md5-signed requests to the SG gateway,
``aliexpress.affiliate.product.query`` for keyword search and
``aliexpress.affiliate.productdetail.get`` for a single product.
"""

from __future__ import annotations

import hashlib
import re
import time

import httpx

from app.core.config import settings
from app.schemas.product import ProductCard, ProductDetail
from app.services.products.base import ProductError, dedupe_keep_order
from app.services.products.describe import generate_description

_API_URL = "https://api-sg.aliexpress.com/sync"
_ID_PATTERNS = (
    re.compile(r"/item/(\d+)\.html"),
    re.compile(r"(\d{8,})\.html"),
    re.compile(r"productId=(\d+)"),
    re.compile(r"(\d{8,})"),
)


class AliExpressClient:
    source = "aliexpress"
    name = "AliExpress"

    def __init__(self) -> None:
        self.app_key = settings.ALIEXPRESS_APP_KEY or ""
        self.app_secret = settings.ALIEXPRESS_APP_SECRET or ""
        self.tracking_id = settings.ALIEXPRESS_TRACKING_ID or ""
        self.currency = settings.ALIEXPRESS_TARGET_CURRENCY
        self.language = settings.ALIEXPRESS_TARGET_LANGUAGE

    @property
    def configured(self) -> bool:
        return settings.aliexpress_configured

    # --- signing / transport --------------------------------------------- #
    def _sign(self, params: dict[str, object]) -> str:
        items = sorted((k, v) for k, v in params.items() if k != "sign" and v is not None)
        base = self.app_secret + "".join(f"{k}{v}" for k, v in items) + self.app_secret
        return hashlib.md5(base.encode("utf-8")).hexdigest().upper()

    async def _call(self, method: str, params: dict[str, object]) -> dict:
        if not self.configured:
            raise ProductError("AliExpress import isn't configured. Add API credentials in .env.")
        payload: dict[str, object] = {
            "method": method,
            "app_key": self.app_key,
            "sign_method": "md5",
            "timestamp": str(int(time.time() * 1000)),
            **{k: v for k, v in params.items() if v is not None},
        }
        payload["sign"] = self._sign(payload)
        try:
            async with httpx.AsyncClient(timeout=settings.PRODUCT_IMPORT_TIMEOUT) as client:
                resp = await client.post(
                    _API_URL, json=payload, headers={"Content-Type": "application/json"}
                )
        except httpx.HTTPError as exc:
            raise ProductError(f"Couldn't reach AliExpress: {exc}") from exc
        if resp.status_code != 200:
            raise ProductError(f"AliExpress API failed (HTTP {resp.status_code}).")
        data = resp.json()
        # Affiliate API reports auth/quota errors in an error_response envelope.
        if "error_response" in data:
            msg = data["error_response"].get("msg") or "AliExpress request was rejected."
            raise ProductError(f"AliExpress: {msg}")
        return data

    @staticmethod
    def _extract_id(url: str) -> str | None:
        for pat in _ID_PATTERNS:
            m = pat.search(url)
            if m:
                return m.group(1)
        return None

    # --- mapping --------------------------------------------------------- #
    def _card(self, p: dict) -> ProductCard:
        pid = str(p.get("product_id") or p.get("productId") or "")
        price = p.get("target_sale_price") or p.get("targetSalePrice")
        return ProductCard(
            source=self.source,
            product_id=pid,
            title=str(p.get("product_title") or p.get("productTitle") or f"Product #{pid}"),
            price=str(price) if price is not None else None,
            currency=p.get("target_sale_price_currency") or self.currency,
            image=p.get("product_main_image_url") or p.get("productMainImageUrl"),
            url=p.get("product_detail_url")
            or p.get("productDetailUrl")
            or f"https://www.aliexpress.com/item/{pid}.html",
        )

    # --- public API ------------------------------------------------------ #
    async def search(self, keyword: str, page: int = 1, size: int = 20) -> tuple[list[ProductCard], bool]:
        data = await self._call(
            "aliexpress.affiliate.product.query",
            {
                "keywords": keyword,
                "target_currency": self.currency,
                "target_language": self.language,
                "tracking_id": self.tracking_id,
                "page_no": page,
                "page_size": size,
            },
        )
        result = (
            data.get("aliexpress_affiliate_product_query_response", {})
            .get("resp_result", {})
            .get("result", {})
        ) or {}
        products = (result.get("products") or {}).get("product") or []
        cards = [self._card(p) for p in products]
        total_pages = int(result.get("total_page_no") or 1)
        return cards, page < total_pages

    async def detail(self, url: str) -> ProductDetail:
        pid = self._extract_id(url)
        if not pid:
            raise ProductError("Couldn't read the AliExpress product id from that link.")
        data = await self._call(
            "aliexpress.affiliate.productdetail.get",
            {
                "product_ids": pid,
                "target_currency": self.currency,
                "target_language": self.language,
                "tracking_id": self.tracking_id,
            },
        )
        try:
            product = (
                data["aliexpress_affiliate_productdetail_get_response"]["resp_result"]["result"][
                    "products"
                ]["product"][0]
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise ProductError("AliExpress returned no details for that product.") from exc

        images = dedupe_keep_order(
            [product.get("product_main_image_url")]
            + ((product.get("product_small_image_urls") or {}).get("string") or [])
        )
        title = str(product.get("product_title") or f"Product #{pid}")
        price = product.get("target_sale_price")
        description = await generate_description(title, source="AliExpress")
        return ProductDetail(
            source=self.source,
            product_id=pid,
            title=title,
            description=description,
            price=str(price) if price is not None else None,
            currency=product.get("target_sale_price_currency") or self.currency,
            images=images,
            video_url=product.get("product_video_url") or None,
            affiliate_link=product.get("promotion_link") or product.get("product_detail_url"),
            url=product.get("product_detail_url") or url,
        )
