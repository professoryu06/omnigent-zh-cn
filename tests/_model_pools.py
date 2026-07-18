"""Deterministic model load-balancing for real-LLM tests.

:func:`resolve_model` spreads pooled models across same-tier siblings
(stable hash of the test nodeid; off unless
``OMNIGENT_TEST_MODEL_SPREAD=1``, set in e2e CI) and rotates to a
different model on each ``@pytest.mark.llm_flaky`` rerun.
``@pytest.mark.model_pinned`` opts a test out of both. Pools are
overridable via ``OMNIGENT_TEST_MODEL_POOL_<KEY>`` (comma-separated).

The current-test context (nodeid, attempt, pinned) is stamped by the
``pytest_runtest_setup`` hook in ``tests/conftest.py``, so helpers deep
inside fixtures can resolve without a ``request`` object.
"""

from __future__ import annotations

import os
import zlib
from dataclasses import dataclass

_SPREAD_ENV_VAR = "OMNIGENT_TEST_MODEL_SPREAD"
_POOL_ENV_PREFIX = "OMNIGENT_TEST_MODEL_POOL_"

# Interchangeable same-tier models (mini is its own pool so spreading
# never downgrades a test). Keys are the env-override suffixes.
_DEFAULT_POOLS: dict[str, tuple[str, ...]] = {
    "GPT": ("databricks-gpt-5-4", "databricks-gpt-5-5"),
    "GPT_MINI": ("databricks-gpt-5-4-mini", "databricks-gpt-5-mini"),
    "CLAUDE": ("databricks-claude-sonnet-4-6", "databricks-claude-opus-4-6"),
}

# Per-provider rotation order for llm_flaky reruns. Crosses tiers:
# the goal is "pass on ANY model", not workload parity.
_RETRY_CHAINS: dict[str, tuple[str, ...]] = {
    "openai": (
        "databricks-gpt-5-4",
        "databricks-gpt-5-5",
        "databricks-gpt-5-4-mini",
        "databricks-gpt-5-mini",
    ),
    "anthropic": (
        "databricks-claude-sonnet-4-6",
        "databricks-claude-opus-4-6",
    ),
}

_POOL_PROVIDER: dict[str, str] = {
    "GPT": "openai",
    "GPT_MINI": "openai",
    "CLAUDE": "anthropic",
}


@dataclass
class _TestContext:
    """The currently-running test, as stamped by the conftest hook.

    :param nodeid: Hash key for spreading, e.g.
        ``"tests/e2e/test_foo.py::test_bar[codex]"``.
    :param attempt: Zero-based rerun attempt (``0`` = first run).
    :param pinned: ``@pytest.mark.model_pinned`` present; disables
        spreading and rotation.
    """

    nodeid: str
    attempt: int
    pinned: bool


_CURRENT: _TestContext | None = None


def set_current_test(nodeid: str | None, *, attempt: int = 0, pinned: bool = False) -> None:
    """Stamp (or clear, with ``nodeid=None``) the current test context.

    :param nodeid: Pytest nodeid of the test about to run, or ``None``
        to clear.
    :param attempt: Zero-based rerun attempt number for this run.
    :param pinned: Whether the test opted out via ``model_pinned``.
    """
    global _CURRENT
    _CURRENT = None if nodeid is None else _TestContext(nodeid, attempt, pinned)


def current_attempt() -> int:
    """Zero-based rerun attempt of the running test (``0`` outside one)."""
    return _CURRENT.attempt if _CURRENT is not None else 0


def spread_enabled() -> bool:
    """Whether hash-spreading is enabled via ``OMNIGENT_TEST_MODEL_SPREAD``."""
    return os.environ.get(_SPREAD_ENV_VAR, "").strip().lower() in {"1", "true", "yes"}


def _pool_members(pool_key: str) -> tuple[str, ...]:
    """The (env-overridable) member list for *pool_key*, e.g. ``"GPT"``."""
    raw = os.environ.get(_POOL_ENV_PREFIX + pool_key, "")
    members = tuple(m.strip() for m in raw.split(",") if m.strip())
    return members or _DEFAULT_POOLS[pool_key]


def _pool_key_of(model: str) -> str | None:
    """The balance-pool key *model* belongs to, or ``None`` if unpooled.

    Checks env-overridden pools AND built-in defaults, so a model
    removed via env override still classifies (and rotates on retry).
    """
    for key in _DEFAULT_POOLS:
        if model in _pool_members(key) or model in _DEFAULT_POOLS[key]:
            return key
    return None


def _is_drained(model: str) -> bool:
    """Whether *model* was removed from its pool via env override.

    A model that appears in a pool's built-in defaults but not in the
    pool's active (env-overridden) members has been deliberately
    drained — e.g. a rate-limited endpoint — and retry rotation must
    not route traffic back to it.
    """
    key = _pool_key_of(model)
    return key is not None and model not in _pool_members(key)


def _retry_chain(model: str, pool_key: str) -> tuple[str, ...]:
    """Ordered retry chain for *model*; env-added pool members are appended.

    Drained models (see :func:`_is_drained`) are excluded, except
    *model* itself, which must stay in the chain so rotation has a
    stable index to start from.

    :param model: The resolved base model, e.g. ``"databricks-gpt-5-4"``.
    :param pool_key: The model's balance-pool key, e.g. ``"GPT"``.
    """
    chain = list(_RETRY_CHAINS[_POOL_PROVIDER[pool_key]])
    for member in _pool_members(pool_key):
        if member not in chain:
            chain.append(member)
    if model not in chain:
        chain.append(model)
    return tuple(m for m in chain if m == model or not _is_drained(m))


def resolve_model(
    model: str,
    *,
    key: str | None = None,
    attempt: int | None = None,
    spread: bool = True,
) -> str:
    """Resolve *model* to the model the current test should actually use.

    Unpooled models pass through unchanged. Pooled models get spread
    (``crc32(key) % len(pool)`` when enabled) then rotated along the
    provider retry chain when *attempt* > 0; ``model_pinned`` skips both.

    :param model: Model as written in the test / spec / probe,
        e.g. ``"databricks-gpt-5-4"``.
    :param key: Hash key for spreading; defaults to the running test's
        nodeid. Pass an explicit key for session-scoped resolutions
        that must not depend on which test runs first.
    :param attempt: Zero-based retry attempt; defaults to the running
        test's rerunfailures attempt.
    :param spread: ``False`` for explicitly-chosen models (marker pins):
        skips spreading but keeps retry rotation.
    :returns: The model name to use, e.g. ``"databricks-gpt-5-5"``.
    """
    pool_key = _pool_key_of(model)
    if pool_key is None:
        return model
    if _CURRENT is not None and _CURRENT.pinned:
        return model

    resolved = model
    hash_key = key if key is not None else (_CURRENT.nodeid if _CURRENT is not None else None)
    if spread and spread_enabled() and hash_key is not None:
        pool = _pool_members(pool_key)
        resolved = pool[zlib.crc32(hash_key.encode()) % len(pool)]

    effective_attempt = attempt if attempt is not None else current_attempt()
    if effective_attempt > 0:
        chain = _retry_chain(resolved, pool_key)
        resolved = chain[(chain.index(resolved) + effective_attempt) % len(chain)]
    return resolved
