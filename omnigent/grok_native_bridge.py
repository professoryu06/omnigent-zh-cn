"""Session isolation + spawn-env bridge for the grok-native harness.

The task card (CODEX_TASK_GROK_NATIVE_01) requires every grok-native session
to own an isolated ``GROK_HOME`` rooted at
``/home/administrator/.grok-omnigent[/sessions/<session-id>]``, its own leader
socket, its own grok session id, and a deny-by-default subprocess env that
never inherits Claude / Qwen / Codex / OpenCodex credentials.

This module is the single place those isolation decisions live:

- :func:`grok_session_id_for_conversation` — deterministic UUIDv5 of the
  Omnigent conversation id (stable across resumes; never stored).
- :func:`grok_session_home` — per-session ``GROK_HOME`` (base + ``/sessions/``).
- :func:`grok_leader_socket` — per-session ``--leader-socket`` path.
- :func:`build_grok_native_spawn_env` — the deny-by-default env handed to the
  ``grok`` subprocess (base allowlist + ``GROK_``/``XAI_`` families +
  forced ``NO_PROXY``).
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from omnigent.inner.agent_env import BASE_ALLOW_EXACT, BASE_ALLOW_PREFIXES, clean_agent_env

#: Root of the isolated grok home tree (task card §进程与认证隔离).
#: Every session gets ``<root>/sessions/<session-id>`` as its GROK_HOME so two
#: concurrent sessions never share auth/leader state.
DEFAULT_GROK_HOME_ROOT = "/home/administrator/.grok-omnigent"

#: Env var overriding the grok home root (tests point this at a tmp dir).
GROK_HOME_ROOT_ENV_VAR = "OMNIGENT_GROK_HOME_ROOT"

#: Env var carrying an optional outbound proxy for the grok subprocess
#: (HTTPS_PROXY/HTTP_PROXY/ALL_PROXY). Only set when TUN bridging needs it.
GROK_PROXY_ENV_VAR = "OMNIGENT_GROK_PROXY"

#: Fixed namespace for deriving a stable grok ``--session-id`` from an Omnigent
#: conversation id (UUIDv5). Never change it — it would orphan every existing
#: grok session (resume would mint a new id and lose history).
_GROK_SESSION_NAMESPACE = uuid.UUID("7d3f6a9b-2c4e-5f81-a0b6-3e8d9c1f4a72")

#: Prefix families the grok subprocess legitimately reads. ``GROK_`` covers
#: home/config knobs; ``XAI_`` covers grok's own API-key auth family.
_GROK_ALLOW_PREFIXES = ("GROK_", "XAI_")


def grok_home_root() -> str:
    """Return the configured grok home root (env override for tests)."""
    return os.environ.get(GROK_HOME_ROOT_ENV_VAR, DEFAULT_GROK_HOME_ROOT)


def grok_session_id_for_conversation(conversation_id: str) -> str:
    """Return the deterministic grok ``--session-id`` for an Omnigent conversation.

    UUIDv5 of the conversation id: stable across resumes (recomputable, never
    stored) and a valid UUID (grok's ``--session-id`` requires one). The
    executor launches a fresh session with ``--session-id <this>`` and later
    restores it with ``--resume <this>`` so the second round reuses the same
    conversational context.

    :param conversation_id: Omnigent conversation id, e.g. ``"conv_abc123"``.
    :returns: A stable UUID string usable as grok's session id.
    """
    return str(uuid.uuid5(_GROK_SESSION_NAMESPACE, conversation_id))


def grok_session_home(conversation_id: str) -> Path:
    """Return the per-session ``GROK_HOME`` for an Omnigent conversation.

    ``<root>/sessions/<session-id>`` — distinct per conversation, so two
    sessions never share auth files or the leader socket.

    :param conversation_id: Omnigent conversation id.
    :returns: Absolute per-session grok home directory path.
    """
    session_id = grok_session_id_for_conversation(conversation_id)
    return Path(grok_home_root()) / "sessions" / session_id


def grok_leader_socket(conversation_id: str) -> Path:
    """Return the per-session ``--leader-socket`` path for a conversation.

    The default leader socket lives at ``~/.grok/leader.sock`` (shared across
    every grok process on the host). We point each session at its own socket
    under its isolated ``GROK_HOME`` so concurrent grok-native sessions never
    contend on the shared socket and never touch the user's real ``~/.grok``.

    :param conversation_id: Omnigent conversation id.
    :returns: Absolute per-session leader socket path.
    """
    return grok_session_home(conversation_id) / "leader.sock"


#: Name of grok's auth file inside GROK_HOME (verified via ``grok inspect``
#: against the isolated home; the login command writes it there).
_AUTH_FILE = "auth.json"


def ensure_session_auth(conversation_id: str) -> Path:
    """Ensure the per-session ``GROK_HOME`` has a usable ``auth.json``.

    grok stores its OIDC auth in ``$GROK_HOME/auth.json``. The task card
    requires per-session ``GROK_HOME`` (``<root>/sessions/<session-id>``) so
    two sessions never share leader sockets — but a fresh session dir has no
    auth file, so ``grok`` would report "Not signed in".

    The user authenticates ONCE against the isolated root
    (``GROK_HOME=/home/administrator/.grok-omnigent grok login --device-code``);
    each per-session home symlinks the root's ``auth.json``. A symlink is a
    reference, not a copy — the task card forbids *copying* auth files and
    touching the user's real ``~/.grok``; neither happens here. Token refresh
    writes through the symlink back to the root file, so a refresh in any
    session keeps every session authenticated.

    :param conversation_id: Omnigent conversation id.
    :returns: The per-session home that now carries the auth symlink.
    :raises OSError: If the session home cannot be created.
    """
    home = grok_session_home(conversation_id)
    home.mkdir(parents=True, exist_ok=True)
    auth_target = home / _AUTH_FILE
    if auth_target.is_symlink() or auth_target.exists():
        return home
    root_auth = Path(grok_home_root()) / _AUTH_FILE
    if root_auth.is_file():
        try:
            auth_target.symlink_to(root_auth)
        except OSError:
            # Symlinks can be unavailable (e.g. restricted filesystems); the
            # caller still gets a home dir, and grok will surface its own
            # auth error if auth truly is missing.
            pass
    return home


def build_grok_native_spawn_env(session_id: str) -> dict[str, str]:
    """Build the deny-by-default env handed to the ``grok`` subprocess.

    The subprocess sees:

    - the shared safe base (``HTTP_``/``HTTPS_``/``ALL_PROXY``/``NO_PROXY``/
      ``SSL_``/``XDG_``/``LANG``/``LC_`` + ``HOME``/``PATH``/``TERM``/…),
    - grok's own ``GROK_`` and ``XAI_`` families,
    - a forced per-session ``GROK_HOME`` (never the user's ``~/.grok``),
    - a forced ``NO_PROXY=127.0.0.1,localhost`` (task card requirement),
    - ``HTTPS_PROXY``/``HTTP_PROXY``/``ALL_PROXY`` only when
      :data:`GROK_PROXY_ENV_VAR` is set (TUN bridging, opt-in).

    It never sees ``ANTHROPIC_*``, ``DASHSCOPE_*``, ``OPENAI_*``,
    ``CODEX_*``, ``OPENCODE_*``, or the user's real ``~/.grok``.

    :param session_id: Omnigent session/conversation id (keys the per-session
        ``GROK_HOME``).
    :returns: Environment dict for the grok subprocess.
    """
    proc_env = clean_agent_env(
        allow_prefixes=_GROK_ALLOW_PREFIXES,
        extra_allowed=BASE_ALLOW_EXACT,
    )
    proc_env["GROK_HOME"] = str(grok_session_home(session_id))
    # The per-session home must carry grok's auth (symlinked from the isolated
    # root) or the CLI reports "Not signed in" despite a completed login.
    ensure_session_auth(session_id)
    # Proxy isolation: strip every inherited proxy variable (upper and lower
    # case) first — clean_agent_env's base allow-list lets HTTP_*/HTTPS_*/
    # ALL_PROXY/NO_PROXY through, so without this a parent's proxy would leak
    # into the Grok child even when OMNIGENT_GROK_PROXY is unset. Only an
    # explicit OMNIGENT_GROK_PROXY re-injects the trio.
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
    # Task card: NO_PROXY must always be exactly this, regardless of the
    # parent env's NO_PROXY value.
    proc_env["NO_PROXY"] = "127.0.0.1,localhost"
    proxy = os.environ.get(GROK_PROXY_ENV_VAR, "").strip()
    if proxy:
        proc_env["HTTPS_PROXY"] = proxy
        proc_env["HTTP_PROXY"] = proxy
        proc_env["ALL_PROXY"] = proxy
    return proc_env
