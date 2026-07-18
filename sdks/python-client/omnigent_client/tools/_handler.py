"""Adapter that turns ``@tool``-decorated functions into a ToolHandler.

The stream-layer ``ToolHandler`` takes a list of OpenAI-shape JSON
schemas and a single ``execute`` callable. Users who have written
tools with the ``@tool`` decorator (Python functions with type hints
and Google-style docstrings) shouldn't have to hand-roll that shape:
:func:`build_tool_handler` reads each function's tool metadata and
builds the handler for them.

Dispatch is by tool name. Calling an unknown tool raises — the SDK
surfaces the error back to the agent as a tool error.
"""

from __future__ import annotations

import asyncio
import inspect
import json
from collections.abc import Callable
from typing import Any

from .._tool_handler import ToolCallInfo, ToolHandler
from ._decorator import TOOL_MARKER_ATTR, ToolMetadata


def build_tool_handler(functions: list[Callable[..., Any]]) -> ToolHandler:
    """Build a :class:`ToolHandler` from ``@tool``-decorated functions.

    Each function must carry tool metadata attached by the
    :func:`~omnigent_client.tool` decorator (checked via
    :data:`TOOL_MARKER_ATTR`). The returned handler exposes the
    OpenAI-shape schemas the SDK sends to the server, and an
    ``execute`` callable that dispatches incoming tool calls by
    name.

    :param functions: List of ``@tool``-decorated Python functions,
        e.g. ``[get_current_time, search_docs]``. Each must be a
        module-level ``def`` or ``async def`` decorated with
        ``@tool``.
    :returns: A :class:`ToolHandler` ready to pass as
        ``session.tool_handler`` or via the ``tools=`` keyword on
        ``OmnigentClient.query`` / ``Session.query``.
    :raises TypeError: If any function is missing the ``@tool``
        marker (i.e. wasn't decorated).
    :raises ValueError: If two functions share the same tool name
        — tool names must be unique per handler.
    """
    if not functions:
        raise ValueError("build_tool_handler() requires at least one function")

    schemas: list[dict[str, object]] = []
    funcs_by_name: dict[str, Callable[..., Any]] = {}

    for fn in functions:
        meta: ToolMetadata | None = getattr(fn, TOOL_MARKER_ATTR, None)
        if meta is None:
            raise TypeError(
                f"{fn.__module__}.{fn.__qualname__} is not decorated with "
                f"@tool. Decorate it with `from omnigent_client import tool` "
                f"and apply @tool above the function definition."
            )
        if meta.name in funcs_by_name:
            raise ValueError(
                f"Duplicate tool name {meta.name!r}: "
                f"{funcs_by_name[meta.name].__qualname__} and "
                f"{fn.__qualname__} both export the same name."
            )
        funcs_by_name[meta.name] = fn
        schema: dict[str, object] = {
            "type": "function",
            "function": {
                "name": meta.name,
                "description": meta.description,
                "parameters": meta.json_schema,
            },
        }
        schemas.append(schema)

    async def execute(call: ToolCallInfo) -> str:
        """Dispatch ``call`` to the matching ``@tool`` function.

        Async functions (``async def``) are awaited on the
        event loop. Sync functions (``def``) are dispatched to
        a worker thread via ``asyncio.to_thread`` so blocking
        calls inside — ``time.sleep``, file I/O, subprocess,
        ``requests`` — don't stall the event loop. Without the
        thread bounce, several concurrent ``@tool`` invocations
        (e.g. a parallel fan-out of async client tools) would
        serialize: each body would block every sibling AND any
        caller render loop sharing the loop.

        The return value is JSON-serialized unless the function
        already returned a string (which is passed through).
        """
        fn = funcs_by_name.get(call.name)
        if fn is None:
            # The SDK will surface this back to the agent as a tool
            # error — this typically means the LLM invented a tool
            # name that wasn't in the schemas we sent.
            raise KeyError(f"Unknown tool {call.name!r}. Registered: {sorted(funcs_by_name)}")
        if inspect.iscoroutinefunction(fn):
            result = await fn(**call.arguments)
        else:
            # Sync body — route to a worker thread so it
            # doesn't block the event loop (see the fan-out
            # serialization case above).
            result = await asyncio.to_thread(lambda: fn(**call.arguments))
        if isinstance(result, str):
            return result
        # Pydantic models and dataclasses commonly aren't JSON-ready
        # out of the box — ``default=str`` handles datetime/UUID/etc.
        return json.dumps(result, default=str)

    return ToolHandler(schemas=schemas, execute=execute)
