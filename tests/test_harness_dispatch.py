"""Harness dispatch registry tests (referenced by CODEX_TASK_GROK_NATIVE_01 Task 4).

Verifies the runtime dispatch seam every harness subprocess goes through:

- ``_HARNESS_MODULES`` resolves canonical harness ids to importable modules
  (aliases included).
- the grok-native module exports ``create_app()`` (the harness contract the
  shared ``_runner`` invokes).
"""

from __future__ import annotations

import importlib
from collections.abc import Iterator
from pathlib import Path

import pytest

import omnigent.harness_plugins as hp
from omnigent.runtime.harnesses import _HARNESS_MODULES


@pytest.fixture(autouse=True)
def _reset_plugin_state() -> Iterator[None]:
    hp.reset_plugin_state_for_tests()
    yield
    hp.reset_plugin_state_for_tests()


def test_harness_modules_cover_registered_harnesses() -> None:
    # open-responses is resolved via an alternate path and legitimately has no
    # _HARNESS_MODULES entry; every other valid harness must dispatch.
    skip = frozenset({"open-responses"})
    for harness in hp.valid_harnesses() - skip:
        assert harness in _HARNESS_MODULES, harness


def test_grok_native_resolves_to_harness_module() -> None:
    assert _HARNESS_MODULES["grok-native"] == "omnigent.inner.grok_native_harness"


def test_every_harness_module_exports_create_app() -> None:
    for harness, module_path in _HARNESS_MODULES.items():
        module = importlib.import_module(module_path)
        assert callable(getattr(module, "create_app", None)), module_path


def test_grok_native_harness_app_builds() -> None:
    from omnigent.inner.grok_native_harness import create_app

    app = create_app()
    assert app is not None
    # The wrap is the shared ExecutorAdapter (FastAPI app with the harness API).
    assert app.title or app.version or app.routes


def test_harness_module_paths_are_repo_local() -> None:
    """Every built-in harness module must live under the omnigent package."""
    for harness, module_path in _HARNESS_MODULES.items():
        if harness.startswith("acp:"):
            continue
        assert module_path.startswith("omnigent."), f"{harness}: {module_path}"
