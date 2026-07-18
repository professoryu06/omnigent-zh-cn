"""add session_state to conversations

Revision ID: f2a3b4c5d6e7
Revises: e1c4a7b2f309
Create Date: 2026-06-02 00:00:00.000000

Adds per-conversation session_state column for persisting
policy engine session state across turns. Stored as a JSON
string in a Text column for SQLite compatibility.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f2a3b4c5d6e7"
down_revision: str | None = "e1c4a7b2f309"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.add_column(
            sa.Column("session_state", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("session_state")
