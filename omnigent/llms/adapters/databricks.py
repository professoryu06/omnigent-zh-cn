"""
Databricks Model Serving adapter.

Extends the OpenAI-compatible adapter with Databricks-specific
authentication. When ``connection_params`` omits ``base_url``, the
adapter auto-resolves credentials via
:func:`~omnigent.runtime.credentials.databricks.resolve_databricks_workspace`,
which honors ``DATABRICKS_CONFIG_PROFILE`` for profile selection.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from omnigent.errors import ErrorCode, OmnigentError
from omnigent.llms.adapters.openai import OpenAICompatibleAdapter
from omnigent.runtime.credentials.databricks import resolve_databricks_workspace


class DatabricksAdapter(OpenAICompatibleAdapter):
    """
    Adapter for Databricks Model Serving.

    Credentials are resolved in the following order:

    1. ``connection_params`` passed at call time (from the ``connection:``
       block in the agent spec's ``llm:`` config) — used when present.
    2. Auto-resolved via
       :func:`~omnigent.runtime.credentials.databricks.resolve_databricks_workspace`,
       which tries the databricks-sdk (all auth types) then falls back to
       the raw ``~/.databrickscfg`` configparser, honoring
       ``DATABRICKS_CONFIG_PROFILE`` for profile selection.

    An :class:`~omnigent.errors.OmnigentError` is raised only when
    both paths fail.
    """

    def __init__(self) -> None:
        super().__init__()

    def _build_payload(
        self,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None,
        stream: bool,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build the Chat Completions payload without ``stream_options``.

        Databricks model serving rejects ``stream_options`` with a 400 error
        (the field is an OpenAI extension that Databricks does not support).
        This override builds the standard payload and removes the key.

        :param messages: Chat Completions messages.
        :param model: Model name, e.g. ``"databricks-kimi-k2-6"``.
        :param tools: Tool schemas or ``None``.
        :param stream: Whether to enable streaming.
        :param extra: Additional kwargs (temperature, etc.).
        :returns: The request payload dict without ``stream_options``.
        """
        payload = super()._build_payload(messages, model, tools, stream, extra)
        payload.pop("stream_options", None)
        return payload

    async def chat_completions(
        self,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None,
        stream: bool,
        extra: dict[str, Any],
        *,
        connection_params: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        """
        Send a Chat Completions request to Databricks Model Serving.

        :param messages: Chat Completions format messages.
        :param model: Model name, e.g. ``"databricks-gpt-5-4"``.
        :param tools: Tool schemas or ``None``.
        :param stream: Enable streaming.
        :param extra: Additional kwargs.
        :param connection_params: Optional. When provided, must contain
            ``"base_url"``; ``"api_key"`` is also expected. When absent
            or missing ``"base_url"``, credentials are auto-resolved via
            :func:`~omnigent.runtime.credentials.databricks.resolve_databricks_workspace`.
        :param timeout: Request timeout in seconds. ``None`` uses
            the module default.
        :returns: Response dict or async iterator of chunk dicts.
        :raises OmnigentError: If ``connection_params`` lacks
            ``"base_url"`` and auto-resolution from ``~/.databrickscfg``
            also fails.
        """
        if not connection_params or "base_url" not in connection_params:
            try:
                creds = resolve_databricks_workspace(None)
            except OSError as exc:
                raise OmnigentError(str(exc), code=ErrorCode.INVALID_INPUT) from exc
            resolved = {
                "base_url": creds.host + "/serving-endpoints",
                "api_key": creds.token,
            }
            connection_params = {**resolved, **(connection_params or {})}
        return await super().chat_completions(
            messages,
            model,
            tools,
            stream,
            extra,
            connection_params=connection_params,
            timeout=timeout,
        )
