"""C-2746: codex-native must read ``spec.executor.model``."""

from __future__ import annotations

from omnigent.runner.app import _codex_native_model_from_spec
from omnigent.spec.types import AgentSpec, ExecutorSpec


def test_codex_native_model_prefers_executor_model_over_missing_config() -> None:
    """Single-file agents populate ``executor.model``, not ``config.model``."""
    spec = AgentSpec(
        spec_version=1,
        name="my-codex",
        executor=ExecutorSpec(
            type="omnigent",
            model="databricks-gpt-5-4-mini",
            config={"harness": "codex-native", "profile": ""},
        ),
    )
    assert _codex_native_model_from_spec(spec) == "databricks-gpt-5-4-mini"


def test_codex_native_model_falls_back_to_config_model() -> None:
    """Bundles that only store model under config still work."""
    spec = AgentSpec(
        spec_version=1,
        name="my-codex",
        executor=ExecutorSpec(
            type="omnigent",
            model=None,
            config={"harness": "codex-native", "model": "from-config-only"},
        ),
    )
    assert _codex_native_model_from_spec(spec) == "from-config-only"


def test_codex_native_model_none_when_unset() -> None:
    """No model in either slot returns None (provider default at launch)."""
    spec = AgentSpec(
        spec_version=1,
        name="my-codex",
        executor=ExecutorSpec(
            type="omnigent",
            model=None,
            config={"harness": "codex-native", "profile": ""},
        ),
    )
    assert _codex_native_model_from_spec(spec) is None
