"""LLM client error types and context-overflow detection."""

from __future__ import annotations

from dataclasses import dataclass

from omnigent.errors import OmnigentError

# Provider ``exc.code`` / ``exc.body.error.code`` values that signal
# a context-window overflow.  Currently OpenAI-origin codes; add
# Anthropic / Gemini / other codes here as their SDKs start stamping
# structured codes on exceptions (today they embed the signal in the
# error *message*, which ``llm_retry.classify_llm_error`` handles
# separately via regex).
CONTEXT_EXCEEDED_CODES: frozenset[str] = frozenset(
    {
        # OpenAI / Databricks gateway
        "context_length_exceeded",
        "max_tokens_exceeded",
        "string_above_max_length",
    }
)


def is_context_length_exceeded(exc: BaseException) -> bool:
    """Return ``True`` when *exc* signals a context-window overflow.

    Walks ``exc.code``, ``exc.body``, and the ``__cause__`` /
    ``__context__`` chain so the check works regardless of which SDK
    raised the exception or how many layers of wrapping it went
    through.  New providers only need to add their error codes to
    :data:`CONTEXT_EXCEEDED_CODES`.

    :param exc: The exception to inspect.
    :returns: ``True`` if any exception in the chain carries an error
        code from :data:`CONTEXT_EXCEEDED_CODES`.
    """
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        code = getattr(current, "code", None)
        if isinstance(code, str) and code in CONTEXT_EXCEEDED_CODES:
            return True
        body = getattr(current, "body", None)
        if isinstance(body, dict):
            nested = body.get("error", body)
            if isinstance(nested, dict):
                nested_code = nested.get("code")
                if isinstance(nested_code, str) and nested_code in CONTEXT_EXCEEDED_CODES:
                    return True
        next_exc = current.__cause__ or current.__context__
        current = next_exc if isinstance(next_exc, BaseException) else None
    return False


@dataclass
class LLMErrorDetail:
    """
    Structured detail about an LLM call failure.

    :param provider: Provider name, e.g. ``"openai"``, ``"anthropic"``.
        ``None`` when the provider cannot be determined.
    :param status_code: HTTP status code from the provider, e.g.
        ``429``. ``None`` for non-HTTP errors (timeouts, connection
        errors).
    :param response_body: Raw response body from the provider, e.g.
        ``'{"error": {"message": "Rate limit"}}'``. ``None`` when
        no response body is available.
    """

    provider: str | None = None
    status_code: int | None = None
    response_body: str | None = None


class RetryableLLMError(OmnigentError):
    """
    An LLM call failure that may be retried.

    Raised by the retry loop when the adapter throws a retryable
    exception (timeout or configured HTTP status code). Carries
    a string ``code`` for SSE events and structured ``detail``
    for diagnostics.

    :param message: Human-readable error description, e.g.
        ``"OpenAI rate limit exceeded"``.
    :param code: Error code string for SSE events, e.g.
        ``"429"``, ``"timeout"``, ``"connection_error"``.
    :param detail: Structured provider-specific detail.
        ``None`` when no additional detail is available.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str = "unknown",
        detail: LLMErrorDetail | None = None,
    ) -> None:
        super().__init__(message, code=code)
        self.detail = detail


class PermanentLLMError(OmnigentError):
    """
    An LLM call failure that should NOT be retried.

    Raised when the adapter throws a non-retryable exception
    (auth failure, bad request, connection refused).

    :param message: Human-readable error description.
    :param code: Error code string for SSE events, e.g.
        ``"401"``, ``"connection_error"``.
    :param detail: Structured provider-specific detail.
        ``None`` when no additional detail is available.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str = "unknown",
        detail: LLMErrorDetail | None = None,
    ) -> None:
        super().__init__(message, code=code)
        self.detail = detail


class ContextWindowExceededError(PermanentLLMError):
    """
    The LLM rejected the request because the prompt exceeded the
    model's context window. Unlike other permanent errors, this one
    is recoverable after compaction — the caller can compact the
    conversation history and retry.

    Subclasses :class:`PermanentLLMError` so existing ``except
    PermanentLLMError`` catch blocks still work. If the workflow does
    not specifically catch this subclass, the error propagates as
    fatal — the safe default.

    :param message: Human-readable description, e.g.
        ``"Context window exceeded: 142000 tokens > 128000 max"``.
    :param code: Error code string, e.g.
        ``"context_length_exceeded"``.
    :param detail: Structured provider detail. ``None`` when
        unavailable.
    :param max_context_tokens: The model's context window size as
        reported by the provider, e.g. ``128000``.
    :param actual_tokens: The token count the provider measured for
        the rejected request, e.g. ``142000``.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str,
        detail: LLMErrorDetail | None = None,
        max_context_tokens: int,
        actual_tokens: int,
    ) -> None:
        super().__init__(message, code=code, detail=detail)
        self.max_context_tokens = max_context_tokens
        self.actual_tokens = actual_tokens
