"""Native harness system_prompt delivery policy (phase 1: fail-loud).

Native CLI harnesses historically discarded agent-spec ``system_prompt``
with ``del system_prompt`` and no diagnostics. This module is the shared
fail-loud contract:

* **apply** — reserved for harnesses with a verified safe delivery channel.
  Only ``codex-native`` fresh threads qualify (phase 2).
* **warn** — non-empty prompt is not applied; emit a clear warning that
  never includes the prompt body (only ``chars=N``).
* **error** — when ``OMNIGENT_STRICT_PROMPT`` is enabled; fail before the
  user message is injected into the native terminal.

Strict mode is controlled only by the process environment variable
``OMNIGENT_STRICT_PROMPT`` (``1`` / ``true`` / ``yes`` / ``on``).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Literal

_logger = logging.getLogger(__name__)

PromptDeliveryMode = Literal["apply", "warn", "error"]

_STRICT_TRUTHY = frozenset({"1", "true", "TRUE", "yes", "YES", "on", "ON"})

# Phase-1/2 capability matrix. Only codex-native has a verified safe
# channel (private CODEX_HOME/config.toml developer_instructions).
# Every other native harness stays warn/error — no unverified apply.
NATIVE_PROMPT_CAPABILITY_MATRIX: dict[str, PromptDeliveryMode] = {
    "codex-native": "apply",
    "claude-native": "warn",
    "cursor-native": "warn",
    "hermes-native": "warn",
    "opencode-native": "warn",
    "goose-native": "warn",
    "kimi-native": "warn",
    "kiro-native": "warn",
    "qwen-native": "warn",
    "antigravity-native": "warn",
    "pi-native": "warn",
}


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

    :param harness_id: Harness id, e.g. ``"claude-native"``.
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
        f"OMNIGENT_STRICT_PROMPT=1 to fail fast, or clear the prompt."
    )
    if strict_prompt_enabled():
        _logger.error(message)
        raise ValueError(message)
    _logger.warning(message)
    return "warn"


# ── Phase 2 receipt API ────────────────────────────────────────────

_RECEIPT_FILENAME = "prompt_delivery.receipt.json"
_RECEIPT_HARNESS_ID = "codex-native"
_RECEIPT_CHANNEL = "codex_home_config_toml"


def clear_prompt_receipt(bridge_dir: Path) -> None:
    """Remove any prior delivery receipt under *bridge_dir*.

    Called on every app-server start before deciding whether this launch
    writes a fresh receipt. Must not raise for missing files; OS errors
    propagate so callers cannot mark the session applied after a failed
    clear.

    :param bridge_dir: Per-session bridge directory.
    """
    for old in bridge_dir.glob("*.receipt.json"):
        old.unlink(missing_ok=True)


def write_prompt_receipt(
    bridge_dir: Path,
    *,
    harness_id: str,
    prompt: str,
    channel: str = _RECEIPT_CHANNEL,
) -> None:
    """Write a delivery receipt to *bridge_dir* after successful config write.

    The receipt contains only metadata and a SHA-256 digest — never the
    prompt body. Prior receipts are cleaned before writing. Empty/blank
    prompts only clear stale receipts and do not write a new file.

    :param bridge_dir: Per-session bridge directory.
    :param harness_id: Harness id, e.g. ``"codex-native"``.
    :param prompt: The prompt that was delivered (hashed, not stored).
    :param channel: Delivery channel identifier.
    """
    text = prompt if isinstance(prompt, str) else ""
    clear_prompt_receipt(bridge_dir)
    if not text.strip():
        return
    receipt: dict[str, Any] = {
        "harness_id": harness_id,
        "channel": channel,
        "chars": len(text),
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
    }
    receipt_path = bridge_dir / _RECEIPT_FILENAME
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def read_prompt_receipt(bridge_dir: Path) -> dict[str, Any] | None:
    """Read the delivery receipt from *bridge_dir*, or None if missing/corrupt.

    Never raises on missing or corrupt files — returns None so callers
    fall back to the Phase 1 warn/error path. Invalid UTF-8, illegal JSON,
    and non-object payloads all degrade to None.
    """
    receipt_path = bridge_dir / _RECEIPT_FILENAME
    if not receipt_path.exists():
        return None
    try:
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None


def receipt_matches_prompt(receipt: dict[str, Any] | None, prompt: str | None) -> bool:
    """Return True only when *receipt* fully matches *prompt* metadata.

    Requires fixed harness id, fixed channel, character count, and
    SHA-256 digest. Missing fields, wrong types, or digest mismatch
    all return False (not applied).
    """
    if receipt is None or not prompt or not prompt.strip():
        return False
    if receipt.get("harness_id") != _RECEIPT_HARNESS_ID:
        return False
    if receipt.get("channel") != _RECEIPT_CHANNEL:
        return False
    if receipt.get("chars") != len(prompt):
        return False
    expected = hashlib.sha256(prompt.encode()).hexdigest()
    return receipt.get("sha256") == expected
