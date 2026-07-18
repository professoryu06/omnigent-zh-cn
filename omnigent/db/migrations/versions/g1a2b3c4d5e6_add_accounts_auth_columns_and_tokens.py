"""add accounts auth columns and tokens table

Revision ID: g1a2b3c4d5e6
Revises: 3b9be5d67c90
Create Date: 2026-06-02 23:30:00.000000

Adds the schema for the ``accounts`` auth provider — built-in
username + password identity with first-user-is-admin bootstrapping.

Columns on the existing ``users`` table:

- ``password_hash`` (nullable) — argon2id hash. ``NULL`` for users
  created via ``header``/``oidc`` modes (their password is the
  upstream IdP's).
- ``created_at`` (nullable) — unix epoch seconds. ``NULL`` for the
  ``"local"`` row backfilled by the original permissions migration
  and any pre-accounts upserts.
- ``last_login_at`` (nullable) — unix epoch seconds; bumped on
  every successful ``/auth/login``.

New ``account_tokens`` table backs both invite tokens
(admin-issued, allow self-serve registration) and magic-login
tokens (CLI-minted, hand off a signed-in session into the web
UI). Single-table because both share short-TTL + single-use
semantics. See ``designs/ACCOUNTS_AUTH.md``.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "g1a2b3c4d5e6"
# Single-parent chain off main's latest head. Earlier iterations
# of this file declared a tuple to "merge two parallel heads" —
# tracing the graph showed those candidates were actually linear
# descendants, so the tuple was redundant. Each rebase onto main
# just bumps this to whatever the new tip is.
down_revision: str | None = "3b9be5d67c90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add password / timestamp columns to users; create account_tokens."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("password_hash", sa.String(256), nullable=True))
        batch_op.add_column(sa.Column("created_at", sa.Integer, nullable=True))
        batch_op.add_column(sa.Column("last_login_at", sa.Integer, nullable=True))

    op.create_table(
        "account_tokens",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("user_id", sa.String(128), nullable=True),
        sa.Column("created_by", sa.String(128), nullable=True),
        sa.Column("created_at", sa.Integer, nullable=False),
        sa.Column("expires_at", sa.Integer, nullable=False),
        sa.Column("redeemed_at", sa.Integer, nullable=True),
        sa.Column(
            "invited_is_admin",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
        sa.CheckConstraint("kind IN ('invite', 'magic')", name="ck_account_tokens_kind"),
    )
    op.create_index(
        "ix_account_tokens_expires_at",
        "account_tokens",
        ["expires_at"],
    )


def downgrade() -> None:
    """Drop account_tokens and the three accounts columns on users."""
    op.drop_index("ix_account_tokens_expires_at", table_name="account_tokens")
    op.drop_table("account_tokens")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("last_login_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("password_hash")
