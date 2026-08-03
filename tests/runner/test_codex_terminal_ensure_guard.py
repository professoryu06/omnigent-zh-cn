"""BUG-2: bare ``harness: codex`` must not enter native Codex terminal create.

The ensure_native_terminal path must only refuse when the session harness is
*known* to be non-native-codex. Unresolved specs fail open (historical ensure
behavior for CLI resume / cold callers). Explicit ``codex-native`` still
auto-creates.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from omnigent.runner import create_runner_app
from omnigent.spec.types import AgentSpec, ExecutorSpec
from tests.runner.helpers import NullServerClient


def _spec(*, harness: str) -> AgentSpec:
    return AgentSpec(
        spec_version=1,
        name="controller",
        description="test",
        executor=ExecutorSpec(type="omnigent", config={"harness": harness, "model": "gpt-5.6-sol"}),
    )


async def _post_ensure(client: httpx.AsyncClient, session_id: str) -> httpx.Response:
    return await client.post(
        f"/v1/sessions/{session_id}/resources/terminals",
        json={
            "terminal": "codex",
            "session_key": "main",
            "ensure_native_terminal": True,
        },
    )


@pytest.mark.asyncio
async def test_ensure_native_terminal_refuses_bare_codex(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Known SDK ``codex`` sessions reject ensure_native_terminal; no launch."""
    launch_calls: list[Any] = []
    auto_create = AsyncMock(side_effect=AssertionError("_auto_create_codex_terminal must not run"))
    monkeypatch.setattr("omnigent.runner.app._auto_create_codex_terminal", auto_create)

    from omnigent.terminals import registry as terminal_registry_mod

    real_launch = terminal_registry_mod.TerminalRegistry.launch

    async def _tracking_launch(self: Any, *args: Any, **kwargs: Any) -> Any:
        launch_calls.append((args, kwargs))
        return await real_launch(self, *args, **kwargs)

    monkeypatch.setattr(terminal_registry_mod.TerminalRegistry, "launch", _tracking_launch)

    async def _resolver(agent_id: str, session_id: str | None = None) -> AgentSpec:
        del agent_id, session_id
        return _spec(harness="codex")

    pm = MagicMock()
    pm.get_client = AsyncMock(return_value=MagicMock())

    app = create_runner_app(
        process_manager=pm,  # type: ignore[arg-type]
        server_client=NullServerClient(),  # type: ignore[arg-type]
        spec_resolver=_resolver,
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://runner") as client:
        start = await client.post(
            "/v1/sessions",
            json={"session_id": "conv_sdk_codex", "agent_id": "ag_test"},
        )
        assert start.status_code in (200, 201, 204), start.text
        resp = await _post_ensure(client, "conv_sdk_codex")

    assert resp.status_code == 400, resp.text
    body = resp.json()
    assert body["error"]["code"] == "native_terminal_not_applicable"
    assert "codex-native" in body["error"]["message"]
    auto_create.assert_not_awaited()
    assert launch_calls == []


@pytest.mark.asyncio
async def test_ensure_native_terminal_allows_codex_native_to_enter_auto_create(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Explicit codex-native still reaches ``_auto_create_codex_terminal``."""
    called = {"n": 0}

    async def _auto_create(*args: Any, **kwargs: Any) -> Any:
        called["n"] += 1
        raise RuntimeError("native terminal not supported on Windows (test sentinel)")

    monkeypatch.setattr("omnigent.runner.app._auto_create_codex_terminal", _auto_create)

    async def _resolver(agent_id: str, session_id: str | None = None) -> AgentSpec:
        del agent_id, session_id
        return _spec(harness="codex-native")

    pm = MagicMock()
    pm.get_client = AsyncMock(return_value=MagicMock())

    app = create_runner_app(
        process_manager=pm,  # type: ignore[arg-type]
        server_client=NullServerClient(),  # type: ignore[arg-type]
        spec_resolver=_resolver,
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://runner") as client:
        await client.post(
            "/v1/sessions",
            json={"session_id": "conv_native_codex", "agent_id": "ag_test"},
        )
        resp = await _post_ensure(client, "conv_native_codex")

    assert called["n"] >= 1, "codex-native must enter _auto_create_codex_terminal"
    if resp.status_code == 400:
        assert resp.json().get("error", {}).get("code") != "native_terminal_not_applicable"


@pytest.mark.asyncio
async def test_ensure_native_terminal_unknown_spec_fail_open(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unresolved session harness must not invent ``codex`` and 400.

    Historical ensure callers (CLI resume, parametrized native route tests)
    may hit ensure before a session spec is cached. Fail-open on the explicit
    ``ensure_native_terminal`` marker; only a *known* bare ``codex`` refuses.
    """
    called = {"n": 0}

    async def _auto_create(*args: Any, **kwargs: Any) -> Any:
        called["n"] += 1
        from omnigent.entities.session_resources import SessionResourceView

        return SessionResourceView(
            id="terminal_codex_main",
            type="terminal",
            session_id=args[0] if args else "conv_unknown",
            name="auto-created",
        )

    monkeypatch.setattr("omnigent.runner.app._auto_create_codex_terminal", _auto_create)

    # No spec_resolver → session harness stays unresolved at ensure time.
    app = create_runner_app(
        server_client=NullServerClient(),  # type: ignore[arg-type]
        spec_resolver=None,
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://runner") as client:
        # Skip POST /v1/sessions (would fail without resolver/PM); hit ensure cold.
        resp = await _post_ensure(client, "conv_unknown_harness")

    assert resp.status_code == 200, resp.text
    assert called["n"] == 1
    assert resp.json()["name"] == "auto-created"
