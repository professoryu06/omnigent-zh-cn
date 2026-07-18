"""End-to-end regression test: ``omnigent claude --resume`` restores history.

Reproduces the user-reported bug: running

    omnigent claude --server <url> --resume <conv_id>

attached a Claude Code session with **no history** — the prior conversation
was silently lost because the runner auto-created a *fresh* Claude terminal
(no ``--resume``) for the CLI-driven session, racing and beating the CLI's own
cold-resume launch. The fix gates the runner's auto-create to host-spawned
(web-UI) sessions only; CLI-driven sessions keep their own cold-resume launch.

This is the robust, outcome-based check: it drives the REAL ``omnigent
claude`` CLI to create a conversation that knows a passphrase, resumes it, and
then — through the server's message API, the same path the web UI uses —
verifies Claude answers a follow-up with that passphrase. The passphrase
coming back proves the resumed session actually had the earlier turn. The
shared flow lives in :func:`assert_native_cli_resume_restores_history` (see
``tests/e2e/_native_resume_helpers.py``); the deterministic
``--resume``-injection mechanism is separately guarded by the runner unit
tests in ``tests/runner/test_app_sessions_native.py``.

Environment requirements (why this is opt-in, not pure-CI)
----------------------------------------------------------
* **Opt-in only**: set ``OMNIGENT_E2E_CLAUDE_NATIVE=1`` to run. claude-native
  needs an *interactive* Claude login (OAuth/Enterprise) anchored to the real
  ``$HOME`` — it cannot be relocated into CI. The ``claude`` binary IS present
  in CI (claude-sdk installs it), so gating on binary presence alone would let
  this run unauthenticated and hang the TUI. The env-var gate keeps it out of
  CI; a developer with a logged-in Claude opts in explicitly.
* Run it the same way as the host claude-native test::

    OMNIGENT_E2E_CLAUDE_NATIVE=1 \
    .venv/bin/python -m pytest tests/e2e/test_claude_native_cli_resume_e2e.py \
        --profile oss \
        --llm-api-key "$(databricks auth token -p oss \
            | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')" \
        -v
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from tests.e2e._native_resume_helpers import assert_native_cli_resume_restores_history

# ``resume_test_server`` is provided by tests/e2e/conftest.py (shared with the
# codex resume test) and resolved by pytest fixture discovery.

# Opt-in only — see module docstring. The `claude` binary alone is not a
# sufficient gate (present-but-unauthenticated in CI hangs the TUI), so
# require an explicit env var that only a developer with a logged-in Claude
# sets.
pytestmark = pytest.mark.skipif(
    os.environ.get("OMNIGENT_E2E_CLAUDE_NATIVE") != "1" or shutil.which("claude") is None,
    reason=(
        "claude-native CLI resume e2e needs an interactive Claude login; set "
        "OMNIGENT_E2E_CLAUDE_NATIVE=1 (and have `claude` installed + logged in) to run"
    ),
)


def test_claude_native_cli_resume_restores_history(
    resume_test_server: str,
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    """
    Cross-context ``omnigent claude --resume`` restores conversation history.

    Drives the real ``omnigent claude --server …`` CLI (gateway routing
    via the config-home auth block from the pytest ``--profile``) to teach
    Claude a passphrase, **deletes Claude's local transcript** for that session,
    then resumes — so the resume cannot reuse Claude's own on-disk transcript
    and must go through Omnigent' cold-resume *synthesis* (rebuild the
    transcript from server-side items and hand it to ``claude --resume``). A
    recall message is sent through the server and Claude must reply with the
    passphrase, proving the resumed session loaded the prior turn.

    This is the exact scenario a user hits resuming a conversation created
    elsewhere / in another cwd / on another machine — the path that was
    silently losing history. It exercises both halves of the fix end-to-end:
    the runner re-creating the terminal on a reused daemon runner (the ensure
    path) and ``_ensure_local_claude_resume_transcript`` synthesizing the
    transcript. (We deliberately do NOT also test the same-machine fast path —
    that only exercises Claude resuming its own file, not Omnigent' code, and
    running a second back-to-back CLI flow thrashes the shared host daemon.)

    :param resume_test_server: Base URL of the allow-list-free test server.
    :param tmp_path: Per-test temp dir.
    :param request: Pytest request — reads ``--profile`` for the LLM gateway.
    """
    profile = request.config.getoption("--profile")
    assert profile, "this test requires --profile (e.g. --profile oss) for the LLM gateway"
    assert_native_cli_resume_restores_history(
        harness="claude",
        server=resume_test_server,
        profile=profile,
        tmp_path=tmp_path,
        force_cold_resume=True,
    )
