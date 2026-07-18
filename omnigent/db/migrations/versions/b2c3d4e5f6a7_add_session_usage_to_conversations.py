"""add session_usage to conversations

Revision ID: b2c3d4e5f6a7
Revises: a7f3c2d18e94
Create Date: 2026-06-02 00:00:01.000000

Adds per-conversation session_usage column for persisting
cumulative LLM token usage across turns. Stored as a JSON
string in a Text column for SQLite compatibility.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a7f3c2d18e94"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.add_column(
            sa.Column("session_usage", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("session_usage")
