"""
Rate-limit policy factories for the `rate-limited-search`
fixture agent.

Ports omnigent ``examples/search_rate_limit_policy.py`` and
``examples/rate_limit_policy.py``.
"""

from __future__ import annotations

from typing import Any

_ALLOW: dict[str, Any] = {"result": "ALLOW"}


def rate_limit_search(limit: int = 3) -> Any:
    """
    Factory for a stateful web-search rate limiter.

    After ``limit`` free searches, additional calls ASK for
    user approval instead of blocking outright. The classic
    omnigent IFC-ergonomics example.

    :param limit: Free-call budget before ASK kicks in.
    :returns: Evaluator callable with closure state that
        counts invocations.
    """
    calls = 0

    def _eval(event: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluator: count ``web_search`` tool_call invocations, ALLOW up to
        ``limit``, ASK thereafter. Returns ALLOW for all other events
        (other tools, request/response phases).
        """
        nonlocal calls
        if event.get("type") != "tool_call":
            return _ALLOW
        data = event.get("data")
        tool_name = data.get("name", "") if isinstance(data, dict) else ""
        if tool_name != "web_search":
            return _ALLOW
        calls += 1
        if calls <= limit:
            return _ALLOW
        return {
            "result": "ASK",
            "reason": (f"Free search budget ({limit}) exhausted; this search is call #{calls}."),
        }

    return _eval


def max_tool_calls_per_turn(limit: int = 15) -> Any:
    """
    Factory for a per-workflow total-tool-call cap.

    Ports omnigent ``max_tool_calls_per_turn`` — used as a
    safety-net policy alongside more targeted guards.

    :param limit: Total calls before DENY.
    :returns: Evaluator callable with closure state.
    """
    calls = 0

    def _eval(event: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        """
        Deny after ``limit`` total tool calls. Returns ALLOW for non-tool-call events.
        """
        nonlocal calls
        if event.get("type") != "tool_call":
            return _ALLOW
        calls += 1
        if calls > limit:
            return {
                "result": "DENY",
                "reason": f"Tool-call budget ({limit}) exceeded.",
            }
        return _ALLOW

    return _eval
