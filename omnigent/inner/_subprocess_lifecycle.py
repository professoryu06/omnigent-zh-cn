"""Force-close asyncio subprocess transports before loop teardown.

``asyncio.subprocess.Process.wait()`` returns when the subprocess exits,
but the transport is only marked ``_closed`` when something calls
``transport.close()`` explicitly. If the test event loop closes first,
GC later calls ``BaseSubprocessTransport.__del__`` which does
``self._loop.call_soon(...)`` on a closed loop and raises
``RuntimeError('Event loop is closed')``.

``_transport`` is a stable private attr on
``asyncio.subprocess.Process`` across CPython 3.10+.
"""

from __future__ import annotations

import contextlib
from typing import Any


def close_subprocess_transport(proc: Any) -> None:  # type: ignore[explicit-any]
    """Force-close ``proc._transport``. Safe on missing/already-closed."""
    transport = getattr(proc, "_transport", None)
    if transport is None:
        return
    is_closing = getattr(transport, "is_closing", None)
    if callable(is_closing) and is_closing():
        return
    with contextlib.suppress(Exception):
        transport.close()


def close_anyio_subprocess_transport(anyio_proc: Any) -> None:  # type: ignore[explicit-any]
    """Unwrap an anyio ``Process`` to its underlying asyncio process and close its transport."""
    inner = getattr(anyio_proc, "_process", None)
    if inner is None:
        return
    close_subprocess_transport(inner)


__all__ = [
    "close_anyio_subprocess_transport",
    "close_subprocess_transport",
]
