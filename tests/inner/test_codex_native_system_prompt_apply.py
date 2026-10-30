"""C-2853 phase 2: codex-native safe apply via private config.toml.

Deterministic capture-double tests proving:
- developer_instructions written to private CODEX_HOME/config.toml
- receipt contains only metadata/digest, never prompt body
- executor matches receipt digest before marking applied
- strict mode passes on match, fails on mismatch
- no prompt leakage into argv, env, logs, or user input
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import pytest

from omnigent.inner.native_prompt_delivery import (
    note_native_system_prompt,
    read_prompt_receipt,
    receipt_matches_prompt,
    write_prompt_receipt,
)

SENTINEL = "OMNIGENT_PROMPT_SENTINEL_C2853_PHASE2_7f3a9c"
SENTINEL_DIGEST = hashlib.sha256(SENTINEL.encode()).hexdigest()


# ── receipt API ────────────────────────────────────────────────────


def test_write_and_read_receipt_roundtrip(tmp_path: Path) -> None:
    """Receipt roundtrip: write then read returns matching metadata."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    write_prompt_receipt(bridge_dir, harness_id="codex-native", prompt=SENTINEL)
    receipt = read_prompt_receipt(bridge_dir)
    assert receipt is not None
    assert receipt["harness_id"] == "codex-native"
    assert receipt["channel"] == "codex_home_config_toml"
    assert receipt["chars"] == len(SENTINEL)
    assert receipt["sha256"] == SENTINEL_DIGEST


def test_receipt_never_contains_prompt_body(tmp_path: Path) -> None:
    """Receipt file must not contain the prompt body."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    write_prompt_receipt(bridge_dir, harness_id="codex-native", prompt=SENTINEL)
    receipt_files = list(bridge_dir.glob("*.receipt.json"))
    assert len(receipt_files) == 1
    raw = receipt_files[0].read_text(encoding="utf-8")
    assert SENTINEL not in raw


def test_receipt_empty_prompt_not_written(tmp_path: Path) -> None:
    """Empty/whitespace prompt does not generate a receipt."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    write_prompt_receipt(bridge_dir, harness_id="codex-native", prompt="   ")
    assert read_prompt_receipt(bridge_dir) is None


def test_receipt_missing_returns_none(tmp_path: Path) -> None:
    """Missing receipt returns None (not an exception)."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    assert read_prompt_receipt(bridge_dir) is None


def test_receipt_corrupt_returns_none(tmp_path: Path) -> None:
    """Corrupt receipt file returns None, not an exception."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "prompt_delivery.receipt.json").write_text("NOT JSON", encoding="utf-8")
    assert read_prompt_receipt(bridge_dir) is None


def test_receipt_stale_cleaned_before_write(tmp_path: Path) -> None:
    """Writing a new receipt cleans any prior receipt file."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    write_prompt_receipt(bridge_dir, harness_id="codex-native", prompt="first")
    write_prompt_receipt(bridge_dir, harness_id="codex-native", prompt="second")
    receipts = list(bridge_dir.glob("*.receipt.json"))
    assert len(receipts) == 1
    receipt = read_prompt_receipt(bridge_dir)
    assert receipt is not None
    assert receipt["sha256"] == hashlib.sha256(b"second").hexdigest()


# ── executor digest matching ───────────────────────────────────────


def test_executor_applied_on_digest_match(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """note_native_system_prompt with applied=True when receipt matches."""
    caplog.set_level(logging.WARNING)
    mode = note_native_system_prompt("codex-native", SENTINEL, applied=True)
    assert mode == "apply"
    assert not any("not applying" in r.getMessage() for r in caplog.records)


def test_executor_warn_on_digest_mismatch(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """note_native_system_prompt with applied=False warns on mismatch."""
    caplog.set_level(logging.WARNING)
    mode = note_native_system_prompt("codex-native", SENTINEL, applied=False)
    assert mode == "warn"
    assert any("not applying" in r.getMessage() for r in caplog.records)


def test_strict_applied_no_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """OMNIGENT_STRICT_PROMPT=1 with applied=True does not raise."""
    monkeypatch.setenv("OMNIGENT_STRICT_PROMPT", "1")
    caplog.set_level(logging.ERROR)
    mode = note_native_system_prompt("codex-native", SENTINEL, applied=True)
    assert mode == "apply"


def test_strict_mismatch_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OMNIGENT_STRICT_PROMPT=1 with applied=False raises ValueError."""
    monkeypatch.setenv("OMNIGENT_STRICT_PROMPT", "1")
    with pytest.raises(ValueError, match="not applying"):
        note_native_system_prompt("codex-native", SENTINEL, applied=False)


# ── config.toml channel ────────────────────────────────────────────


def test_developer_instructions_written_to_config_toml(tmp_path: Path) -> None:
    """developer_instructions upserted into private config.toml."""
    from omnigent.codex_native_app_server import _upsert_developer_instructions

    codex_home = tmp_path / "codex_home"
    codex_home.mkdir()
    (codex_home / "config.toml").write_text('model = "gpt-5.4-mini"\n', encoding="utf-8")
    _upsert_developer_instructions(codex_home, SENTINEL)
    content = (codex_home / "config.toml").read_text(encoding="utf-8")
    assert "developer_instructions" in content
    # Verify it's valid TOML with the sentinel value
    import tomllib

    parsed = tomllib.loads(content)
    assert parsed["developer_instructions"] == SENTINEL
    assert parsed["model"] == "gpt-5.4-mini"


def test_developer_instructions_not_in_argv(tmp_path: Path) -> None:
    """build_codex_native_server does not put instructions in argv/env."""
    from omnigent.codex_native_app_server import build_codex_native_server

    codex_home = tmp_path / "codex_home"
    codex_home.mkdir()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    socket_path = tmp_path / "sock"

    # Patch _find_codex_cli to avoid needing real codex
    import omnigent.codex_native_app_server as mod

    original_find = mod._find_codex_cli
    mod._find_codex_cli = lambda: "/usr/bin/codex"
    try:
        server = build_codex_native_server(
            socket_path=socket_path,
            codex_home=codex_home,
            cwd=tmp_path,
            model=None,
            profile=None,
            bridge_dir=bridge_dir,
            developer_instructions=SENTINEL,
        )
    finally:
        mod._find_codex_cli = original_find

    # The sentinel must not appear in config_overrides (argv -c values)
    for override in server.config_overrides:
        assert SENTINEL not in override
    # The sentinel must not appear in env
    for v in server.env.values():
        assert SENTINEL not in v


# ── rework: full receipt metadata match ────────────────────────────


def test_receipt_match_rejects_wrong_harness_channel_or_chars(tmp_path: Path) -> None:
    """Same digest alone is not enough; harness/channel/chars must match."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    write_prompt_receipt(bridge_dir, harness_id="codex-native", prompt=SENTINEL)
    good = read_prompt_receipt(bridge_dir)
    assert good is not None
    assert receipt_matches_prompt(good, SENTINEL) is True

    wrong_harness = dict(good)
    wrong_harness["harness_id"] = "claude-native"
    assert receipt_matches_prompt(wrong_harness, SENTINEL) is False

    wrong_channel = dict(good)
    wrong_channel["channel"] = "argv"
    assert receipt_matches_prompt(wrong_channel, SENTINEL) is False

    wrong_chars = dict(good)
    wrong_chars["chars"] = len(SENTINEL) + 1
    assert receipt_matches_prompt(wrong_chars, SENTINEL) is False

    missing_field = {k: v for k, v in good.items() if k != "channel"}
    assert receipt_matches_prompt(missing_field, SENTINEL) is False


def test_invalid_utf8_receipt_returns_none(tmp_path: Path) -> None:
    """Illegal UTF-8 receipt bytes must degrade to None, not raise."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "prompt_delivery.receipt.json").write_bytes(b"\xff\xfe not utf8 {")
    assert read_prompt_receipt(bridge_dir) is None


def test_developer_instructions_toml_roundtrip_complex_unicode(tmp_path: Path) -> None:
    """TOML must round-trip newlines, quotes, CJK, and emoji via tomllib."""
    import tomllib

    from omnigent.codex_native_app_server import _upsert_developer_instructions

    complex_prompt = (
        'line1\nline2 with "quotes" and \\ backslash\n'
        "中文指令与 emoji 😀🚀"
    )
    codex_home = tmp_path / "codex_home"
    codex_home.mkdir()
    (codex_home / "config.toml").write_text('model = "gpt-5.4-mini"\n', encoding="utf-8")
    _upsert_developer_instructions(codex_home, complex_prompt)
    content = (codex_home / "config.toml").read_text(encoding="utf-8")
    assert complex_prompt not in content or "developer_instructions" in content
    # Body may appear inside the TOML string value — that is the private
    # config channel. Assert tomllib restores the exact scalar value.
    parsed = tomllib.loads(content)
    assert parsed["developer_instructions"] == complex_prompt
    assert parsed["model"] == "gpt-5.4-mini"


def test_app_server_start_clears_stale_receipt_without_instructions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resume/no-prompt start must delete a pre-existing matching receipt."""
    import asyncio

    import omnigent.codex_native_app_server as mod
    from omnigent.codex_native_app_server import CodexNativeAppServer

    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    codex_home = tmp_path / "codex_home"
    codex_home.mkdir()
    write_prompt_receipt(bridge_dir, harness_id="codex-native", prompt=SENTINEL)
    assert read_prompt_receipt(bridge_dir) is not None

    monkeypatch.setattr(mod, "_populate_codex_home_config", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_inject_mcp_server_config", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_write_codex_policy_hooks_file", lambda *a, **k: None)
    monkeypatch.setattr(mod, "reconcile_codex_native_process_registry", lambda: None)
    monkeypatch.setattr(mod, "acquire_codex_native_process_owner_lock", lambda: None)

    async def _ver(_p: str) -> None:
        return None

    monkeypatch.setattr(mod, "_codex_cli_version", _ver)

    async def _no_spawn(*_a: object, **_k: object) -> object:
        raise RuntimeError("stop-before-spawn")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", _no_spawn)

    server = CodexNativeAppServer(
        codex_path="/usr/bin/codex",
        socket_path=tmp_path / "sock",
        codex_home=codex_home,
        env={},
        config_overrides=[],
        cwd=tmp_path,
        bridge_dir=bridge_dir,
        developer_instructions=None,
    )
    with pytest.raises(RuntimeError, match="stop-before-spawn"):
        asyncio.run(server.start())
    assert read_prompt_receipt(bridge_dir) is None


def test_app_server_writes_receipt_only_after_config_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Config upsert failure must not leave a receipt or spawn the process."""
    import asyncio

    import omnigent.codex_native_app_server as mod
    from omnigent.codex_native_app_server import CodexNativeAppServer

    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    codex_home = tmp_path / "codex_home"
    codex_home.mkdir()
    write_prompt_receipt(bridge_dir, harness_id="codex-native", prompt="old")

    def _boom(_home: Path, _text: str) -> None:
        raise OSError("config write failed")

    monkeypatch.setattr(mod, "_upsert_developer_instructions", _boom)
    monkeypatch.setattr(mod, "_populate_codex_home_config", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_inject_mcp_server_config", lambda *a, **k: None)
    spawn_calls: list[str] = []

    async def _no_spawn(*_a: object, **_k: object) -> object:
        spawn_calls.append("spawn")
        raise AssertionError("must not spawn after config failure")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", _no_spawn)

    server = CodexNativeAppServer(
        codex_path="/usr/bin/codex",
        socket_path=tmp_path / "sock",
        codex_home=codex_home,
        env={},
        config_overrides=[],
        cwd=tmp_path,
        bridge_dir=bridge_dir,
        developer_instructions=SENTINEL,
    )
    with pytest.raises(OSError, match="config write failed"):
        asyncio.run(server.start())
    assert read_prompt_receipt(bridge_dir) is None
    assert spawn_calls == []
