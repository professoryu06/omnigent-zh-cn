"""Theme definitions for the terminal TUI.

The terminal UI cannot reliably detect whether the user's emulator is
using a light or dark background.  Keep the palette explicit and
mutable so the REPL can offer a small ``/theme`` command instead of
hard-coding dark-terminal assumptions in Markdown and status-bar
rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

from rich.theme import Theme

TerminalThemeName = Literal["dark", "light"]


@dataclass(frozen=True)
class TerminalTheme:
    """Palette used by Rich and prompt-toolkit terminal rendering."""

    name: TerminalThemeName
    code_theme: str
    muted: str
    assistant: str
    warning: str
    error: str
    success: str
    reasoning_style: str
    toolbar_background: str
    toolbar_model: str
    rich_theme: Theme


DARK_THEME = TerminalTheme(
    name="dark",
    code_theme="monokai",
    muted="#6a6a6a",
    assistant="bold green",
    warning="#ffa500",
    error="bold #ff6b80",
    success="#4eba65",
    reasoning_style="dim italic #8a8a8a",
    toolbar_background="#2a2a2a",
    toolbar_model="#6a6a6a",
    rich_theme=Theme(),
)

LIGHT_THEME = TerminalTheme(
    name="light",
    code_theme="default",
    muted="#6b7280",
    assistant="bold #166534",
    warning="#9a5a00",
    error="bold #b42318",
    success="#16703a",
    reasoning_style="italic #6b7280",
    toolbar_background="",
    toolbar_model="#4b5563",
    rich_theme=Theme(
        {
            # Rich's built-in Markdown style for inline code is
            # ``bold cyan on black``. That works on dark terminals but
            # leaves black boxes in light mode, even when code blocks
            # use a light Pygments theme. Override the semantic
            # Markdown code style alongside the rest of the light
            # palette so inline code reads as a subtle light chip.
            "markdown.code": "not bold black on bright_white",
        }
    ),
)

THEMES: dict[TerminalThemeName, TerminalTheme] = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}


def get_theme(name: TerminalThemeName | str) -> TerminalTheme:
    """Return the named terminal theme, raising ``ValueError`` if unknown."""

    key = name.lower()
    try:
        return THEMES[cast(TerminalThemeName, key)]
    except KeyError as exc:
        raise ValueError(f"unknown theme {name!r}; expected dark or light") from exc
