"""re-add created_by to conversation_items (restore per-message attribution)

Revision ID: i1a2b3c4d5e6
Revises: b9c0d1e2f3a4
Create Date: 2026-06-05 00:00:00.000000

Re-adds the ``created_by`` column to ``conversation_items``, restoring the
per-message actor attribution feature. The column was originally added by
``e1c4a7b2f309``, dropped by ``b9c0d1e2f3a4`` when the feature was reverted,
and is now reinstated.

This sits at the head of the chain (after ``b9c0d1e2f3a4``) as a new
forward step rather than by deleting ``b9c0d1e2f3a4``: databases that
already applied the drop must converge by re-adding the column, and a
deleted revision would orphan their recorded alembic version. Every path
ends with the column present:

- fresh install: ``e1c4a7b2f309`` adds, ``b9c0d1e2f3a4`` drops, this re-adds.
- DB that applied the drop: this re-adds.
- DB still at ``e1c4a7b2f309``: ``b9c0d1e2f3a4`` drops, this re-adds.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "i1a2b3c4d5e6"
down_revision: str | None = "b9c0d1e2f3a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "conversation_items",
        sa.Column("created_by", sa.String(128), nullable=True),
    )


def downgrade() -> None:
    with op.batch_alter_table("conversation_items") as batch_op:
        batch_op.drop_column("created_by")
