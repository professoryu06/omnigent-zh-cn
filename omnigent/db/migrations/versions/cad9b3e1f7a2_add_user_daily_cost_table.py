"""add user_daily_cost table

Revision ID: cad9b3e1f7a2
Revises: i1a2b3c4d5e6
Create Date: 2026-06-05 00:00:00.000000

Adds the ``user_daily_cost`` table: a per-user, per-UTC-day rollup of
LLM spend used by cost-aware policies to read a user's accumulated
daily cost in O(1). One row per ``(user_id, day_utc)``, incremented at
each turn boundary.

This is a brand-new table (not a column on the shared
``conversation_items`` table), so it does not affect deployments whose
database lacks it: the server only ever reads or writes it from
policy-gated code paths, which are inert when no policy is configured.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "cad9b3e1f7a2"
down_revision: str | None = "i1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the ``user_daily_cost`` table."""
    op.create_table(
        "user_daily_cost",
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("day_utc", sa.String(10), nullable=False),
        sa.Column("cost_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "day_utc"),
    )


def downgrade() -> None:
    """Drop the ``user_daily_cost`` table."""
    op.drop_table("user_daily_cost")
