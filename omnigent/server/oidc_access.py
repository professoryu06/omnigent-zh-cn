"""OIDC admission policy — who may sign in via the configured IdP.

Standard OIDC consent screens (e.g. a Google "External" app, or
GitHub) will authenticate *any* account, so the server needs its own
access control on top of the IdP. This module centralizes that single
admit/deny decision so the callback route has one place to ask "may
this email in?".

A login is admitted when ANY of these hold:

1. **Domain allowlist.** The email's domain is in the effective
   allowlist — the union of ``OMNIGENT_OIDC_ALLOWED_DOMAINS`` (env,
   frozen at startup in :class:`~omnigent.server.oidc.OIDCConfig`)
   and an optional runtime-editable file ``<data_dir>/allowed_domains``
   (same mtime-cached loader as the admin list). If the effective
   allowlist is **empty**, there is no domain restriction and every
   authenticated email is admitted (the OSS default — a fresh deploy
   with no domain config lets any IdP user in).
2. **Admin list.** The email is in ``<data_dir>/admins``. An operator
   listing themselves as admin should never be locked out by a domain
   typo, and they may legitimately be on a different domain.
3. **Individual invite.** The email was pre-authorized via an opt-in
   OIDC invite (``OMNIGENT_OIDC_ALLOW_INVITES`` — see
   :mod:`omnigent.server.accounts_store` /
   ``invited_emails``). Lets an admin admit a single external
   collaborator whose domain isn't allowlisted.

Conditions 2 and 3 are *additive bypasses* — they widen access, never
restrict it.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from omnigent.server.admin_list import AdminList, MtimeCachedIdentitySet, resolve_data_dir


def resolve_allowed_domains_path() -> Path:
    """Resolve the path to the optional allowed-domains file.

    :returns: ``OMNIGENT_OIDC_ALLOWED_DOMAINS_PATH`` if set, else
        ``<data_dir>/allowed_domains`` (see
        :func:`omnigent.server.admin_list.resolve_data_dir`).
    """
    explicit = os.environ.get("OMNIGENT_OIDC_ALLOWED_DOMAINS_PATH", "").strip()
    if explicit:
        return Path(explicit)
    return resolve_data_dir() / "allowed_domains"


class InvitedEmailLookup(Protocol):
    """The slice of the invite store the admission policy consults.

    Implemented by
    :class:`~omnigent.server.accounts_store.SqlAlchemyAccountStore`
    (Stage 4). Kept as a Protocol so this module doesn't depend on the
    accounts store and the policy works with ``None`` when invites are
    disabled.
    """

    def is_email_invited(self, email: str) -> bool:
        """Return whether ``email`` was pre-authorized via an invite."""
        ...


class OidcAdmissionPolicy:
    """Decides whether an authenticated OIDC email may sign in.

    :param env_allowed_domains: The frozen domain allowlist parsed from
        ``OMNIGENT_OIDC_ALLOWED_DOMAINS`` (``OIDCConfig.allowed_domains``).
        ``None`` when the env var is unset.
    :param domains_file_path: Path to the optional runtime-editable
        allowed-domains file. Need not exist.
    :param admin_list: The file-backed admin roster — admins bypass the
        domain check.
    :param invited_lookup: Optional invite store for individual
        pre-authorization. ``None`` when OIDC invites are disabled.
    :param config_allowed_domains: Domains from the server config's
        ``allowed_domains:`` key. Lowercased; union'd with env + file.
    """

    def __init__(
        self,
        env_allowed_domains: frozenset[str] | None,
        domains_file_path: Path,
        admin_list: AdminList,
        invited_lookup: InvitedEmailLookup | None = None,
        config_allowed_domains: frozenset[str] | None = None,
    ) -> None:
        self._env_domains: frozenset[str] = env_allowed_domains or frozenset()
        self._config_domains: frozenset[str] = frozenset(
            d.strip().lower() for d in (config_allowed_domains or frozenset()) if d.strip()
        )
        self._file_domains = MtimeCachedIdentitySet(domains_file_path)
        self._admin_list = admin_list
        self._invited_lookup = invited_lookup

    def effective_domains(self) -> frozenset[str]:
        """Return the union of env, config, and file allowed domains.

        :returns: All currently-configured allowed domains (lowercased).
            Empty when no domain restriction is configured.
        """
        return self._env_domains | self._config_domains | self._file_domains.snapshot()

    def is_admitted(self, email: str) -> bool:
        """Whether ``email`` may sign in.

        :param email: The IdP-returned email, already lowercased by the
            callback, e.g. ``"alice@example.com"``.
        :returns: ``True`` if admitted by domain, admin list, or invite.
        """
        domains = self.effective_domains()
        if not domains:
            return True  # no domain restriction configured → admit all

        domain = email.rsplit("@", 1)[-1] if "@" in email else ""
        if domain in domains:
            return True
        if self._admin_list.is_admin(email):
            return True
        if self._invited_lookup is not None and self._invited_lookup.is_email_invited(email):
            return True
        return False
