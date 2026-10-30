"""Headless grok-native wrapper module (CODEX_TASK_GROK_NATIVE_01).

The task card requires a ``grok-native-ui`` agent that other agents can
dispatch through AgentCenter. Unlike qwen-native (a tmux TUI wrapper), grok
runs headless: the agent spec pins ``executor.harness: grok-native`` and the
harness subprocess drives ``grok --single --output-format json`` directly.
There is deliberately no native terminal / tmux / PTY involvement — the task
card forbids faking native-terminal resources on Windows.

This module owns the CLI-side orchestration surface that mirrors qwen-native's
module boundary:

- :func:`run_grok_native` — create/resume a headless grok-native session on an
  Omnigent server via a daemon runner (no terminal creation).
- :func:`_materialize_grok_agent_spec` — write the terminal-free agent spec
  YAML used to seed ``grok-native-ui`` as a built-in agent and to create
  sessions (bundle).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import click
import httpx
import yaml

from omnigent._native_resume_hint import echo_native_cold_resume_hint, echo_native_resume_hint
from omnigent._runner_startup import RunnerStartupProgress, runner_startup_progress
from omnigent._wrapper_labels import GROK_NATIVE_WRAPPER_VALUE as _WRAPPER_LABEL_VALUE
from omnigent._wrapper_labels import WRAPPER_LABEL_KEY as _WRAPPER_LABEL_KEY
from omnigent.conversation_browser import conversation_url, open_conversation_link_if_enabled
from omnigent.host.daemon_launch import (
    error_text,
    launch_or_reuse_daemon_runner,
    wait_for_host_online,
    wait_for_runner_online,
)
from omnigent.native_terminal import DAEMON_HOST_ONLINE_TIMEOUT_S as _DAEMON_HOST_ONLINE_TIMEOUT_S
from omnigent.native_terminal import (
    DAEMON_RUNNER_ONLINE_TIMEOUT_S as _DAEMON_RUNNER_ONLINE_TIMEOUT_S,
)

_AGENT_NAME = "grok-native-ui"
_SESSION_LABELS = {
    "omnigent.ui": "chat",  # headless — NOT terminal-first
    _WRAPPER_LABEL_KEY: _WRAPPER_LABEL_VALUE,
}


def _materialize_grok_agent_spec(tmpdir: Path) -> Path:
    """Write the headless grok-native agent spec used for seeding / bundles.

    :param tmpdir: Temporary directory for the generated YAML file.
    :returns: Path to the generated YAML spec.
    """
    yaml_path = tmpdir / "grok-native-ui.yaml"
    raw: dict[str, Any] = {
        "name": _AGENT_NAME,
        "prompt": (
            "grok runs headless through the Grok CLI (grok-4.5). "
            "The user talks to grok through the web UI; no terminal is involved."
        ),
        "executor": {"harness": "grok-native"},
        "spawn": True,
        "os_env": {
            "type": "caller_process",
            "cwd": ".",
            "sandbox": {"type": "none"},
        },
    }
    yaml_path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    return yaml_path


def run_grok_native(
    *,
    server: str | None,
    session_id: str | None,
    auto_open_conversation: bool = False,
) -> None:
    """Create/resume a headless grok-native session on an Omnigent server.

    :param server: Resolved Omnigent server URL.
    :param session_id: Optional existing Omnigent conversation id to resume.
    :param auto_open_conversation: When ``True``, open the browser conversation
        URL after launch.
    :returns: None after the session is bound to a runner.
    """
    if server is None:
        raise click.ClickException(
            "grok requires a resolved Omnigent server URL. The CLI should call "
            "_ensure_backend before run_grok_native."
        )
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(prefix="omnigent-grok-native-") as tmpdir:
        spec_path = _materialize_grok_agent_spec(Path(tmpdir))
        _run_with_remote_server(
            server.rstrip("/"),
            spec_path,
            session_id=session_id,
            auto_open_conversation=auto_open_conversation,
        )


def _run_with_remote_server(
    base_url: str,
    spec_path: Path,
    *,
    session_id: str | None,
    auto_open_conversation: bool = False,
) -> None:
    """Create/resume a grok-native session via a daemon-spawned runner."""
    from omnigent.chat import _bundle_agent, _remote_headers
    from omnigent.cli import _ensure_host_daemon
    from omnigent.host.identity import load_or_create_host_identity

    headers = _remote_headers(server_url=base_url)
    try:
        async def _drive() -> None:
            with runner_startup_progress(initial_message="Preparing grok...") as progress:
                _update_startup_progress(progress, "Connecting to local daemon...")
                _ensure_host_daemon(base_url)
                host_id = load_or_create_host_identity().host_id
                bundle = None if session_id is not None else _bundle_agent(spec_path)
                prepared = await _prepare_grok_session_via_daemon(
                    base_url=base_url,
                    headers=headers,
                    session_id=session_id,
                    session_bundle=bundle,
                    host_id=host_id,
                    workspace=str(Path.cwd().resolve()),
                    startup_progress=progress,
                )
            click.echo(f"Web UI: {conversation_url(base_url, prepared)}", err=True)
            open_conversation_link_if_enabled(
                base_url=base_url,
                conversation_id=prepared,
                enabled=auto_open_conversation,
                warn=lambda message: click.echo(message, err=True),
            )
            if session_id is None:
                echo_native_resume_hint(
                    native_command="grok",
                    session_id=prepared,
                    server=base_url,
                )
            else:
                echo_native_cold_resume_hint(agent_label="grok")

        asyncio.run(_drive())
    except httpx.ConnectError as exc:
        raise click.ClickException(
            f"Could not reach the omnigent server at {base_url}. "
            "Confirm the server is running and reachable from here "
            f"(e.g. `curl {base_url}/health`), and that --server is correct."
        ) from exc


async def _prepare_grok_session_via_daemon(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str | None,
    session_bundle: bytes | None,
    host_id: str,
    workspace: str,
    startup_progress: RunnerStartupProgress | None = None,
) -> str:
    """Create (or reuse) a headless grok-native session through a daemon runner.

    Headless: no terminal resource is ensured — the harness subprocess
    (``omnigent.inner.grok_native_harness``) is spawned by the runner when the
    first response is requested.

    :returns: The resolved session id.
    """
    timeout = httpx.Timeout(30.0, read=120.0)
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=timeout) as client:
        cold_resumed = False
        if session_id is None:
            if session_bundle is None:
                raise click.ClickException("Creating a grok session requires a session bundle.")
            _update_startup_progress(startup_progress, "Creating grok session...")
            session_id = await _create_grok_session(client, session_bundle)
        else:
            _update_startup_progress(startup_progress, "Loading grok session...")
            payload = await _fetch_grok_session(client, session_id)
            labels = payload.get("labels") if isinstance(payload, dict) else None
            if (
                not isinstance(labels, dict)
                or labels.get(_WRAPPER_LABEL_KEY) != _WRAPPER_LABEL_VALUE
            ):
                raise click.ClickException(
                    f"Conversation {session_id!r} is not a grok-native session."
                )
            cold_resumed = True

        await wait_for_host_online(client, host_id, timeout_s=_DAEMON_HOST_ONLINE_TIMEOUT_S)
        _update_startup_progress(startup_progress, "Starting runner...")
        runner_id = await launch_or_reuse_daemon_runner(
            client,
            host_id=host_id,
            session_id=session_id,
            workspace=workspace,
        )
        _update_startup_progress(startup_progress, "Waiting for runner...")
        await wait_for_runner_online(client, runner_id, timeout_s=_DAEMON_RUNNER_ONLINE_TIMEOUT_S)
        _update_startup_progress(startup_progress, "grok session ready.")
    return session_id


async def _create_grok_session(client: httpx.AsyncClient, bundle: bytes) -> str:
    """Create a bundled headless grok-native session."""
    metadata: dict[str, Any] = {"labels": dict(_SESSION_LABELS)}
    resp = await client.post(
        "/v1/sessions",
        data={"metadata": json.dumps(metadata)},
        files={"bundle": ("grok-native-ui.tar.gz", bundle, "application/gzip")},
        timeout=120.0,
    )
    if resp.status_code >= 400:
        raise click.ClickException(
            f"grok session creation failed ({resp.status_code}): {error_text(resp)}"
        )
    body = resp.json()
    new_session_id = body.get("session_id")
    if not isinstance(new_session_id, str) or not new_session_id:
        raise click.ClickException("grok session creation response did not include session_id.")
    return new_session_id


async def _fetch_grok_session(client: httpx.AsyncClient, session_id: str) -> dict[str, Any]:
    """Fetch an existing Omnigent session."""
    from omnigent.native_terminal import url_component

    resp = await client.get(f"/v1/sessions/{url_component(session_id)}")
    if resp.status_code == 404:
        raise click.ClickException(f"Conversation {session_id!r} not found on the server.")
    if resp.status_code >= 400:
        raise click.ClickException(
            f"Failed to fetch conversation {session_id!r} ({resp.status_code}): {error_text(resp)}"
        )
    payload = resp.json()
    if not isinstance(payload, dict):
        raise click.ClickException("Conversation fetch returned non-object JSON.")
    return payload


def _update_startup_progress(
    progress: RunnerStartupProgress,
    message: str,
) -> None:
    """Update the runner startup progress line (no-op-safe wrapper)."""
    progress.update(message)
