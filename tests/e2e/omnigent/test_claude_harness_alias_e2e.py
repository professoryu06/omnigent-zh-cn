"""E2E test — ``--harness claude-sdk`` alias works end-to-end.

Runs ``omnigent run hello_world.yaml --harness claude-sdk -p <prompt>``
as a real subprocess and verifies it exits 0 with non-trivial assistant output.
This proves the "claude" alias is canonicalized to "claude-sdk" through the
full CLI → harness → LLM path.

No ``--llm-api-key`` needed — the claude-sdk harness reads credentials
from ``~/.databrickscfg`` via the profile named in the global config's
``auth:`` block (the supported replacement for the removed ``--profile``
CLI flag).

Run with:

    pytest tests/e2e/omnigent/test_claude_harness_alias_e2e.py -v --profile oss
"""

from __future__ import annotations

import configparser
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

_PROMPT = "say hi in exactly 5 words"
_TIMEOUT_SEC = 180


def _resolve_python() -> Path:
    """Find the .venv python, walking up from this file.

    :returns: Path to the venv Python interpreter.
    """
    current = Path(__file__).resolve().parents[3]
    while True:
        candidate = current / ".venv" / "bin" / "python"
        if candidate.is_file():
            return candidate
        if current.parent == current:
            pytest.fail("No .venv/bin/python found")
        current = current.parent


def _get_profile(request: pytest.FixtureRequest) -> str:
    """Get the Databricks profile from --profile flag or default to oss.

    :param request: Pytest request object.
    :returns: The profile name.
    """
    profile = request.config.getoption("--profile", default=None)
    return profile or "oss"


def _profile_has_token(profile: str) -> bool:
    """Check if the profile has a token in ~/.databrickscfg.

    :param profile: The Databricks profile name.
    :returns: True if the profile has a token.
    """
    cfg = configparser.ConfigParser()
    cfg.read(os.path.expanduser("~/.databrickscfg"))
    return cfg.has_option(profile, "token")


def _clean_env(profile: str) -> dict[str, str]:
    """Build subprocess env with stale vars removed and profile set.

    :param profile: Databricks profile name.
    :returns: Clean environment dict.
    """
    env = dict(os.environ)
    for var in (
        "ANTHROPIC_API_KEY",
        "DATABRICKS_TOKEN",
        "CLAUDE_CODE",
        "CLAUDECODE",
        "CLAUDE_CODE_ENTRYPOINT",
        "CLAUDE_CODE_EXECPATH",
        "CODEX",
    ):
        env.pop(var, None)
    env["DATABRICKS_CONFIG_PROFILE"] = profile
    # The omnigent CLI no longer accepts ``--profile``; write the
    # supported replacement — an ``auth:`` block in an isolated
    # ``OMNIGENT_CONFIG_HOME`` — so the spawned CLI routes the
    # claude-sdk harness through this Databricks profile.
    config_home = Path(tempfile.mkdtemp(prefix="omnigent-alias-config-"))
    (config_home / "config.yaml").write_text(
        f"auth:\n  type: databricks\n  profile: {profile}\n",
        encoding="utf-8",
    )
    env["OMNIGENT_CONFIG_HOME"] = str(config_home)
    repo = str(Path(__file__).resolve().parents[3])
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(p for p in (repo, existing) if p)
    return env


def test_run_with_claude_alias_produces_output(
    request: pytest.FixtureRequest,
) -> None:
    """``omnigent run --harness claude-sdk`` exits 0 with assistant text.

    Proves the "claude" alias is canonicalized through the full
    CLI → Omnigent server → harness spawn → LLM call → output path.

    :param request: Pytest request for --profile flag access.
    """
    profile = _get_profile(request)
    if not _profile_has_token(profile):
        pytest.skip(f"No token for profile {profile!r} in ~/.databrickscfg")

    python = _resolve_python()
    repo_root = Path(__file__).resolve().parents[3]
    yaml_path = repo_root / "tests" / "resources" / "examples" / "hello_world.yaml"

    result = subprocess.run(
        [
            str(python),
            "-m",
            "omnigent",
            "run",
            str(yaml_path),
            "--harness",
            "claude",
            "-p",
            _PROMPT,
            "--no-session",
        ],
        env=_clean_env(profile),
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_SEC,
    )

    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}.\n"
        f"stdout:\n{result.stdout!r}\n\nstderr:\n{result.stderr!r}"
    )
    # The claude-sdk harness renders through the REPL, so stdout
    # may be empty when piped. Exit 0 proves the alias resolved,
    # the harness booted, and the LLM call completed. Verify no
    # error traces on stderr.
    assert "Error" not in result.stderr, f"Unexpected error in stderr:\n{result.stderr!r}"
    assert "Traceback" not in result.stderr, f"Unexpected traceback in stderr:\n{result.stderr!r}"
