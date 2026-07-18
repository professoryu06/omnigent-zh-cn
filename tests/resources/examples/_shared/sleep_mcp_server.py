"""Minimal MCP server exposing a ``sleep`` tool for policy-demo agents.

Run as a stdio MCP server:

    python -m tests.resources.examples._shared.sleep_mcp_server

Used by ``tests/resources/examples/agent_with_policies.yaml`` so the
sleep tool travels through the Omnigent server's MCP proxy endpoint and is
subject to TOOL_CALL policy evaluation (``block_long_sleep``).

:raises SystemExit: Delegates to ``mcp.run()`` which blocks until the
    stdio transport is closed.
"""

from __future__ import annotations

import time

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sleep-server")


@mcp.tool()
def sleep(seconds: float) -> str:
    """Sleep for a given number of seconds.

    :param seconds: Number of seconds to sleep.
    :returns: Confirmation message with the elapsed duration.
    """
    time.sleep(seconds)
    return f"Slept for {seconds} seconds."


if __name__ == "__main__":
    mcp.run()
