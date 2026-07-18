"""add sub_agent_name column to conversations

Revision ID: f1a2b3c4d5e6
Revises: d4e5f6a7b8c9
Create Date: 2026-05-21 00:00:00.000000

Adds ``conversations.sub_agent_name`` so the runner can resolve
the correct sub-agent spec from the parent's spec tree when
starting a child turn. Replaces ``task.agent_name`` from the
removed task store (RUNNER_SUBAGENT_DISPATCH.md).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: str | None = "b7f29e3a1c84"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Add the ``sub_agent_name`` column to ``conversations``.

    Nullable: top-level sessions have no sub-agent name. Only
    child sessions created by ``sys_session_send`` set this.
    """
    op.add_column(
        "conversations",
        sa.Column("sub_agent_name", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    """Drop the ``sub_agent_name`` column from ``conversations``."""
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("sub_agent_name")
