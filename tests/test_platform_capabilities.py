from __future__ import annotations

from click.testing import CliRunner

from omnigent._platform import inspect_platform, native_harness_guidance


def test_windows_native_is_sdk_and_web_only() -> None:
    capabilities = inspect_platform(
        os_name="nt",
        sys_platform="win32",
        release="Windows 11",
    )

    assert capabilities.family == "windows"
    assert capabilities.is_wsl is False
    assert capabilities.native_tmux_supported is False
    assert capabilities.sandbox_backend == "windows_jobobject"
    assert capabilities.recommended_mode == "sdk_or_web"


def test_wsl_is_linux_with_native_tmux_support() -> None:
    capabilities = inspect_platform(
        os_name="posix",
        sys_platform="linux",
        release="5.15.153.1-microsoft-standard-WSL2",
    )

    assert capabilities.family == "linux"
    assert capabilities.is_wsl is True
    assert capabilities.native_tmux_supported is True
    assert capabilities.sandbox_backend == "linux_bwrap"
    assert capabilities.recommended_mode == "native_cli"


def test_macos_uses_seatbelt_without_bubblewrap() -> None:
    capabilities = inspect_platform(
        os_name="posix",
        sys_platform="darwin",
        release="24.6.0",
    )

    assert capabilities.family == "macos"
    assert capabilities.is_wsl is False
    assert capabilities.native_tmux_supported is True
    assert capabilities.sandbox_backend == "darwin_seatbelt"
    assert capabilities.requires_bubblewrap is False


def test_windows_native_harness_guidance_points_to_wsl2() -> None:
    message = native_harness_guidance("claude", inspect_platform(os_name="nt", sys_platform="win32"))

    assert "Windows 原生模式" in message
    assert "WSL2" in message
    assert "omnigent-zh run <agent.yaml>" in message


def test_platform_info_command_prints_machine_readable_mode() -> None:
    from omnigent.cli import cli

    result = CliRunner().invoke(cli, ["platform-info", "--json"])

    assert result.exit_code == 0
    assert '"recommended_mode"' in result.output
