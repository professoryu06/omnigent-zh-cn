"""add ask_approved_usd to user_daily_cost

Revision ID: d4f1a9c2b8e3
Revises: cad9b3e1f7a2
Create Date: 2026-06-06 00:00:00.000000

Adds the ``ask_approved_usd`` column to ``user_daily_cost``: the highest
soft warning checkpoint (USD) a user has approved continuing past for
that UTC day. The per-user daily cost-budget policy reads it (so an
approved checkpoint prompts at most once per day across all the user's
sessions) and writes it on approve.

Like the table itself, this column is only ever read/written from
policy-gated code paths, so it's inert in deployments with no policies
configured. ``server_default="0"`` backfills existing rows.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4f1a9c2b8e3"
down_revision: str | None = "cad9b3e1f7a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the ``ask_approved_usd`` column."""
    with op.batch_alter_table("user_daily_cost") as batch_op:
        batch_op.add_column(
            sa.Column("ask_approved_usd", sa.Float(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    """Drop the ``ask_approved_usd`` column."""
    with op.batch_alter_table("user_daily_cost") as batch_op:
        batch_op.drop_column("ask_approved_usd")
