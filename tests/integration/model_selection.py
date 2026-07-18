"""Model selection helpers for the integration journey suite."""

from __future__ import annotations

from tests import _model_pools


def resolve_default_model(model: str, harness_name: str) -> str:
    """Resolve the workflow/default model for one integration harness.

    Codex opts out of hash-spreading because its CI leg is pinned to the
    higher-headroom model after lower-headroom GPT models hit gateway 429s.

    :param model: Model from ``--model``, e.g. ``"databricks-gpt-5-5"``.
    :param harness_name: Harness under test, e.g. ``"codex"``.
    :returns: The resolved model to register on the inline test agent.
    """
    return _model_pools.resolve_model(model, spread=harness_name != "codex")
