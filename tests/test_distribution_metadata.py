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


def test_public_docs_describe_a_complete_distribution() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    agent_install = (root / "docs" / "zh-CN" / "AGENT_INSTALL.md").read_text(
        encoding="utf-8"
    )

    install_url = "git+https://github.com/professoryu06/omnigent-zh-cn.git"
    assert "完整源码发行版" in readme
    assert "无需另行安装官方 Omnigent" in readme
    assert install_url in readme
    assert "omnigent-ai/omnigent" in readme
    assert "公开仓库" in agent_install
    assert install_url in agent_install
    assert "gh auth setup-git" not in agent_install
