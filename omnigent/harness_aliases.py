"""Shared harness-name alias helpers.

Keep user-facing shorthand spellings at the edges while the rest of
Omnigent continues to use canonical harness identifiers internally.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from omnigent.harness_plugins import harness_aliases, harness_modules, native_harnesses

HARNESS_ALIASES: dict[str, str] = harness_aliases()

# Canonical native-CLI harness spellings. These harnesses type messages into
# a resident terminal process and mirror their transcript back to Omnigent, so
# the runner must not replay Omnigent history or treat a completed queue call
# as a full in-process model turn. ``AgentSpec.harness_kind`` returns these
# canonical spellings for native agents, so no executor-type aliasing is needed
# here.
NATIVE_HARNESSES: frozenset[str] = native_harnesses()

# How the runner should drive a resolved harness: in-process / CLI-subprocess
# SDK path vs native TUI terminal path. ``unknown`` covers test/custom ids.
HarnessDispatchMode = Literal["sdk", "native", "unknown"]


@dataclass(frozen=True, slots=True)
class HarnessDispatch:
    """Single source of truth for runner harness routing.

    :param raw_harness: Pre-canonicalize spelling from the spec/override,
        e.g. ``"codex"`` or ``"native-codex"``.
    :param canonical_harness: Canonical id after alias fold, e.g.
        ``"codex"`` or ``"codex-native"``. Bare ``codex`` stays ``codex``
        (never rewritten to ``codex-native``).
    :param is_native: ``True`` only for native-CLI harnesses that need a
        terminal pane (``codex-native``, ``claude-native``, …).
    :param module: Import path for the harness FastAPI wrap, e.g.
        ``"omnigent.inner.codex_harness"``, or ``None`` when unregistered.
    :param dispatch_mode: ``"sdk"`` for process-manager harnesses,
        ``"native"`` for terminal-first harnesses, ``"unknown"`` otherwise.
    """

    raw_harness: str
    canonical_harness: str
    is_native: bool
    module: str | None
    dispatch_mode: HarnessDispatchMode


def resolve_harness_dispatch(
    harness: str | None,
    *,
    override: str | None = None,
) -> HarnessDispatch:
    """Resolve how the runner must dispatch a harness spelling.

    Session create, turn dispatch, and terminal ensure endpoints share this
    so bare ``codex`` cannot silently take the ``codex-native`` terminal path.

    :param harness: Spec / executor harness id, e.g. ``"codex"``.
    :param override: Optional per-session harness override; wins when set.
    :returns: :class:`HarnessDispatch` with canonical id, native flag, and
        registered module path.
    """
    raw = (override if override is not None else harness) or ""
    canonical = canonicalize_harness(raw) or raw or "unknown"
    native = is_native_harness(canonical)
    module = harness_modules().get(canonical)
    if native:
        mode: HarnessDispatchMode = "native"
    elif module is not None:
        mode = "sdk"
    else:
        mode = "unknown"
    return HarnessDispatch(
        raw_harness=raw or canonical,
        canonical_harness=canonical,
        is_native=native,
        module=module,
        dispatch_mode=mode,
    )


def canonicalize_harness(harness: str | None) -> str | None:
    """Return the canonical harness identifier for *harness*.

    Unknown names are returned unchanged so callers can still produce
    their normal validation error messages.
    """
    if harness is None:
        return None
    # Namespaced generic-ACP ids (``acp:<slug>``) canonicalize to the base
    # ``acp`` harness for identity / validity / module resolution / model-family
    # checks. The ``<slug>`` selecting the concrete agent is carried separately in
    # the spec's ``executor.config`` and read by ``_build_acp_spawn_env``.
    if harness.startswith("acp:"):
        return "acp"
    return HARNESS_ALIASES.get(harness, harness)


def is_claude_sdk_harness_name(harness: str | None) -> bool:
    """Return ``True`` for the canonical Claude SDK harness and aliases."""
    return canonicalize_harness(harness) == "claude-sdk"


def is_native_harness(harness: str | None) -> bool:
    """Return whether *harness* is a native CLI harness.

    Native harnesses boot a vendor TUI in a terminal and route user messages
    into that running process. Accepts the canonical native spellings that
    :attr:`AgentSpec.harness_kind` returns plus their reversed aliases.

    :param harness: A harness id, e.g. ``"codex-native"`` or ``"claude_sdk"``;
        ``None`` returns ``False``.
    :returns: ``True`` for a native CLI harness, else ``False``.
    """
    if harness is None:
        return False
    return (canonicalize_harness(harness) or harness) in NATIVE_HARNESSES


def native_terminal_name(harness: str | None) -> str | None:
    """Return the tmux terminal short-name a native harness runs its CLI in.

    Native CLI panes are keyed ``(conversation_id, <short-name>, "main")`` in the
    terminal registry, where the short name is the canonical native harness id
    with the ``-native`` suffix dropped — e.g. ``"claude-native"`` -> ``"claude"``,
    ``"native-codex"`` -> ``"codex"``, ``"opencode-native"`` -> ``"opencode"``.

    :param harness: A harness id (canonical or reversed alias), e.g.
        ``"cursor-native"``; ``None`` or a non-native harness returns ``None``.
    :returns: The terminal short-name, e.g. ``"cursor"``, or ``None`` when
        *harness* is not a native CLI harness.
    """
    if not is_native_harness(harness):
        return None
    canonical = canonicalize_harness(harness) or harness
    # Canonical native ids are ``<name>-native``; some accepted aliases keep the
    # reversed ``native-<name>`` spelling (not all are folded by
    # ``canonicalize_harness``), so strip either affix.
    return canonical.removesuffix("-native").removeprefix("native-")
