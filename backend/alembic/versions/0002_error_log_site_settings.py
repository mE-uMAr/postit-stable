"""error_logs + site_settings tables

Adds the persisted error log (Workstream D) and the site-content control-plane
(Workstream E). Idempotent: uses ``checkfirst`` so it is a no-op on fresh
databases where the baseline already created everything from current metadata.

Revision ID: 0002_error_site
Revises: 0001_initial
Create Date: 2026-06-04
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from app.models import Base

revision: str = "0002_error_site"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = ("error_logs", "site_settings")


def upgrade() -> None:
    bind = op.get_bind()
    for name in _TABLES:
        Base.metadata.tables[name].create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for name in reversed(_TABLES):
        Base.metadata.tables[name].drop(bind=bind, checkfirst=True)
