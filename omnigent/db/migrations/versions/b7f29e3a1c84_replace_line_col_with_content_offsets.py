"""Drop start_line and end_line from comments table.

Revision ID: b7f29e3a1c84
Revises: 2a4e0380be0c
Create Date: 2026-05-21

Removes the line-number fields (start_line, end_line) from the comments
table. The remaining start_index and end_index fields are reinterpreted
as absolute character offsets within the file content (0-based,
start inclusive, end exclusive), replacing the old meaning of
"column within a line".

Re-anchoring after file edits continues to rely on anchor_content.
Existing rows have their start_index/end_index reset to 0 by the
server_default; they will be re-anchored via anchor_content on the
next file load.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "b7f29e3a1c84"
down_revision: str | None = "2a4e0380be0c"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Drop start_line and end_line."""
    with op.batch_alter_table("comments") as batch_op:
        batch_op.drop_column("start_line")
        batch_op.drop_column("end_line")


def downgrade() -> None:
    """Restore start_line and end_line with a placeholder value of 1."""
    with op.batch_alter_table("comments") as batch_op:
        batch_op.add_column(
            sa.Column("start_line", sa.Integer(), nullable=False, server_default="1")
        )
        batch_op.add_column(
            sa.Column("end_line", sa.Integer(), nullable=False, server_default="1")
        )
