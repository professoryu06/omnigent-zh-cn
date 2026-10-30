"""GrokNativeExecutor: run agent turns through the Grok CLI (headless).

Spawns ``grok --single <prompt> --output-format json`` as a subprocess per
turn, the machine interface verified against Grok CLI 0.2.106
(``grok --help`` / ``grok models`` / unauthenticated probe). Session state
lives in the isolated ``GROK_HOME`` (see :mod:`omnigent.grok_native_bridge`),
so the executor uses a deterministic per-conversation ``--session-id`` on the
first turn and ``--resume <same-id>`` on subsequent turns to maintain
conversational context across the Omnigent session without re-serialising the
full history.

Hard task-card constraints enforced here:

- deny-by-default spawn env (never Claude/Qwen/Codex/OpenCodex vars),
- forced ``NO_PROXY=127.0.0.1,localhost``,
- unauthenticated CLI output (``{"type":"error","message":"Not signed in..."}``)
  maps to a clear auth-required :class:`ExecutorError` that never leaks tokens
  (grok returns exit code 0 even when unauthenticated — output must be parsed,
  the exit code must NOT be trusted).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

from omnigent.grok_native_bridge import (
    GROK_PROXY_ENV_VAR,
    grok_leader_socket,
    grok_session_id_for_conversation,
    grok_session_home,
)
from omnigent.inner.agent_env import clean_agent_env
from omnigent.inner.datamodel import OSEnvSandboxSpec, OSEnvSpec
from omnigent.inner.executor import (
    Executor,
    ExecutorConfig,
    ExecutorError,
    ExecutorEvent,
    Message,
    TextChunk,
    TurnComplete,
)

_logger = logging.getLogger(__name__)

#: Maximum seconds to wait for a grok subprocess to complete a single turn.
_GROK_TURN_TIMEOUT_S = 600.0

#: Default model id (task card: grok-4.5).
DEFAULT_GROK_MODEL = "grok-4.5"

#: Env var override for the grok CLI binary path.
GROK_PATH_ENV_VAR = "OMNIGENT_GROK_PATH"


@dataclass
class GrokOutput:
    """Parsed result of one ``grok --output-format json`` invocation.

    :param text: The assistant's response text (``""`` when the output was an
        error or carried no text).
    :param error: Human-readable error message, or ``None`` on success.
    :param auth_required: ``True`` when the error means the user must log in
        (``Not signed in`` / ``authenticate``). The surfaced message tells the
        user what to run but never contains a token.
    """

    text: str = ""
    error: str | None = None
    auth_required: bool = False


def _unwrap_nested_json(raw: str) -> str:
    """Unwrap a JSON-string payload that grok nests under ``response``.

    grok's ``--output-format json`` result carries the assistant payload as a
    JSON string (``{"text": "...", "sessionId": "...", ...}``). When the string
    parses and carries a ``text`` member, return that clean text; otherwise
    return the raw string unchanged (non-JSON passthrough).

    :param raw: The ``response`` value from a grok result record.
    :returns: The unwrapped ``text``, or *raw* when it is not a JSON object
        with a ``text`` member.
    """
    stripped = raw.strip()
    if not stripped.startswith("{"):
        return raw
    try:
        parsed = json.loads(stripped)
    except (json.JSONDecodeError, TypeError):
        return raw
    if isinstance(parsed, dict):
        text = parsed.get("text")
        if isinstance(text, str) and text:
            return text
    return raw


def _parse_grok_output(stdout: str) -> GrokOutput:
    """Parse ``grok --output-format json`` stdout into a :class:`GrokOutput`.

    grok's ``json`` output mode emits ONE pretty-printed JSON object per run
    (``{"text": ..., "sessionId": ..., ...}`` — verified live against grok
    0.2.106; there is NO ``type`` discriminator in that mode). The
    ``streaming-json`` mode instead emits a JSONL stream of typed records
    (``{"type":"result"/"error"/...}``).

    Strategy: try parsing the WHOLE stdout as a single JSON object first
    (covers the plain ``json`` mode); if that fails, scan line-by-line for
    typed records (covers ``streaming-json`` and mixed output); if neither
    yields a usable payload, fall back to treating the raw text as the
    response.

    :param stdout: Raw stdout from the grok subprocess.
    :returns: Parsed :class:`GrokOutput`.
    """
    stripped_all = stdout.strip()
    if stripped_all:
        try:
            payload = json.loads(stripped_all)
        except (json.JSONDecodeError, TypeError):
            payload = None
        if isinstance(payload, dict):
            parsed = _grok_record_to_output(payload)
            if parsed is not None:
                return parsed
        # Whole-object parse failed or wasn't a usable record — fall through
        # to the per-line scan so streaming-json / mixed output still works.
    return _scan_grok_lines(stdout)


def _grok_record_to_output(payload: dict) -> GrokOutput | None:
    """Map one grok JSON record to a :class:`GrokOutput` (or ``None`` if skip).

    Handles both typed records (``type`` field) and the bare assistant payload
    shape grok's plain ``json`` mode emits (``text`` / ``error`` members with
    no ``type``).
    """
    kind = payload.get("type")
    if kind == "error":
        message = payload.get("message")
        if isinstance(message, str) and message:
            low = message.lower()
            auth_required = (
                "not signed in" in low or "authenticate" in low or "login" in low
            )
            return GrokOutput(text="", error=message, auth_required=auth_required)
        return None
    if kind == "result":
        response = payload.get("response")
        if isinstance(response, str) and response:
            # grok's --output-format json nests the assistant payload as a
            # JSON string under "response" in some modes (verified live).
            return GrokOutput(text=_unwrap_nested_json(response))
        nested = response if isinstance(response, dict) else None
        nested_text = nested.get("text") if nested else None
        if isinstance(nested_text, str) and nested_text:
            return GrokOutput(text=nested_text)
        return None
    if kind is None:
        # Bare assistant payload from plain ``json`` mode: {"text": ...}.
        text = payload.get("text")
        if isinstance(text, str) and text:
            return GrokOutput(text=text)
        error = payload.get("error")
        if isinstance(error, str) and error:
            return GrokOutput(text="", error=error)
    return None


def _scan_grok_lines(stdout: str) -> GrokOutput:
    """Scan stdout line-by-line for typed JSON records (streaming-json mode)."""
    text_parts: list[str] = []
    error: str | None = None
    auth_required = False
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except (json.JSONDecodeError, TypeError):
            text_parts.append(stripped)
            continue
        if not isinstance(payload, dict):
            text_parts.append(stripped)
            continue
        parsed = _grok_record_to_output(payload)
        if parsed is None:
            # Unknown typed record — keep any text fields, else skip.
            for key in ("text", "content"):
                value = payload.get(key)
                if isinstance(value, str) and value:
                    text_parts.append(value)
            continue
        if parsed.error is not None:
            error = parsed.error
            auth_required = parsed.auth_required
            continue
        if parsed.text:
            text_parts.append(parsed.text)
    if error is not None:
        return GrokOutput(text="", error=error, auth_required=auth_required)
    return GrokOutput(text="\n".join(text_parts).strip())


def _build_grok_args(
    grok_path: str,
    message: str,
    *,
    model: str | None = None,
    session_id: str | None = None,
    resume: str | None = None,
    leader_socket: str | None = None,
    cwd: str | None = None,
) -> list[str]:
    """Build the argument list for a grok subprocess call.

    :param grok_path: Path to the ``grok`` CLI binary.
    :param message: The user message text.
    :param model: Model id (``-m``); defaults to grok's own default.
    :param session_id: Fresh session id for the first turn (``--session-id``).
    :param resume: Session id to resume on subsequent turns (``--resume``).
        Exactly one of *session_id* / *resume* should be set per turn.
    :param leader_socket: Per-session ``--leader-socket`` path (isolation).
    :param cwd: Working directory (``--cwd``).
    :returns: A list of CLI arguments.
    """
    args = [grok_path, "--single", message, "--output-format", "json"]
    if model:
        args.extend(["-m", model])
    if session_id and not resume:
        args.extend(["--session-id", session_id])
    if resume:
        args.extend(["--resume", resume])
    if leader_socket:
        args.extend(["--leader-socket", leader_socket])
    if cwd:
        args.extend(["--cwd", cwd])
    return args


def _extract_last_user_message(messages: list[Message]) -> str:
    """Extract the text of the most recent user message from the message list."""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, list):
                parts: list[str] = []
                for block in content:
                    if isinstance(block, dict):
                        text = block.get("text")
                        if isinstance(text, str):
                            parts.append(text)
                if parts:
                    return "\n".join(parts)
            elif isinstance(content, str):
                return content
    return ""


class GrokNativeExecutor(Executor):
    """Executor that drives the Grok CLI headless as a subprocess.

    Each turn runs ``grok --single "<message>" --output-format json`` and
    parses the JSON output. The per-conversation grok session id is derived
    deterministically from the Omnigent conversation id (UUIDv5), so the first
    turn mints it with ``--session-id`` and every later turn resumes with
    ``--resume <same-id>`` — the second round reuses the same conversational
    context instead of opening a fresh session.
    """

    def __init__(
        self,
        grok_path: str | None = None,
        cwd: str | None = None,
        model: str | None = None,
        grok_home_root: str | None = None,
        os_env: OSEnvSpec | None = None,
    ) -> None:
        """Construct a :class:`GrokNativeExecutor`.

        :param grok_path: Path to the ``grok`` CLI binary. ``None`` searches
            ``PATH`` (or ``OMNIGENT_GROK_PATH``).
        :param cwd: Working directory for the subprocess. ``None`` uses the
            current directory.
        :param model: Model id override. ``None`` uses ``grok-4.5``.
        :param grok_home_root: Root of the isolated grok home tree. ``None``
            uses :data:`omnigent.grok_native_bridge.DEFAULT_GROK_HOME_ROOT`.
        :param os_env: OS environment spec (declared passthrough honored).
        """
        configured = os.environ.get(GROK_PATH_ENV_VAR, "").strip()
        self._grok_path = grok_path or configured or shutil.which("grok") or "grok"
        self._cwd = cwd or os.getcwd()
        self._model = model or DEFAULT_GROK_MODEL
        if grok_home_root is not None:
            self._grok_home_root = grok_home_root
        else:
            from omnigent.grok_native_bridge import grok_home_root as _resolve_root

            self._grok_home_root = _resolve_root()
        self._os_env = os_env or OSEnvSpec(
            type="caller_process",
            sandbox=OSEnvSandboxSpec(type="none"),
        )
        # Session key of the most recent turn (used by _build_spawn_env when
        # called standalone).
        self._active_session_key = "conv_unnamed"

    def _session_key(self, messages: list[Message]) -> str:
        """Derive a stable Omnigent session key from the message list."""
        for msg in messages:
            sid = msg.get("session_id")
            if isinstance(sid, str) and sid:
                return sid
        return str(
            hash(tuple((m.get("role", ""), str(m.get("content", ""))[:200]) for m in messages))
        )

    def _has_assistant_history(self, messages: list[Message]) -> bool:
        """Return whether *messages* contain an assistant reply (i.e. not round 1)."""
        return any(m.get("role") == "assistant" for m in messages)

    def supports_streaming(self) -> bool:
        """Return True — the CLI supports ``--output-format streaming-json``."""
        return True

    def handles_tools_internally(self) -> bool:
        """Return True — grok executes tools inside its own agent loop."""
        return True

    def _build_spawn_env(self, session_key: str | None = None) -> dict[str, str]:
        """The deny-by-default env handed to the grok subprocess.

        Same isolation as :func:`omnigent.grok_native_bridge.build_grok_native_spawn_env`
        but rooted at *this* executor's ``grok_home_root`` (tests point it at a
        tmp dir). ``GROK_HOME`` is the per-session home under
        ``<root>/sessions/<session-id>``; ``NO_PROXY`` is forced to
        ``127.0.0.1,localhost``.
        """
        key = session_key or self._active_session_key
        session_id = grok_session_id_for_conversation(key)
        session_home = Path(self._grok_home_root) / "sessions" / session_id
        session_home.mkdir(parents=True, exist_ok=True)
        proc_env = clean_agent_env(
            allow_prefixes=("GROK_", "XAI_"),
            extra_allowed=("NO_PROXY",),
        )
        proc_env["GROK_HOME"] = str(session_home)
        # Proxy isolation: strip every inherited proxy variable (upper and
        # lower case) first, then force NO_PROXY and re-inject the trio only
        # when OMNIGENT_GROK_PROXY is explicitly set. Without the strip, a
        # parent's HTTP_PROXY/HTTPS_PROXY/ALL_PROXY would leak into the Grok
        # child (clean_agent_env's base allow-list passes them through).
        for _key in (
            "HTTP_PROXY",
            "http_proxy",
            "HTTPS_PROXY",
            "https_proxy",
            "ALL_PROXY",
            "all_proxy",
            "NO_PROXY",
            "no_proxy",
        ):
            proc_env.pop(_key, None)
        proc_env["NO_PROXY"] = "127.0.0.1,localhost"
        # Mirror the bridge's auth symlink so a per-session home sees the
        # user's completed login even on the first turn.
        root_auth = Path(self._grok_home_root) / "auth.json"
        if root_auth.is_file() and not (session_home / "auth.json").exists():
            try:
                (session_home / "auth.json").symlink_to(root_auth)
            except OSError:
                pass
        proxy = os.environ.get(GROK_PROXY_ENV_VAR, "").strip()
        if proxy:
            proc_env["HTTPS_PROXY"] = proxy
            proc_env["HTTP_PROXY"] = proxy
            proc_env["ALL_PROXY"] = proxy
        return proc_env

    async def run_turn(
        self,
        messages: list[Message],
        tools: list[dict[str, object]],
        system_prompt: str,
        config: ExecutorConfig | None = None,
    ) -> AsyncIterator[ExecutorEvent]:
        """Run one agent turn by spawning ``grok --single ... --output-format json``.

        :param messages: Conversation history from Omnigent.
        :param tools: Tool schemas (grok uses its own tools internally).
        :param system_prompt: System prompt (used by grok internally).
        :param config: Per-turn config (model override, etc.).
        :yields: ``TextChunk`` and ``TurnComplete``, or ``ExecutorError``.
        """
        _logger.debug(
            "GrokNativeExecutor.run_turn: %d messages, tools=%d, prompt_len=%d",
            len(messages),
            len(tools),
            len(system_prompt),
        )

        user_text = _extract_last_user_message(messages)
        if not user_text:
            yield TurnComplete(response=None)
            return

        model = (config.model if config else None) or self._model
        session_key = self._session_key(messages)
        self._active_session_key = session_key
        session_id = grok_session_id_for_conversation(session_key)
        resume = session_id if self._has_assistant_history(messages) else None

        leader_socket = str(grok_leader_socket(session_key))
        args = _build_grok_args(
            grok_path=self._grok_path,
            message=user_text,
            model=model,
            session_id=None if resume else session_id,
            resume=resume,
            leader_socket=leader_socket,
            cwd=self._cwd,
        )
        proc_env = self._build_spawn_env(session_key)

        _logger.debug("Grok subprocess: %s", " ".join(args))

        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=proc_env,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=_GROK_TURN_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            _logger.warning("Grok subprocess timed out after %ss", _GROK_TURN_TIMEOUT_S)
            yield ExecutorError(
                message=f"Grok subprocess timed out after {_GROK_TURN_TIMEOUT_S}s",
                retryable=True,
            )
            return
        except FileNotFoundError:
            yield ExecutorError(
                message=(
                    f"Grok CLI not found at '{self._grok_path}'. "
                    "Install the Grok CLI or set OMNIGENT_GROK_PATH to its absolute path."
                ),
                retryable=False,
            )
            return
        except OSError as exc:
            yield ExecutorError(
                message=f"Failed to spawn grok subprocess: {exc}",
                retryable=True,
            )
            return

        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")

        parsed = _parse_grok_output(stdout)
        if parsed.error is not None:
            # grok exits 0 even when unauthenticated — the JSON payload is the
            # only reliable signal. Never surface tokens in the error message.
            if parsed.auth_required:
                _logger.warning("Grok is not authenticated for session %s", session_key)
                yield ExecutorError(
                    message=(
                        "Grok is not authenticated. Run the login command in WSL:\n"
                        "  GROK_HOME=/home/administrator/.grok-omnigent "
                        "grok login --device-code"
                    ),
                    retryable=False,
                )
            else:
                yield ExecutorError(
                    message=f"Grok error: {parsed.error[:500]}",
                    retryable=True,
                )
            return

        if proc.returncode != 0:
            error_msg = stderr.strip() or stdout.strip()
            _logger.warning("Grok exited with code %d: %s", proc.returncode, error_msg[:500])
            yield ExecutorError(
                message=f"Grok exited with code {proc.returncode}: {error_msg[:500]}",
                retryable=True,
            )
            return

        response_text = parsed.text
        if response_text:
            yield TextChunk(text=response_text)
        yield TurnComplete(response=response_text or None)

    async def close_session(self, session_key: str) -> None:
        """Release resources for a specific session.

        The grok session persists in its isolated GROK_HOME and can be resumed
        later via ``--resume``. Nothing to clean up here beyond logging.
        """
        _logger.debug("Closed grok-native session %s", session_key)
