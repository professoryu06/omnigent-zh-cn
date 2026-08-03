"""C-2853 phase 2 rework: builder capture for fresh/resume/fork boundaries.

Exercises ``_auto_create_codex_terminal`` with real AgentSpec/ResolvedSpec
and captures ``build_codex_native_server(..., developer_instructions=)``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest

from omnigent.runner.app import (
    ResolvedSpec,
    _codex_native_developer_instructions,
)
from omnigent.spec.types import AgentSpec, ExecutorSpec

SENTINEL = "OMNIGENT_PROMPT_SENTINEL_C2853_PHASE2_7f3a9c"


def _agent_spec_with_instructions(text: str = SENTINEL) -> AgentSpec:
    return AgentSpec(
        spec_version=1,
        name="prompt_probe",
        instructions=text,
        executor=ExecutorSpec(model="gpt-5.4-mini", config={"harness": "codex-native"}),
    )


def test_spec_instructions_extracted_for_fresh_thread() -> None:
    """Non-empty instructions from AgentSpec are extracted for fresh threads."""
    assert _codex_native_developer_instructions(_agent_spec_with_instructions()) == SENTINEL


def test_spec_instructions_none_for_empty() -> None:
    """Empty/whitespace/None instructions return None."""
    assert _codex_native_developer_instructions(_agent_spec_with_instructions("   ")) is None
    bare = AgentSpec(
        spec_version=1,
        name="n",
        instructions=None,
        executor=ExecutorSpec(model="gpt-5.4-mini"),
    )
    assert _codex_native_developer_instructions(bare) is None
    assert _codex_native_developer_instructions(_agent_spec_with_instructions("")) is None


def test_spec_instructions_none_for_non_string() -> None:
    """Non-string instructions return None."""
    spec = MagicMock()
    spec.instructions = 12345
    assert _codex_native_developer_instructions(spec) is None


def test_spec_instructions_none_when_no_spec() -> None:
    """None spec returns None."""
    assert _codex_native_developer_instructions(None) is None


def test_spec_instructions_from_resolved_wrapper() -> None:
    """ResolvedSpec unwraps to AgentSpec instructions."""
    wrapped = ResolvedSpec(spec=_agent_spec_with_instructions(), workdir=Path("/tmp"))
    assert _codex_native_developer_instructions(wrapped) == SENTINEL


async def _capture_developer_instructions(
    *,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    snapshot: dict[str, Any],
    agent_spec: AgentSpec | ResolvedSpec | None,
) -> Any:
    """Run ``_auto_create_codex_terminal`` far enough to capture builder kwargs."""
    import omnigent.codex_native_bridge as codex_native_bridge
    import omnigent.runner.app as runner_app_mod

    session_id = snapshot.get("id") or "conv_prompt_capture"
    monkeypatch.setattr(codex_native_bridge, "_BRIDGE_ROOT", tmp_path / "codex-bridge")
    monkeypatch.setenv("OMNIGENT_RUNNER_WORKSPACE", str(tmp_path / "workspace"))
    monkeypatch.setenv("RUNNER_SERVER_URL", "http://ap.example")
    monkeypatch.delenv("DATABRICKS_CONFIG_PROFILE", raising=False)
    monkeypatch.setattr("omnigent.runner._entry._make_auth_token_factory", lambda: None)
    monkeypatch.setattr(
        "omnigent.inner.codex_executor._find_codex_cli",
        lambda: "/usr/bin/codex",
    )
    monkeypatch.setattr(
        "omnigent.codex_native_app_server.resolve_native_codex_launch",
        lambda **_k: type(
            "L",
            (),
            {"model": "gpt-5.4-mini", "profile": None, "config_overrides": []},
        )(),
    )
    monkeypatch.setattr(
        "omnigent.codex_native_app_server.codex_session_meta_model_provider",
        lambda _launch: None,
    )
    monkeypatch.setattr(
        "omnigent.inner.codex_executor.populate_codex_skills_from_bundle",
        lambda *_a, **_k: None,
    )
    monkeypatch.setattr(
        "omnigent.codex_native_app_server.codex_terminal_env",
        lambda _s: {},
    )
    monkeypatch.setattr(
        "omnigent.codex_native_app_server.build_codex_remote_args",
        lambda **_k: ["resume", "--remote", "ws://x"],
    )

    class _SnapshotClient:
        async def get(self, url: str, **kwargs: Any) -> httpx.Response:
            if "/items" in url:
                return httpx.Response(
                    200,
                    json={"data": [], "has_more": False},
                    request=httpx.Request("GET", url),
                )
            return httpx.Response(
                200,
                json=snapshot,
                request=httpx.Request("GET", url),
            )

        async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
            return httpx.Response(200, json={}, request=httpx.Request("PATCH", url))

    build_calls: list[dict[str, Any]] = []

    class _FakeAppServer:
        codex_path = "/usr/bin/codex"
        env: dict[str, str] = {}
        config_overrides: list[str] = []
        listen_url: str | None = None

        def __init__(self) -> None:
            self.codex_home = tmp_path / "codex-home"
            self.started = False

        async def start(self) -> None:
            self.started = True

        async def close(self) -> None:
            return None

    fake = _FakeAppServer()

    def _fake_build(**kwargs: Any) -> _FakeAppServer:
        build_calls.append(kwargs)
        fake.codex_home = kwargs["codex_home"]
        return fake

    monkeypatch.setattr(
        "omnigent.codex_native_app_server.build_codex_native_server",
        _fake_build,
    )
    # Default: fork clone fails (fallback). Tests may override before calling.

    async def _ensure_rollout(*_a: Any, **_k: Any) -> Path | None:
        return None

    monkeypatch.setattr(
        "omnigent.codex_native._ensure_local_codex_resume_rollout",
        _ensure_rollout,
    )
    monkeypatch.setattr(
        "omnigent.codex_native._mint_codex_thread_id",
        lambda: "minted-thread-id",
    )

    class _FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

        async def connect(self) -> None:
            return None

        async def close(self) -> None:
            return None

    monkeypatch.setattr(
        "omnigent.codex_native_app_server.CodexAppServerClient",
        _FakeClient,
    )

    async def _preload(*_a: Any, **_k: Any) -> None:
        return None

    monkeypatch.setattr(
        "omnigent.codex_native_app_server.preload_codex_thread_for_resume",
        _preload,
    )

    class _Reg:
        async def launch_auxiliary_terminal(self, **kwargs: Any) -> Any:
            raise RuntimeError("stop-after-builder-capture")

    async def _no_forwarder(*_a: Any, **_k: Any) -> None:
        return None

    monkeypatch.setattr(runner_app_mod, "_cancel_auto_forwarder_task", _no_forwarder)
    runner_app_mod._AUTO_CODEX_APP_SERVERS.pop(session_id, None)

    try:
        await runner_app_mod._auto_create_codex_terminal(
            session_id,
            _Reg(),  # type: ignore[arg-type]
            lambda *_a, **_k: None,
            agent_spec=agent_spec,
            server_client=_SnapshotClient(),  # type: ignore[arg-type]
        )
    except RuntimeError as exc:
        if "stop-after-builder-capture" not in str(exc) and not build_calls:
            raise
    except Exception:
        if not build_calls:
            raise
    assert build_calls, "build_codex_native_server was not called"
    return build_calls[0].get("developer_instructions")


@pytest.mark.asyncio
async def test_builder_fresh_non_fork_receives_sentinel(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """True fresh non-fork launch passes developer_instructions."""
    di = await _capture_developer_instructions(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        snapshot={
            "id": "conv_fresh",
            "workspace": str(tmp_path / "ws"),
            "external_session_id": None,
        },
        agent_spec=_agent_spec_with_instructions(),
    )
    assert di == SENTINEL


@pytest.mark.asyncio
async def test_builder_resume_receives_none(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resume with external_session_id must not pass instructions."""
    di = await _capture_developer_instructions(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        snapshot={
            "id": "conv_resume",
            "workspace": str(tmp_path / "ws"),
            "external_session_id": "thread-resume-1",
            "terminal_launch_args": [],
        },
        agent_spec=_agent_spec_with_instructions(),
    )
    assert di is None


@pytest.mark.asyncio
async def test_builder_fork_success_receives_none(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Successful fork clone path must not pass instructions."""
    import omnigent.codex_native as codex_native_mod
    from omnigent.stores.conversation_store import (
        FORK_SOURCE_EXTERNAL_SESSION_LABEL_KEY,
        FORK_SOURCE_LABEL_KEY,
    )

    monkeypatch.setattr(
        codex_native_mod,
        "_clone_codex_rollout",
        lambda **_k: tmp_path / "cloned-rollout.jsonl",
    )
    (tmp_path / "cloned-rollout.jsonl").write_text("{}", encoding="utf-8")

    di = await _capture_developer_instructions(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        snapshot={
            "id": "conv_fork_ok",
            "workspace": str(tmp_path / "ws"),
            "external_session_id": None,
            "labels": {
                FORK_SOURCE_LABEL_KEY: "conv_source",
                FORK_SOURCE_EXTERNAL_SESSION_LABEL_KEY: "thread-source",
            },
        },
        agent_spec=_agent_spec_with_instructions(),
    )
    assert di is None


@pytest.mark.asyncio
async def test_builder_fork_fallback_fresh_still_none(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fork clone/rebuild failure that degrades to fresh launch still passes None."""
    import omnigent.codex_native as codex_native_mod
    from omnigent.stores.conversation_store import (
        FORK_SOURCE_EXTERNAL_SESSION_LABEL_KEY,
        FORK_SOURCE_LABEL_KEY,
    )

    monkeypatch.setattr(
        codex_native_mod,
        "_clone_codex_rollout",
        lambda **_k: (_ for _ in ()).throw(RuntimeError("clone fail")),
    )

    di = await _capture_developer_instructions(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        snapshot={
            "id": "conv_fork_fail",
            "workspace": str(tmp_path / "ws"),
            "external_session_id": None,
            "labels": {
                FORK_SOURCE_LABEL_KEY: "conv_source",
                FORK_SOURCE_EXTERNAL_SESSION_LABEL_KEY: "thread-source",
            },
        },
        agent_spec=_agent_spec_with_instructions(),
    )
    assert di is None
