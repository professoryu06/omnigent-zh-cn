"""
macOS Seatbelt sandbox backend — re-export wrapper.

Importing this module is sufficient to register the
``darwin_seatbelt`` backend with the sandbox registry:
:mod:`omnigent.inner.seatbelt_sandbox` calls
``register_backend(SeatbeltSandboxBackend())`` at import time, and
re-importing it through this wrapper triggers the same side effect.

New code should import the backend through this module so legacy
``inner.seatbelt_sandbox`` references can eventually retire without
breaking any current consumer (parallel to
:mod:`omnigent.sandbox.bwrap`).

Like ``linux_bwrap`` on Linux, the Seatbelt backend is the macOS
platform default (selected by :func:`omnigent.inner.sandbox._default_sandbox_for_platform`
when ``sys.platform == "darwin"`` and the ``sandbox-exec`` binary
is on ``PATH``). Spec authors can still opt in explicitly with
``os_env.sandbox.type: darwin_seatbelt`` for clarity.
"""

from __future__ import annotations

from omnigent.inner.seatbelt_sandbox import SeatbeltSandboxBackend

__all__ = [
    "SeatbeltSandboxBackend",
]
