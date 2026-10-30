"""Native harness system_prompt delivery policy (phase 1: fail-loud).

Native CLI harnesses historically discarded agent-spec ``system_prompt``
with ``del system_prompt`` and no diagnostics. This module is the shared
fail-loud contract for **phase 1** (mitigation only — not full delivery):

* **apply** — reserved for harnesses with a verified safe delivery channel.
  Not implemented for native CLIs in phase 1 (no blind argv injection).
* **warn** — non-empty prompt is not applied; emit a clear warning that
  never includes the prompt body (only ``chars=N``).
* **error** — when ``OMNIGENT_STRICT_PROMPT`` is enabled; fail before the
  user message is injected into the native terminal.

Phase-1 goal: never silently drop a non-empty system prompt.
Phase-2 (open): per-harness capability matrix and safe apply channels.

Strict mode is controlled only by the process environment variable
``OMNIGENT_STRICT_PROMPT`` (``1`` / ``true`` / ``yes``). There is no
per-agent YAML field in this phase.
"""

from __future__ import annotations

import logging
import os
from typing import Literal

_logger = logging.getLogger(__name__)

PromptDeliveryMode = Literal["apply", "warn", "error"]

_STRICT_TRUTHY = frozenset({"1", "true", "TRUE", "yes", "YES", "on", "ON"})


def strict_prompt_enabled() -> bool:
    """Return whether missing native prompt delivery must fail the turn.

    Controlled only by ``OMNIGENT_STRICT_PROMPT`` in the process environment.
    """
    return os.environ.get("OMNIGENT_STRICT_PROMPT", "").strip() in _STRICT_TRUTHY


def note_native_system_prompt(
    harness_id: str,
    system_prompt: str | None,
    *,
    applied: bool = False,
) -> PromptDeliveryMode:
    """Record how a native harness handled agent-spec system_prompt.

    Log lines include ``chars=N`` only — never the prompt body.

    :param harness_id: Harness id, e.g. ``\"claude-native\"``.
    :param system_prompt: Prompt from the agent spec (may be empty).
    :param applied: True only when a verified channel delivered the prompt.
    :returns: The effective mode used (``apply``, ``warn``, or ``error``).
    :raises ValueError: When ``OMNIGENT_STRICT_PROMPT`` is on, prompt is
        non-empty, and ``applied`` is false.
    """
    text = system_prompt if isinstance(system_prompt, str) else ""
    if not text.strip():
        return "apply" if applied else "warn"
    if applied:
        return "apply"
    # Never interpolate the prompt body into logs (secrets / role text).
    message = (
        f"{harness_id} is not applying agent spec system_prompt/prompt "
        f"(chars={len(text)}). Native harnesses must not silently drop "
        f"role instructions; use a harness that delivers prompts, set "
        f"OMNIGENT_STRICT_PROMPT=1 to fail fast, or clear the prompt. "
        f"(phase-1 fail-loud only; prompt apply is not implemented.)"
    )
    if strict_prompt_enabled():
        _logger.error(message)
        raise ValueError(message)
    _logger.warning(message)
    return "warn"
