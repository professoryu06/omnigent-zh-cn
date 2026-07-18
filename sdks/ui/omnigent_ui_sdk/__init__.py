"""omnigent UI SDK — terminal UI components for omnigent frontends.

Built on top of :mod:`omnigent_client`. This package provides
Rich-based block formatting and a prompt_toolkit-based terminal host
for building REPLs. For the headless client (HTTP, SSE, blocks),
import from :mod:`omnigent_client` directly.

Usage::

    from omnigent_client import OmnigentClient, BlockStream
    from omnigent_ui_sdk import RichBlockFormatter, TerminalHost
"""

from .terminal import (
    DARK_THEME,
    DEFAULT_USER_CONFIG,
    LIGHT_THEME,
    THEMES,
    FileMentionCompleter,
    Overlay,
    OverlayAction,
    OverlayTarget,
    PendingAttachment,
    RichBlockFormatter,
    StreamingText,
    TerminalHost,
    TerminalTheme,
    TerminalThemeName,
    UserConfig,
    UserConfigError,
    extract_at_mentions,
    load_user_config,
    save_user_config,
    state_dir,
    strip_at_mentions,
    update_user_config,
    user_config_path,
)

__all__ = [
    "DARK_THEME",
    "DEFAULT_USER_CONFIG",
    "LIGHT_THEME",
    "THEMES",
    "FileMentionCompleter",
    "Overlay",
    "OverlayAction",
    "OverlayTarget",
    "PendingAttachment",
    "RichBlockFormatter",
    "StreamingText",
    "TerminalHost",
    "TerminalTheme",
    "TerminalThemeName",
    "UserConfig",
    "UserConfigError",
    "extract_at_mentions",
    "load_user_config",
    "save_user_config",
    "state_dir",
    "strip_at_mentions",
    "update_user_config",
    "user_config_path",
]
