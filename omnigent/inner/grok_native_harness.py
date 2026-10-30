"""``harness: grok-native`` wrap.

Thin module exposing :func:`create_app` — the entry point the shared
:mod:`omnigent.runtime.harnesses._runner` invokes after the parent process
resolves ``"grok-native"`` to this module via
:data:`omnigent.runtime.harnesses._HARNESS_MODULES`.

Wraps a :class:`omnigent.inner.grok_native_executor.GrokNativeExecutor` via the
shared :class:`~omnigent.runtime.harnesses._executor_adapter.ExecutorAdapter`,
mirroring the headless ``hermes`` harness wrap
(:mod:`omnigent.inner.hermes_harness`) — grok-native is a headless CLI
subprocess harness, NOT a native terminal/TUI harness (the task card forbids
faking a native terminal and calling tmux/PTY on Windows).

Env vars read at startup:

- ``HARNESS_GROK_MODEL``: model identifier, e.g. ``"grok-4.5"``. ``None``
  falls back to the executor default (``grok-4.5``).
- ``HARNESS_GROK_CWD``: working directory the subprocess runs in. ``None``
  falls back to ``os.getcwd()``.
- ``OMNIGENT_GROK_PATH``: absolute path to the ``grok`` CLI binary. ``None``
  searches ``PATH``.
- ``OMNIGENT_GROK_HOME_ROOT``: root of the isolated grok home tree. ``None``
  uses the bridge default (``/home/administrator/.grok-omnigent``).
- ``HARNESS_GROK_OS_ENV``: JSON-encoded :class:`OSEnvSpec`. ``None`` falls
  back to ``caller_process + sandbox=none``.
"""

from __future__ import annotations

import json
import logging
import os

from fastapi import FastAPI

from omnigent.inner.datamodel import OSEnvSandboxSpec, OSEnvSpec
from omnigent.inner.executor import Executor
from omnigent.inner.grok_native_executor import GrokNativeExecutor
from omnigent.runtime.harnesses._executor_adapter import ExecutorAdapter

_logger = logging.getLogger(__name__)

_ENV_MODEL = "HARNESS_GROK_MODEL"
_ENV_CWD = "HARNESS_GROK_CWD"
_ENV_OS_ENV = "HARNESS_GROK_OS_ENV"


def _resolve_os_env() -> OSEnvSpec:
    """Resolve the inner-executor :class:`OSEnvSpec` from env config."""
    raw = os.environ.get(_ENV_OS_ENV, "").strip()
    if raw:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            _logger.warning("%s is not valid JSON (%s); falling back to default os_env", _ENV_OS_ENV, exc)
            payload = None
        if isinstance(payload, dict):
            sandbox_payload = payload.get("sandbox")
            sandbox = (
                OSEnvSandboxSpec(**sandbox_payload) if isinstance(sandbox_payload, dict) else None
            )
            return OSEnvSpec(
                type=str(payload.get("type", "caller_process")),
                cwd=payload.get("cwd"),
                sandbox=sandbox,
                fork=bool(payload.get("fork", False)),
            )
    return OSEnvSpec(
        type="caller_process",
        cwd=None,
        sandbox=OSEnvSandboxSpec(type="none"),
        fork=False,
    )


def _build_grok_native_executor() -> Executor:
    """Construct a :class:`GrokNativeExecutor` from env-var config."""
    return GrokNativeExecutor(
        cwd=os.environ.get(_ENV_CWD) or os.environ.get("OMNIGENT_RUNNER_WORKSPACE"),
        model=os.environ.get(_ENV_MODEL),
        os_env=_resolve_os_env(),
    )


def create_app() -> FastAPI:
    """Build the grok-native harness's FastAPI app (required entry point)."""
    adapter = ExecutorAdapter(executor_factory=_build_grok_native_executor)
    return adapter.build()
