"""add managed-sandbox columns to hosts

Revision ID: k1a2b3c4d5e6
Revises: ecc0e25727b0
Create Date: 2026-06-09 00:00:00.000000

Adds the server-managed sandbox host columns to ``hosts``: the
launch-token digest + expiry that authenticate a sandbox-hosted
``omnigent host`` over the host tunnel, and the provider/sandbox
handle the server terminates on session delete. All four are NULL for
external (user-connected) hosts; they are set while a host is backed
by a server-provisioned sandbox, and overwritten as a unit when the
sandbox is relaunched (the host row is durable; the token/sandbox
generation is not). See ``omnigent/server/managed_hosts.py``.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "k1a2b3c4d5e6"
down_revision: str | None = "ecc0e25727b0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Add the managed-sandbox columns (and the token-digest uniqueness
    constraint) to ``hosts``.

    Batch mode so the unique constraint lands on SQLite too (which
    cannot ALTER a constraint onto an existing table in place).
    """
    with op.batch_alter_table("hosts") as batch_op:
        batch_op.add_column(sa.Column("token_hash", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("token_expires_at", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("sandbox_provider", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("sandbox_id", sa.String(length=256), nullable=True))
        batch_op.create_unique_constraint("uq_hosts_token_hash", ["token_hash"])


def downgrade() -> None:
    """Drop the managed-sandbox columns and constraint from ``hosts``."""
    with op.batch_alter_table("hosts") as batch_op:
        batch_op.drop_constraint("uq_hosts_token_hash", type_="unique")
        batch_op.drop_column("sandbox_id")
        batch_op.drop_column("sandbox_provider")
        batch_op.drop_column("token_expires_at")
        batch_op.drop_column("token_hash")
