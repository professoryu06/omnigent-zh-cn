"""
Bubblewrap sandbox backend — re-export wrapper.

Importing this module is sufficient to register the Linux
``linux_bwrap`` backend with the sandbox registry:
:mod:`omnigent.inner.bwrap_sandbox` calls
``register_backend(BwrapSandboxBackend())`` at import time, and
re-importing it through this wrapper triggers the same side effect.

New code should import the backend through this module so legacy
``inner.bwrap_sandbox`` references can eventually retire without
breaking any current consumer (parallel to
:mod:`omnigent.sandbox.seatbelt`).

The bwrap backend is the Linux platform default when the ``bwrap``
binary is on ``PATH`` (selected by
:func:`omnigent.inner.sandbox._default_sandbox_for_platform`). When
``bwrap`` is missing, the default falls back to ``none``. Spec
authors can pin a specific backend via
``os_env.sandbox.type: linux_bwrap`` for clarity.
"""

from __future__ import annotations

from omnigent.inner.bwrap_sandbox import BwrapSandboxBackend

__all__ = [
    "BwrapSandboxBackend",
]
