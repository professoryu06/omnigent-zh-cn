"""backfill unbound runner affinity sentinel

Revision ID: e9f2a7c4d1b8
Revises: d7a6b3c91f48
Create Date: 2026-05-14 00:00:00.000000

PR 2 of the Alpha runner-state pivot makes dispatch read
``conversations.runner_id`` instead of lazily selecting an online
runner. Existing conversations with ``runner_id IS NULL`` cannot be
backfilled to a live runner after deployment, so they are marked with a
stable offline sentinel. Dispatch then follows the same single code
path as any offline runner binding and tells the user to resume.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e9f2a7c4d1b8"
down_revision: str | None = "d7a6b3c91f48"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OFFLINE_MIGRATED_RUNNER_ID = "__omnigent_migrated_offline_runner__"


def upgrade() -> None:
    """
    Mark pre-existing unbound conversations with an offline runner id.

    New conversations created after this migration still start with
    ``runner_id=NULL`` until ``PATCH /v1/sessions/{id}`` binds them.
    Only rows present at migration time are backfilled.
    """
    op.execute(
        sa.text(
            "UPDATE conversations SET runner_id = :runner_id WHERE runner_id IS NULL",
        ).bindparams(runner_id=OFFLINE_MIGRATED_RUNNER_ID),
    )


def downgrade() -> None:
    """Restore the nullable pre-PR2 representation."""
    op.execute(
        sa.text(
            "UPDATE conversations SET runner_id = NULL WHERE runner_id = :runner_id",
        ).bindparams(runner_id=OFFLINE_MIGRATED_RUNNER_ID),
    )
