"""Auth token payloads."""

from __future__ import annotations

from pydantic import BaseModel


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # access token TTL in seconds


class RefreshRequest(BaseModel):
    refresh_token: str
