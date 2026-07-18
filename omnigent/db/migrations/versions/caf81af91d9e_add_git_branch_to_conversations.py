"""add git_branch column to conversations

Revision ID: caf81af91d9e
Revises: b8c4f2e7a9d1
Create Date: 2026-05-29 15:00:00.000000

Adds ``conversations.git_branch``: the git branch checked out in the
session's worktree when the session was created with a server-created
git worktree (designs/SESSION_GIT_WORKTREE.md). ``NULL`` for sessions
with no created worktree. ``git_branch IS NOT NULL`` is the gate for
offering worktree cleanup on session delete.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "caf81af91d9e"
down_revision: str | None = "b8c4f2e7a9d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Add the nullable ``git_branch`` column to ``conversations``.

    Batch mode is used for SQLite compatibility, consistent with the
    other conversations migrations.
    """
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.add_column(sa.Column("git_branch", sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Drop the ``git_branch`` column."""
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("git_branch")
