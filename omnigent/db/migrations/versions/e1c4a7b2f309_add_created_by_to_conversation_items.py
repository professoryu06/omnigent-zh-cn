"""Add created_by column to conversation_items table.

Revision ID: e1c4a7b2f309
Revises: caf81af91d9e
Create Date: 2026-06-01

Records which human actor authored each conversation item, enabling
per-message attribution in shared sessions. Nullable because
pre-existing items have no author data, agent/tool/system items are not
human-authored, and single-user mode does not track user identity.
Mirrors the comments ``created_by`` column.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "e1c4a7b2f309"
down_revision: str | None = "caf81af91d9e"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Add created_by column to conversation_items table."""
    op.add_column(
        "conversation_items",
        sa.Column("created_by", sa.String(128), nullable=True),
    )


def downgrade() -> None:
    """Remove created_by column from conversation_items table."""
    with op.batch_alter_table("conversation_items") as batch_op:
        batch_op.drop_column("created_by")
