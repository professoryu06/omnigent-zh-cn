"""Shared helpers for the Omnigent REPL pexpect tests.

These helpers are used by multiple ``test_repl_*.py`` files in
this directory. They are intentionally kept separate from
``_pexpect_harness.py`` (the phase 0 foundation) to avoid
diverging the foundation file across worktrees during the
phase 0 merge — the foundation is shared with another agent's
work-in-progress and must remain byte-identical there.

If a helper here proves stable across phases it can later be
folded into ``_pexpect_harness.py`` as part of a deliberate
foundation-update commit.
"""

from __future__ import annotations

import pexpect

# Per-chunk read window for :func:`drain_for`. Tuned so that
# prompt-toolkit's default ~50 ms refresh tick still fires at
# least once inside one chunk — keeps draining responsive
# without wasting a full chunk-budget on each idle slice.
_CHUNK_TIMEOUT_SEC = 0.3


def drain_for(child: pexpect.spawn, total_timeout: float) -> str:
    """
    Collect all PTY output that arrives within a bounded
    window.

    Issues repeated short ``read_nonblocking`` calls and
    concatenates the chunks. More robust than a single long
    ``read_nonblocking`` when prompt-toolkit emits a render
    burst across multiple frames — a single read can return
    after the first chunk and miss follow-up frames painted
    by the next refresh tick.

    The function returns early if the PTY idles for one
    chunk-interval before the budget elapses, so the wall-
    clock cost is bounded by whichever is shorter.

    :param child: Live ``pexpect.spawn`` child returned by
        :func:`tests.e2e.omnigent._pexpect_harness.spawn_omnigent_run`.
    :param total_timeout: Overall seconds to spend draining,
        e.g. ``5.0``. A typical value for "let the post-key
        render frames settle" is 2–6 seconds.
    :returns: Concatenated raw PTY output collected during the
        drain window. May be empty if the PTY produced no
        output during the budget.
    """
    chunks: list[str] = []
    remaining = total_timeout
    while remaining > 0:
        chunk_timeout = min(_CHUNK_TIMEOUT_SEC, remaining)
        try:
            chunk = child.read_nonblocking(size=65536, timeout=chunk_timeout)
        except pexpect.TIMEOUT:
            break
        chunks.append(chunk)
        remaining -= chunk_timeout
    return "".join(chunks)
