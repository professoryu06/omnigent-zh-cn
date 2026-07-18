"""add configured_harnesses to hosts

Revision ID: l1a2b3c4d5e6
Revises: d7e8f9a0b1c2
Create Date: 2026-06-10 00:00:00.000000

Adds ``hosts.configured_harnesses`` — the JSON-encoded per-harness
readiness map a host reports in its ``host.hello`` frame (e.g.
``'{"claude-sdk": true, "codex": false}'``). NULL means the host has
never reported it (an older host build) and is treated as unknown,
never as "nothing configured". Surfaced via ``GET /v1/hosts`` so the
web agent picker can warn when an agent's harness is unconfigured on
the selected host.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "l1a2b3c4d5e6"
down_revision: str | None = "d7e8f9a0b1c2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the nullable ``configured_harnesses`` column to ``hosts``.

    Batch mode so the DDL runs on SQLite too, and so the project's
    migration-safety test (which requires every schema change to go
    through ``batch_alter_table``) passes.
    """
    with op.batch_alter_table("hosts") as batch_op:
        batch_op.add_column(sa.Column("configured_harnesses", sa.Text(), nullable=True))


def downgrade() -> None:
    """Drop the ``configured_harnesses`` column from ``hosts``.

    Batch mode so ``DROP COLUMN`` works on SQLite (rejected by the bare
    ``op`` proxy pre-3.35).
    """
    with op.batch_alter_table("hosts") as batch_op:
        batch_op.drop_column("configured_harnesses")
