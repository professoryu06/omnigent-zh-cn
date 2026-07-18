"""add terminal_launch_args to conversations

Revision ID: a7f3c2d18e94
Revises: f2a3b4c5d6e7
Create Date: 2026-06-01 00:00:00.000000

Adds per-session native-terminal launch args to the conversations
table:

- ``terminal_launch_args``: nullable Text — JSON-encoded list of
  pass-through CLI args for a native terminal wrapper (claude / codex),
  e.g. ``'["--dangerously-skip-permissions"]'``. NULL means no args
  (non-native sessions, or a native session launched with none). The
  runner reconstructs the terminal launch command from these plus the
  harness binary; the command and all bridge / Omnigent / auth wiring stay
  runner-owned and are never stored here.

Set via ``POST /v1/sessions`` metadata at create-time (so the runner
has them before it boots) and updated via ``PATCH /v1/sessions/{id}``
on resume (last-write-wins). See
designs/NATIVE_RUNNER_SERVER_LAUNCH.md.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a7f3c2d18e94"
down_revision: str | None = "f2a3b4c5d6e7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.add_column(
            sa.Column("terminal_launch_args", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("terminal_launch_args")
