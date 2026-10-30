"""Tests for runner idle-shutdown stream drain (#3060).

Verifies that ``app.state.drain_session_streams`` enqueues a ``None``
sentinel into every active session event queue so that SSE generators
terminate promptly during graceful shutdown.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from omnigent.runner.app import create_runner_app


def _scaffold_app() -> Any:
    """Create a runner app in scaffold mode (no process manager).

    :returns: The FastAPI application instance.
    """
    return create_runner_app(server_client=httpx.AsyncClient())


async def test_drain_session_streams_enqueues_done_sentinel() -> None:
    """drain_session_streams puts exactly one None into each queue.

    Two session queues are registered; after calling the drain hook
    each queue must contain exactly one ``None`` sentinel and nothing
    else. The global queue registry is cleaned up in a finally block.
    """
    from omnigent.runner.app import _session_event_queues_ref

    app = _scaffold_app()
    # Register two session queues directly on the module-level ref.
    q1: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
    q2: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
    _session_event_queues_ref["sess_a"] = q1
    _session_event_queues_ref["sess_b"] = q2
    try:
        drain = getattr(app.state, "drain_session_streams", None)
        assert drain is not None, "app.state.drain_session_streams not exposed"
        assert callable(drain), "drain_session_streams is not callable"
        drain()
        # Each queue must have exactly one None sentinel.
        assert q1.qsize() == 1, f"q1 size {q1.qsize()}, expected 1"
        assert q2.qsize() == 1, f"q2 size {q2.qsize()}, expected 1"
        assert q1.get_nowait() is None
        assert q2.get_nowait() is None
    finally:
        _session_event_queues_ref.pop("sess_a", None)
        _session_event_queues_ref.pop("sess_b", None)
