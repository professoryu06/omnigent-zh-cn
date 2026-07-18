"""Test tools for the sys_call_async / sys_read_inbox / sys_cancel_async
e2e suite (sys-async-inbox-test, sys-async-inbox-harness-test).

The ``SYS_ASYNC_TAG[...]`` and ``SLEEP_LABEL_DONE[...]`` markers are the
distinctive substrings the e2e assertions check for.
"""

from __future__ import annotations

import time


def tag_label(label: str) -> str:
    """
    Echo ``label`` inside an unambiguous marker. Returns instantly.

    :param label: Text to echo back, e.g. ``"alpha"``.
    :returns: ``f"SYS_ASYNC_TAG[{label}]"``.
    """
    return f"SYS_ASYNC_TAG[{label}]"


def sleep_label(label: str, seconds: int) -> str:
    """
    Sleep for ``seconds`` then echo ``label`` inside an unambiguous marker.

    Used by the cancel path: long enough for the LLM to dispatch and
    cancel within the window. Never returns when cancelled (the
    background workflow's cancel interrupts the sleep).

    :param label: Text to echo back.
    :param seconds: How long to sleep before returning.
    :returns: ``f"SLEEP_LABEL_DONE[{label}]"`` if uninterrupted.
    """
    time.sleep(seconds)
    return f"SLEEP_LABEL_DONE[{label}]"
