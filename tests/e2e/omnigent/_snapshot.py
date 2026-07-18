"""Snapshot loader + comparator for Omnigent Phase 0 characterization tests.

Snapshots are JSON files under ``tests/e2e/omnigent/snapshots/``
and capture the *structural* observations a test makes about a
live Omnigent run. They are the golden-master contract the
Phase 0 design requires: written against current Omnigent,
re-run unchanged in later phases to prove the integration
doesn't change observable behavior.

This helper distinguishes three comparator kinds so LLM
non-determinism doesn't cause flakes:

- ``"exact"`` — the observed value must equal the snapshot
  value. Used for statuses, field presence, tool names,
  known-constant strings.
- ``"contains"`` — the observed string must contain the snapshot
  substring. Used for error messages or partial banners.
- ``"min_length"`` — the observed string must be at least
  ``value`` characters. Used for free-form assistant text where
  the exact content is LLM-dependent.

A snapshot file is a JSON object mapping field name → comparator
entry; each entry is ``{"kind": "...", "value": ...}``. A single
``compare_snapshot(path, observed)`` call returns a list of
human-readable diffs; empty list means pass.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# Directory (relative to this module) where snapshot JSONs live.
# Tests reference snapshots by their pytest test name so each test
# owns exactly one file — makes update-churn tractable in review.
SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"

# Valid comparator kinds. Kept as a frozenset so the loader can
# fail loud if a snapshot file introduces an unknown kind before
# the comparator is implemented.
_VALID_KINDS: frozenset[str] = frozenset({"exact", "contains", "min_length"})

ComparatorKind = Literal["exact", "contains", "min_length"]


@dataclass(frozen=True)
class SnapshotField:
    """
    One field's comparator entry as loaded from a snapshot JSON.

    :param kind: Which comparator to apply, e.g. ``"exact"``.
    :param value: The reference value. For ``"exact"``, any JSON
        type that supports ``==``. For ``"contains"``, a string
        substring. For ``"min_length"``, a non-negative int
        minimum-length threshold.
    """

    kind: ComparatorKind
    value: object


def load_snapshot(test_name: str) -> dict[str, SnapshotField]:
    """
    Load the JSON snapshot for a single test.

    :param test_name: The test's base name, used to locate the
        file at ``snapshots/<test_name>.json``. Example:
        ``"test_per_harness_claude_sdk"``.
    :returns: Mapping of observed-field name to
        :class:`SnapshotField`.
    :raises FileNotFoundError: If the snapshot file is missing —
        Phase 0 requires every test to ship with a captured
        snapshot, so the missing file is a bug, not a
        first-run side effect.
    :raises ValueError: If the JSON contains a comparator kind
        outside :data:`_VALID_KINDS`.
    """
    path = SNAPSHOTS_DIR / f"{test_name}.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"Snapshot not found: {path}. Phase 0 tests ship with "
            f"their snapshots captured against current Omnigent."
        )
    raw = json.loads(path.read_text())
    out: dict[str, SnapshotField] = {}
    for field_name, entry in raw.items():
        kind = entry["kind"]
        if kind not in _VALID_KINDS:
            raise ValueError(
                f"Snapshot {path} field {field_name!r} uses unknown "
                f"comparator kind {kind!r}; valid kinds: {sorted(_VALID_KINDS)}."
            )
        out[field_name] = SnapshotField(kind=kind, value=entry["value"])
    return out


def compare_snapshot(
    test_name: str,
    observed: dict[str, object],
) -> list[str]:
    """
    Compare observed fields against the named snapshot.

    :param test_name: The snapshot name — see :func:`load_snapshot`.
        Example: ``"test_per_harness_claude_sdk"``.
    :param observed: Dict of observed values the test gathered
        from the live Omnigent run, e.g.
        ``{"exit_code": 0, "assistant_text": "Hello there..."}``.
    :returns: A list of human-readable mismatch descriptions.
        Empty list means all comparators passed; callers assert
        ``compare_snapshot(...) == []``.
    """
    snapshot = load_snapshot(test_name)
    diffs: list[str] = []
    # Any snapshot field missing from the observed dict is a
    # structural regression — the test no longer produces the
    # observation the snapshot was written against.
    for field_name, entry in snapshot.items():
        if field_name not in observed:
            diffs.append(
                f"{field_name}: missing from observed; "
                f"snapshot expected kind={entry.kind} value={entry.value!r}"
            )
            continue
        diff = _compare_field(field_name, entry, observed[field_name])
        if diff is not None:
            diffs.append(diff)
    return diffs


def _compare_field(
    field_name: str,
    entry: SnapshotField,
    observed: object,
) -> str | None:
    """
    Apply one comparator and return a mismatch string or None.

    :param field_name: The observed-field name for diff labels,
        e.g. ``"exit_code"``.
    :param entry: The :class:`SnapshotField` from the snapshot
        JSON.
    :param observed: The live-captured value for this field.
    :returns: ``None`` on match. Otherwise a human-readable
        one-line mismatch description suitable for appending to
        an assertion failure message.
    """
    if entry.kind == "exact":
        if observed != entry.value:
            return f"{field_name}: exact mismatch; expected {entry.value!r}, got {observed!r}"
        return None
    if entry.kind == "contains":
        if not isinstance(observed, str):
            return f"{field_name}: contains requires str observed; got {type(observed).__name__}"
        needle = entry.value
        if not isinstance(needle, str):
            return (
                f"{field_name}: contains snapshot value must be str; got {type(needle).__name__}"
            )
        if needle not in observed:
            return (
                f"{field_name}: contains mismatch; expected "
                f"substring {needle!r} in observed of length "
                f"{len(observed)}"
            )
        return None
    if entry.kind == "min_length":
        if not isinstance(observed, str):
            return f"{field_name}: min_length requires str observed; got {type(observed).__name__}"
        threshold = entry.value
        if not isinstance(threshold, int):
            return (
                f"{field_name}: min_length snapshot value must be int; "
                f"got {type(threshold).__name__}"
            )
        if len(observed) < threshold:
            return (
                f"{field_name}: min_length mismatch; expected "
                f">= {threshold} chars, got {len(observed)}"
            )
        return None
    # Should be impossible — load_snapshot already validates
    # kinds — but fail loud rather than silently pass.
    raise ValueError(f"Unreachable: unknown kind {entry.kind!r}")
