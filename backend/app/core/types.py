"""Portable SQLAlchemy column types so the same models run on MySQL and SQLite.

- ``GUID``  : stores UUIDs as CHAR(36) everywhere, returns ``uuid.UUID`` objects.
- ``JSONType``: SQLAlchemy's generic JSON (native JSON on MySQL 5.7+/SQLite TEXT).
"""

from __future__ import annotations

import uuid

from sqlalchemy import JSON
from sqlalchemy.types import CHAR, TypeDecorator

# Generic JSON adapts to the dialect automatically.
JSONType = JSON


class GUID(TypeDecorator):
    """Platform-independent UUID stored as CHAR(36)."""

    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):  # noqa: ANN001
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):  # noqa: ANN001
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()
