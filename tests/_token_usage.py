"""Per-test nodeid attribution for the token-usage auto-recorder.

The recording + JSON-writing logic lives in
:mod:`omnigent.llms._usage_observer`, which auto-activates whenever
``OMNIGENT_TOKEN_USAGE_JSON`` is set in the environment (including in
subprocesses spawned by tests). This plugin's only job is to mark
which test is currently running so LLM calls get attributed to the
right ``nodeid``: both in-process calls (via a module global) and
calls fired in spawned server / runner / harness subprocesses (via
the per-worker sidecar file that ``set_current_test`` publishes).

See the observer module's docstring for the file format and how
multi-process writes are merged at the workflow level.
"""

from __future__ import annotations

from typing import Any

import pytest

from omnigent.llms import _usage_observer


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None) -> Any:
    _usage_observer.set_current_test(item.nodeid)
    try:
        yield
    finally:
        _usage_observer.set_current_test(None)
