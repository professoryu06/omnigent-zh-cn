from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.skipif(shutil.which("powershell") is None, reason="requires Windows PowerShell")
def test_release_audit_allows_clean_repo_and_rejects_secret_file(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    audit = root / "scripts" / "audit-release.ps1"
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "README.md").write_text("safe content\n", encoding="utf-8")

    clean = subprocess.run(
        ["powershell", "-NoProfile", "-File", str(audit), "-RepositoryPath", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert clean.returncode == 0, clean.stderr

    fake_key = "sk-" + "0123456789abcdef0123456789abcdef"
    (tmp_path / ".env").write_text(f"OPENAI_API_KEY={fake_key}\n", encoding="utf-8")
    blocked = subprocess.run(
        ["powershell", "-NoProfile", "-File", str(audit), "-RepositoryPath", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert ".env" in blocked.stdout
    assert fake_key not in blocked.stdout

    (tmp_path / ".env").unlink()
    (tmp_path / "README.md").write_text(f"token={fake_key}\n", encoding="utf-8")
    secret_content = subprocess.run(
        ["powershell", "-NoProfile", "-File", str(audit), "-RepositoryPath", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert secret_content.returncode != 0
    assert "Possible secret content: README.md" in secret_content.stdout
    assert fake_key not in secret_content.stdout


@pytest.mark.skipif(shutil.which("powershell") is None, reason="requires Windows PowerShell")
def test_release_audit_uses_its_parent_as_default_repository(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy2(root / "scripts" / "audit-release.ps1", scripts / "audit-release.ps1")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "README.md").write_text("safe content\n", encoding="utf-8")

    result = subprocess.run(
        ["powershell", "-NoProfile", "-File", str(scripts / "audit-release.ps1")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
