"""Shared schema base + simple response envelopes."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base for read schemas mapped from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class Message(BaseModel):
    message: str


class IdResponse(BaseModel):
    id: str
