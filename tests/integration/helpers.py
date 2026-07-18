"""Shared helpers for the per-harness journey tests."""

from __future__ import annotations

from typing import Any

import httpx

from tests.e2e.conftest import (
    poll_session_until_terminal,
    send_user_message_to_session,
)


def all_message_text(body: dict[str, Any]) -> str:
    """Concatenate every message text block from a terminal turn body.

    :param body: The dict returned by ``poll_session_until_terminal``.
    :returns: All assistant text joined by newlines.
    """
    parts: list[str] = []
    for item in body.get("output", []):
        if item.get("type") == "message":
            for block in item.get("content", []):
                text = block.get("text")
                if text:
                    parts.append(text)
    return "\n".join(parts)


def failure_detail(body: dict[str, Any]) -> str:
    """Compact failure description for assertion messages.

    The session's ``error`` field is often ``None`` for harness-side
    failures (the real reason is embedded in the output items), so
    include the raw items too.

    :param body: The dict returned by ``run_turn``.
    """
    return f"error={body.get('error')!r} output={str(body.get('output'))[:600]}"


def run_turn(
    client: httpx.Client,
    *,
    session_id: str,
    content: str,
    timeout: float = 50,
) -> dict[str, Any]:
    """Send one user turn and wait for the session to go terminal.

    :param client: HTTP client pointed at the live server.
    :param session_id: Runner-bound session id.
    :param content: User prompt text.
    :param timeout: Max seconds to wait for the turn. Healthy turns
        finish in 5-20s; 50s keeps even the three-turn journey under
        the CI per-test ``--timeout=180`` cap PER RERUN ATTEMPT, so a
        slow turn fails with a poll error instead of a thread-timeout
        hard kill (which would break the codex rerun path).
    :returns: ``{"status": ..., "output": ...}``.
    """
    response_id = send_user_message_to_session(client, session_id=session_id, content=content)
    return poll_session_until_terminal(
        client, session_id=session_id, response_id=response_id, timeout=timeout
    )
