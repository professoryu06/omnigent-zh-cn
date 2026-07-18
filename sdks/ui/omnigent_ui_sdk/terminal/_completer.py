"""``@``-mention file completer and mention extraction for the TUI composer.

Provides fuzzy file completion triggered by ``@`` in the input buffer,
plus submit-time helpers that resolve ``@path`` tokens into
:class:`PendingAttachment` objects and strip them from the prompt text.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
from collections.abc import Iterable

from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    ThreadedCompleter,
)
from prompt_toolkit.document import Document

from ._host import _IMAGE_EXTENSIONS, PendingAttachment


def _find_at_mention(text_before_cursor: str) -> tuple[str, int] | None:
    """Detect an ``@``-mention trigger in the text before the cursor.

    Returns ``(query, start_position)`` where *query* is the text after
    ``@`` (may be empty for a bare ``@``) and *start_position* is the
    negative offset from the cursor to the ``@`` character (inclusive).

    Returns ``None`` when ``@`` is embedded inside a word (e.g.
    ``user@domain.com``) or is not present.

    :param text_before_cursor: The text from the start of the input
        up to (but not including) the cursor position,
        e.g. ``"check @ho"``.
    :returns: ``(query, start_position)`` or ``None``.
    """
    # Walk backwards to find the nearest ``@``.
    at_pos = text_before_cursor.rfind("@")
    if at_pos < 0:
        return None

    # ``@`` must be at position 0 or preceded by whitespace — this
    # prevents email addresses and other ``@``-containing tokens from
    # triggering the completer.
    if at_pos > 0 and not text_before_cursor[at_pos - 1].isspace():
        return None

    query = text_before_cursor[at_pos + 1 :]

    # If the query itself contains whitespace the user has moved past
    # the mention token — don't trigger.
    if " " in query or "\t" in query or "\n" in query:
        return None

    # start_position is negative: distance from cursor back to ``@``.
    start_position = -(len(query) + 1)  # +1 for the ``@`` itself
    return query, start_position


def _fuzzy_score(query: str, candidate: str) -> int | None:
    """Score *candidate* against *query* using ordered character matching.

    Rewards consecutive runs, word-boundary hits (after ``/``, ``_``,
    ``.``, ``-`` or at position 0), and exact-case matches.  Higher
    scores are better.  Returns ``None`` when the query characters
    cannot be found in order.

    :param query: User-typed text after ``@``, e.g. ``"hostp"``.
    :param candidate: Relative file path, e.g. ``"_host.py"``.
    :returns: Integer score (higher = better match), or ``None``.
    """
    if not query:
        return 0  # bare ``@`` matches everything

    _CONSECUTIVE_BONUS = 4
    _BOUNDARY_BONUS = 3
    _CASE_BONUS = 1

    score = 0
    c_idx = 0  # current scan position in candidate
    prev_match_idx = -2  # impossible initial value (not adjacent to 0)
    candidate_lower = candidate.lower()
    query_lower = query.lower()

    for q_pos, q_ch in enumerate(query_lower):
        found = candidate_lower.find(q_ch, c_idx)
        if found < 0:
            return None
        # Base point per matched character.
        score += 1
        # Consecutive bonus: previous match was at found - 1.
        if found == prev_match_idx + 1:
            score += _CONSECUTIVE_BONUS
        # Word-boundary bonus: match at start or after a separator.
        if found == 0 or candidate[found - 1] in "/_.-":
            score += _BOUNDARY_BONUS
        # Case-exact bonus.
        if candidate[found] == query[q_pos]:
            score += _CASE_BONUS
        prev_match_idx = found
        c_idx = found + 1

    return score


def _is_hidden(path: str) -> bool:
    """Return ``True`` if any component of *path* starts with ``.``.

    :param path: Forward-slash-separated relative path,
        e.g. ``"src/.secret/file.py"``.
    :returns: Whether the path contains a hidden component.
    """
    return any(part.startswith(".") for part in path.split("/") if part)


def _list_files(cwd: str) -> list[str]:
    """List non-hidden files under *cwd*, respecting ``.gitignore``.

    Tries ``git ls-files`` first (fast, natively honours
    ``.gitignore``).  Falls back to :func:`_walk_files` when *cwd*
    is not inside a git repository or ``git`` is unavailable.

    :param cwd: Root directory to scan.
    :returns: List of relative paths, e.g.
        ``["main.py", "src/utils.py"]``.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=5,
        )
        if result.returncode == 0:
            return [f for f in result.stdout.splitlines() if f and not _is_hidden(f)]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return _walk_files(cwd)


def _walk_files(cwd: str) -> list[str]:
    """Recursively list non-hidden files under *cwd*.

    Fallback for non-git directories — skips hidden entries but does
    **not** respect ``.gitignore``.  Prefer :func:`_list_files`.

    :param cwd: Root directory to scan.
    :returns: Sorted list of relative paths, e.g.
        ``["main.py", "src/utils.py"]``.
    """
    results: list[str] = []
    base = pathlib.Path(cwd)
    for dirpath, dirnames, filenames in os.walk(cwd):
        rel = pathlib.Path(dirpath).relative_to(base)
        # Prune hidden directories in-place so os.walk skips them.
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        depth = len(rel.parts)  # 0 for cwd itself
        for fname in sorted(filenames):
            if fname.startswith("."):
                continue
            rel_path = str(rel / fname) if depth > 0 else fname
            results.append(rel_path)
    return results


class _FileMentionCompleterCore(Completer):
    """Synchronous fuzzy file completer (internal).

    Use :class:`FileMentionCompleter` instead — it wraps this in a
    :class:`~prompt_toolkit.completion.ThreadedCompleter` so the
    directory scan runs off the main event-loop thread.

    :param cwd: Working directory to scan.  ``None`` means use
        ``os.getcwd()`` at completion time.
    """

    def __init__(self, cwd: str | None = None) -> None:
        self._cwd = cwd

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent,
    ) -> Iterable[Completion]:
        """Yield file completions when an ``@`` trigger is detected.

        :param document: prompt-toolkit's input-buffer view.
        :param complete_event: prompt-toolkit trigger metadata (unused).
        :returns: :class:`Completion` entries for matching files.
        """
        result = _find_at_mention(document.text_before_cursor)
        if result is None:
            return

        query, start_position = result
        cwd = self._cwd or os.getcwd()

        try:
            candidates = _list_files(cwd)
        except OSError:
            return

        scored: list[tuple[int, str]] = []
        for path in candidates:
            score = _fuzzy_score(query, path)
            if score is not None:
                scored.append((score, path))

        # Sort by score descending (best first), alphabetically as
        # tie-breaker.
        scored.sort(key=lambda item: (-item[0], item[1]))

        for _score, path in scored:
            yield Completion(
                text=f"@{path}",
                start_position=start_position,
                display=path,
            )


class FileMentionCompleter(ThreadedCompleter):
    """Suggest files from the working directory when the user types ``@``.

    Wraps :class:`_FileMentionCompleterCore` in a
    :class:`~prompt_toolkit.completion.ThreadedCompleter` so the
    file-system scan (``git ls-files`` / ``os.walk``) and fuzzy
    scoring run in a background thread, keeping the input responsive.

    :param cwd: Working directory to scan.  ``None`` means use
        ``os.getcwd()`` at completion time.
    """

    def __init__(self, cwd: str | None = None) -> None:
        super().__init__(_FileMentionCompleterCore(cwd=cwd))


def extract_at_mentions(
    text: str,
    cwd: str | None = None,
) -> list[PendingAttachment]:
    """Resolve ``@filename`` tokens in *text* to attachments.

    Called at submit time to convert ``@``-mention tokens into
    :class:`PendingAttachment` objects.  Only tokens whose path
    resolves to an existing file are returned.

    :param text: The full input line, e.g.
        ``"check @src/main.py for bugs"``.
    :param cwd: Working directory for resolving relative paths.
        ``None`` means ``os.getcwd()``.
    :returns: List of resolved attachments.
    """
    cwd = cwd or os.getcwd()
    attachments: list[PendingAttachment] = []
    for token in text.split():
        if not token.startswith("@"):
            continue
        rel_path = token[1:]
        if not rel_path:
            continue
        try:
            p = pathlib.Path(cwd, rel_path).resolve()
        except (OSError, ValueError):
            continue
        if not p.is_file():
            continue
        is_image = p.suffix.lower() in _IMAGE_EXTENSIONS
        attachments.append(PendingAttachment(path=str(p), is_image=is_image))
    return attachments


def strip_at_mentions(
    text: str,
    attachments: list[PendingAttachment],
) -> str:
    """Remove resolved ``@filename`` tokens from the input text.

    Prevents raw ``@path`` strings from appearing in the echoed
    prompt — the ``📎`` chip already shows the filename.  The
    caller is responsible for re-injecting paths into the text
    sent to the LLM if needed.

    :param text: The raw input line.
    :param attachments: Attachments returned by
        :func:`extract_at_mentions`.
    :returns: The text with ``@filename`` tokens removed, stripped.
    """
    resolved_paths = {a.path for a in attachments}
    cwd = os.getcwd()
    remaining: list[str] = []
    for token in text.split():
        if token.startswith("@") and len(token) > 1:
            rel_path = token[1:]
            try:
                p = pathlib.Path(cwd, rel_path).resolve()
            except (OSError, ValueError):
                remaining.append(token)
                continue
            if str(p) in resolved_paths:
                continue
        remaining.append(token)
    return " ".join(remaining).strip()
