"""``subprocess.run`` variant that SIGKILLs the whole process group on timeout.

Stock ``subprocess.run(timeout=N)`` only kills the immediate child.
Grandchildren that inherited stdout/stderr keep the captured pipes
open, so the caller can wedge for many minutes past N. E2E tests
spawn ``omnigent run`` (AP server + runner + harness as
grandchildren) and hit this in CI.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
from typing import Any


def run_with_group_timeout(
    args: list[str],
    *,
    timeout: float,
    **kwargs: Any,
) -> subprocess.CompletedProcess[Any]:
    """Like ``subprocess.run`` but SIGKILLs the whole group on timeout.

    ``start_new_session=True`` is forced; ``capture_output=True`` is
    expanded. On ``TimeoutExpired``, the captured stdout/stderr up
    to that point are attached to the exception.
    """
    if kwargs.pop("capture_output", False):
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
    if kwargs.pop("start_new_session", True) is not True:
        raise ValueError("start_new_session must be True for run_with_group_timeout")

    proc = subprocess.Popen(args, start_new_session=True, **kwargs)
    # PGID == PID under start_new_session. Capture eagerly: by the
    # time the timeout fires, the leader may already be reaped and
    # ``getpgid(proc.pid)`` would raise ProcessLookupError -- but
    # killpg(pid) still reaches any surviving group members.
    pgid = proc.pid
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(pgid, signal.SIGKILL)
        # Drain pipes now that the group is dead. Bounded so a
        # truly stuck FD doesn't translate one hang into another.
        try:
            stdout, stderr = proc.communicate(timeout=10)
            exc.stdout = stdout
            exc.stderr = stderr
        except subprocess.TimeoutExpired:
            pass
        raise
    return subprocess.CompletedProcess(args, proc.returncode, stdout, stderr)
