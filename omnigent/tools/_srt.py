"""Shared ``srt`` sandbox wrap for subprocess-based tool execution.

Callers that spawn subprocesses and want OS-level sandboxing use
:func:`wrap_with_srt` to prepend ``srt`` when it's installed and
sandboxing is enabled, or pass the command through unchanged
otherwise.

One in-tree consumer today:

- :class:`~omnigent.tools.local.LocalPythonTool` — wraps its
  ``python _runner.py`` spawn. Stateful tools pass a per-call
  ``settings_file`` path that whitelists their ToolState dir for
  writes.

Stdio MCP servers (``omnigent/tools/mcp.py``) used to go
through this helper too, but the wrap was removed in step 7 of
the harness contract migration — srt's default policy blocks
outbound network, which broke every useful MCP server (Glean,
Slack, GitHub, UC, etc. all need outbound HTTPS). Stdio MCPs
now spawn unsandboxed, matching the legacy inner stack at
``omnigent/inner/mcp_tools.py`` (which has never sandboxed
stdio MCPs). Future per-MCP sandboxing — if reintroduced —
should flow through the ``omnigent/environments/`` primitive
with explicit outbound-host allowlists, not srt-defaults.

The PTY-mode wrap used by :class:`~omnigent.terminals.shell.Shell`
is a different shape (srt's Node library API + the ``_srt_shell.mjs``
wrapper, not the ``srt`` CLI) and is not covered here — that path
needs a PTY-compatible entry, which the ``srt -c`` CLI doesn't
provide.
"""

from __future__ import annotations

import shlex
import shutil


def is_srt_available() -> bool:
    """
    Return ``True`` when the ``srt`` CLI is on ``PATH``.

    Separate from :func:`wrap_with_srt` so callers can probe once
    at construction time (cheap on module import) and cache the
    result — the wrap itself runs on every subprocess spawn and
    shouldn't hit ``shutil.which`` each time.

    :returns: Whether ``srt`` resolves via the current ``PATH``.
    """
    return shutil.which("srt") is not None


def wrap_with_srt(
    cmd: list[str],
    *,
    sandbox_enabled: bool,
    srt_available: bool,
    settings_file: str | None = None,
) -> list[str]:
    """
    Prepend ``srt`` to *cmd* when sandboxing is enabled AND available.

    When either condition is false, returns *cmd* unchanged so the
    caller spawns the plain subprocess. This is the project's
    "sandbox-if-possible, subprocess-otherwise" contract — any
    caller that spawns a subprocess and wants optional srt wrapping
    should go through this function rather than hand-rolling the
    same 3-line branch.

    When wrapping, the returned form is ``srt [-s <settings>] -c
    <quoted>``. The ``-c`` flag takes a single quoted command string
    (like ``bash -c``), so *cmd* is joined with :func:`shlex.join`
    to preserve word boundaries / embedded spaces.

    :param cmd: The unwrapped command argv, e.g.
        ``["python", "/path/to/_runner.py"]`` or
        ``["npx", "some-mcp-server", "--flag"]``.
    :param sandbox_enabled: Operator-level opt-in for sandboxing
        this caller. The spec-level knob
        (:attr:`SandboxConfig.enabled`, etc.) flows into this arg.
    :param srt_available: Whether ``srt`` is on ``PATH``. Typically
        cached from :func:`is_srt_available` at construction time.
    :param settings_file: Absolute path to a per-call srt settings
        JSON file, or ``None`` for the default srt sandbox.
        Settings files are used when a caller needs a writable path
        that srt's defaults deny (e.g. :class:`LocalPythonTool`'s
        per-call ToolState directory). MCP stdio callers usually
        pass ``None`` — the MCP server lives inside its own
        filesystem expectations and srt's permissive read defaults
        + the caller's ``cwd`` cover the common case.
    :returns: The wrapped command argv, or *cmd* unchanged when
        not wrapping.
    """
    if not (sandbox_enabled and srt_available):
        return cmd
    base = ["srt"]
    if settings_file is not None:
        base += ["-s", settings_file]
    return [*base, "-c", shlex.join(cmd)]
