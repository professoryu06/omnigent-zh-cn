"""add hosts table and host_id column to conversations

Revision ID: a7b3c9d1e5f2
Revises: b9c1d2e3f4a5
Create Date: 2026-05-27 18:00:00.000000

Adds the ``hosts`` table for tracking machines connected via
``omnigent host``. Each row represents a host that has connected
at least once; the ``status`` column reflects whether the host
currently has an active WebSocket tunnel.

Also adds ``conversations.host_id`` so the server knows which host
launched (or should launch) the runner for a given session. Used for
retry-on-reconnect: if the server restarts before the runner
connects, it re-sends the launch request to this host.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7b3c9d1e5f2"
down_revision: str | None = "b9c1d2e3f4a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Create the ``hosts`` table and add ``host_id`` to
    ``conversations``.
    """
    op.create_table(
        "hosts",
        sa.Column("owner", sa.String(length=256), primary_key=True),
        sa.Column("name", sa.String(length=256), primary_key=True),
        sa.Column("host_id", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default="offline",
        ),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "status IN ('online', 'offline')",
            name="ck_hosts_status",
        ),
        sa.UniqueConstraint("host_id", name="uq_hosts_host_id"),
    )

    op.add_column(
        "conversations",
        sa.Column("host_id", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    """Drop ``conversations.host_id`` and the ``hosts`` table."""
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("host_id")
    op.drop_table("hosts")
