"""
Local Python tool for the inbox-test agent.

A trivial sync function the LLM dispatches via ``sys_call_async``.
The dispatched task lands on the parent agent workflow's
``async_work_complete`` mailbox; the LLM's subsequent
``sys_read_inbox`` call drains it via the harness-side inline
async-tool dispatch (see
``the harness HTTP client._dispatch_async_tool_inline``).

The marker string is intentionally distinctive so a manual
REPL session can confirm end-to-end that the drain returned
the dispatched payload (rather than the empty-inbox sentinel).
"""

from __future__ import annotations


def tag_label(label: str) -> str:
    """
    Return ``label`` wrapped in an unambiguous marker.

    :param label: Text to echo back, e.g. ``"alpha"``.
    :returns: The literal string ``f"INBOX_TEST_TAG[{label}]"``.
    """
    return f"INBOX_TEST_TAG[{label}]"
