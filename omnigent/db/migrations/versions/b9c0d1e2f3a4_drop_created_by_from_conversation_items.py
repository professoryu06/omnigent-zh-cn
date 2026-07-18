"""drop created_by from conversation_items (revert per-message attribution)

Revision ID: b9c0d1e2f3a4
Revises: h1a2b3c4d5e6
Create Date: 2026-06-04 00:00:00.000000

Drops the ``created_by`` column from ``conversation_items``. The column
was added by ``e1c4a7b2f309`` as part of the per-message actor attribution
feature, which was subsequently reverted because the database is shared
with an existing managed repo where adding new columns is not feasible.

This migration sits at the head of the chain (after ``h1a2b3c4d5e6``) so
that it runs regardless of which revision a database is currently at.
Alembic walks down from the head to the DB's recorded revision, so a drop
inserted in the middle of the chain would be skipped by any database that
had already migrated past that point. Existing users who already applied
``e1c4a7b2f309`` get the column dropped; fresh installs have it added by
``e1c4a7b2f309`` and removed here, both via ``alembic upgrade head``.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b9c0d1e2f3a4"
down_revision: str | None = "h1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("conversation_items") as batch_op:
        batch_op.drop_column("created_by")


def downgrade() -> None:
    # Re-add the column so the chain stays symmetric: e1c4a7b2f309's
    # downgrade drops created_by, and it must exist for that to succeed.
    op.add_column(
        "conversation_items",
        sa.Column("created_by", sa.String(128), nullable=True),
    )
