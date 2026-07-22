"""C-2853: native harnesses must not silently drop system_prompt."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

import pytest

from omnigent.inner.executor import ExecutorError, Message
from omnigent.inner.native_prompt_delivery import note_native_system_prompt


SENTINEL = "OMNIGENT_PROMPT_SENTINEL_C2853_UNIQUE_7f3a9c"


def test_note_warns_when_prompt_not_applied(caplog: pytest.LogCaptureFixture) -> None:
    """Non-empty prompt without apply logs a warning (fail-loud phase 1)."""
    caplog.set_level(logging.WARNING)
    mode = note_native_system_prompt("claude-native", SENTINEL, applied=False)
    assert mode == "warn"
    assert any("not applying" in r.message for r in caplog.records)
    assert any(SENTINEL not in r.message or "chars=" in r.message for r in caplog.records)


def test_note_empty_prompt_is_quiet(caplog: pytest.LogCaptureFixture) -> None:
    """Empty prompt does not warn."""
    caplog.set_level(logging.WARNING)
    note_native_system_prompt("claude-native", "   ", applied=False)
    assert not any("not applying" in r.message for r in caplog.records)


def test_note_strict_raises() -> None:
    """strict_prompt / OMNIGENT_STRICT_PROMPT fails fast."""
    with pytest.raises(ValueError, match="not applying"):
        note_native_system_prompt("codex-native", SENTINEL, applied=False, strict=True)


def test_note_applied_skips_warn(caplog: pytest.LogCaptureFixture) -> None:
    """Verified apply path does not warn."""
    caplog.set_level(logging.WARNING)
    mode = note_native_system_prompt("claude-native", SENTINEL, applied=True)
    assert mode == "apply"
    assert not any("not applying" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_claude_native_run_turn_warns_on_dropped_prompt(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Any,
) -> None:
    """ClaudeNativeExecutor warns instead of silently discarding prompt."""
    from omnigent.inner import claude_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir()
    monkeypatch.setenv(mod.BRIDGE_DIR_ENV_VAR, str(bridge))
    # Avoid real tmux: force inactive session so turn ends after prompt note.
    monkeypatch.setattr(mod, "_session_is_active", lambda *_a, **_k: False)

    caplog.set_level(logging.WARNING)
    exe = mod.ClaudeNativeExecutor(bridge_dir=bridge)
    events: list[object] = []
    async for ev in exe.run_turn(
        messages=[Message(role="user", content="hi")],
        tools=[],
        system_prompt=SENTINEL,
        config=None,
    ):
        events.append(ev)
    assert any("not applying" in r.message for r in caplog.records)
    assert events  # inactive session error after warn


@pytest.mark.asyncio
async def test_claude_native_strict_prompt_yields_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Any,
) -> None:
    """With OMNIGENT_STRICT_PROMPT=1, dropped prompt becomes ExecutorError."""
    from omnigent.inner import claude_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir()
    monkeypatch.setenv("OMNIGENT_STRICT_PROMPT", "1")
    monkeypatch.setenv(mod.BRIDGE_DIR_ENV_VAR, str(bridge))
    monkeypatch.setattr(mod, "_session_is_active", lambda *_a, **_k: True)

    exe = mod.ClaudeNativeExecutor(bridge_dir=bridge)
    events: list[object] = []
    async for ev in exe.run_turn(
        messages=[Message(role="user", content="hi")],
        tools=[],
        system_prompt=SENTINEL,
        config=None,
    ):
        events.append(ev)
    assert len(events) == 1
    assert isinstance(events[0], ExecutorError)
    assert "not applying" in events[0].message
