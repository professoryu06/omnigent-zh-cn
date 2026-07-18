"""drop inbox_closed from tasks

Revision ID: a1b2c3d4e5f6
Revises: c1d2e3f4a5b6
Create Date: 2026-05-28

``inbox_closed`` was only read inside ``create_if_idle``, which was
never called from any production code path and has been removed.
This migration drops the now-dead column from existing databases.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "e3b1f2a4c9d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_column("inbox_closed")


def downgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column(
            "inbox_closed",
            sa.Boolean(),
            nullable=False,
            server_default="0",
        ),
    )
