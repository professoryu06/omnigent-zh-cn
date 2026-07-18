"""Local word-count tool for the archer e2e fixture."""

from __future__ import annotations

from omnigent_client.tools import tool


@tool
def word_count(text: str) -> dict[str, int]:
    """
    Count whitespace-delimited words in ``text``.

    :param text: Text to count.
    :returns: A JSON-serializable dict containing ``word_count``.
    """
    return {"word_count": len(text.split())}
