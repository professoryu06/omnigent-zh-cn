"""Function-based policies for the secure research agent example.

Uses ``set_labels`` and ``session_state`` to implement information
flow control:

- ``taint_web_search``: ALLOW + set integrity=0 when web search is called.
- ``taint_confidential_read``: ALLOW + set confidentiality=1 when reading
  confidential docs.
- ``deny_contaminated_shell``: DENY shell/write when both confidentiality=1
  AND integrity=0 (data exfiltration risk).
- ``ask_high_confidentiality``: ASK for shell when confidentiality=1.
- ``ask_low_integrity``: ASK for shell/write when integrity=0.
"""

from __future__ import annotations

from omnigent.policies.schema import PolicyEvent, PolicyResponse

_ALLOW: PolicyResponse = {"result": "ALLOW"}

_SHELL_TOOLS = frozenset({"run_shell", "write_file"})


def taint_web_search(event: PolicyEvent) -> PolicyResponse:
    """
    ALLOW web search calls and taint integrity to 0.

    :param event: V0 event dict.
    :returns: ALLOW with ``set_labels`` to lower integrity.
    """
    if event.get("type") != "tool_call":
        return _ALLOW
    data = event.get("data")
    tool = data.get("name", "") if isinstance(data, dict) else ""
    if tool != "search_web":
        return _ALLOW
    return {
        "result": "ALLOW",
        "state_updates": {"integrity": "0"},
    }


def taint_confidential_read(event: PolicyEvent) -> PolicyResponse:
    """
    ALLOW confidential doc reads and taint confidentiality to 1.

    :param event: V0 event dict.
    :returns: ALLOW with ``set_labels`` to raise confidentiality.
    """
    if event.get("type") != "tool_call":
        return _ALLOW
    data = event.get("data")
    tool = data.get("name", "") if isinstance(data, dict) else ""
    if tool != "read_internal_doc":
        return _ALLOW
    return {
        "result": "ALLOW",
        "state_updates": {"confidentiality": "1"},
    }


def deny_contaminated_shell(event: PolicyEvent) -> PolicyResponse:
    """
    DENY shell/write when both high-confidentiality AND low-integrity.

    This is the strictest enforcement: if the agent has seen
    confidential data AND consumed untrusted web content, shell and
    file operations are blocked to prevent data exfiltration via
    prompt injection.

    :param event: V0 event dict.
    :returns: DENY if labels match, ALLOW otherwise.
    """
    if event.get("type") != "tool_call":
        return _ALLOW
    data = event.get("data")
    tool = data.get("name", "") if isinstance(data, dict) else ""
    if tool not in _SHELL_TOOLS:
        return _ALLOW
    state = event.get("session_state") or {}
    if state.get("confidentiality") == "1" and state.get("integrity") == "0":
        return {
            "result": "DENY",
            "reason": (
                "Agent has both confidential data AND untrusted content. "
                "Shell and file operations are denied to prevent data "
                "exfiltration via prompt injection."
            ),
        }
    return _ALLOW


def ask_high_confidentiality(event: PolicyEvent) -> PolicyResponse:
    """
    ASK for shell when confidentiality is high.

    :param event: V0 event dict.
    :returns: ASK if confidentiality=1, ALLOW otherwise.
    """
    if event.get("type") != "tool_call":
        return _ALLOW
    data = event.get("data")
    tool = data.get("name", "") if isinstance(data, dict) else ""
    if tool != "run_shell":
        return _ALLOW
    state = event.get("session_state") or {}
    if state.get("confidentiality") == "1":
        return {
            "result": "ASK",
            "reason": (
                "Agent has accessed confidential data. "
                "Shell command requires explicit user approval."
            ),
        }
    return _ALLOW


def ask_low_integrity(event: PolicyEvent) -> PolicyResponse:
    """
    ASK for shell/write when integrity is low.

    :param event: V0 event dict.
    :returns: ASK if integrity=0, ALLOW otherwise.
    """
    if event.get("type") != "tool_call":
        return _ALLOW
    data = event.get("data")
    tool = data.get("name", "") if isinstance(data, dict) else ""
    if tool not in _SHELL_TOOLS:
        return _ALLOW
    state = event.get("session_state") or {}
    if state.get("integrity") == "0":
        return {
            "result": "ASK",
            "reason": (
                "Agent has consumed untrusted web content. "
                "This action requires explicit user approval "
                "to mitigate potential prompt injection risks."
            ),
        }
    return _ALLOW
