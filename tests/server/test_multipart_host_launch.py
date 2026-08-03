"""BUG-3: multipart POST /v1/sessions must honor metadata.host_id.

Previously the multipart branch returned 201 after uploading the bundle
and never sent host.launch_runner, so sessions stayed forever idle with
no runner bound.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from omnigent.server.routes import sessions as sessions_routes
from tests.server.helpers import build_agent_bundle


@pytest.mark.asyncio
async def test_multipart_create_with_host_id_invokes_host_launch(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """multipart metadata.host_id must call the shared create-time launch."""
    called: dict[str, Any] = {}

    async def _fake_launch(**kwargs: Any) -> str:
        called.update(kwargs)
        return "runner_token_multipart_test"

    monkeypatch.setattr(
        sessions_routes,
        "_multipart_create_time_host_launch",
        _fake_launch,
    )

    bundle = build_agent_bundle(
        name="controller-d2",
        executor={"type": "omnigent", "config": {"harness": "codex", "model": "gpt-5.6-sol"}},
    )
    metadata = {
        "host_id": "host_0d637c9f10f640ab9d3b346cdf0eddae",
        "workspace": "C:\\Users\\Administrator\\workspace",
        "title": "BUG-3 multipart host launch",
    }
    resp = await client.post(
        "/v1/sessions",
        data={"metadata": json.dumps(metadata)},
        files={"bundle": ("agent.tar.gz", bundle, "application/gzip")},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["session_id"]
    assert called.get("session_id") == body["session_id"]
    assert called.get("agent_id") == body["agent_id"]
    assert called["metadata"].host_id == metadata["host_id"]
    assert called["metadata"].workspace == metadata["workspace"]


@pytest.mark.asyncio
async def test_multipart_create_without_host_id_skips_host_launch(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """multipart without host_id must not attempt a host launch."""
    launch = AsyncMock(return_value="runner_should_not_run")
    monkeypatch.setattr(sessions_routes, "_multipart_create_time_host_launch", launch)

    bundle = build_agent_bundle(name="no-host-agent")
    resp = await client.post(
        "/v1/sessions",
        data={"metadata": json.dumps({"title": "no host"})},
        files={"bundle": ("agent.tar.gz", bundle, "application/gzip")},
    )
    assert resp.status_code == 201, resp.text
    launch.assert_not_awaited()


@pytest.mark.asyncio
async def test_multipart_host_id_requires_workspace(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """host_id without workspace is a structured 4xx, not a silent idle 201."""
    # Do not stub the launch helper — the guard runs first.
    bundle = build_agent_bundle(name="missing-ws-agent")
    resp = await client.post(
        "/v1/sessions",
        data={
            "metadata": json.dumps(
                {"host_id": "host_0d637c9f10f640ab9d3b346cdf0eddae"}
            )
        },
        files={"bundle": ("agent.tar.gz", bundle, "application/gzip")},
    )
    # Session row may already exist; the host-launch step must still fail
    # loudly rather than return a successful idle session with no runner.
    assert resp.status_code in (400, 422, 500), resp.text
    if resp.status_code != 201:
        detail = resp.text.lower()
        assert "workspace" in detail or "host" in detail


@pytest.mark.asyncio
async def test_create_time_bind_and_launch_runner_sends_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Shared helper binds runner_id and sends HostLaunchRunnerFrame once."""
    from types import SimpleNamespace

    from omnigent.host.frames import HostLaunchRunnerFrame, decode_host_frame

    sent: list[str] = []
    pending: dict[str, Any] = {}

    class _Conn:
        pending_launches: dict[str, Any]

        def __init__(self) -> None:
            self.pending_launches = pending

    conn = _Conn()

    def _resolve_host_launch(**kwargs: Any) -> Any:
        del kwargs
        return SimpleNamespace(conn=conn)

    def _send_text(_conn: Any, frame: str) -> None:
        sent.append(frame)
        decoded = decode_host_frame(frame)
        assert isinstance(decoded, HostLaunchRunnerFrame)
        fut = pending.get(decoded.request_id)
        assert fut is not None
        fut.set_result({"status": "launched", "runner_id": "runner_from_host"})

    class _Registry:
        def send_text(self, c: Any, frame: str) -> None:
            _send_text(c, frame)

    class _Store:
        def set_runner_id(self, session_id: str, runner_id: str) -> bool:
            del session_id
            assert runner_id.startswith("runner_token_")
            return True

    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                host_registry=_Registry(),
                host_store=object(),
            )
        )
    )
    monkeypatch.setattr(
        "omnigent.server.routes._host_launch.resolve_host_launch",
        _resolve_host_launch,
    )

    result = await sessions_routes._create_time_bind_and_launch_runner(
        session_id="conv_test",
        host_id="host_test",
        workspace="/tmp/ws",
        harness="codex",
        user_id=None,
        request=request,  # type: ignore[arg-type]
        conversation_store=_Store(),  # type: ignore[arg-type]
        permission_store=None,
    )
    assert result.soft_failed is False
    assert result.runner_id.startswith("runner_token_")
    assert len(sent) == 1
    frame = decode_host_frame(sent[0])
    assert isinstance(frame, HostLaunchRunnerFrame)
    assert frame.workspace == "/tmp/ws"
    assert frame.session_id == "conv_test"
    assert frame.harness == "codex"
