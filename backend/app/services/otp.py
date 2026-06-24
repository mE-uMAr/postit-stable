"""Signup email-verification OTP codes, stored hashed in the KV with a TTL."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from app.core.config import settings
from app.core.redis import get_kv


def _norm(email: str) -> str:
    return email.lower().strip()


def _key(email: str) -> str:
    return f"otp:signup:{_norm(email)}"


def _attempts_key(email: str) -> str:
    return f"otp:signup:attempts:{_norm(email)}"


def _hash(code: str) -> str:
    return hashlib.sha256(f"{settings.SECRET_KEY}:{code}".encode()).hexdigest()


def generate_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(settings.OTP_LENGTH))


async def issue(email: str) -> str:
    """Generate a fresh OTP for the email and store its hash. Returns the code."""
    code = generate_code()
    kv = get_kv()
    await kv.set(_key(email), _hash(code), settings.OTP_TTL_SECONDS)
    await kv.delete(_attempts_key(email))
    return code


async def verify(email: str, code: str) -> bool:
    """Validate a code (constant-time), enforcing an attempt cap. Single-use."""
    kv = get_kv()
    stored = await kv.get(_key(email))
    if not stored:
        return False
    attempts = await kv.incr(_attempts_key(email), settings.OTP_TTL_SECONDS)
    if attempts > settings.OTP_MAX_ATTEMPTS:
        await kv.delete(_key(email))
        return False
    if hmac.compare_digest(stored, _hash(code)):
        await kv.delete(_key(email))
        await kv.delete(_attempts_key(email))
        return True
    return False
