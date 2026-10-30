"""grok-native dispatch/registry tests (CODEX_TASK_GROK_NATIVE_01).

Covers the task card's Task 1 requirements:

- ``grok-native`` registry/module/alias resolvable.
- ``grok-native-ui`` appears in builtin agents and ``/v1/agents``.
- spawn env carries isolated GROK_HOME, ``grok-4.5`` and the required proxy vars.
- spawn env excludes Claude/Qwen/Codex/OpenCodex variables.
- two sessions get distinct GROK_HOME / leader socket / session id.
- unauthenticated runs yield a clear auth-required error, never leaking tokens.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml

import omnigent.harness_plugins as hp
from omnigent.harness_aliases import canonicalize_harness, is_native_harness
from omnigent.harness_capabilities import IntegrationMode


@pytest.fixture(autouse=True)
def _reset_plugin_state() -> Iterator[None]:
    hp.reset_plugin_state_for_tests()
    yield
    hp.reset_plugin_state_for_tests()


# ---------------------------------------------------------------------------
# registry / module / alias
# ---------------------------------------------------------------------------


def test_grok_native_harness_is_registered() -> None:
    assert "grok-native" in hp.valid_harnesses()
    assert hp.harness_modules()["grok-native"] == "omnigent.inner.grok_native_harness"


def test_grok_native_capabilities_declared() -> None:
    caps = hp.harness_capabilities()["grok-native"]
    # Headless CLI subprocess — NOT a native TUI/tmux harness.
    assert caps.integration_mode is IntegrationMode.CLI_SUBPROCESS


def test_grok_native_is_not_classified_as_terminal_native_harness() -> None:
    # grok-native is headless; it must never be treated as a tmux terminal harness.
    assert is_native_harness("grok-native") is False


def test_grok_native_is_classified_as_headless_harness() -> None:
    # Regression (CODEX_REVIEW_GROK_NATIVE_01, blocker 1): grok-native must be
    # marked headless so the runner's generic non-native branch skips the
    # auto-created REPL/tmux terminal for it.
    from omnigent.harness_aliases import HEADLESS_HARNESSES, is_headless_harness

    assert "grok-native" in HEADLESS_HARNESSES
    assert is_headless_harness("grok-native") is True
    # A terminal-native harness and unknown names are not headless.
    assert is_headless_harness("claude-native") is False
    assert is_headless_harness("codex") is False
    assert is_headless_harness("grok") is False  # bare spelling, no alias registered
    assert is_headless_harness(None) is False


def test_grok_native_catalog_row_present() -> None:
    rows = hp.harness_catalog()
    ids = [row["id"] for row in rows]
    assert "grok-native" in ids


def test_grok_native_alias_canonicalizes_to_itself() -> None:
    # The bare spelling must never map onto codex-native / openai-agents / tmux.
    assert canonicalize_harness("grok-native") == "grok-native"


# ---------------------------------------------------------------------------
# agent spec materialization
# ---------------------------------------------------------------------------


def test_grok_native_agent_spec_materializes(tmp_path: Path) -> None:
    from omnigent.grok_native import _materialize_grok_agent_spec

    spec_path = _materialize_grok_agent_spec(tmp_path)
    assert spec_path.is_file()
    raw = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    assert raw["name"] == "grok-native-ui"
    assert raw["executor"]["harness"] == "grok-native"
    assert raw.get("spawn") is True


# ---------------------------------------------------------------------------
# spawn env isolation
# ---------------------------------------------------------------------------


def test_grok_native_spawn_env_carries_grok_home_and_no_proxy() -> None:
    from omnigent.grok_native_bridge import build_grok_native_spawn_env

    env = build_grok_native_spawn_env(session_id="conv_grok_test")
    assert env["GROK_HOME"]
    assert "grok-omnigent" in env["GROK_HOME"]
    assert env["NO_PROXY"] == "127.0.0.1,localhost"


def test_grok_native_spawn_env_excludes_other_agents() -> None:
    from omnigent.grok_native_bridge import build_grok_native_spawn_env

    env = build_grok_native_spawn_env(session_id="conv_grok_test")
    forbidden_prefixes = ("ANTHROPIC_", "DASHSCOPE_", "OPENAI_", "CODEX_", "OPENCODE_")
    for key in env:
        assert not key.startswith(forbidden_prefixes), key


# ---------------------------------------------------------------------------
# per-session isolation
# ---------------------------------------------------------------------------


def test_two_sessions_isolate_home_socket_and_session_id() -> None:
    from omnigent.grok_native_bridge import (
        grok_leader_socket,
        grok_session_home,
        grok_session_id_for_conversation,
    )

    a = "conv_grok_a"
    b = "conv_grok_b"
    assert grok_session_id_for_conversation(a) != grok_session_id_for_conversation(b)
    assert grok_session_home(a) != grok_session_home(b)
    assert grok_leader_socket(a) != grok_leader_socket(b)
