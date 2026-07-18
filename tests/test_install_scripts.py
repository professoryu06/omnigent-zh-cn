from __future__ import annotations

from pathlib import Path


def test_platform_installers_use_the_isolated_chinese_commands() -> None:
    root = Path(__file__).resolve().parents[1]
    powershell = (root / "scripts" / "install-zh.ps1").read_text(encoding="utf-8")
    shell = (root / "scripts" / "install-zh.sh").read_text(encoding="utf-8")

    for content in (powershell, shell):
        assert "omnigent-zh" in content
        assert "Node.js 22" in content
        assert "platform-info" in content

    assert "WSL2" in powershell
    assert "bubblewrap" in shell
