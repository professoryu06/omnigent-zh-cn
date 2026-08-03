"""C-3016: failed session snapshot must not poison workspace projection cache.

A transient non-200 ``GET /v1/sessions/{id}`` can yield ``workspace=None``.
If that value is memoized in ``_session_workspace_cache``, later recovery
never re-fetches the session worktree path and harness/filesystem code
falls back to the runner global workspace.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import httpx
import pytest

from omnigent.entities import DEFAULT_ENVIRONMENT_ID
from omnigent.inner.datamodel import OSEnvSandboxSpec, OSEnvSpec
from omnigent.inner.os_env import create_os_environment
from omnigent.runner import create_runner_app
from omnigent.runner.resource_registry import SessionResourceRegistry


def _git_env() -> dict[str, str]:
    """Minimal env for non-interactive git in temp repos."""
    return {
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }


def _init_git_repo(path: Path) -> None:
    """Create an empty commit so git status works."""
    path.mkdir(parents=True, exist_ok=True)
    env = _git_env()
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, env=env)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=path,
        check=True,
        capture_output=True,
        env=env,
    )


def _paths_from_changes(resp: httpx.Response) -> list[str]:
    """Extract path-like fields from a /changes JSON body."""
    data = resp.json().get("data", [])
    out: list[str] = []
    for item in data:
        raw = item.get("path") or item.get("name")
        if isinstance(raw, str):
            out.append(raw)
    return out


def _seed_os_env(session_id: str, cwd: Path) -> SessionResourceRegistry:
    """Attach a caller-process OS env so filesystem endpoints authorize."""
    os_env = create_os_environment(
        OSEnvSpec(
            type="caller_process",
            cwd=str(cwd),
            sandbox=OSEnvSandboxSpec(type="none"),
        ),
    )
    assert os_env is not None
    reg = SessionResourceRegistry()
    reg._primary_envs[session_id] = os_env
    return reg


@pytest.mark.asyncio
async def test_failed_snapshot_does_not_poison_workspace_cache(
    tmp_path: Path,
) -> None:
    """First snapshot failure must not pin workspace=None forever.

    After the server recovers with a worktree path, ``/changes`` must
    report files from that worktree — not the empty runner global repo.

    No ``spec_resolver`` is installed so ``_require_os_env`` stays a no-op
    (dev/standalone path used by other filesystem unit tests).
    """
    runner_ws = tmp_path / "runner_global"
    session_ws = tmp_path / "session_worktree"
    _init_git_repo(runner_ws)
    _init_git_repo(session_ws)
    (session_ws / "agent_change.py").write_text("# only in session worktree\n", encoding="utf-8")

    session_id = "conv_ws_poison"
    snapshot_count = 0

    async def _server_handler(request: httpx.Request) -> httpx.Response:
        nonlocal snapshot_count
        if request.method == "GET" and request.url.path == f"/v1/sessions/{session_id}":
            snapshot_count += 1
            if snapshot_count == 1:
                return httpx.Response(503, json={})
            return httpx.Response(
                200,
                json={
                    "id": session_id,
                    "agent_id": "ag_ws_poison",
                    "workspace": str(session_ws),
                    "created_at": 1_000.0,
                },
            )
        return httpx.Response(200, json={})

    server_client = httpx.AsyncClient(
        transport=httpx.MockTransport(_server_handler),
        base_url="http://server",
    )
    app = create_runner_app(
        resource_registry=_seed_os_env(session_id, session_ws),
        runner_workspace=runner_ws,
        server_client=server_client,
    )
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://runner") as client:
            first = await client.get(
                f"/v1/sessions/{session_id}/resources/environments/"
                f"{DEFAULT_ENVIRONMENT_ID}/changes"
            )
            second = await client.get(
                f"/v1/sessions/{session_id}/resources/environments/"
                f"{DEFAULT_ENVIRONMENT_ID}/changes"
            )
    finally:
        await server_client.aclose()

    assert snapshot_count >= 1
    assert second.status_code == 200, second.text
    paths = _paths_from_changes(second)
    assert any("agent_change.py" in p for p in paths), (
        "expected session worktree change after snapshot recovery; "
        f"got paths={paths!r} status_first={first.status_code} "
        f"snapshot_count={snapshot_count}. "
        "Missing agent_change.py means workspace cache stayed poisoned "
        "and the runner used the global workspace."
    )


@pytest.mark.asyncio
async def test_reset_agent_cache_evicts_workspace_projection(
    tmp_path: Path,
) -> None:
    """``POST .../agent-cache/reset`` must drop workspace projection.

    After reset, a new server-provided workspace path must take effect
    for filesystem registry resolution.
    """
    runner_ws = tmp_path / "runner_global"
    ws_a = tmp_path / "worktree_a"
    ws_b = tmp_path / "worktree_b"
    _init_git_repo(runner_ws)
    _init_git_repo(ws_a)
    _init_git_repo(ws_b)
    (ws_a / "only_a.py").write_text("a\n", encoding="utf-8")
    (ws_b / "only_b.py").write_text("b\n", encoding="utf-8")

    session_id = "conv_ws_reset"
    served: dict[str, str] = {"workspace": str(ws_a)}

    async def _server_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path == f"/v1/sessions/{session_id}":
            return httpx.Response(
                200,
                json={
                    "id": session_id,
                    "agent_id": "ag_ws_reset",
                    "workspace": served["workspace"],
                    "created_at": 1_000.0,
                },
            )
        return httpx.Response(200, json={})

    server_client = httpx.AsyncClient(
        transport=httpx.MockTransport(_server_handler),
        base_url="http://server",
    )
    app = create_runner_app(
        resource_registry=_seed_os_env(session_id, ws_a),
        runner_workspace=runner_ws,
        server_client=server_client,
    )
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://runner") as client:
            first = await client.get(
                f"/v1/sessions/{session_id}/resources/environments/"
                f"{DEFAULT_ENVIRONMENT_ID}/changes"
            )
            assert first.status_code == 200, first.text
            assert any("only_a.py" in p for p in _paths_from_changes(first)), _paths_from_changes(
                first
            )

            served["workspace"] = str(ws_b)
            reset = await client.post(f"/v1/sessions/{session_id}/agent-cache/reset")
            assert reset.status_code == 200, reset.text

            second = await client.get(
                f"/v1/sessions/{session_id}/resources/environments/"
                f"{DEFAULT_ENVIRONMENT_ID}/changes"
            )
    finally:
        await server_client.aclose()

    assert second.status_code == 200, second.text
    paths = _paths_from_changes(second)
    assert any("only_b.py" in p for p in paths), (
        "after agent-cache reset, expected workspace B changes; "
        f"got {paths!r}. Missing only_b.py means workspace and/or "
        "per-session fs registry projection survived reset."
    )
