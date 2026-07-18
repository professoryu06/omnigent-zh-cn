"""Minimal echo tool shared by the tool-gate / tool-result-gate /
sub-agent-tool-gate fixtures."""

from __future__ import annotations


def echo(message: str) -> str:
    """
    Return the input message unchanged (with a stable prefix so
    downstream e2e asserts can distinguish tool output from raw
    LLM text).

    :param message: The text to echo back.
    :returns: ``f"echo: {message}"``.
    """
    return f"echo: {message}"
