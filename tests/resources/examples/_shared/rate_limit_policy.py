"""Example: rate-limiting policy factory.

This is a stateful policy factory — call it with a ``limit`` argument to get
a policy callable that denies after that many tool calls per turn.  The
returned callable exposes a ``reset_turn()`` method so ``FunctionPolicy``
can reset the counter between turns.

The returned callable follows the Service Policies V0 contract:
``fn(event) -> {"result": ..., "reason": ...}``.

YAML usage::

    policies:
      rate_limit:
        type: function
        on: [tool_call]
        callable: tests.resources.examples._shared.rate_limit_policy.max_tool_calls_per_turn
        factory_params:
          limit: 15
"""

from omnigent.policies.schema import PolicyCallable, PolicyEvent, PolicyResponse


def max_tool_calls_per_turn(limit: int = 10) -> PolicyCallable:
    """Factory: returns a policy callable that denies after *limit* tool calls per turn."""
    state = {"count": 0}

    def evaluate(event: PolicyEvent) -> PolicyResponse:
        """V0 policy evaluator.

        :param event: V0 event dict with ``type``, ``target``,
            ``data``, ``context`` keys.
        :returns: V0 decision dict.
        """
        if event.get("type") == "tool_call":
            state["count"] += 1
            if state["count"] > limit:
                return {
                    "result": "DENY",
                    "reason": f"Exceeded max tool calls per turn ({limit})",
                }
        return {"result": "ALLOW"}

    def reset_turn():
        state["count"] = 0

    evaluate.reset_turn = reset_turn
    return evaluate
