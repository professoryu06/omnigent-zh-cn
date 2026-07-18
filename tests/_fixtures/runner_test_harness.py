"""Minimal harness module for runner tests.

A registerable harness (per the harness contract: exposes
``create_app() -> FastAPI``) that drives a streaming LLM call. The
runner-tests inject this into ``_HARNESS_MODULES`` under a test-only
key so :class:`HarnessProcessManager` can spawn it as a real uvicorn
subprocess on a UDS — exercising the full runner→harness dispatch
architecture without a vendor SDK.

Why a test-only harness rather than reusing claude-sdk /
openai-agents: keeps the test self-contained (no extra package
deps, no Databricks profile, no model selection issue). The loop
body is intentionally minimal — call the LLM with streaming, forward
each event as SSE, terminate on response.completed or response.failed.
"""

from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from omnigent.llms.client import Client


def _encode_sse(event_type: str, data: dict[str, Any]) -> bytes:
    """Standard SSE frame: ``event: <type>\\ndata: <json>\\n\\n``."""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode()


def _event_to_dict(event: Any) -> dict[str, Any]:
    """Best-effort serialize an LLM streaming event to a JSON-shaped dict."""
    if isinstance(event, dict):
        return event
    if hasattr(event, "__dict__"):
        out: dict[str, Any] = {}
        for k, v in vars(event).items():
            if hasattr(v, "__dict__") and not isinstance(v, dict):
                out[k] = _event_to_dict(v)
            elif isinstance(v, list):
                out[k] = [_event_to_dict(i) if hasattr(i, "__dict__") else i for i in v]
            else:
                out[k] = v
        return out
    return {"value": str(event)}


async def _run_turn(
    *,
    client: Client,
    input_items: list[dict[str, Any]],
    model: str,
    instructions: str | None,
    tools: list[dict[str, Any]],
    connection_params: dict[str, str] | None,
) -> AsyncIterator[bytes]:
    """Drive a single LLM turn and yield SSE bytes."""
    yield _encode_sse(
        "response.created",
        {
            "type": "response.created",
            "response": {"id": "resp_runner_test", "status": "in_progress"},
        },
    )
    try:
        create_kwargs: dict[str, Any] = {
            "input": input_items,
            "instructions": instructions,
            "model": model,
            "tools": tools or None,
            "stream": True,
        }
        if connection_params is not None:
            create_kwargs["connection_params"] = connection_params
        stream = await client.responses.create(**create_kwargs)
    except Exception as exc:
        yield _encode_sse(
            "response.failed",
            {
                "type": "response.failed",
                "error": {"message": str(exc), "type": type(exc).__name__},
            },
        )
        return

    saw_completed = False
    async for event in stream:
        event_type = getattr(event, "type", "response.event")
        yield _encode_sse(event_type, _event_to_dict(event))
        if event_type == "response.completed":
            saw_completed = True
            break
    if not saw_completed:
        # Synthesize a terminal so the SSE stream isn't open-ended
        # if the provider drops without one.
        yield _encode_sse(
            "response.completed",
            {
                "type": "response.completed",
                "response": {"id": "resp_runner_test", "status": "completed"},
            },
        )


def create_app() -> FastAPI:
    """Harness FastAPI app — the entrypoint HarnessProcessManager spawns."""
    app = FastAPI(title="omnigent-runner-test-harness")
    llm_client = Client()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    def _start_turn(body: dict[str, Any]) -> Any:
        # Body shape comes from ``POST /v1/sessions/{id}/events``: the
        # runner wraps the synthesized request body as a
        # ``MessageEvent``, exposing ``content`` (and historically
        # ``input``). Accept either field name.
        input_items = body.get("input") or body.get("content")
        model = body.get("model")
        if not isinstance(input_items, list) or not isinstance(model, str):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_request",
                    "detail": "'input' (list) and 'model' (string) required",
                },
            )
        connection_params = body.get("connection_params")
        if connection_params is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                connection_params = {"api_key": api_key}
        return StreamingResponse(
            _run_turn(
                client=llm_client,
                input_items=input_items,
                model=model,
                instructions=body.get("instructions"),
                tools=body.get("tools") or [],
                connection_params=connection_params,
            ),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.post("/v1/sessions/{conversation_id}/events")
    async def post_session_events(conversation_id: str, request: Request) -> Any:
        return _start_turn(await request.json())

    return app
