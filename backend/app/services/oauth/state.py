"""Signed OAuth ``state`` + PKCE handling.

The callback hits the backend directly (no user session), so the workspace/user
that started the flow are carried in a short-lived signed ``state`` JWT. PKCE
verifiers are kept server-side in the KV store, keyed by the state nonce.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import time

import jwt

from app.core.config import settings
from app.core.redis import get_kv

STATE_TTL_SECONDS = 600  # 10 minutes to complete the consent flow
_STATE_TYPE = "oauth_state"


def make_pkce_pair() -> tuple[str, str]:
    """Return (code_verifier, code_challenge) for PKCE (S256)."""
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def sign_state(*, workspace_id: str, user_id: str, platform_id: str, nonce: str) -> str:
    now = int(time.time())
    payload = {
        "ws": workspace_id,
        "uid": user_id,
        "plat": platform_id,
        "nonce": nonce,
        "type": _STATE_TYPE,
        "iat": now,
        "exp": now + STATE_TTL_SECONDS,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_state(token: str) -> dict:
    """Decode + validate a state JWT. Raises ``jwt.PyJWTError`` on failure."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != _STATE_TYPE:
        raise jwt.InvalidTokenError("not an oauth state token")
    return payload


def _pkce_key(nonce: str) -> str:
    return f"oauth:pkce:{nonce}"


async def store_verifier(nonce: str, verifier: str) -> None:
    await get_kv().set(_pkce_key(nonce), verifier, STATE_TTL_SECONDS)


async def pop_verifier(nonce: str) -> str | None:
    kv = get_kv()
    key = _pkce_key(nonce)
    value = await kv.get(key)
    if value is not None:
        await kv.delete(key)
    return value
