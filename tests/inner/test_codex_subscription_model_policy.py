"""Omnigent Codex subscription model policy: gpt-5.6-luna + reasoning max.

Product contract (CODEX_TASK_MODEL_1_LUNA_MAX):
- OpenAI subscription path defaults to ``gpt-5.6-luna`` (not mini / sol).
- Unset reasoning_effort defaults to ``max`` on the subscription path.
- Explicit model / effort from cfg or constructor still win.
- Gateway / Databricks defaults stay independent of this product pin.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

from omnigent.inner.codex_executor import (
    _DATABRICKS_CODEX_DEFAULT_MODEL,
    _OPENAI_CODEX_DEFAULT_MODEL,
    _OPENAI_CODEX_DEFAULT_REASONING_EFFORT,
    CodexExecutor,
)
from omnigent.inner.databricks_executor import DatabricksCredentials
from omnigent.inner.executor import ExecutorConfig, TurnComplete
from omnigent.reasoning_effort import CODEX_EFFORTS


def _run(coro: Any) -> Any:
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


@dataclass
class _FakeAppSession:
    scripted_turns: list[list[object]]
    calls: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        self.calls = []

    async def run_turn(self, **kwargs: Any):
        assert self.calls is not None
        self.calls.append(kwargs)
        for event in self.scripted_turns.pop(0):
            yield event

    async def close(self) -> None:
        return None

    async def interrupt_turn(self) -> bool:
        return True


def _messages() -> list[dict[str, str]]:
    return [{"role": "user", "content": "hi", "session_id": "s-policy"}]


def test_subscription_default_constants_are_luna_max() -> None:
    assert _OPENAI_CODEX_DEFAULT_MODEL == "gpt-5.6-luna"
    assert _OPENAI_CODEX_DEFAULT_REASONING_EFFORT == "max"
    assert "max" in CODEX_EFFORTS
    # Never the forbidden silent-fallback ids as product constants.
    assert _OPENAI_CODEX_DEFAULT_MODEL != "gpt-5.6-sol"
    assert _OPENAI_CODEX_DEFAULT_MODEL != "gpt-5.4-mini"
    assert "sol" not in _OPENAI_CODEX_DEFAULT_MODEL
    assert "mini" not in _OPENAI_CODEX_DEFAULT_MODEL


def test_subscription_run_turn_defaults_to_luna_and_max_effort() -> None:
    async def _t() -> None:
        fake = _FakeAppSession([[TurnComplete(response="ok")]])
        executor = CodexExecutor(
            codex_path="/bin/echo",
            app_session_factory=lambda **_kwargs: fake,
        )
        events = [e async for e in executor.run_turn(_messages(), [], "sys")]
        assert events
        assert fake.calls is not None
        call = fake.calls[0]
        assert call["model"] == "gpt-5.6-luna"
        assert call["reasoning_effort"] == "max"

    _run(_t())


def test_subscription_does_not_fallback_to_sol_or_mini() -> None:
    async def _t() -> None:
        fake = _FakeAppSession([[TurnComplete(response="ok")]])
        executor = CodexExecutor(
            codex_path="/bin/echo",
            app_session_factory=lambda **_kwargs: fake,
        )
        async for _ in executor.run_turn(_messages(), [], "sys"):
            pass
        assert fake.calls is not None
        model = fake.calls[0]["model"]
        assert model != "gpt-5.6-sol"
        assert model != "gpt-5.4-mini"
        assert "sol" not in model
        assert model == "gpt-5.6-luna"

    _run(_t())


def test_explicit_model_and_effort_still_win_on_subscription() -> None:
    async def _t() -> None:
        fake = _FakeAppSession([[TurnComplete(response="ok")]])
        executor = CodexExecutor(
            model="gpt-5.5",
            codex_path="/bin/echo",
            app_session_factory=lambda **_kwargs: fake,
        )
        cfg = ExecutorConfig(extra={"reasoning_effort": "high"})
        async for _ in executor.run_turn(_messages(), [], "sys", config=cfg):
            pass
        assert fake.calls is not None
        assert fake.calls[0]["model"] == "gpt-5.5"
        assert fake.calls[0]["reasoning_effort"] == "high"

    _run(_t())


def test_cfg_model_override_wins_over_product_default() -> None:
    async def _t() -> None:
        fake = _FakeAppSession([[TurnComplete(response="ok")]])
        executor = CodexExecutor(
            codex_path="/bin/echo",
            app_session_factory=lambda **_kwargs: fake,
        )
        cfg = ExecutorConfig(model="gpt-5.5")
        async for _ in executor.run_turn(_messages(), [], "sys", config=cfg):
            pass
        assert fake.calls is not None
        assert fake.calls[0]["model"] == "gpt-5.5"

    _run(_t())


def test_databricks_gateway_default_model_unchanged() -> None:
    async def _t() -> None:
        fake = _FakeAppSession([[TurnComplete(response="ok")]])
        with patch(
            "omnigent.inner.codex_executor._read_databrickscfg",
            return_value=DatabricksCredentials(
                host="https://example.cloud.databricks.com",
                token="[REDACTED]",
            ),
        ):
            executor = CodexExecutor(
                codex_path="/bin/echo",
                gateway=True,
                app_session_factory=lambda **_kwargs: fake,
            )
            async for _ in executor.run_turn(_messages(), [], "sys"):
                pass
        assert fake.calls is not None
        assert fake.calls[0]["model"] == _DATABRICKS_CODEX_DEFAULT_MODEL
        # Gateway keeps None effort when unset (no product max pin).
        assert fake.calls[0]["reasoning_effort"] is None

    _run(_t())


def test_neutral_gateway_still_requires_explicit_model() -> None:
    with patch(
        "omnigent.inner.codex_executor._read_databrickscfg",
        return_value=None,
    ):
        try:
            CodexExecutor(
                codex_path="/bin/echo",
                gateway=True,
                gateway_host="https://gw.example.com",
                base_url_override="https://gw.example.com/v1",
                gateway_auth_command="printf %s [REDACTED]",
            )
            raised = False
        except OSError as exc:
            raised = True
            assert "requires a model" in str(exc)
    assert raised
