"""add policies table

Revision ID: 8a4f1e9c2b07
Revises: 43fb65b29464
Create Date: 2026-05-01 12:00:00.000000

Adds the ``policies`` table for runtime-authored and
spec-baked PromptPolicy entries
(designs/LIVE_POLICIES.md §4.2).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a4f1e9c2b07"
down_revision: str | None = "43fb65b29464"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "policies",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("actions", sa.Text(), nullable=False),
        sa.Column("phases", sa.Text(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("agent_id", "name", name="uq_policies_agent_id_name"),
    )
    op.create_index("ix_policies_created_at", "policies", ["created_at"], unique=False)
    op.create_index("ix_policies_agent_id", "policies", ["agent_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_policies_agent_id", table_name="policies")
    op.drop_index("ix_policies_created_at", table_name="policies")
    op.drop_table("policies")
