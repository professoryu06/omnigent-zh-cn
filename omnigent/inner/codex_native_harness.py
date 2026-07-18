"""``harness: codex-native`` wrap for the native Codex TUI."""

from __future__ import annotations

from fastapi import FastAPI

from omnigent.inner.codex_native_executor import CodexNativeExecutor
from omnigent.inner.executor import Executor
from omnigent.runtime.harnesses._executor_adapter import ExecutorAdapter


def _build_codex_native_executor() -> Executor:
    """
    Construct the native Codex bridge executor.

    :returns: A :class:`CodexNativeExecutor` configured from the
        harness spawn environment.
    """
    return CodexNativeExecutor()


def create_app() -> FastAPI:
    """
    Build the ``codex-native`` harness FastAPI app.

    :returns: The FastAPI app from :class:`ExecutorAdapter`.
    """
    adapter = ExecutorAdapter(executor_factory=_build_codex_native_executor)
    return adapter.build()
