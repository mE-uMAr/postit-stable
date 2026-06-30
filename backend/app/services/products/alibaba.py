"""Alibaba Open Platform client.

Ported from the BabaProds WordPress plugin: HMAC-SHA256 signed requests (the API
path is prepended to the sorted param string), automatic access-token refresh, and
``/eco/buyer/product/search`` + ``/eco/buyer/product/description`` endpoints.

Refreshed tokens are cached in-process (the refresh token from .env is long-lived);
they are not persisted, so a fresh access token is fetched again after a restart.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import time

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.schemas.product import ProductCard, ProductDetail
from app.services.products.base import ProductError, dedupe_keep_order, strip_html

_BASE_URL = "https://openapi-api.alibaba.com/rest"
_API_VERSION = "/2.0"
_REFRESH_PATH = "/auth/token/refresh"
_ID_PATTERNS = (
    re.compile(r"_(\d+)\.html"),
    re.compile(r"(\d{10,})\.html"),
    re.compile(r"productId=(\d+)"),
    re.compile(r"(\d{10,})"),
)

# In-process token cache, seeded lazily from .env, updated on refresh.
_token: dict[str, object] = {"loaded": False, "access_token": None, "expires_at": 0.0}


class AlibabaClient:
    source = "alibaba"
    name = "Alibaba"

    def __init__(self) -> None:
        self.app_key = settings.ALIBABA_APP_KEY or ""
        self.app_secret = settings.ALIBABA_APP_SECRET or ""
        self.refresh_token = settings.ALIBABA_REFRESH_TOKEN or ""

    @property
    def configured(self) -> bool:
        return settings.alibaba_configured

    # --- tokens ---------------------------------------------------------- #
    def _access_token(self) -> str:
        if not _token["loaded"]:
            _token["access_token"] = settings.ALIBABA_ACCESS_TOKEN
            _token["loaded"] = True
        return _token["access_token"] or ""

    # --- signing / transport --------------------------------------------- #
    def _sign(self, params: dict[str, object], api_path: str) -> str:
        items = sorted((k, v) for k, v in params.items() if k != "sign" and v not in (None, ""))
        string_to_sign = api_path + "".join(f"{k}{v}" for k, v in items)
        return (
            hmac.new(
                self.app_secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256
            )
            .hexdigest()
            .upper()
        )

    async def _request(self, endpoint: str, params: dict[str, object], *, versioned: bool = True) -> dict:
        api_path = (_API_VERSION + endpoint) if versioned else endpoint
        all_params: dict[str, object] = {
            "app_key": self.app_key,
            "sign_method": "sha256",
            "timestamp": int(time.time() * 1000),
            **params,
        }
        token = self._access_token()
        if token:
            all_params["access_token"] = token
        all_params["sign"] = self._sign(all_params, api_path)
        url = f"{_BASE_URL}{api_path}"
        try:
            async with httpx.AsyncClient(timeout=settings.PRODUCT_IMPORT_TIMEOUT) as client:
                resp = await client.get(
                    url, params=all_params, headers={"Content-Type": "application/json"}
                )
        except httpx.HTTPError as exc:
            raise ProductError(f"Couldn't reach Alibaba: {exc}") from exc
        if resp.status_code >= 400:
            raise ProductError(f"Alibaba API failed (HTTP {resp.status_code}).")
        return resp.json()

    async def _refresh(self) -> bool:
        if not self.refresh_token:
            return False
        params: dict[str, object] = {
            "refresh_token": self.refresh_token,
            "app_key": self.app_key,
            "sign_method": "sha256",
            "timestamp": int(time.time() * 1000),
        }
        params["sign"] = self._sign(params, _REFRESH_PATH)
        try:
            async with httpx.AsyncClient(timeout=settings.PRODUCT_IMPORT_TIMEOUT) as client:
                resp = await client.get(f"{_BASE_URL}{_REFRESH_PATH}", params=params)
            data = resp.json()
        except (httpx.HTTPError, ValueError):
            logger.warning("Alibaba token refresh request failed", exc_info=True)
            return False
        if data.get("access_token"):
            _token["access_token"] = data["access_token"]
            _token["loaded"] = True
            try:
                _token["expires_at"] = time.time() + int(data.get("expires_in", 0))
            except (TypeError, ValueError):
                _token["expires_at"] = 0.0
            return True
        logger.warning("Alibaba token refresh returned no access_token: %s", data)
        return False

    async def _call(self, endpoint: str, params: dict[str, object]) -> dict:
        if not self.configured:
            raise ProductError("Alibaba import isn't configured. Add API credentials in .env.")
        data = await self._request(endpoint, params)
        # On an auth failure, refresh the access token once and retry.
        if self._looks_like_auth_error(data):
            if await self._refresh():
                data = await self._request(endpoint, params)
        return data

    @staticmethod
    def _looks_like_auth_error(data: dict) -> bool:
        code = str(data.get("code") or data.get("error_code") or "")
        if code and code not in ("0", "200"):
            blob = json.dumps(data).lower()
            return "token" in blob or "auth" in blob or code.startswith("4")
        return False

    @staticmethod
    def _extract_id(url: str) -> str | None:
        for pat in _ID_PATTERNS:
            m = pat.search(url)
            if m:
                return m.group(1)
        return None

    def _affiliate_link(self, product_id: str) -> str:
        code = settings.ALIBABA_AFFILIATE_CODE
        if code:
            return f"https://offer.alibaba.com/cps/{code}?bm=cps&src=saf&productId={product_id}"
        return f"https://www.alibaba.com/product-detail/_{product_id}.html"

    # --- public API ------------------------------------------------------ #
    def _card(self, p: dict) -> ProductCard:
        pid = str(p.get("product_id") or "")
        image = (p.get("image") or {}).get("main_image") if isinstance(p.get("image"), dict) else None
        price = p.get("price")
        return ProductCard(
            source=self.source,
            product_id=pid,
            title=str(p.get("title") or f"Product #{pid}"),
            price=str(price) if price not in (None, "") else None,
            image=image,
            url=f"https://www.alibaba.com/product-detail/_{pid}.html",
        )

    async def search(self, keyword: str, page: int = 1, size: int = 20) -> tuple[list[ProductCard], bool]:
        param0 = json.dumps({"size": size, "index": page, "keyword": keyword})
        data = await self._call("/eco/buyer/product/search", {"param0": param0})
        result = (data.get("result") or {}).get("data") or {}
        products = result.get("products") or []
        if not products and "result" not in data:
            raise ProductError("Alibaba search returned an unexpected response.")
        cards = [self._card(p) for p in products]
        pagination = result.get("pagination") or {}
        has_more = bool(pagination.get("has_next")) or len(cards) >= size
        return cards, has_more

    async def detail(self, url: str) -> ProductDetail:
        pid = self._extract_id(url)
        if not pid:
            raise ProductError("Couldn't read the Alibaba product id from that link.")
        query_req = json.dumps({"product_id": int(pid), "country": settings.PRODUCT_SHIP_TO_COUNTRY})
        data = await self._call("/eco/buyer/product/description", {"query_req": query_req})
        product = (data.get("result") or {}).get("result_data")
        if not product:
            msg = (data.get("result") or {}).get("error_message") or "No details returned."
            raise ProductError(f"Alibaba: {msg}")

        images = dedupe_keep_order(product.get("images") or [])
        price = None
        skus = product.get("skus") or []
        if skus and isinstance(skus[0], dict):
            ladder = skus[0].get("ladder_price") or []
            if ladder:
                lo = ladder[0].get("price")
                hi = ladder[-1].get("price")
                price = f"{lo} - {hi}" if hi and hi != lo else str(lo)
        return ProductDetail(
            source=self.source,
            product_id=pid,
            title=str(product.get("title") or f"Product #{pid}"),
            description=strip_html(product.get("description")),
            price=price,
            images=images,
            video_url=product.get("video_url") or None,
            affiliate_link=product.get("affiliate_link") or self._affiliate_link(pid),
            url=url,
        )
