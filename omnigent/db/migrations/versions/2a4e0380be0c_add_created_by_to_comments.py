"""Add created_by column to comments table.

Revision ID: 2a4e0380be0c
Revises: 5db033a3d4b7
Create Date: 2026-05-21

Records which user created each comment. Nullable because pre-existing
comments do not have author data, and single-user mode does not track
user identity.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "2a4e0380be0c"
down_revision: str | None = "5db033a3d4b7"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Add created_by column to comments table."""
    op.add_column(
        "comments",
        sa.Column("created_by", sa.String(128), nullable=True),
    )


def downgrade() -> None:
    """Remove created_by column from comments table."""
    with op.batch_alter_table("comments") as batch_op:
        batch_op.drop_column("created_by")
