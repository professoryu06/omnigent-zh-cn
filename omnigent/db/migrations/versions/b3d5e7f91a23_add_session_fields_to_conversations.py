"""add reasoning_effort to conversations

Revision ID: b3d5e7f91a23
Revises: 93c04fcdff56
Create Date: 2026-05-13 00:00:00.000000

Adds per-session reasoning effort to the conversations table:

- ``reasoning_effort``: nullable String(32) — per-session reasoning
  effort hint (e.g. "high"). NULL means use the agent default.

Set via ``PATCH /v1/sessions/{id}`` and read by the workflow
at turn start.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b3d5e7f91a23"
down_revision: str | None = "b5e8d2f1a7c3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.add_column(
            sa.Column("reasoning_effort", sa.String(length=32), nullable=True),
        )


def downgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("reasoning_effort")
