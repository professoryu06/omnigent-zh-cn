"""Native harness system_prompt delivery policy (apply | warn | error).

Native CLI harnesses historically discarded agent-spec ``system_prompt``
with ``del system_prompt`` and no diagnostics. This module is the shared
fail-loud contract:

* **apply** — reserved for harnesses with a verified safe delivery channel
  (not assumed for every native CLI).
* **warn** — non-empty prompt is not applied; emit a clear warning.
* **error** — when ``strict_prompt`` / ``OMNIGENT_STRICT_PROMPT=1`` is set.

Phase-1 goal: never silently drop a non-empty system prompt.
"""

from __future__ import annotations

import logging
import os
from typing import Literal

_logger = logging.getLogger(__name__)

PromptDeliveryMode = Literal["apply", "warn", "error"]


def strict_prompt_enabled(config_flag: bool | None = None) -> bool:
    """Return whether missing native prompt delivery must fail the turn.

    :param config_flag: Optional per-call strict override from executor config.
    :returns: True when fail-fast is required.
    """
    if config_flag is True:
        return True
    return os.environ.get("OMNIGENT_STRICT_PROMPT", "").strip() in {"1", "true", "TRUE", "yes"}


def note_native_system_prompt(
    harness_id: str,
    system_prompt: str | None,
    *,
    applied: bool = False,
    strict: bool | None = None,
) -> PromptDeliveryMode:
    """Record how a native harness handled agent-spec system_prompt.

    :param harness_id: Harness id, e.g. ``\"claude-native\"``.
    :param system_prompt: Prompt from the agent spec (may be empty).
    :param applied: True only when a verified channel delivered the prompt.
    :param strict: Optional override for fail-fast.
    :returns: The effective mode used (``apply``, ``warn``, or ``error``).
    :raises ValueError: When strict mode is on, prompt is non-empty, and
        ``applied`` is false.
    """
    text = system_prompt if isinstance(system_prompt, str) else ""
    if not text.strip():
        return "apply" if applied else "warn"
    if applied:
        return "apply"
    message = (
        f"{harness_id} is not applying agent spec system_prompt/prompt "
        f"(chars={len(text)}). Native harnesses must not silently drop "
        f"role instructions; use a harness that delivers prompts, set "
        f"OMNIGENT_STRICT_PROMPT=1 to fail fast, or clear the prompt."
    )
    if strict_prompt_enabled(strict):
        _logger.error(message)
        raise ValueError(message)
    _logger.warning(message)
    return "warn"
