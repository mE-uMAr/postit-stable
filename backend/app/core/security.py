"""Password hashing (argon2), JWT issuance/verification, token encryption & hashing."""

from __future__ import annotations

import base64
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

_ph = PasswordHasher()

TokenType = Literal["access", "refresh"]


# --------------------------------------------------------------------------- #
# Passwords
# --------------------------------------------------------------------------- #
def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return _ph.verify(hashed, password)
    except (VerifyMismatchError, InvalidHashError, Exception):
        return False


def needs_rehash(hashed: str) -> bool:
    try:
        return _ph.check_needs_rehash(hashed)
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# JWT
# --------------------------------------------------------------------------- #
def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_token(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    extra: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Return (encoded_jwt, jti)."""
    jti = uuid.uuid4().hex
    now = _now()
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": jti,
    }
    if extra:
        payload.update(extra)
    encoded = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded, jti


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> tuple[str, str]:
    return create_token(
        subject, "access", timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES), extra
    )


def create_refresh_token(subject: str, extra: dict[str, Any] | None = None) -> tuple[str, str]:
    return create_token(
        subject, "refresh", timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS), extra
    )


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    """Decode & validate a JWT. Raises ``jwt.PyJWTError`` on failure."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    if expected_type and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"Expected {expected_type} token")
    return payload


def refresh_token_expiry() -> datetime:
    return _now() + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)


# --------------------------------------------------------------------------- #
# Opaque tokens / hashing (refresh-token storage, idempotency, invites)
# --------------------------------------------------------------------------- #
def generate_opaque_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# At-rest encryption for stored OAuth connection tokens
# --------------------------------------------------------------------------- #
def _fernet() -> Fernet:
    key = settings.TOKEN_ENCRYPTION_KEY
    if not key:
        # Derive a stable key from SECRET_KEY for dev so the app still runs.
        digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        key = base64.urlsafe_b64encode(digest).decode()
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_secret(plaintext: str | None) -> str | None:
    if plaintext is None:
        return None
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_secret(ciphertext: str | None) -> str | None:
    if not ciphertext:
        return None
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        return None
