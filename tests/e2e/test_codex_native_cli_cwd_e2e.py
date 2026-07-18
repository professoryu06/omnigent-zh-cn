"""End-to-end test: ``omnigent codex`` runs the agent in the launch cwd.

The CLI sibling of the host worktree/workspace cwd tests in
``test_host_codex_native_e2e.py``. The ``omnigent codex`` wrapper launches
its runner in the user's current working directory, so a file that exists only
in that directory must be readable by the Codex agent. This pins the
wrapper-path half of the codex-native cwd-resolution fix: the runner resolves
the terminal cwd from the session workspace falling back to
``OMNIGENT_RUNNER_WORKSPACE`` (the wrapper's launch cwd), never the
spec-bundle extraction dir.

Environment requirements (why this is opt-in, not pure-CI)
----------------------------------------------------------
* **Opt-in only**: set ``OMNIGENT_E2E_CODEX_NATIVE=1`` to run. codex-native
  needs an interactive Codex login anchored to the real ``$HOME``; a present-
  but-unauthenticated binary would hang the TUI. The env-var gate keeps it out
  of CI; a developer with a logged-in Codex opts in.
* Run it like the host codex-native test::

    OMNIGENT_E2E_CODEX_NATIVE=1 \
    .venv/bin/python -m pytest tests/e2e/test_codex_native_cli_cwd_e2e.py \
        --profile oss \
        --llm-api-key "$(databricks auth token -p oss \
            | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')" \
        -v
"""

from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

import httpx
import pytest

from tests.e2e._native_resume_helpers import (
    cli_env,
    inject_user_message,
    omnigent_console_script,
    poll_for_assistant_marker,
    spawn_cli_background,
    wait_for_conversation_id,
    wait_for_terminal_ready,
)

# ``resume_test_server`` is provided by tests/e2e/conftest.py (the allow-list-
# free server the CLI wrapper's self-spawned host daemon can register against).

# Opt-in only — see module docstring. Binary presence is not a sufficient gate
# (present-but-unauthenticated hangs the TUI), so require the explicit env var.
pytestmark = pytest.mark.skipif(
    os.environ.get("OMNIGENT_E2E_CODEX_NATIVE") != "1" or shutil.which("codex") is None,
    reason=(
        "codex-native CLI cwd e2e needs an interactive Codex login; set "
        "OMNIGENT_E2E_CODEX_NATIVE=1 (and have `codex` installed + logged in) to run"
    ),
)

_CWD_MARKER_FILE = "CWD_MARKER.txt"


def test_codex_native_cli_runs_in_launch_cwd(
    resume_test_server: str,
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    """
    ``omnigent codex`` launches the agent in the directory it was run from.

    Spawns a backgrounded ``omnigent codex`` session whose process cwd is a
    temp directory containing a marker file, then injects (via the server, the
    web-UI path) a request to read that file. The marker exists only in the
    launch cwd (never in the runner's spec-bundle dir), so it can come back
    only if the wrapper resolved the agent's cwd to the launch directory —
    i.e. ``OMNIGENT_RUNNER_WORKSPACE`` / the session workspace, not the
    bundle dir.

    Uses the kept-alive background + HTTP-inject pattern (not a one-shot
    ``-p``) because a tool-using Codex turn returns the TUI to its idle
    composer rather than exiting, which a one-shot exit-wait would mistake for
    a hang.

    :param resume_test_server: Base URL of the allow-list-free test server.
    :param tmp_path: Per-test temp dir; its ``pwd`` subdir is the launch cwd.
    :param request: Pytest request — reads ``--profile`` for the LLM gateway.
    :returns: None.
    """
    profile = request.config.getoption("--profile")
    assert profile, "this test requires --profile (e.g. --profile oss) for the LLM gateway"

    pwd_dir = tmp_path / "pwd"
    pwd_dir.mkdir()
    marker = f"PWD_{uuid.uuid4().hex[:6].upper()}"
    (pwd_dir / _CWD_MARKER_FILE).write_text(marker + "\n")

    omni = str(omnigent_console_script())
    # ``--profile`` was removed from the omnigent CLI; cli_env(profile=…)
    # supplies the gateway routing via the config-home auth block instead.
    handle = spawn_cli_background(
        [omni, "codex", "--server", resume_test_server],
        env=cli_env(profile=profile),
        cwd=str(pwd_dir),
    )
    try:
        conversation_id = wait_for_conversation_id(handle, timeout=120.0)
        with httpx.Client(base_url=resume_test_server, timeout=30) as client:
            wait_for_terminal_ready(
                client, conversation_id=conversation_id, harness="codex", timeout=90.0
            )
            inject_user_message(
                client,
                conversation_id=conversation_id,
                text=(
                    f"Read the file {_CWD_MARKER_FILE} in your current directory "
                    "and reply with its exact contents and nothing else."
                ),
            )
            # The forwarder persists Codex's reply as an assistant item. The
            # marker appears only if Codex read the launch-cwd file — i.e. its
            # terminal launched in pwd_dir, not the spec-bundle dir.
            # poll_for_assistant_marker returns once the marker appears and
            # raises AssertionError on timeout — re-raise with the cwd-focused
            # context so a failure points at the launch-cwd resolution.
            try:
                poll_for_assistant_marker(
                    client,
                    conversation_id=conversation_id,
                    marker=marker,
                    timeout=180.0,
                )
            except AssertionError as exc:
                raise AssertionError(
                    f"`omnigent codex` did not return marker {marker!r} from "
                    f"{_CWD_MARKER_FILE} — it did not run the agent in its launch "
                    "cwd (the wrapper-path cwd resolution regressed, likely the "
                    "spec-bundle dir)."
                ) from exc
    finally:
        handle.terminate()
