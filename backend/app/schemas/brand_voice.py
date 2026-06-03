"""Brand voice schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class BrandVoiceRead(ORMModel):
    tone: str
    guidelines: str | None = None
    words_to_avoid: list


class BrandVoiceUpdate(BaseModel):
    tone: str | None = Field(default=None, max_length=40)
    guidelines: str | None = None
    words_to_avoid: list[str] | None = None
