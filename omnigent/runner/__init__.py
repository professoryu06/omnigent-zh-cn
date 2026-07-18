"""Runner package — execution-side counterpart to the Omnigent server.

The runner is the data-plane component that owns harness subprocesses,
OS environments, MCP connections, sub-agent harnesses, the async-work
inbox, and every priority-1-5 tool resolution from the harness contract
(see ``designs/SERVER_HARNESS_CONTRACT.md`` and ``designs/RUNNER.md``).

The runner exposes a FastAPI app implementing the harness API subset
(``POST /v1/sessions``, ``POST /v1/sessions/{id}/events``,
``GET /v1/sessions/{id}/stream``, cancel, elicitations,
``GET /health``). Local server-to-runner traffic reaches that app
through the WebSocket tunnel.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnigent.runner.app import create_runner_app

__all__ = [
    "create_runner_app",
]


def __getattr__(name: str) -> object:
    """Lazily resolve ``create_runner_app`` (PEP 562).

    An eager import pulls in ``runner.app`` and the whole FastAPI stack,
    which the stdlib-only ``runner.identity`` (imported at each spawn
    boundary) would then pay — ~0.5s on the sandbox-launcher
    hot path. Deferring keeps submodule imports cheap while preserving
    ``from omnigent.runner import create_runner_app``.

    :param name: Attribute being accessed, e.g. ``"create_runner_app"``.
    :returns: The resolved attribute.
    :raises AttributeError: If *name* is not a package export.
    """
    if name == "create_runner_app":
        from omnigent.runner.app import create_runner_app

        return create_runner_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
