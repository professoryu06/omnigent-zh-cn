"""Backward-compatibility shim for the env-var prefix renames -> ``OMNIGENT_*``.

The project's env-var prefix has changed twice as the name evolved:
``OMNIAGENTS_`` (original) -> ``OMNIGENTS_`` -> ``OMNIGENT_`` (current). All
current code reads the new ``OMNIGENT_`` names. To keep existing deployments,
CI configs, and shell profiles that still export either older prefix working,
this shim mirrors every legacy variable onto its ``OMNIGENT_`` equivalent at
process startup -- but only when the new name is unset, so an explicitly-set
``OMNIGENT_`` value always wins.

The mirror is installed once, as early as possible, from
``omnigent/__init__.py`` so it runs before any submodule reads the
environment. Out-of-package entry points that read env *before* importing the
``omnigent`` package (the Docker / Databricks deploy entrypoints) call
:func:`mirror_legacy_env` directly.
"""

from __future__ import annotations

import os

# The current prefix, and every legacy prefix that maps onto it. Ordered
# newest-first so that when more than one legacy prefix is set for the same
# variable, the newer one wins (``setdefault`` keeps the first mirrored value).
# A variable named ``OMNIGENTS_FOO`` or ``OMNIAGENTS_FOO`` is mirrored to
# ``OMNIGENT_FOO``.
_NEW_PREFIX = "OMNIGENT_"
_LEGACY_PREFIXES = ("OMNIGENTS_", "OMNIAGENTS_")

# Module-level guard so repeated imports/calls don't rescan the environment.
_mirrored = False


def mirror_legacy_env() -> None:
    """
    Mirror legacy ``OMNIGENTS_*`` / ``OMNIAGENTS_*`` env vars onto ``OMNIGENT_*``.

    For every environment variable whose name starts with one of the legacy
    prefixes in :data:`_LEGACY_PREFIXES`, set the corresponding ``OMNIGENT_``
    variable if (and only if) it is not already present -- so an explicitly-set
    new-name variable always takes precedence over a legacy one, and a newer
    legacy prefix takes precedence over an older one. Idempotent and cheap:
    calls after the first are no-ops.

    Example: with ``OMNIAGENTS_SKIP_WEB_UI=1`` in the environment and no
    ``OMNIGENT_SKIP_WEB_UI`` set, this leaves ``OMNIGENT_SKIP_WEB_UI=1``.

    :returns: ``None``. Mutates :data:`os.environ` in place.
    """
    global _mirrored
    if _mirrored:
        return
    for legacy_prefix in _LEGACY_PREFIXES:
        for name, value in list(os.environ.items()):
            if name.startswith(legacy_prefix):
                new_name = _NEW_PREFIX + name[len(legacy_prefix) :]
                os.environ.setdefault(new_name, value)
    _mirrored = True
