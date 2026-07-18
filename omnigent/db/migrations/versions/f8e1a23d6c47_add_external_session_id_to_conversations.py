"""add external_session_id column to conversations

Revision ID: f8e1a23d6c47
Revises: f1a2b3c4d5e6
Create Date: 2026-05-22 12:00:00.000000

Adds the ``conversations.external_session_id`` column so the server
can persist the runtime-native session id (e.g. Claude Code's
session uuid, future Codex / Pi session ids) that a conversation
wraps. Captured by the wrapper bridge from the underlying runtime
and PATCHed onto the conversation. Generic across runtimes — each
conversation wraps at most one external runtime session.

Lives as its own migration (rather than amending an earlier one)
so existing databases get the column via a real upgrade step
instead of an in-place rewrite of an already-applied migration —
the latter is invisible to alembic because the alembic_version
table already says the DB is at HEAD, so the new column never
gets added.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8e1a23d6c47"
down_revision: str | None = "f1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Add the ``external_session_id`` column to ``conversations``.

    The column is nullable: existing rows pre-date the column and
    conversations that are not backed by an external runtime
    (regular AP-only sessions) never set it. No FK because the id
    is generated externally (by Claude Code, Codex, Pi, etc.) and
    is not tracked in any AP-side table.
    """
    op.add_column(
        "conversations",
        sa.Column("external_session_id", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    """Drop the ``external_session_id`` column from ``conversations``."""
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("external_session_id")
