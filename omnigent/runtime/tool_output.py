"""Canonical cap for a ``function_call_output``'s ``output``, applied by every
producer so a multi-MB tool result can't become one giant SSE frame."""

# 1 MiB: bounds AP's streamed/persisted mirror; the model's own view stays full.
MAX_TOOL_OUTPUT_BYTES = 1024 * 1024


def cap_tool_output(output: str) -> str:
    """Cap *output* to ``MAX_TOOL_OUTPUT_BYTES`` UTF-8 on a char boundary for AP's mirror."""
    encoded = output.encode("utf-8")
    if len(encoded) <= MAX_TOOL_OUTPUT_BYTES:
        return output
    omitted = len(encoded) - MAX_TOOL_OUTPUT_BYTES
    # Drop a partial trailing multibyte char left by slicing on a byte boundary.
    kept = encoded[:MAX_TOOL_OUTPUT_BYTES].decode("utf-8", errors="ignore")
    return f"{kept}\n\n[output truncated by omnigent: {omitted} of {len(encoded)} bytes omitted]"
