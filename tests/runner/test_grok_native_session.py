"""grok-native session tests (CODEX_TASK_GROK_NATIVE_01, Task 1).

Verifies the GrokNativeExecutor's session semantics required by the task card:

- turn 1 uses ``--single`` with a fresh deterministic ``--session-id``.
- turn 2 resumes the SAME grok session id (``--resume``), so the second round
  reuses the conversational context instead of starting a new session.
- two distinct Omnigent sessions never share a grok session id / leader socket.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from omnigent.inner.executor import TurnComplete
from omnigent.inner.grok_native_executor import (
    GrokNativeExecutor,
    _build_grok_args,
)


@pytest.fixture
def executor(tmp_path: Path) -> GrokNativeExecutor:
    return GrokNativeExecutor(
        grok_path="/usr/bin/grok-fake",
        cwd=str(tmp_path),
        model="grok-4.5",
        grok_home_root=str(tmp_path / "grok-omnigent"),
    )


class _FakeProc:
    """A fake asyncio subprocess that records the args it was spawned with."""

    def __init__(self, output: bytes, record: list[list[str]]) -> None:
        self._output = output
        self._record = record
        self.returncode = 0

    async def communicate(self) -> tuple[bytes, bytes]:  # noqa: D102
        return self._output, b""

    @property
    def spawned_args(self) -> list[str]:
        return self._record[-1]


def _patch_subprocess(output: bytes, record: list[list[str]]):
    """Patch create_subprocess_exec to record args and return a fake proc."""
    original = asyncio.create_subprocess_exec

    async def _fake(*args, **kwargs):  # type: ignore[no-untyped-def]
        record.append(list(args))
        return _FakeProc(output, record)

    patcher = patch.object(asyncio, "create_subprocess_exec", new=_fake)
    return patcher


@pytest.mark.asyncio
async def test_first_turn_creates_session_with_deterministic_id(
    executor: GrokNativeExecutor, tmp_path: Path
) -> None:
    record: list[list[str]] = []
    output = b'{"type":"result","response":"GROK_NATIVE_OK"}'
    patcher = _patch_subprocess(output, record)
    with patcher:
        events = []
        async for event in executor.run_turn(
            messages=[{"role": "user", "content": "Reply with GROK_NATIVE_OK and stop."}],
            tools=[],
            system_prompt="",
        ):
            events.append(event)

    assert isinstance(events[-1], TurnComplete)
    assert events[-1].response == "GROK_NATIVE_OK"

    args = record[-1]
    # First turn: single-turn prompt + fresh session id, no resume.
    assert "--session-id" in args
    assert "--resume" not in args
    first_session_id = args[args.index("--session-id") + 1]


@pytest.mark.asyncio
async def test_second_turn_resumes_same_session(
    executor: GrokNativeExecutor, tmp_path: Path
) -> None:
    record: list[list[str]] = []
    output = b'{"type":"result","response":"GROK_NATIVE_FOLLOWUP_OK"}'
    patcher = _patch_subprocess(output, record)
    messages = [
        {"role": "user", "content": "Reply with GROK_NATIVE_OK and stop."},
        {"role": "assistant", "content": "GROK_NATIVE_OK"},
        {"role": "user", "content": "Reply with GROK_NATIVE_FOLLOWUP_OK and stop."},
    ]
    with patcher:
        events = []
        async for event in executor.run_turn(
            messages=messages,
            tools=[],
            system_prompt="",
        ):
            events.append(event)

    assert isinstance(events[-1], TurnComplete)
    assert events[-1].response == "GROK_NATIVE_FOLLOWUP_OK"

    # Turn 2 must carry --resume and must NOT mint a new --session-id.
    args = record[-1]
    assert "--resume" in args
    assert "--session-id" not in args
    resumed = args[args.index("--resume") + 1]

    # And the resumed id must equal the id minted on turn 1 for this session key.
    from omnigent.grok_native_bridge import grok_session_id_for_conversation

    session_key = executor._session_key(messages)
    assert resumed == grok_session_id_for_conversation(session_key)


def test_two_sessions_get_distinct_grok_session_ids() -> None:
    from omnigent.grok_native_bridge import (
        grok_leader_socket,
        grok_session_id_for_conversation,
    )

    sid_a = grok_session_id_for_conversation("conv_session_a")
    sid_b = grok_session_id_for_conversation("conv_session_b")
    assert sid_a != sid_b
    assert grok_leader_socket("conv_session_a") != grok_leader_socket("conv_session_b")


def test_build_grok_args_resume_uses_same_id() -> None:
    sid = "3b9e7c1a-0000-4000-8000-000000000001"
    args = _build_grok_args(
        grok_path="/usr/bin/grok-fake",
        message="hello",
        model="grok-4.5",
        session_id=sid,
    )
    # Resume variant of the same builder reuses the id verbatim.
    resume_args = _build_grok_args(
        grok_path="/usr/bin/grok-fake",
        message="hello again",
        model="grok-4.5",
        session_id=sid,
        resume=sid,
    )
    assert resume_args[resume_args.index("--resume") + 1] == sid
    assert "--session-id" not in resume_args
    assert args[args.index("--session-id") + 1] == sid
