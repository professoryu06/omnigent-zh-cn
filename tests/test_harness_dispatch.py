"""Harness dispatch: bare codex stays SDK; only codex-native is native TUI."""

from __future__ import annotations

from omnigent.harness_aliases import (
    canonicalize_harness,
    is_native_harness,
    native_terminal_name,
    resolve_harness_dispatch,
)


def test_bare_codex_dispatch_is_sdk_not_native() -> None:
    """``harness: codex`` maps to codex_harness / CodexExecutor, not native TUI."""
    d = resolve_harness_dispatch("codex")
    assert d.canonical_harness == "codex"
    assert d.is_native is False
    assert d.dispatch_mode == "sdk"
    assert d.module == "omnigent.inner.codex_harness"
    assert native_terminal_name("codex") is None
    assert is_native_harness("codex") is False


def test_codex_native_dispatch_is_native_terminal() -> None:
    """Only explicit ``codex-native`` may use CodexNativeExecutor / TUI."""
    d = resolve_harness_dispatch("codex-native")
    assert d.canonical_harness == "codex-native"
    assert d.is_native is True
    assert d.dispatch_mode == "native"
    assert d.module == "omnigent.inner.codex_native_harness"
    assert native_terminal_name("codex-native") == "codex"


def test_codex_never_aliases_to_codex_native() -> None:
    """No codex → codex-native alias (would reintroduce Windows tmux/PTY)."""
    assert canonicalize_harness("codex") == "codex"
    assert canonicalize_harness("codex") != "codex-native"
    d = resolve_harness_dispatch("codex", override=None)
    assert d.canonical_harness == "codex"


def test_harness_override_wins_in_dispatch() -> None:
    """Per-session override replaces the spec harness in resolve_harness_dispatch."""
    d = resolve_harness_dispatch("claude-sdk", override="codex")
    assert d.raw_harness == "codex"
    assert d.canonical_harness == "codex"
    assert d.is_native is False
