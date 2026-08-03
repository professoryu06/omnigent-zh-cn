"""Tests for codex-native model resolution from the agent spec (#3175).

``_codex_native_model_from_spec`` reads the canonical ``executor.model``
field first, falling back to ``executor.config["model"]`` for legacy
single-file specs that predate the canonical field.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from omnigent.runner.app import ResolvedSpec, _codex_native_model_from_spec
from omnigent.spec.types import AgentSpec, ExecutorSpec


def _spec(
    model: str | None = None,
    config_model: str | None = None,
) -> AgentSpec:
    """Build a minimal agent spec with optional canonical and config model."""
    config: dict[str, object] = {}
    if config_model is not None:
        config["model"] = config_model
    return AgentSpec(
        spec_version=1,
        name="codex_test",
        executor=ExecutorSpec(model=model, config=config),
    )


@pytest.mark.parametrize(
    ("model", "config_model", "expected"),
    [
        ("gpt-5.4-mini", None, "gpt-5.4-mini"),
        ("databricks-gpt-5-4-mini", None, "databricks-gpt-5-4-mini"),
        (None, None, None),
        ("", None, None),
        (None, "gpt-5.4-mini", "gpt-5.4-mini"),
        ("gpt-5.4-mini", "gpt-4o", "gpt-5.4-mini"),
    ],
    ids=[
        "canonical-model",
        "databricks-passthrough",
        "no-model",
        "empty-model",
        "config-fallback",
        "canonical-wins",
    ],
)
def test_codex_native_model_from_spec(
    model: str | None,
    config_model: str | None,
    expected: str | None,
) -> None:
    """Canonical executor.model wins; config fallback for legacy specs."""
    assert _codex_native_model_from_spec(_spec(model, config_model)) == expected


def test_codex_native_model_non_string_config_ignored() -> None:
    """A non-string config model value is ignored (returns None)."""
    spec = AgentSpec(
        spec_version=1,
        name="codex_test",
        executor=ExecutorSpec(model=None, config={"model": 42}),
    )
    assert _codex_native_model_from_spec(spec) is None


def test_codex_native_model_from_spec_none_spec() -> None:
    """A missing spec yields no model."""
    assert _codex_native_model_from_spec(None) is None


def test_codex_native_model_from_spec_resolved_wrapper() -> None:
    """A ResolvedSpec wrapper unwraps to the canonical model."""
    wrapped = ResolvedSpec(spec=_spec("gpt-5.4-mini"), workdir=Path("/tmp"))
    assert _codex_native_model_from_spec(wrapped) == "gpt-5.4-mini"
