"""
Async-dispatch demo tool set for ``omnigent run --tools async_demo``.

Ships one tool — ``slow_compute`` — registered as a client-side
tool. The LLM dispatches it asynchronously by calling
``sys_call_async(tool="slow_compute", args=...)`` instead of
calling the tool directly. The server's
:meth:`SysCallAsyncTool.dispatch_async` creates a
``kind="client_tool"`` task, registers a pending_tool_call, and
synthesizes a ``function_call(action_required)`` SSE event — the
SDK's action_required handler runs the tool body locally and
PATCHes ``tool_results`` back; the server bridges the PATCH to
``CLIENT_TOOL_RESULT_TOPIC`` so the holder workflow signals
``async_work_complete`` and the parent's drain renders
``[System: task ... (client_tool) completed]\\n<body>``.

The tool itself is deliberately boring (sleep + echo) — the
point is to show the async protocol end-to-end in the TUI
without needing a real compute workload.

Registered via :func:`omnigent.client_tools.get_tool_set`,
which ``omnigent run`` calls when ``--tools async_demo`` is
passed.
"""

from __future__ import annotations

import time
from typing import Any

# Tool schemas in standard OpenAI function-calling format. There
# is no longer a ``synchronous`` property in the schema — async
# dispatch is the LLM's choice via ``sys_call_async`` at call
# site, not an author-time / per-call schema flag.
TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "slow_compute",
            "description": (
                "Simulates a long-running background computation. "
                "Dispatch via sys_call_async so the LLM gets a "
                "handle immediately; the real output arrives later "
                "as a [System: task ... completed] user message."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "number",
                        "description": (
                            "How long to sleep before returning, e.g. 3.0. "
                            "Use values between 1 and 30 for demo purposes."
                        ),
                    },
                    "label": {
                        "type": "string",
                        "description": "A tag to echo in the output.",
                    },
                },
                "required": ["seconds", "label"],
            },
        },
    },
]


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """
    Execute a client-side tool call from ``omnigent run``.

    Called by the SDK's action_required handler
    (``_execute_and_patch``) after the server's
    ``_dispatch_client_tool_async`` synthesized the
    ``function_call(action_required)`` SSE event.

    :param name: Tool name from the LLM's ``function_call``.
        Only ``"slow_compute"`` is registered; anything else
        raises :class:`KeyError` and surfaces as a tool error.
    :param arguments: Arg dict from the LLM. ``seconds`` is
        coerced to float; ``label`` is used verbatim.
    :returns: A string describing the completion, e.g.
        ``"finished 'hello' after 3.0s"``.
    :raises KeyError: If ``name`` is not ``"slow_compute"`` —
        the registry only exports one tool.
    """
    if name != "slow_compute":
        raise KeyError(f"async_demo only exports 'slow_compute'; got {name!r}")
    seconds = float(arguments.get("seconds") or 0)
    label = str(arguments.get("label") or "")
    # ``time.sleep`` blocks the current thread. That's fine
    # because the SDK invokes ``execute_tool`` via
    # ``asyncio.to_thread`` (see ``_call_execute_off_loop`` in
    # the SDK) — the event loop stays free to handle the rest
    # of the stream while this task sleeps.
    time.sleep(seconds)
    return f"finished {label!r} after {seconds}s"
