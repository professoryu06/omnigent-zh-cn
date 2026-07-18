from __future__ import annotations

import tomllib
from pathlib import Path


def test_chinese_distribution_uses_isolated_package_and_commands() -> None:
    root = Path(__file__).resolve().parents[1]
    metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

    assert metadata["project"]["name"] == "omnigent-zh-cn"
    assert metadata["project"]["version"] == "0.6.0.dev0+zhcn.1"
    assert metadata["project"]["scripts"] == {
        "omnigent-zh": "omnigent.cli:main",
        "omni-zh": "omnigent.cli:main",
    }
    assert "omnigent-zh-cn-client==0.6.0.dev0+zhcn.1" in metadata["project"]["dependencies"]
    assert "omnigent-zh-cn-ui-sdk==0.6.0.dev0+zhcn.1" in metadata["project"]["dependencies"]


def test_chinese_sdk_distributions_depend_on_each_other() -> None:
    root = Path(__file__).resolve().parents[1]
    client = tomllib.loads((root / "sdks" / "python-client" / "pyproject.toml").read_text(encoding="utf-8"))
    ui = tomllib.loads((root / "sdks" / "ui" / "pyproject.toml").read_text(encoding="utf-8"))

    assert client["project"]["name"] == "omnigent-zh-cn-client"
    assert "omnigent-zh-cn==0.6.0.dev0+zhcn.1" in client["project"]["dependencies"]
    assert ui["project"]["name"] == "omnigent-zh-cn-ui-sdk"
    assert "omnigent-zh-cn-client==0.6.0.dev0+zhcn.1" in ui["project"]["dependencies"]
