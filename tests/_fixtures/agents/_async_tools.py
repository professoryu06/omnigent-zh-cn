"""Test tools for the async-tool E2E suite.

Plain Python callables referenced by ``callable:`` in
``async-tools-test/async-tools-test.yaml``. The slow tools
sleep briefly so the dispatch ↔ auto-delivery sequence is
observable as distinct events; the markers returned are
deliberately distinctive substrings so e2e assertions like
``"ECHO_FROM_ASYNC[..." in final_text`` are unambiguous.
"""

from __future__ import annotations

import time


def delayed_echo(label: str) -> str:
    """
    Sleep 2s, then echo ``label`` inside an unambiguous marker.

    :param label: Text to echo back, e.g. ``"alpha"``.
    :returns: ``f"ECHO_FROM_ASYNC[{label}]"``.
    """
    time.sleep(2)
    return f"ECHO_FROM_ASYNC[{label}]"


def boom_async() -> str:
    """
    Always raise so the failure path of the async pipeline is exercised.

    :raises RuntimeError: Always, with message ``ASYNC_TOOL_BOOM_MARKER``.
    """
    raise RuntimeError("ASYNC_TOOL_BOOM_MARKER")


def count_chars(text: str) -> int:
    """
    Return the literal character count of ``text``.

    :param text: Text to measure.
    :returns: Length of ``text``.
    """
    return len(text)
