"""add model_override to conversations

Revision ID: c1d2e3f4a5b6
Revises: f8e1a23d6c47
Create Date: 2026-05-27 00:00:00.000000

Adds per-session LLM model override to the conversations table:

- ``model_override``: nullable String(128) — per-session LLM model
  override (e.g. ``"claude-opus-4-7"``). NULL means use the agent
  default from the spec.

Set via ``PATCH /v1/sessions/{id}`` (parallel to ``reasoning_effort``)
and read by the workflow at turn start.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: str | None = "f8e1a23d6c47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.add_column(
            sa.Column("model_override", sa.String(length=128), nullable=True),
        )


def downgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("model_override")
