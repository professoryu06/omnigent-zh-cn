"""make policies.session_id nullable and add created_by

Revision ID: h1a2b3c4d5e6
Revises: g1a2b3c4d5e6
Create Date: 2026-06-04 12:00:00.000000

Makes ``session_id`` nullable on the ``policies`` table so the same
table can store both session-scoped policies (``session_id`` set) and
server-wide default policies (``session_id IS NULL``). Also adds a
``created_by`` column for admin attribution on default policies.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "h1a2b3c4d5e6"
down_revision: str | None = "g1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Make session_id nullable and add created_by column."""
    with op.batch_alter_table("policies") as batch_op:
        # Make session_id nullable so default policies can have NULL.
        batch_op.alter_column(
            "session_id",
            existing_type=sa.String(64),
            nullable=True,
        )
        batch_op.add_column(
            sa.Column("created_by", sa.String(128), nullable=True),
        )


def downgrade() -> None:
    """Revert session_id to non-nullable and drop created_by."""
    # Delete any rows with NULL session_id before making it NOT NULL.
    op.execute("DELETE FROM policies WHERE session_id IS NULL")
    with op.batch_alter_table("policies") as batch_op:
        batch_op.drop_column("created_by")
        batch_op.alter_column(
            "session_id",
            existing_type=sa.String(64),
            nullable=False,
        )
