"""Sample policy functions for testing PreToolUse/PostToolUse enforcement."""

from __future__ import annotations

from omnigent.policies.schema import PolicyEvent, PolicyResponse

_ALLOW: PolicyResponse = {"result": "ALLOW"}


def block_bash_rm(event: PolicyEvent) -> PolicyResponse:
    """
    Block Bash tool calls that contain ``rm``.

    Returns ALLOW for non-tool-call events and tool calls that aren't
    Bash or don't contain ``rm``.

    :param event: V0 event dict with ``type``, ``target``, ``data``,
        ``context`` keys.
    :returns: V0 decision dict.
    """
    if event.get("type") != "tool_call":
        return _ALLOW

    data = event.get("data")
    tool_name: str = data.get("name", "") if isinstance(data, dict) else ""
    if tool_name != "Bash":
        return _ALLOW

    args = data.get("arguments")
    command: str = args.get("command", "") if isinstance(args, dict) else ""
    if "rm " in command or command.startswith("rm"):
        return {
            "result": "DENY",
            "reason": "Destructive rm commands are blocked by admin policy.",
        }

    return _ALLOW


def block_sensitive_output(event: PolicyEvent) -> PolicyResponse:
    """
    Flag tool results that contain ``/etc/passwd`` content.

    Fires on ``tool_result`` phase. Returns DENY with a reason so the
    PostToolUse hook surfaces a warning to Claude.

    :param event: V0 event dict.
    :returns: V0 decision dict.
    """
    if event.get("type") != "tool_result":
        return _ALLOW

    data = event.get("data")
    if not isinstance(data, str):
        data = str(data)
    if "root:x:0:0" in data:
        return {
            "result": "DENY",
            "reason": "Tool output contains sensitive system data.",
        }

    return _ALLOW
