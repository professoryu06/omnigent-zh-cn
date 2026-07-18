"""add cost_control_mode_override to conversations

Revision ID: d7e8f9a0b1c2
Revises: k1a2b3c4d5e6
Create Date: 2026-06-10 00:00:00.000000

Adds the per-session cost-control switch to the conversations table:

- ``cost_control_mode_override``: nullable String(8) — ``"on"``
  activates the spec's configured cost-control mode, ``"off"``
  disables cost control for the session, NULL defers to the spec
  default.

Set via ``POST /v1/sessions`` / ``PATCH /v1/sessions/{id}`` (parallel
to ``model_override``) and read by the cost-control advisor pipeline
at turn start.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d7e8f9a0b1c2"
down_revision: str | None = "k1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.add_column(
            sa.Column("cost_control_mode_override", sa.String(length=8), nullable=True),
        )


def downgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("cost_control_mode_override")
