# 安装总览

## 私有仓库安装

1. 安装 Git、GitHub CLI、Python 3.12+、uv、Node.js 22 LTS+ 和 npm。
2. 执行 `gh auth login`，确保账号有 `professoryu06/omnigent-zh-cn` 的读取权限。
3. 执行 `gh auth setup-git`，让 Git 使用 GitHub CLI 凭据。
4. 执行：

```bash
uv tool install --force --python 3.12 "git+https://github.com/professoryu06/omnigent-zh-cn.git"
```

5. 执行 `omnigent-zh platform-info` 检查模式，再运行 `omnigent-zh setup` 配置模型。

源码安装会构建 Web UI，因此 Node.js 低于 22、npm 无法联网或前端构建失败都会导致安装失败。这是刻意的失败保护，避免安装一个没有网页界面的不完整版本。

## 本地 clone 安装

```bash
git clone https://github.com/professoryu06/omnigent-zh-cn.git
cd omnigent-zh-cn
```

- Windows PowerShell：`powershell -ExecutionPolicy Bypass -File scripts/install-zh.ps1`
- macOS/Linux/WSL2：`sh scripts/install-zh.sh`

安装脚本会检查 Node.js 22、uv、npm 和平台需要的 tmux/bubblewrap，并在源码目录构建中文 Web UI。
