"""add comments table

Revision ID: 93c04fcdff56
Revises: c9d3a1f2e4b5
Create Date: 2026-05-12 10:00:00.000000

Adds the ``comments`` table for persisting per-file review
comments associated with a conversation. Comments survive server
restarts and are cleaned up explicitly when the owning conversation
is deleted.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "93c04fcdff56"
down_revision: str | None = "a2c7e8f19b34"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("conversation_id", sa.String(length=64), nullable=False),
        sa.Column("path", sa.String(length=4096), nullable=False),
        sa.Column("line", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comments_conversation_id", "comments", ["conversation_id"], unique=False)
    op.create_index("ix_comments_created_at", "comments", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_comments_created_at", table_name="comments")
    op.drop_index("ix_comments_conversation_id", table_name="comments")
    op.drop_table("comments")
