"""add idx_conversations_parent (partial index for sub-agent child listing)

Revision ID: j1a2b3c4d5e6
Revises: d4f1a9c2b8e3
Create Date: 2026-06-07 00:00:00.000000

Adds a partial composite index used when listing the sub-agent children
of a parent session (the ``parent_conversation_id`` FK walk powering
``GET /v1/sessions/{id}/child_sessions``). The covered query filters on
``kind = 'sub_agent'`` and orders newest-first by ``(created_at, id)``,
so the index columns and their DESC ordering match the scan exactly:

    CREATE INDEX idx_conversations_parent
    ON conversations (parent_conversation_id, created_at DESC, id DESC)
    WHERE kind = 'sub_agent';

The ``WHERE kind = 'sub_agent'`` predicate keeps the index small — it
covers only sub-agent rows, never top-level sessions. Both SQLite and
PostgreSQL support partial (``WHERE``) indexes and per-column DESC
ordering, so the partial predicate is expressed via the dialect-specific
``sqlite_where`` / ``postgresql_where`` kwargs (mirroring the existing
``ix_conversations_parent_title_unique`` partial index) and the DESC
ordering via ``sa.text`` column expressions.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "j1a2b3c4d5e6"
down_revision: str | None = "d4f1a9c2b8e3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "idx_conversations_parent",
        "conversations",
        # DESC ordering is expressed through text() column expressions
        # because Alembic's create_index column list doesn't take a
        # per-column sort direction otherwise. Both SQLite and Postgres
        # honor DESC in a CREATE INDEX column list.
        [
            "parent_conversation_id",
            sa.text("created_at DESC"),
            sa.text("id DESC"),
        ],
        unique=False,
        sqlite_where=sa.text("kind = 'sub_agent'"),
        postgresql_where=sa.text("kind = 'sub_agent'"),
    )


def downgrade() -> None:
    op.drop_index("idx_conversations_parent", table_name="conversations")
