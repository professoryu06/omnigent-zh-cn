"""
Python policies for the `policies-demo` fixture agent.

Ports relevant callables from omnigent
`examples/tool_functions.py` into a location importable by the
omnigent parser (dotted path `tests._fixtures.agents.*`).

All callables follow the Service Policies V0 contract:
``fn(event) -> {"result": ..., "reason": ...}``.
"""

from __future__ import annotations

import json

from omnigent.policies.schema import PolicyEvent, PolicyResponse

# Long-sleep threshold. Sleep calls over this many seconds are
# blocked. Chosen small enough that trivial test args (like 8 s)
# trip the guard; large enough that the canonical "sleep 2" ALLOW
# path keeps working.
_MAX_SLEEP_SECONDS = 5

_ALLOW: PolicyResponse = {"result": "ALLOW"}


def block_long_sleep(event: PolicyEvent) -> PolicyResponse:
    """
    Ported from omnigent ``block_long_sleep``.

    Blocks when the requested sleep duration exceeds
    :data:`_MAX_SLEEP_SECONDS`. Returns ALLOW for non-``tool_call``
    events and tool calls that aren't ``sleep``.

    :param event: V0 event dict with ``type``, ``target``,
        ``data``, ``context`` keys. On TOOL_CALL phase,
        ``event["data"]`` is a dict ``{"tool": name,
        "args": <args>}``.
    :returns: V0 decision dict — DENY when args ask for a
        long sleep, ALLOW otherwise.
    """
    if event.get("type") != "tool_call":
        return _ALLOW
    data = event.get("data")
    tool_name = data.get("name", "") if isinstance(data, dict) else ""
    if not tool_name.endswith("sleep"):
        return _ALLOW
    args = _extract_args(event.get("data"))
    seconds = args.get("seconds")
    try:
        secs_num = float(seconds) if seconds is not None else 0.0
    except (TypeError, ValueError):
        # Malformed args — let the tool handler produce its
        # own error. Policy does not gate on argument type.
        secs_num = 0.0
    if secs_num > _MAX_SLEEP_SECONDS:
        return {
            "result": "DENY",
            "reason": (
                f"Requested sleep {secs_num}s exceeds the {_MAX_SLEEP_SECONDS}s policy limit."
            ),
        }
    return _ALLOW


def _extract_args(content: object) -> dict[str, object]:
    """
    Pull the tool-call argument mapping out of ``event["data"]``.

    The workflow builds TOOL_CALL events with data shaped as
    ``{"name": name, "arguments": <args>}``. Args may be either
    already-parsed dicts or JSON-encoded strings (Omnigent'
    ToolManager passes strings before JSON-decode for some
    paths).

    :param content: Whatever was on ``event["data"]``.
    :returns: Argument dict. Empty dict when the content does
        not conform to the expected shape — safer than raising
        from a policy callable.
    """
    if not isinstance(content, dict):
        return {}
    args = content.get("arguments")
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        try:
            parsed = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}
