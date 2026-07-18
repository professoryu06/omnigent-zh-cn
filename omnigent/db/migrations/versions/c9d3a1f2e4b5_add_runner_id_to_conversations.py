"""add runner_id column to conversations

Revision ID: c9d3a1f2e4b5
Revises: 8a4f1e9c2b07
Create Date: 2026-05-04 12:00:00.000000

Adds the ``conversations.runner_id`` column the runtime needs to
pin a conversation to a specific runner (designs/RUNNER.md §5).

Lives as its own migration (rather than amending the initial
schema) so existing databases get the column via a real upgrade
step instead of an in-place rewrite of the initial migration —
the latter is invisible to alembic because the alembic_version
table already says the DB is at HEAD, so the new column never
gets added.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9d3a1f2e4b5"
down_revision: str | None = "8a4f1e9c2b07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Add the ``runner_id`` column to ``conversations``.

    The column is nullable: existing rows have no runner pinning
    and will lazily acquire one on the next dispatch. No FK
    because runner records are not persisted in v1 — the registry
    is purely in-memory.
    """
    op.add_column(
        "conversations",
        sa.Column("runner_id", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    """Drop the ``runner_id`` column from ``conversations``."""
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("runner_id")
