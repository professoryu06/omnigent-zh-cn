"""C-2747: single-file YAML must honor nested executor.config.harness."""

from __future__ import annotations

from pathlib import Path

from omnigent.inner.loader import _parse_executor_spec, load_agent_def
from omnigent.spec import load


def test_parse_executor_spec_reads_nested_config_harness() -> None:
    """Nested ``config.harness`` is folded into ``ExecutorSpec.harness``."""
    parsed = _parse_executor_spec(
        {
            "type": "omnigent",
            "config": {"harness": "codex-native"},
            "model": "databricks-gpt-5-4-mini",
        }
    )
    assert parsed is not None
    assert parsed.harness == "codex-native"
    assert parsed.model == "databricks-gpt-5-4-mini"


def test_parse_executor_spec_flat_harness_wins_over_nested() -> None:
    """Flat ``harness`` takes precedence over nested ``config.harness``."""
    parsed = _parse_executor_spec(
        {
            "harness": "claude-native",
            "config": {"harness": "codex-native"},
            "model": "databricks-claude-sonnet-4",
        }
    )
    assert parsed is not None
    assert parsed.harness == "claude-native"


def test_load_agent_def_nested_harness_not_dropped() -> None:
    """``load_agent_def`` keeps nested harness on the inner ExecutorSpec."""
    agent = load_agent_def(
        {
            "name": "my-codex-agent",
            "prompt": "You are a helpful coding agent.",
            "executor": {
                "type": "omnigent",
                "config": {"harness": "codex-native"},
                "model": "databricks-gpt-5-4-mini",
            },
        }
    )
    assert agent.executor is not None
    assert agent.executor.harness == "codex-native"


def test_spec_load_nested_harness_not_replaced_by_model_prefix(tmp_path: Path) -> None:
    """``omnigent.spec.load`` must not silently swap codex-native for openai-agents.

    Pre-fix: ``executor.config.harness: codex-native`` with a
    ``databricks-gpt-*`` model produced ``harness_kind == openai-agents``.
    """
    path = tmp_path / "agent.yaml"
    path.write_text(
        "name: my-codex-agent\n"
        "prompt: You are a helpful coding agent.\n"
        "executor:\n"
        "  type: omnigent\n"
        "  config:\n"
        "    harness: codex-native\n"
        "  model: databricks-gpt-5-4-mini\n",
        encoding="utf-8",
    )
    spec = load(path)
    assert spec.executor.config.get("harness") == "codex-native", spec.executor.config
    # Runtime-observable harness must be codex-native (not optional/None-soft).
    assert spec.executor.harness_kind == "codex-native"
