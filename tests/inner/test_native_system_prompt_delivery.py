"""C-2853 phase 1: native harnesses must fail-loud when system_prompt is dropped.

This is **mitigation / fail-loud**, not proof that prompts are delivered.
Phase 2 (apply via safe per-CLI channels) remains open.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from omnigent.inner.executor import Executor, ExecutorError, Message
from omnigent.inner.native_prompt_delivery import (
    note_native_system_prompt,
    strict_prompt_enabled,
)

SENTINEL = "OMNIGENT_PROMPT_SENTINEL_C2853_UNIQUE_7f3a9c"


def _assert_logs_never_contain_sentinel(caplog: pytest.LogCaptureFixture) -> None:
    """Prompt body must never appear in log records."""
    assert all(SENTINEL not in r.message for r in caplog.records), (
        "system_prompt body leaked into logs: "
        + "; ".join(r.message for r in caplog.records if SENTINEL in r.message)
    )


# ── helper unit tests ──────────────────────────────────────────────


def test_note_warns_when_prompt_not_applied(caplog: pytest.LogCaptureFixture) -> None:
    """Non-empty prompt without apply logs a warning (phase-1 fail-loud)."""
    caplog.set_level(logging.WARNING)
    mode = note_native_system_prompt("claude-native", SENTINEL, applied=False)
    assert mode == "warn"
    warn_records = [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert any("not applying" in r.message for r in warn_records)
    assert any("chars=" in r.message for r in warn_records)
    _assert_logs_never_contain_sentinel(caplog)


def test_note_empty_prompt_is_quiet(caplog: pytest.LogCaptureFixture) -> None:
    """Empty prompt does not warn."""
    caplog.set_level(logging.WARNING)
    note_native_system_prompt("claude-native", "   ", applied=False)
    assert not any("not applying" in r.message for r in caplog.records)


def test_note_strict_env_raises(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """OMNIGENT_STRICT_PROMPT=1 fails fast without logging the body."""
    monkeypatch.setenv("OMNIGENT_STRICT_PROMPT", "1")
    assert strict_prompt_enabled() is True
    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError, match="not applying"):
        note_native_system_prompt("codex-native", SENTINEL, applied=False)
    _assert_logs_never_contain_sentinel(caplog)


def test_note_applied_skips_warn(caplog: pytest.LogCaptureFixture) -> None:
    """Verified apply path does not warn."""
    caplog.set_level(logging.WARNING)
    mode = note_native_system_prompt("claude-native", SENTINEL, applied=True)
    assert mode == "apply"
    assert not any("not applying" in r.message for r in caplog.records)


# ── per-executor fail-loud wiring ──────────────────────────────────


def _user_messages() -> list[Message]:
    return [Message(role="user", content="hi")]


async def _collect_turn(
    exe: Executor,
    *,
    system_prompt: str,
) -> list[object]:
    events: list[object] = []
    async for ev in exe.run_turn(
        messages=_user_messages(),
        tools=[],
        system_prompt=system_prompt,
        config=None,
    ):
        events.append(ev)
    return events


def _make_claude(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import claude_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.BRIDGE_DIR_ENV_VAR, str(bridge))
    monkeypatch.setattr(mod, "_session_is_active", lambda *_a, **_k: False)
    monkeypatch.setattr(
        mod,
        "inject_user_message",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("inject after fail-loud")),
    )
    return mod.ClaudeNativeExecutor(bridge_dir=bridge)


def _make_cursor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import cursor_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.BRIDGE_DIR_ENV_VAR, str(bridge))
    inject_calls: list[str] = []

    def _inject(*_a: Any, **_k: Any) -> None:
        inject_calls.append("inject")
        raise RuntimeError("blocked inject")

    monkeypatch.setattr(mod, "inject_user_message", _inject)
    exe = mod.CursorNativeExecutor(bridge_dir=bridge)
    exe._inject_calls = inject_calls  # type: ignore[attr-defined]
    return exe


def _make_kiro(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import kiro_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.KIRO_NATIVE_BRIDGE_DIR_ENV_VAR, str(bridge))

    def _inject(*_a: Any, **_k: Any) -> None:
        raise RuntimeError("blocked inject")

    monkeypatch.setattr(mod, "inject_user_message", _inject)
    return mod.KiroNativeExecutor(bridge_dir=bridge)


def _make_hermes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import hermes_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.BRIDGE_DIR_ENV_VAR, str(bridge))
    monkeypatch.setattr(
        mod,
        "inject_user_message",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("blocked")),
    )
    return mod.HermesNativeExecutor(bridge_dir=bridge)


def _make_goose(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import goose_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.BRIDGE_DIR_ENV_VAR, str(bridge))
    monkeypatch.setattr(
        mod,
        "inject_user_message",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("blocked")),
    )
    return mod.GooseNativeExecutor(bridge_dir=bridge)


def _make_kimi(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import kimi_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.BRIDGE_DIR_ENV_VAR, str(bridge))
    monkeypatch.setattr(
        mod,
        "inject_user_message",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("blocked")),
    )
    return mod.KimiNativeExecutor(bridge_dir=bridge)


def _make_qwen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import qwen_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.BRIDGE_DIR_ENV_VAR, str(bridge))
    monkeypatch.setattr(mod, "wait_for_ready", lambda *_a, **_k: True)
    monkeypatch.setattr(mod, "submit_user_message", lambda *_a, **_k: None)
    return mod.QwenNativeExecutor(bridge_dir=bridge)


def _make_pi(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import pi_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.PI_NATIVE_BRIDGE_DIR_ENV_VAR, str(bridge))
    # Warn path continues into enqueue; keep it a no-op (do not raise).
    monkeypatch.setattr(mod, "enqueue_user_message", lambda *_a, **_k: None)
    monkeypatch.setattr(mod.PiNativeExecutor, "_refresh_auth_headers", lambda self: None)
    return mod.PiNativeExecutor(bridge_dir=bridge)


def _make_antigravity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import antigravity_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.ANTIGRAVITY_NATIVE_BRIDGE_DIR_ENV_VAR, str(bridge))

    async def _no_bridge_deliver(self: Any, text: str) -> str:
        del text
        return "Antigravity native bridge state is missing"

    monkeypatch.setattr(mod.AntigravityNativeExecutor, "_deliver", _no_bridge_deliver)
    return mod.AntigravityNativeExecutor(bridge_dir=bridge)


def _make_codex(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    from omnigent.inner import codex_native_executor as mod

    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    monkeypatch.setenv(mod.CODEX_NATIVE_BRIDGE_DIR_ENV_VAR, str(bridge))
    monkeypatch.setattr(mod, "read_bridge_state", lambda *_a, **_k: None)
    # Exit the 60s boot poll on the first iteration.
    monkeypatch.setattr(mod, "read_bridge_startup_error", lambda *_a, **_k: "forced-missing")

    async def _no_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(mod.asyncio, "sleep", _no_sleep)
    return mod.CodexNativeExecutor(bridge_dir=bridge)


def _make_native_server(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Executor:
    """opencode path: NativeServerHarness base used by OpenCodeNativeExecutor."""
    del tmp_path, monkeypatch
    from omnigent.native_server_harness import NativeServerHarness
    from omnigent.native_server_transport import NativePrompt

    class _Transport:
        async def send_prompt(self, session_id: str, prompt: Any) -> None:
            del session_id, prompt
            raise AssertionError("send_prompt after fail-loud")

        async def abort(self, session_id: str) -> None:
            del session_id

    async def _resolve() -> str | None:
        return "sess_test"

    def _build(content: Any) -> NativePrompt | None:
        text = content if isinstance(content, str) else "hi"
        return NativePrompt(text=str(text))

    return NativeServerHarness(
        harness_id="opencode-native",
        supports_enqueue=True,
        transport=_Transport(),  # type: ignore[arg-type]
        resolve_session_id=_resolve,
        build_prompt=_build,
        boot_poll_attempts=0,
        boot_poll_delay=0.0,
    )


# (harness_id, factory)
_NATIVE_CASES: list[tuple[str, Callable[[Path, pytest.MonkeyPatch], Executor]]] = [
    ("claude-native", _make_claude),
    ("cursor-native", _make_cursor),
    ("kiro-native", _make_kiro),
    ("hermes-native", _make_hermes),
    ("goose-native", _make_goose),
    ("kimi-native", _make_kimi),
    ("qwen-native", _make_qwen),
    ("pi-native", _make_pi),
    ("antigravity-native", _make_antigravity),
    ("codex-native", _make_codex),
    ("opencode-native", _make_native_server),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("harness_id,factory", _NATIVE_CASES, ids=[c[0] for c in _NATIVE_CASES])
async def test_native_executor_warns_on_dropped_prompt(
    harness_id: str,
    factory: Callable[[Path, pytest.MonkeyPatch], Executor],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Each native path warns when system_prompt is non-empty and not applied."""
    monkeypatch.delenv("OMNIGENT_STRICT_PROMPT", raising=False)
    caplog.set_level(logging.WARNING)
    exe = factory(tmp_path, monkeypatch)
    await _collect_turn(exe, system_prompt=SENTINEL)
    warn_records = [r for r in caplog.records if "not applying" in r.message]
    assert warn_records, f"{harness_id}: expected fail-loud warning"
    assert any(harness_id in r.message or "native" in r.message for r in warn_records)
    _assert_logs_never_contain_sentinel(caplog)


@pytest.mark.asyncio
@pytest.mark.parametrize("harness_id,factory", _NATIVE_CASES, ids=[c[0] for c in _NATIVE_CASES])
async def test_native_executor_strict_errors_before_inject(
    harness_id: str,
    factory: Callable[[Path, pytest.MonkeyPatch], Executor],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Strict mode yields ExecutorError and never logs the prompt body.

    Fail-fast happens in note_native_system_prompt before user-message inject.
    """
    monkeypatch.setenv("OMNIGENT_STRICT_PROMPT", "1")
    caplog.set_level(logging.ERROR)
    exe = factory(tmp_path, monkeypatch)
    events = await _collect_turn(exe, system_prompt=SENTINEL)
    assert events, f"{harness_id}: expected at least one event"
    assert isinstance(events[0], ExecutorError), (
        f"{harness_id}: expected ExecutorError first, got {type(events[0])}: {events[0]!r}"
    )
    assert "not applying" in events[0].message
    assert SENTINEL not in events[0].message
    # Only the fail-loud error event — no subsequent inject-driven turn events.
    assert len(events) == 1, f"{harness_id}: expected sole ExecutorError, got {events!r}"
    _assert_logs_never_contain_sentinel(caplog)


def test_native_executor_modules_wire_shared_helper() -> None:
    """Every patched native module imports the shared fail-loud helper.

    Complements run_turn tests: proves wiring is via the shared contract
    module (not a one-off per-file logger call).
    """
    import importlib

    modules = [
        "omnigent.inner.antigravity_native_executor",
        "omnigent.inner.claude_native_executor",
        "omnigent.inner.codex_native_executor",
        "omnigent.inner.cursor_native_executor",
        "omnigent.inner.goose_native_executor",
        "omnigent.inner.hermes_native_executor",
        "omnigent.inner.kimi_native_executor",
        "omnigent.inner.kiro_native_executor",
        "omnigent.inner.pi_native_executor",
        "omnigent.inner.qwen_native_executor",
        "omnigent.native_server_harness",
    ]
    for name in modules:
        mod = importlib.import_module(name)
        assert hasattr(mod, "note_native_system_prompt"), (
            f"{name} must import note_native_system_prompt for fail-loud wiring"
        )
        assert mod.note_native_system_prompt is note_native_system_prompt
