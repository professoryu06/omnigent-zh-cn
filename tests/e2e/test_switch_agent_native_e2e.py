"""E2E tests for in-place agent switch ACROSS the native boundary.

Companion to ``test_switch_agent_e2e.py`` (SDK→SDK). These exercise the two
harness-crossing in-place switches, which hit code the SDK→SDK test does not:

- **native → SDK**: the SDK target replays the Omnigent transcript as context
  (and the source's terminal-first presentation labels must be dropped).
- **SDK → native**: the native CLI ignores the Omnigent transcript, so the
  runner must REBUILD the on-disk Claude transcript from the session's own AP
  items (``_ensure_local_claude_resume_transcript``) under a fresh uuid and
  ``--resume`` it — the same rebuild path the SDK→native *fork* uses, but
  triggered in place (no new session, no re-launch).

Both run on a real host daemon via the Claude CLI's OAuth, so they're gated
behind ``OMNIGENT_E2E_CLAUDE_NATIVE=1`` like the native fork e2e. Unlike a
fork, an in-place switch keeps the session's host + workspace + runner, so
there is no directory picker / ``_launch_runner`` step — the next turn simply
cold-starts the switched-to harness on the bound runner.

Usage::

    OMNIGENT_E2E_CLAUDE_NATIVE=1 \
      pytest tests/e2e/test_switch_agent_native_e2e.py --llm-api-key <key> -v
"""

from __future__ import annotations

import contextlib
import os
import shutil
import threading
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote

import httpx
import pytest

from tests.e2e.helpers import POLL_INTERVAL_S
from tests.e2e.test_host_claude_native_e2e import (
    _claude_native_agent_id,
    _online_host_id,
    _poll_for_assistant_marker,
)
from tests.e2e.test_host_claude_native_fork_e2e import (
    _builtin_agent_id,
    _create_native_session,
    _host_daemon,
    _send_user_message,
    _workspaces_trusted_in_claude_config,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("OMNIGENT_E2E_CLAUDE_NATIVE") != "1" or shutil.which("claude") is None,
    reason=(
        "claude-native e2e needs an interactive Claude login; set "
        "OMNIGENT_E2E_CLAUDE_NATIVE=1 (and have `claude` installed + logged in) to run"
    ),
)

_PLANT = "Remember this code word for later: {marker}. Reply with exactly one word: ACK"
_RECALL = (
    "Earlier in this conversation I gave you a code word to remember. "
    "Reply with exactly that code word and nothing else."
)


def _wait_for_session_idle(client: httpx.Client, *, session_id: str, timeout: float) -> None:
    """Poll until the session reports ``idle`` status.

    Switching is gated on the session being idle (a running turn → 409), and
    the UI only enables the switcher when idle. A native turn's assistant
    marker can appear in the transcript slightly before the relay reports the
    turn idle, so callers wait here before switching.

    :param client: HTTP client pointed at the test server.
    :param session_id: Session/conversation id.
    :param timeout: Max seconds to wait for idle.
    :raises AssertionError: If the session is not idle within *timeout*.
    """
    deadline = time.monotonic() + timeout
    last_status: str | None = None
    while time.monotonic() < deadline:
        resp = client.get(f"/v1/sessions/{session_id}", timeout=30.0)
        if resp.status_code == 200:
            last_status = resp.json().get("status")
            if last_status == "idle":
                return
        time.sleep(POLL_INTERVAL_S)
    raise AssertionError(
        f"session {session_id} did not return to idle within {timeout}s "
        f"(last status={last_status!r}) — cannot switch agent while busy"
    )


def _claude_terminal_resource_id(client: httpx.Client, session_id: str) -> str:
    """Return the session's claude terminal resource id.

    :param client: HTTP client pointed at the test server.
    :param session_id: Session/conversation id.
    :returns: The terminal resource id, e.g. ``"terminal_claude_main"``.
    :raises AssertionError: If no terminal resource is registered.
    """
    resp = client.get(f"/v1/sessions/{session_id}/resources", timeout=30.0)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    for res in data:
        rid = str(res.get("id", ""))
        if res.get("type") == "terminal" or "terminal" in rid:
            return rid
    raise AssertionError(f"no terminal resource for session {session_id!r}; resources={data}")


@contextmanager
def _hold_terminal_attached(base_url: str, session_id: str, terminal_id: str) -> Iterator[None]:
    """Hold the terminal-attach WebSocket open for the block's duration.

    Mirrors a browser keeping the terminal tab open: the live attach keeps the
    claude terminal registered across an agent switch, which is the condition
    that triggers the switch-back rebuild-skip bug. A background thread drains
    frames so the connection stays alive (ping/pong is automatic).

    :param base_url: The server base URL (``http://...``).
    :param session_id: Session/conversation id.
    :param terminal_id: Terminal resource id to attach to.
    :returns: Iterator yielding once the WS is connected; closed on exit.
    """
    from websockets.sync.client import connect as ws_connect

    ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
    path = (
        f"/v1/sessions/{quote(session_id, safe='')}"
        f"/resources/terminals/{quote(terminal_id, safe='')}/attach"
    )
    conn = ws_connect(ws_url + path, open_timeout=30)
    stop = threading.Event()

    def _drain() -> None:
        while not stop.is_set():
            try:
                conn.recv(timeout=1)
            except TimeoutError:
                continue
            except Exception:
                # Server closed the socket (terminal torn down) / shutdown.
                return

    drainer = threading.Thread(target=_drain, daemon=True)
    drainer.start()
    try:
        yield
    finally:
        stop.set()
        with contextlib.suppress(Exception):
            conn.close()
        drainer.join(timeout=5)


def _bound_agent_id(client: httpx.Client, session_id: str) -> str:
    """Return the id of the session's currently-bound agent.

    :param client: HTTP client pointed at the test server.
    :param session_id: Session/conversation id.
    :returns: The bound agent id.
    """
    resp = client.get(f"/v1/sessions/{session_id}/agent", timeout=30.0)
    resp.raise_for_status()
    return str(resp.json()["id"])


def _switch_agent(client: httpx.Client, *, session_id: str, agent_id: str) -> dict[str, object]:
    """Switch a session in place to *agent_id* and return the response body.

    :param client: HTTP client pointed at the test server.
    :param session_id: Session to switch.
    :param agent_id: Built-in target agent id.
    :returns: The switch response JSON.
    """
    resp = client.post(
        f"/v1/sessions/{session_id}/switch-agent",
        json={"agent_id": agent_id},
        timeout=60.0,
    )
    assert resp.status_code == 200, f"switch failed: {resp.status_code} {resp.text}"
    return dict(resp.json())


def test_switch_native_to_sdk_in_place_carries_history(
    live_server: str,
    http_client: httpx.Client,
    tmp_path: Path,
) -> None:
    """A claude-native session switched in place to claude-sdk recalls history.

    Native source plants a word on the host; switching in place to the
    built-in ``sdk-chat-builtin`` keeps the SAME session, and the SDK agent
    recalls the word from the replayed transcript. Also guards that the
    source's terminal-first presentation labels are dropped (chat mode).

    :param live_server: The test server URL.
    :param http_client: HTTP client pointed at the test server.
    :param tmp_path: Per-test temp dir.
    :returns: None.
    """
    workspace = tmp_path / "native_to_sdk_switch_ws"
    workspace.mkdir()
    marker = f"SWITCHWORD_{uuid.uuid4().hex[:6].upper()}"

    with _workspaces_trusted_in_claude_config([workspace]):
        with _host_daemon(tmp_path, live_server):
            host_id = _online_host_id(http_client, timeout=30.0)
            native_agent_id = _claude_native_agent_id(http_client)
            sdk_agent_id = _builtin_agent_id(http_client, "sdk-chat-builtin")

            # 1. claude-native SOURCE on the host; plant a code word.
            session_id = _create_native_session(
                http_client, agent_id=native_agent_id, host_id=host_id, workspace=workspace
            )
            _send_user_message(
                http_client, session_id=session_id, text=_PLANT.format(marker=marker)
            )
            _poll_for_assistant_marker(
                http_client, session_id=session_id, marker="ACK", timeout=180.0
            )
            _wait_for_session_idle(http_client, session_id=session_id, timeout=60.0)
            original_agent_id = _bound_agent_id(http_client, session_id)

            # 2. Switch IN PLACE to the SDK agent — no fork, no re-launch.
            switched = _switch_agent(http_client, session_id=session_id, agent_id=sdk_agent_id)
            assert switched["id"] == session_id, "switch must keep the same session id"
            assert switched["agent_id"] != original_agent_id, "switch must rebind the agent"
            # Switching to an SDK target must drop terminal-first mode.
            snap = http_client.get(f"/v1/sessions/{session_id}", timeout=30.0).json()
            assert snap.get("labels", {}).get("omnigent.ui") != "terminal", (
                f"SDK target must drop terminal-first mode, got labels {snap.get('labels')!r}"
            )

            # 3. The switched-in SDK agent recalls the planted word.
            _send_user_message(http_client, session_id=session_id, text=_RECALL)
            text = _poll_for_assistant_marker(
                http_client, session_id=session_id, marker=marker, timeout=180.0
            )
            assert marker in text, (
                f"SDK agent did not recall {marker!r} (got {text!r}) — the native "
                "source's transcript was not replayed as context after the switch"
            )


def test_switch_sdk_to_native_in_place_carries_history(
    live_server: str,
    http_client: httpx.Client,
    tmp_path: Path,
) -> None:
    """A claude-sdk session switched in place to claude-native recalls history.

    SDK source plants a word; switching in place to claude-native keeps the
    SAME session, and the runner must REBUILD the native transcript from the
    session's own AP items (the SDK source has no native ``external_session_id``
    to clone) so the native agent recalls the word. A regression launches the
    native harness fresh and the recall fails.

    The SDK source runs on the host daemon (so the post-switch native harness
    has a host + workspace to run in — an in-place switch cannot rebind those).

    :param live_server: The test server URL.
    :param http_client: HTTP client pointed at the test server.
    :param tmp_path: Per-test temp dir.
    :returns: None.
    """
    workspace = tmp_path / "sdk_to_native_switch_ws"
    workspace.mkdir()
    marker = f"SWITCHWORD_{uuid.uuid4().hex[:6].upper()}"

    with _workspaces_trusted_in_claude_config([workspace]):
        with _host_daemon(tmp_path, live_server):
            host_id = _online_host_id(http_client, timeout=30.0)
            native_agent_id = _claude_native_agent_id(http_client)
            sdk_agent_id = _builtin_agent_id(http_client, "sdk-chat-builtin")

            # 1. claude-sdk SOURCE on the host; plant a code word. Binding the
            # built-in sdk agent to a host + workspace makes the session
            # runnable as native after the switch (same host/workspace kept).
            session_id = _create_native_session(
                http_client, agent_id=sdk_agent_id, host_id=host_id, workspace=workspace
            )
            _send_user_message(
                http_client, session_id=session_id, text=_PLANT.format(marker=marker)
            )
            _poll_for_assistant_marker(
                http_client, session_id=session_id, marker="ACK", timeout=180.0
            )
            _wait_for_session_idle(http_client, session_id=session_id, timeout=60.0)
            original_agent_id = _bound_agent_id(http_client, session_id)

            # 2. Switch IN PLACE to claude-native. external_session_id is
            # cleared + the carry-history label is stamped, so the next turn's
            # native cold-start rebuilds the Claude transcript from AP items.
            switched = _switch_agent(http_client, session_id=session_id, agent_id=native_agent_id)
            assert switched["id"] == session_id, "switch must keep the same session id"
            assert switched["agent_id"] != original_agent_id, "switch must rebind the agent"

            # 3. The switched-in native agent recalls the planted word — only
            # possible if the AP items were rebuilt into its Claude transcript.
            _send_user_message(http_client, session_id=session_id, text=_RECALL)
            text = _poll_for_assistant_marker(
                http_client, session_id=session_id, marker=marker, timeout=180.0
            )
            assert marker in text, (
                f"native agent did not recall {marker!r} (got {text!r}) — the SDK "
                "source's AP items were not rebuilt into the native transcript on switch"
            )


def test_switch_native_roundtrip_carries_turns_added_while_away(
    live_server: str,
    http_client: httpx.Client,
    tmp_path: Path,
) -> None:
    """Switching native → SDK → native carries turns added on the SDK leg.

    A session runs claude-native, switches to an SDK agent where the user adds
    a NEW fact, then switches BACK to claude-native. The switched-back native
    agent must recall the fact added while away — which requires the
    switch-back rebuild to use the CURRENT AP items (including the SDK-leg
    turns), not the transcript left over from the first native run. Guards the
    round-trip path (native → other → native), which carries more lingering
    runtime state than a single switch.

    :param live_server: The test server URL.
    :param http_client: HTTP client pointed at the test server.
    :param tmp_path: Per-test temp dir.
    :returns: None.
    """
    workspace = tmp_path / "native_roundtrip_ws"
    workspace.mkdir()
    marker_native = f"NATIVEWORD_{uuid.uuid4().hex[:6].upper()}"
    marker_away = f"AWAYWORD_{uuid.uuid4().hex[:6].upper()}"

    with _workspaces_trusted_in_claude_config([workspace]):
        with _host_daemon(tmp_path, live_server):
            host_id = _online_host_id(http_client, timeout=30.0)
            native_agent_id = _claude_native_agent_id(http_client)
            sdk_agent_id = _builtin_agent_id(http_client, "sdk-chat-builtin")

            # 1. claude-native source; plant the first word (creates the
            # original on-disk transcript + terminal).
            session_id = _create_native_session(
                http_client, agent_id=native_agent_id, host_id=host_id, workspace=workspace
            )
            _send_user_message(
                http_client, session_id=session_id, text=_PLANT.format(marker=marker_native)
            )
            _poll_for_assistant_marker(
                http_client, session_id=session_id, marker="ACK", timeout=180.0
            )
            _wait_for_session_idle(http_client, session_id=session_id, timeout=60.0)

            # 2. Switch to the SDK agent and add a SECOND word while away.
            _switch_agent(http_client, session_id=session_id, agent_id=sdk_agent_id)
            _send_user_message(
                http_client,
                session_id=session_id,
                text=f"Also remember this second code word: {marker_away}. Reply ACK.",
            )
            _poll_for_assistant_marker(
                http_client, session_id=session_id, marker="ACK", timeout=180.0
            )
            _wait_for_session_idle(http_client, session_id=session_id, timeout=60.0)

            # 3. Switch BACK to claude-native. The rebuild must use the CURRENT
            # AP items (including the SDK-leg turns), not the stale transcript
            # from the first native run.
            _switch_agent(http_client, session_id=session_id, agent_id=native_agent_id)

            # 4. The switched-back native agent recalls the word added WHILE on
            # the other agent — the regression loses exactly this word.
            _send_user_message(
                http_client,
                session_id=session_id,
                text=(
                    "Reply with the SECOND code word I asked you to remember, and nothing else."
                ),
            )
            text = _poll_for_assistant_marker(
                http_client, session_id=session_id, marker=marker_away, timeout=180.0
            )
            assert marker_away in text, (
                f"native agent did not recall {marker_away!r} added while on the SDK "
                f"agent (got {text!r}) — the switch-back reused the stale native "
                "terminal/transcript instead of rebuilding from current AP items"
            )


def test_switch_native_roundtrip_with_open_terminal_carries_history(
    live_server: str,
    http_client: httpx.Client,
    tmp_path: Path,
) -> None:
    """Round-trip recall holds even with the terminal tab kept open.

    Same as the round-trip test above, but the claude terminal-attach
    WebSocket is held OPEN across the whole away-and-back sequence — exactly
    what a browser terminal tab does, keeping the original claude terminal
    registered. This was written to reproduce a reported loss of mid-switch
    history on claude-native; it does NOT reproduce it (the switch-back still
    rebuilds and recalls the away-word), which **rules out a lingering
    terminal** as the cause and guards against a regression where holding the
    terminal open would break the round-trip. (The reported bug with nessie as
    the middle agent is still under investigation — likely supervisor-specific
    transcript persistence, not the terminal.)

    :param live_server: The test server URL.
    :param http_client: HTTP client pointed at the test server.
    :param tmp_path: Per-test temp dir.
    :returns: None.
    """
    workspace = tmp_path / "native_roundtrip_open_term_ws"
    workspace.mkdir()
    marker_native = f"NATIVEWORD_{uuid.uuid4().hex[:6].upper()}"
    marker_away = f"AWAYWORD_{uuid.uuid4().hex[:6].upper()}"

    with _workspaces_trusted_in_claude_config([workspace]):
        with _host_daemon(tmp_path, live_server):
            host_id = _online_host_id(http_client, timeout=30.0)
            native_agent_id = _claude_native_agent_id(http_client)
            sdk_agent_id = _builtin_agent_id(http_client, "sdk-chat-builtin")

            # 1. claude-native source; plant the first word + create the terminal.
            session_id = _create_native_session(
                http_client, agent_id=native_agent_id, host_id=host_id, workspace=workspace
            )
            _send_user_message(
                http_client, session_id=session_id, text=_PLANT.format(marker=marker_native)
            )
            _poll_for_assistant_marker(
                http_client, session_id=session_id, marker="ACK", timeout=180.0
            )
            _wait_for_session_idle(http_client, session_id=session_id, timeout=60.0)
            terminal_id = _claude_terminal_resource_id(http_client, session_id)

            # Hold the terminal tab open for the whole away-and-back sequence.
            with _hold_terminal_attached(live_server, session_id, terminal_id):
                # 2. Switch to the SDK agent and add a SECOND word while away.
                _switch_agent(http_client, session_id=session_id, agent_id=sdk_agent_id)
                _send_user_message(
                    http_client,
                    session_id=session_id,
                    text=f"Also remember this second code word: {marker_away}. Reply ACK.",
                )
                _poll_for_assistant_marker(
                    http_client, session_id=session_id, marker="ACK", timeout=180.0
                )
                _wait_for_session_idle(http_client, session_id=session_id, timeout=60.0)

                # 3. Switch BACK to claude-native with the terminal still open.
                _switch_agent(http_client, session_id=session_id, agent_id=native_agent_id)

                # 4. The switched-back native agent must recall the away-word.
                _send_user_message(
                    http_client,
                    session_id=session_id,
                    text=(
                        "Reply with the SECOND code word I asked you to remember, "
                        "and nothing else."
                    ),
                )
                text = _poll_for_assistant_marker(
                    http_client, session_id=session_id, marker=marker_away, timeout=180.0
                )
            assert marker_away in text, (
                f"native agent did not recall {marker_away!r} added while away (got "
                f"{text!r}) — with the terminal tab open, the stale terminal shadowed the "
                "rebuild, so the switch-back resumed the original transcript"
            )
