"""Add anchor_content column to comments table.

Revision ID: c7f2a1d83e49
Revises: b3d5e7f91a23
Create Date: 2026-05-15

Stores the text content of the anchored line at comment creation time.
The frontend uses this to remap comments to their correct line when
the file is subsequently edited (diff-based line remapping). Nullable
because pre-existing comments do not have anchor data.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "c7f2a1d83e49"
down_revision: str | None = "b3d5e7f91a23"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Add anchor_content column to comments table."""
    op.add_column(
        "comments",
        sa.Column("anchor_content", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Remove anchor_content column from comments table."""
    with op.batch_alter_table("comments") as batch_op:
        batch_op.drop_column("anchor_content")
