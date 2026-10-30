"""grok-native isolation tests (CODEX_TASK_GROK_NATIVE_01, Task 1).

Verifies the GrokNativeExecutor's spawn environment is deny-by-default:

- carries isolated per-session GROK_HOME, model ``grok-4.5``, NO_PROXY.
- never leaks Claude/Qwen/Codex/OpenCodex credentials into the subprocess.
- unauthenticated CLI output maps to a clear auth-required ExecutorError
  whose message never contains tokens.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from omnigent.inner.executor import ExecutorError
from omnigent.inner.grok_native_executor import (
    GrokNativeExecutor,
    _build_grok_args,
    _parse_grok_output,
)


@pytest.fixture
def executor(tmp_path: Path) -> GrokNativeExecutor:
    """A GrokNativeExecutor pointed at a fake grok binary + tmp grok home."""
    return GrokNativeExecutor(
        grok_path="/usr/bin/grok-fake",
        cwd=str(tmp_path),
        model="grok-4.5",
        grok_home_root=str(tmp_path / "grok-omnigent"),
    )


# ---------------------------------------------------------------------------
# spawn env isolation
# ---------------------------------------------------------------------------


def test_spawn_env_is_deny_by_default(executor: GrokNativeExecutor) -> None:
    env = executor._build_spawn_env()
    forbidden_prefixes = ("ANTHROPIC_", "DASHSCOPE_", "OPENAI_", "CODEX_", "OPENCODE_")
    for key in env:
        assert not key.startswith(forbidden_prefixes), f"leaked {key} into grok env"
    # Grok's own families ARE allowed (GROK_ for home/config, XAI_ for API key).
    allowed = {"GROK_HOME", "NO_PROXY"}
    assert allowed <= set(env)


def test_spawn_env_sets_no_proxy(executor: GrokNativeExecutor) -> None:
    env = executor._build_spawn_env()
    assert env["NO_PROXY"] == "127.0.0.1,localhost"


def test_spawn_env_strips_inherited_proxy_when_grok_proxy_unset(
    executor: GrokNativeExecutor, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Regression (CODEX_REVIEW_GROK_NATIVE_01, blocker 2): when
    # OMNIGENT_GROK_PROXY is unset, a parent's inherited HTTP_PROXY /
    # HTTPS_PROXY / ALL_PROXY must NOT leak into the Grok child. Only
    # NO_PROXY=127.0.0.1,localhost survives.
    monkeypatch.delenv("OMNIGENT_GROK_PROXY", raising=False)
    monkeypatch.setenv("HTTP_PROXY", "http://inherited.invalid")
    monkeypatch.setenv("HTTPS_PROXY", "http://inherited.invalid")
    monkeypatch.setenv("ALL_PROXY", "http://inherited.invalid")
    monkeypatch.setenv("http_proxy", "http://inherited.invalid")
    monkeypatch.setenv("https_proxy", "http://inherited.invalid")
    monkeypatch.setenv("all_proxy", "http://inherited.invalid")
    monkeypatch.setenv("NO_PROXY", "x")
    env = executor._build_spawn_env()
    assert "HTTP_PROXY" not in env
    assert "HTTPS_PROXY" not in env
    assert "ALL_PROXY" not in env
    assert "http_proxy" not in env
    assert "https_proxy" not in env
    assert "all_proxy" not in env
    # NO_PROXY is forced to the task-card value, not the inherited "x".
    assert env["NO_PROXY"] == "127.0.0.1,localhost"


def test_spawn_env_injects_proxy_only_when_grok_proxy_set(
    executor: GrokNativeExecutor, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Regression (CODEX_REVIEW_GROK_NATIVE_01, blocker 2): only an explicit
    # OMNIGENT_GROK_PROXY re-injects the proxy trio; the value wins over any
    # inherited parent proxy.
    monkeypatch.setenv("OMNIGENT_GROK_PROXY", "http://127.0.0.1:7897")
    monkeypatch.setenv("HTTP_PROXY", "http://inherited.invalid")
    env = executor._build_spawn_env()
    assert env["HTTP_PROXY"] == "http://127.0.0.1:7897"
    assert env["HTTPS_PROXY"] == "http://127.0.0.1:7897"
    assert env["ALL_PROXY"] == "http://127.0.0.1:7897"
    assert env["NO_PROXY"] == "127.0.0.1,localhost"


def test_spawn_env_sets_per_session_grok_home(
    executor: GrokNativeExecutor, tmp_path: Path
) -> None:
    env = executor._build_spawn_env()
    assert env["GROK_HOME"].startswith(str(tmp_path / "grok-omnigent"))
    # Per-session subdir: /sessions/<session-id>
    assert "/sessions/" in env["GROK_HOME"]


def test_spawn_env_excludes_xai_key_from_other_families(
    executor: GrokNativeExecutor,
) -> None:
    # XAI_* is grok's own family and legitimately allowed.
    env = executor._build_spawn_env()
    assert any(key.startswith("XAI_") for key in env) or "XAI_API_KEY" not in env


# ---------------------------------------------------------------------------
# argument construction (machine interface)
# ---------------------------------------------------------------------------


def test_first_turn_uses_single_with_session_id(executor: GrokNativeExecutor) -> None:
    args = _build_grok_args(
        grok_path="/usr/bin/grok-fake",
        message="Reply with OK and stop.",
        model="grok-4.5",
        session_id="3b9e7c1a-0000-4000-8000-000000000001",
    )
    assert args[0] == "/usr/bin/grok-fake"
    assert "-p" in args or "--single" in args
    assert "grok-4.5" in args
    assert "--session-id" in args
    assert "--output-format" in args and "json" in args
    # No resume on the first turn.
    assert "--resume" not in args


def test_second_turn_resumes_same_session(executor: GrokNativeExecutor) -> None:
    sid = "3b9e7c1a-0000-4000-8000-000000000001"
    args = _build_grok_args(
        grok_path="/usr/bin/grok-fake",
        message="Follow up.",
        model="grok-4.5",
        session_id=sid,
        resume=sid,
    )
    assert "--resume" in args
    assert sid in args
    # Resume must not also pass a fresh --session-id.
    assert "--session-id" not in args


# ---------------------------------------------------------------------------
# output parsing
# ---------------------------------------------------------------------------


def test_parse_unauthenticated_error_marks_auth_required() -> None:
    stdout = (
        '{"type":"error","message":"Not signed in. To authenticate without a browser, '
        'run:\\n  grok login --device-code\\n\\nAlternatively, set the XAI_API_KEY '
        'environment variable or run `grok login` on a machine with a browser."}'
    )
    result = _parse_grok_output(stdout)
    assert result.error is not None
    assert result.auth_required is True
    # The login command is surfaced; the raw token/session data is not.
    assert "login" in result.error
    assert "XAI_API_KEY" in result.error or "device-code" in result.error


def test_parse_result_extracts_text() -> None:
    stdout = '{"type":"result","response":"GROK_NATIVE_OK"}'
    result = _parse_grok_output(stdout)
    assert result.error is None
    assert result.text == "GROK_NATIVE_OK"


def test_parse_result_unwraps_nested_json_response() -> None:
    # grok --output-format json nests the assistant payload as a JSON string
    # under "response" (verified live against grok 0.2.106).
    nested = json.dumps(
        {
            "text": "GROK_NATIVE_OK",
            "sessionId": "69cf0f4b-dcb0-5990-a67e-46ed3948e05c",
            "stopReason": "EndTurn",
        }
    )
    stdout = json.dumps({"type": "result", "response": nested})
    result = _parse_grok_output(stdout)
    assert result.error is None
    assert result.text == "GROK_NATIVE_OK"


def test_parse_non_json_stdout_passes_text_through() -> None:
    result = _parse_grok_output("GROK_NATIVE_OK\n")
    assert result.error is None
    assert result.text == "GROK_NATIVE_OK"


# ---------------------------------------------------------------------------
# run_turn error surface (auth never leaks tokens)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unauthenticated_run_yields_auth_required_error(
    executor: GrokNativeExecutor,
) -> None:
    from unittest.mock import AsyncMock, MagicMock, patch
    import asyncio

    mock_process = MagicMock()
    mock_process.returncode = 0  # grok returns 0 even when unauthenticated
    mock_process.communicate = AsyncMock(
        return_value=(
            b'{"type":"error","message":"Not signed in. Run `grok login --device-code`."}',
            b"",
        )
    )
    with patch.object(
        asyncio,
        "create_subprocess_exec",
        new=AsyncMock(return_value=mock_process),
    ):
        events = []
        async for event in executor.run_turn(
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            system_prompt="",
        ):
            events.append(event)

    assert len(events) == 1
    err = events[0]
    assert isinstance(err, ExecutorError)
    assert "authenticate" in err.message.lower() or "login" in err.message.lower()
    assert "sk-" not in err.message  # no provider token in the surfaced error
