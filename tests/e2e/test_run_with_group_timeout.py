"""Unit tests for ``run_with_group_timeout``.

Exercises the bug the helper exists to fix: a parent that exits
after spawning a long-running grandchild which holds stdout open.
Stock ``subprocess.run`` would block until the grandchild dies on
its own; the helper must fail at ~timeout instead.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time

import pytest

from tests.e2e._run_with_group_timeout import run_with_group_timeout


def test_happy_path_returns_completed_process() -> None:
    """Child completes within timeout → CompletedProcess returned."""
    result = run_with_group_timeout(
        [sys.executable, "-c", "print('ok')"],
        timeout=10,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "ok"


def test_timeout_kills_grandchild_holding_pipe(tmp_path) -> None:
    """Helper fails at ~timeout, doesn't wait for the grandchild's 30s sleep."""
    script = tmp_path / "spawn_orphan.py"
    script.write_text(
        textwrap.dedent(
            """
            import subprocess, sys
            # Grandchild inherits stdout via default fork semantics.
            subprocess.Popen(['sleep', '30'])
            print('parent exiting', flush=True)
            sys.exit(0)
            """
        )
    )

    start = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        run_with_group_timeout(
            [sys.executable, str(script)],
            timeout=2,
            capture_output=True,
            text=True,
        )
    elapsed = time.monotonic() - start

    # 2s timeout + ≤10s drain = 12s upper-bound on a working helper.
    # 8s leaves plenty of margin and still proves we didn't block 30s.
    assert elapsed < 8.0, f"helper took {elapsed:.1f}s; expected <8s. Group kill probably failed."


def test_timeout_killed_group_is_actually_dead(tmp_path) -> None:
    """Grandchild PID is unreachable within 2s of the helper raising."""
    pid_file = tmp_path / "grandchild.pid"
    script = tmp_path / "spawn_orphan.py"
    script.write_text(
        textwrap.dedent(
            f"""
            import subprocess, sys
            proc = subprocess.Popen(['sleep', '30'])
            open({str(pid_file)!r}, 'w').write(str(proc.pid))
            sys.exit(0)
            """
        )
    )

    with pytest.raises(subprocess.TimeoutExpired):
        run_with_group_timeout(
            [sys.executable, str(script)],
            timeout=2,
            capture_output=True,
            text=True,
        )

    assert pid_file.exists(), "parent didn't reach the pid_file write"
    gc_pid = int(pid_file.read_text())

    # Poll briefly: kernel may take a moment after killpg to reap.
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        try:
            os.kill(gc_pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.05)
    else:
        pytest.fail(f"grandchild PID {gc_pid} still alive 2s after killpg")


def test_capture_output_is_honored() -> None:
    result = run_with_group_timeout(
        [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
        timeout=10,
        capture_output=True,
        text=True,
    )
    assert "out" in result.stdout
    assert "err" in result.stderr


def test_start_new_session_override_rejected() -> None:
    with pytest.raises(ValueError, match="start_new_session must be True"):
        run_with_group_timeout(
            [sys.executable, "-c", "pass"],
            timeout=1,
            start_new_session=False,
        )
