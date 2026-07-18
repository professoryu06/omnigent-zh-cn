"""Transport factories for talking to a runner.

Local server-to-runner traffic uses the WebSocket tunnel. The UDS and
TCP modules remain focused transport mechanics for runner subprocess
tests and future deployment shapes.

| Transport     | Module                | Phase | Built-in?           |
|---------------|-----------------------|-------|---------------------|
| UDS           | uds.py                | 2     | ✓ httpx.AsyncHTTPTransport(uds=) |
| TCP           | tcp.py                | 3     | ✓ httpx.AsyncHTTPTransport |
| WS tunnel     | ws_tunnel/            | 4     | ✗ custom code       |

Each module exposes a ``create_<transport>_client()`` factory plus
the wire-level pieces specific to the transport (e.g. UDS spawns a
uvicorn subprocess; WS tunnel ships a frame protocol + registry +
adapter).
"""
