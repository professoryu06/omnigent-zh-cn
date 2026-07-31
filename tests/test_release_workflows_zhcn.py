from __future__ import annotations

from pathlib import Path


def test_release_ci_covers_windows_macos_and_linux_install_paths() -> None:
    root = Path(__file__).resolve().parents[1]
    workflows = root / ".github" / "workflows"
    windows = (workflows / "windows.yml").read_text(encoding="utf-8")
    macos = (workflows / "macos.yml").read_text(encoding="utf-8")
    linux = (workflows / "zh-cn-linux-smoke.yml").read_text(encoding="utf-8")

    assert "omnigent-zh --help" in windows
    assert "macos-latest" in macos
    assert "npm run build" in macos
    assert "omnigent-zh server" in macos
    assert "ubuntu-latest" in linux
    assert "bubblewrap" in linux
    assert "install-zh.sh" in linux


def test_upstream_watch_is_read_only_and_creates_a_review_issue() -> None:
    root = Path(__file__).resolve().parents[1]
    watch = (root / ".github" / "workflows" / "upstream-watch.yml").read_text(
        encoding="utf-8"
    )

    assert "schedule:" in watch
    assert "workflow_dispatch:" in watch
    assert "omnigent-ai/omnigent" in watch
    assert "issues: write" in watch
    assert "gh issue create" in watch
    assert "git merge" not in watch
    assert "git push" not in watch
