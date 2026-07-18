"""Shared utility for auto-filling MCP elicitation ``content`` from
``requestedSchema``.

Used by both the runner's inline elicitation callback
(:mod:`omnigent.runner.mcp_manager`) and the REPL's
``_handle_elicitation`` (:mod:`omnigent.repl._repl`).
"""

from __future__ import annotations

from typing import Any


def build_accept_content_from_schema(
    schema: dict[str, Any],
) -> dict[str, str | int | float | bool | list[str] | None] | None:
    """
    Build ``content`` for an MCP elicitation ``accept`` from a
    ``requestedSchema``.

    Returns a dict when every schema property can be auto-filled
    (booleans → ``True``, enums → ``"allow"`` or first option,
    properties with ``default`` → the default). Returns ``None``
    when the schema has properties that require free-form user
    input (strings, numbers without defaults) — the caller should
    decline or direct the user to the web UI.

    Returns ``None`` (no content needed) when the schema has no
    properties (binary approve/decline elicitation).

    :param schema: The ``requestedSchema`` dict from the
        elicitation event. May be empty ``{}``.
    :returns: A flat ``{field: value}`` dict, or ``None``.
    """
    properties = schema.get("properties")
    if not properties or not isinstance(properties, dict):
        return None
    content: dict[str, str | int | float | bool | list[str] | None] = {}
    for key, prop in properties.items():
        if not isinstance(prop, dict):
            return None
        # Enum with oneOf — pick "allow" or the first const.
        one_of = prop.get("oneOf")
        if isinstance(one_of, list) and one_of:
            allow_val = next(
                (o["const"] for o in one_of if isinstance(o, dict) and o.get("const") == "allow"),
                None,
            )
            if allow_val is not None:
                content[key] = allow_val
            else:
                first = next(
                    (o["const"] for o in one_of if isinstance(o, dict) and "const" in o),
                    None,
                )
                if first is None:
                    return None
                content[key] = first
            continue
        # Enum with plain enum list.
        enum_vals = prop.get("enum")
        if isinstance(enum_vals, list) and enum_vals:
            allow_val = next((v for v in enum_vals if v == "allow"), None)
            content[key] = allow_val if allow_val is not None else enum_vals[0]
            continue
        prop_type = prop.get("type", "string")
        if prop_type == "boolean":
            content[key] = True
            continue
        # Has a default — use it.
        if "default" in prop:
            content[key] = prop["default"]
            continue
        # Free-form input required — can't auto-fill.
        return None
    return content
