"""
Runtime policy orchestration — engine, builder, enforcement,
ASK approval.

Pure evaluators (:class:`Policy` ABC + the concrete
``FunctionPolicy`` / ``PromptPolicy``
subclasses) live in :mod:`omnigent.policies`. This package
holds the code that actually runs during a workflow: the
composition loop, label write-through, approval parking.

The public API for callers (workflow, executor hooks) is
:class:`PolicyEngine` + :func:`build_policy_engine` +
:func:`_enforce_policy` + :func:`_await_elicitation`.
"""

from __future__ import annotations

from omnigent.runtime.policies.approval import (
    ELICITATION_PENDING_TOOL_NAME,
    _await_elicitation,
)
from omnigent.runtime.policies.builder import build_policy_engine
from omnigent.runtime.policies.enforcement import _enforce_policy
from omnigent.runtime.policies.engine import PolicyEngine

__all__ = [
    "ELICITATION_PENDING_TOOL_NAME",
    "PolicyEngine",
    "_await_elicitation",
    "_enforce_policy",
    "build_policy_engine",
]
