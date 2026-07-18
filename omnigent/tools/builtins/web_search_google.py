"""Built-in tool: Google Custom Search.

Requires environment variables:
- ``GOOGLE_SEARCH_API_KEY``: API key from Google Cloud Console.
- ``GOOGLE_SEARCH_ENGINE_ID``: Programmable Search Engine ID.

See https://developers.google.com/custom-search/v1/overview
"""

from __future__ import annotations

import logging

# Any: the OpenAI tool schema is a heterogeneous dict with string
# keys and mixed value types (str, dict, list).
from typing import Any

import httpx

_logger = logging.getLogger(__name__)

_GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"

# Maximum results per query (Google CSE limit is 10 per page).
_MAX_RESULTS: int = 10


def _search_google(
    query: str,
    config: dict[str, str],
) -> str:
    """
    Call the Google Custom Search API and format results.

    :param query: The search query string.
    :param config: Spec-level config; checked for ``api_key``
        and ``engine_id`` before falling back to env vars.
    :returns: Formatted results or an error message.
    """
    api_key = config.get("api_key")
    engine_id = config.get("engine_id")
    if not api_key or not engine_id:
        return (
            "Error: api_key and engine_id must be provided in "
            "the web_search config in config.yaml."
        )
    try:
        resp = httpx.get(
            _GOOGLE_CSE_URL,
            params={
                "key": api_key,
                "cx": engine_id,
                "q": query,
                "num": _MAX_RESULTS,
            },
            timeout=15.0,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return f"Google search error: HTTP {exc.response.status_code}"
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        return f"Google search error: {exc}"

    return _format_results(resp.json())


def _format_results(data: dict[str, Any]) -> str:
    """
    Format Google CSE JSON response into readable text.

    :param data: The parsed JSON response from Google CSE.
    :returns: Numbered results with title, link, and snippet.
    """
    items = data.get("items", [])
    if not items:
        return "No results found."
    results: list[str] = []
    for i, item in enumerate(items[:_MAX_RESULTS]):
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")
        results.append(f"{i + 1}. {title}\n   {link}\n   {snippet}")
    return "\n\n".join(results)
