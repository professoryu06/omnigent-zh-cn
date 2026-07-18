"""add session permissions

Revision ID: d4e5f6a7b8c9
Revises: b3d5e7f91a23
Create Date: 2026-05-14 00:00:00.000000

Adds user identity and session-level permissions:

- ``users`` table: user identity from auth header + admin flag.
- ``session_permissions`` table: junction table mapping
  ``(user_id, conversation_id)`` to a numeric level
  (1=read, 2=edit, 3=manage).
- Backfills a ``"local"`` admin user and manage grants for all
  existing conversations so pre-migration sessions remain
  accessible.

See ``designs/SESSIONS_AUTH.md`` for the full design.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "e9f2a7c4d1b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create users and session_permissions tables, backfill existing sessions."""
    op.create_table(
        "users",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "is_admin",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.create_table(
        "session_permissions",
        sa.Column(
            "user_id",
            sa.String(128),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "conversation_id",
            sa.String(64),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("level", sa.Integer, nullable=False),
        sa.CheckConstraint("level IN (1, 2, 3, 4)", name="ck_session_permissions_level"),
    )
    op.create_index(
        "ix_session_permissions_conversation_id",
        "session_permissions",
        ["conversation_id"],
    )

    # Backfill: create "local" admin user and grant manage on all
    # existing conversations so pre-migration sessions stay accessible.
    conn = op.get_bind()
    conn.execute(
        sa.text("INSERT INTO users (id, is_admin) VALUES (:id, :is_admin)"),
        {"id": "local", "is_admin": True},
    )
    conn.execute(
        sa.text(
            "INSERT INTO session_permissions (user_id, conversation_id, level) "
            "SELECT 'local', id, 4 FROM conversations"
        )
    )


def downgrade() -> None:
    """Drop session_permissions and users tables."""
    op.drop_index("ix_session_permissions_conversation_id", table_name="session_permissions")
    op.drop_table("session_permissions")
    op.drop_table("users")
