"""WebSocket tunnel transport for runners behind NAT (Phase 4).

Submodules:
- ``frames`` — JSON frame schema (8 frame kinds + encode/decode).
- ``registry`` — server-side runner_id → WebSocket map.
- ``transport`` — httpx.AsyncBaseTransport for the server side.
- ``serve`` — runner-side ASGI dispatch adapter.
"""
