"""initial baseline schema

Creates the full schema from ``Base.metadata`` so the same definition is applied
identically on MySQL and SQLite (avoids autogenerate rendering of custom column types).

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-04
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from app.models import Base

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
