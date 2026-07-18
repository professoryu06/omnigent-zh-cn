"""add archived column to conversations

Revision ID: 3b9be5d67c90
Revises: a3b4c5d6e7f8
Create Date: 2026-06-03 12:00:00.000000

Adds ``conversations.archived``: whether a session is archived. Archived
sessions are hidden from the default ``GET /v1/sessions`` listing (and the
sidebar), surfacing only when the caller passes ``include_archived=True``.
Reversible via ``PATCH /v1/sessions/{id}``. ``server_default`` of false
backfills existing rows to not-archived so the NOT NULL column applies
cleanly to a populated table.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3b9be5d67c90"
down_revision: str | None = "a3b4c5d6e7f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Add the NOT NULL ``archived`` column to ``conversations``.

    ``server_default=sa.false()`` backfills existing rows to
    not-archived (required for a NOT NULL add against a populated
    table) and matches the ``server_default`` on the ORM model. Batch
    mode is used for SQLite compatibility, consistent with the other
    conversations migrations.
    """
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.add_column(
            sa.Column(
                "archived",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )


def downgrade() -> None:
    """Drop the ``archived`` column."""
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("archived")
