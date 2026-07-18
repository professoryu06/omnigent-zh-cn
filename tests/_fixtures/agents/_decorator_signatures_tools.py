"""Test tools exercising the breadth of Omnigent tool signature handling.

Covers:
- Plain primitive ``str`` arg (``greet``).
- Pydantic ``BaseModel`` arg with optional field (``format_record``).
- Multiple primitive args with defaults (``compute``).
"""

from __future__ import annotations

from pydantic import BaseModel


class PersonRecord(BaseModel):
    """A person record (test fixture)."""

    name: str
    age: int
    email: str | None = None


def greet(name: str) -> str:
    """
    Return a greeting for the given name.

    :param name: The name to greet.
    :returns: ``f"Hello, {name}!"``.
    """
    return f"Hello, {name}!"


def format_record(record: PersonRecord) -> str:
    """
    Format a person record as a one-line string.

    :param record: The person record to format.
    :returns: ``"Person(name=..., age=..., email=...)"``.
    """
    parts = [f"name={record.name}", f"age={record.age}"]
    if record.email is not None:
        parts.append(f"email={record.email}")
    return "Person(" + ", ".join(parts) + ")"


def compute(value: int, multiplier: int = 2, note: str = "") -> dict[str, int | str]:
    """
    Multiply ``value`` by ``multiplier`` and echo the optional note.

    :param value: Base integer value.
    :param multiplier: Multiplier (defaults to 2).
    :param note: Optional note to echo back.
    :returns: ``{"product": value * multiplier, "note": note}``.
    """
    return {"product": value * multiplier, "note": note}
