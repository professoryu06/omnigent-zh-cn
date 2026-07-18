"""Add session_id column to files table.

Revision ID: b5e8d2f1a7c3
Revises: a2c7e8f19b34
Create Date: 2026-05-12

Phase 1c of the Session Resources API adds session ownership to
file metadata so files can be scoped to a specific session. The
column is nullable to preserve backward compatibility with existing
global files uploaded via ``/v1/files``.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "b5e8d2f1a7c3"
down_revision: str | None = "93c04fcdff56"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Add session_id column and composite index to files table."""
    op.add_column(
        "files",
        sa.Column("session_id", sa.String(64), nullable=True),
    )
    op.create_index(
        "ix_files_session_id_created_at",
        "files",
        ["session_id", "created_at", "id"],
    )


def downgrade() -> None:
    """Remove session_id column and index from files table."""
    op.drop_index("ix_files_session_id_created_at", table_name="files")
    with op.batch_alter_table("files") as batch_op:
        batch_op.drop_column("session_id")
