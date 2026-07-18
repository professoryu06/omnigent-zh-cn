"""Focused tests for native Kimi launch defaults."""

from omnigent.kimi_native import _effective_kimi_launch_args


def test_kimi_native_defaults_to_yolo_for_runner_owned_sessions() -> None:
    """Headless runner sessions must not stall at Kimi's TUI permission menu."""
    assert _effective_kimi_launch_args(()) == ["--yolo"]


def test_kimi_native_preserves_explicit_auto_mode() -> None:
    """An explicit selective-review request overrides the unattended default."""
    assert _effective_kimi_launch_args(("--auto", "--model", "k3")) == [
        "--auto",
        "--model",
        "k3",
    ]
