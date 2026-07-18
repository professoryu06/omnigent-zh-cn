"""End-to-end regression test: ``omnigent codex --resume`` restores history.

The codex-native sibling of ``test_claude_native_cli_resume_e2e``. Codex
resumes by a different mechanism than Claude — it re-opens a thread via its
app-server ``thread_id`` rather than a ``--resume`` CLI flag — so the only
harness-agnostic way to verify a resume actually restored history is the
outcome check used here: teach the model a passphrase, resume the
conversation, send a recall message **through the server** (the web-UI path),
and confirm the model answers with the passphrase.

Codex-native already gated its runner-side terminal auto-create on
host-spawned sessions (the gate Claude was missing), so this test is a
guard/confirmation rather than a fix — it pins that ``omnigent codex
--resume`` keeps restoring history, parallel to the Claude regression test.
The shared flow lives in :func:`assert_native_cli_resume_restores_history`
(see ``tests/e2e/_native_resume_helpers.py``).

Environment requirements (why this is opt-in, not pure-CI)
----------------------------------------------------------
* **Opt-in only**: set ``OMNIGENT_E2E_CODEX_NATIVE=1`` to run. codex-native
  needs an interactive Codex login anchored to the real ``$HOME``; the binary
  may be present in CI but unauthenticated, which would hang the TUI. The
  env-var gate keeps it out of CI; a developer with a logged-in Codex opts in.
* Run it like the host codex-native test::

    OMNIGENT_E2E_CODEX_NATIVE=1 \
    .venv/bin/python -m pytest tests/e2e/test_codex_native_cli_resume_e2e.py \
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
# claude resume test) and resolved by pytest fixture discovery.

# Opt-in only — see module docstring. Binary presence is not a sufficient gate
# (present-but-unauthenticated hangs the TUI), so require the explicit env var.
pytestmark = pytest.mark.skipif(
    os.environ.get("OMNIGENT_E2E_CODEX_NATIVE") != "1" or shutil.which("codex") is None,
    reason=(
        "codex-native CLI resume e2e needs an interactive Codex login; set "
        "OMNIGENT_E2E_CODEX_NATIVE=1 (and have `codex` installed + logged in) to run"
    ),
)


def test_codex_native_cli_resume_restores_history(
    resume_test_server: str,
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    """
    Resuming a codex-native conversation via the CLI restores its history.

    Drives ``omnigent codex --server …`` (gateway routing via the
    config-home auth block from the pytest ``--profile``) to teach Codex a
    passphrase, resumes the conversation, sends a recall message through the
    server, and asserts Codex replies with the passphrase — proving the
    resumed thread loaded the prior turn instead of starting empty.

    :param resume_test_server: Base URL of the allow-list-free test server.
    :param tmp_path: Per-test temp dir.
    :param request: Pytest request — reads ``--profile`` for the LLM gateway.
    """
    profile = request.config.getoption("--profile")
    assert profile, "this test requires --profile (e.g. --profile oss) for the LLM gateway"
    assert_native_cli_resume_restores_history(
        harness="codex",
        server=resume_test_server,
        profile=profile,
        tmp_path=tmp_path,
    )
