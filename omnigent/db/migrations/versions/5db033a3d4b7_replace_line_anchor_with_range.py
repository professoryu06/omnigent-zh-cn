"""Replace line column with start_line/start_index/end_line/end_index range.

Revision ID: 5db033a3d4b7
Revises: d4e5f6a7b8c9
Create Date: 2026-05-18

Migrates the ``comments`` table from the old single-line anchor schema
(``line`` + ``anchor_content``) to a proper text-range schema
(``start_line``, ``start_index``, ``end_line``, ``end_index``).
``anchor_content`` is preserved for re-anchoring comments after file edits.

The four new columns are NOT NULL with default values that map each
pre-existing comment to a zero-width range at the start of its original
line (``start_index=0``, ``end_line=start_line``, ``end_index=0``).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "5db033a3d4b7"
down_revision: str | None = "d4e5f6a7b8c9"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Replace the line column with the four range columns; preserve anchor_content."""
    # Add the four new columns with defaults for existing rows.
    op.add_column(
        "comments",
        sa.Column("start_line", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "comments",
        sa.Column("start_index", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "comments",
        sa.Column("end_line", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "comments",
        sa.Column("end_index", sa.Integer(), nullable=False, server_default="0"),
    )
    # Copy the old line value into start_line and end_line for existing rows
    # so legacy comments point at the correct line rather than line 1.
    op.execute("UPDATE comments SET start_line = line, end_line = line")
    # Drop only the old line column; anchor_content is preserved.
    with op.batch_alter_table("comments") as batch_op:
        batch_op.drop_column("line")


def downgrade() -> None:
    """Restore the line column and remove the range columns."""
    op.add_column(
        "comments",
        sa.Column("line", sa.Integer(), nullable=False, server_default="1"),
    )
    # Restore line from start_line for any rows that survive the downgrade.
    op.execute("UPDATE comments SET line = start_line")
    with op.batch_alter_table("comments") as batch_op:
        batch_op.drop_column("end_index")
        batch_op.drop_column("end_line")
        batch_op.drop_column("start_index")
        batch_op.drop_column("start_line")
