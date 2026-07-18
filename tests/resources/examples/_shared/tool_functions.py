"""Example tool functions for Omnigent agents.

These are plain Python functions that can be referenced from YAML agent
definitions via the ``callable`` field on a FunctionTool.
"""

import time
from datetime import datetime, timedelta, timezone

from omnigent.policies.schema import PolicyEvent, PolicyResponse


def web_search(query: str) -> dict:
    """Return deterministic fake web results for examples and tests."""
    query_text = str(query).strip()
    if not query_text:
        return {"results": []}
    return {
        "results": [
            {
                "title": f"Overview of {query_text}",
                "url": f"https://example.com/search?q={query_text.replace(' ', '+')}",
                "snippet": f"Public web summary for {query_text}.",
            },
            {
                "title": f"Recent news about {query_text}",
                "url": f"https://news.example.com/{query_text.replace(' ', '-').lower()}",
                "snippet": f"Synthetic news result related to {query_text}.",
            },
        ]
    }


def summarize(text: str, max_words: int = 30) -> dict:
    """Return a deterministic fake summary of *text*.

    Mirrors :func:`web_search` in shape — a plain callable with a
    deterministic payload, suitable as the ``callable:`` target on
    a YAML ``type: function`` tool. No real LLM or NLP; the
    "summary" is the first ``max_words`` whitespace-delimited
    tokens of the input plus an ellipsis when truncated. Useful
    for examples that pair search → summarize, where the agent
    needs *some* tool to call but the test doesn't care about
    summary quality.

    :param text: The text to summarize, e.g. a search snippet.
    :param max_words: Truncation cap, e.g. ``30``. Values <= 0
        are coerced to 1 so the summary is never empty.
    :returns: Dict with ``summary`` (the truncated text),
        ``input_words`` (token count of the input), and
        ``truncated`` (whether the cap was hit).
    """
    body = str(text).strip()
    cap = max(1, int(max_words)) if isinstance(max_words, int) else 30
    words = body.split()
    truncated = len(words) > cap
    head = words[:cap]
    summary = " ".join(head) + ("…" if truncated else "")
    return {
        "summary": summary,
        "input_words": len(words),
        "truncated": truncated,
    }


def read_internal_doc(doc_id: str) -> dict:
    """Return a deterministic confidential document payload."""
    doc_key = str(doc_id).strip() or "unknown"
    return {
        "doc_id": doc_key,
        "classification": "confidential",
        "content": f"CONFIDENTIAL: internal notes for {doc_key}.",
    }


def run_shell(command: str) -> dict:
    """Return deterministic fake shell output for policy examples."""
    command_text = str(command).strip()
    if command_text == "ls":
        return {"stdout": "README.md\nexamples\nomnigent\ntests", "stderr": "", "exit_code": 0}
    return {
        "stdout": f"simulated shell output for: {command_text}",
        "stderr": "",
        "exit_code": 0,
    }


def write_file(path: str, content: str) -> dict:
    """Pretend to write a file and report what would have happened."""
    return {
        "ok": True,
        "path": str(path),
        "bytes_written": len(str(content).encode("utf-8")),
    }


def get_current_time(timezone_name: str = "UTC") -> str:
    """Return the current date/time in the given timezone.

    Supports a handful of common timezone names for the example.
    A production implementation would use ``zoneinfo`` or ``pytz``.
    """
    offsets = {
        "UTC": 0,
        "US/Eastern": -5,
        "EST": -5,
        "EDT": -4,
        "US/Central": -6,
        "CST": -6,
        "CDT": -5,
        "US/Pacific": -8,
        "PST": -8,
        "PDT": -7,
        "Europe/London": 0,
        "GMT": 0,
        "BST": 1,
        "Europe/Paris": 1,
        "CET": 1,
        "CEST": 2,
        "Asia/Tokyo": 9,
        "JST": 9,
        "Asia/Shanghai": 8,
        "CST_China": 8,
    }
    offset = offsets.get(timezone_name)
    if offset is None:
        return f"Unknown timezone: {timezone_name}. Supported: {', '.join(sorted(offsets.keys()))}"
    tz = timezone(timedelta(hours=offset))
    now = datetime.now(tz)
    return now.strftime(f"%Y-%m-%d %H:%M:%S {timezone_name}")


def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression and return the result.

    Only supports basic arithmetic for safety.
    """
    allowed = set("0123456789+-*/().% ")
    if not all(c in allowed for c in expression):
        return (
            "Error: expression contains disallowed characters. Only basic arithmetic is supported."
        )
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as exc:
        return f"Error evaluating '{expression}': {exc}"


def sleep(seconds: float):
    if seconds < 0 or seconds > 10:
        raise ValueError("Sleep time must be between 0 and 10 seconds")
    time.sleep(seconds)


def sleep_tool(seconds: float) -> dict[str, float]:
    """
    Sleep for ``seconds`` then return a marker payload.

    Plain callable used by ``agent_with_policies.yaml`` and
    ``agent_with_tools.yaml`` (and the matching tests). The LLM
    can call this synchronously for short sleeps or dispatch it
    via ``sys_call_async`` for backgrounded / cancellable sleeps;
    cancellation in the latter case flows through
    ``sys_cancel_task`` → DBOS workflow cancel → SIGINT to the
    runner subprocess (no per-tool cancel hook needed).

    Replaces the legacy ``SleepToolRunner`` runner-protocol class
    that this module previously exported. The runner protocol was
    redundant once ``sys_call_async`` shipped — the framework
    handles cancellable async dispatch uniformly for any plain
    callable, so we don't need a separate tool-shape contract for
    it. See ``designs/SERVER_HARNESS_CONTRACT.md`` §"Async work +
    inbox" for the rationale.

    :param seconds: Sleep duration in seconds, e.g. ``3.5``. Must
        be between 0 and 10 inclusive — values outside the range
        raise ``ValueError`` (matching the policies test that
        expects long-sleep refusal).
    :returns: Dict with ``slept`` set to the sleep duration so
        callers can verify the sleep ran to completion.
    :raises ValueError: When ``seconds`` is negative or greater
        than 10.
    """
    if seconds < 0 or seconds > 10:
        raise ValueError("Sleep time must be between 0 and 10 seconds")
    time.sleep(seconds)
    return {"slept": float(seconds)}


_ALLOW: PolicyResponse = {"result": "ALLOW"}


def block_division(event: PolicyEvent) -> PolicyResponse:
    """Block calculate tool calls whose expression contains division.

    Returns ALLOW for events this policy does not cover. The callable
    self-selects which events to act on without needing an ``on:``
    field in the YAML.

    Used by ``agent_with_policies.yaml`` to verify that ``type: function``
    handler tools go through Omnigent policy enforcement the same way MCP tools do.

    :param event: V0 event dict with ``type``, ``target``, ``data``,
        ``context`` keys.
    :returns: V0 decision dict.
    """
    if event.get("type") != "tool_call":
        return _ALLOW

    data = event.get("data")
    tool_name: str = data.get("name", "") if isinstance(data, dict) else ""
    if tool_name != "calculate":
        return _ALLOW

    args = data.get("arguments")
    expression: str = args.get("expression", "") if isinstance(args, dict) else ""
    if "/" in expression:
        return {
            "result": "DENY",
            "reason": "Division expressions are denied by policy.",
        }

    return _ALLOW


def block_long_sleep(event: PolicyEvent) -> PolicyResponse:
    """Block sleep tool calls longer than 5 seconds.

    Returns ALLOW for events this policy does not cover. The callable
    self-selects which events to act on without needing an ``on:``
    field in the YAML.

    :param event: V0 event dict with ``type``, ``target``, ``data``,
        ``context`` keys.
    :returns: V0 decision dict.
    """
    if event.get("type") != "tool_call":
        return _ALLOW

    data = event.get("data")
    # Match bare name "sleep" or namespaced "sleep-server__sleep".
    tool_name: str = data.get("name", "") if isinstance(data, dict) else ""
    if not tool_name.endswith("sleep"):
        return _ALLOW

    args = data.get("arguments")
    if not isinstance(args, dict):
        return _ALLOW

    seconds = args.get("seconds", 0)
    try:
        seconds_value = float(seconds)
    except (TypeError, ValueError):
        return _ALLOW

    if seconds_value > 5:
        return {
            "result": "DENY",
            "reason": "Sleep calls longer than 5 seconds are denied by policy.",
        }

    return _ALLOW


_CANADA_KEYWORDS = frozenset(
    {
        "canada",
        "canadian",
        "toronto",
        "vancouver",
        "montreal",
        "ottawa",
        "quebec",
        "ontario",
        "alberta",
        "calgary",
        "edmonton",
        "winnipeg",
        "halifax",
        "victoria",
    }
)


def block_canada_input(event):
    """Block user input that mentions Canada or Canadian places.

    Returns ALLOW for non-request events and requests that don't
    mention Canada-related keywords.

    :param event: V0 event dict with ``type``, ``target``, ``data``,
        ``context`` keys.
    :returns: V0 decision dict.
    """
    if event.get("type") != "request":
        return _ALLOW

    data = event.get("data")
    text = data if isinstance(data, str) else str(data)
    lower = text.lower()
    if any(kw in lower for kw in _CANADA_KEYWORDS):
        return {
            "result": "DENY",
            "reason": "Canada-related topics are denied.",
        }

    return _ALLOW


def block_canada_output(event):
    """Block assistant output that mentions Canada or Canadian places.

    Returns ALLOW for non-response events and responses that don't
    mention Canada-related keywords.

    :param event: V0 event dict with ``type``, ``target``, ``data``,
        ``context`` keys.
    :returns: V0 decision dict.
    """
    if event.get("type") != "response":
        return _ALLOW

    data = event.get("data")
    text = data if isinstance(data, str) else str(data)
    lower = text.lower()
    if any(kw in lower for kw in _CANADA_KEYWORDS):
        return {
            "result": "DENY",
            "reason": "Canada-related topics are denied.",
        }

    return _ALLOW
