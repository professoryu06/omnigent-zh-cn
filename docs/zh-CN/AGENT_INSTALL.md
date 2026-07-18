# 给其他 Agent 的安装指令

将以下一句话直接交给拥有 GitHub 私有仓库读取权限的 Agent：

```text
先执行 gh auth setup-git；随后用 uv tool install --force --python 3.12 "git+https://github.com/professoryu06/omnigent-zh-cn.git"，安装后运行 omnigent-zh setup；Windows 需要多 CLI/tmux 时在 WSL2 内执行同一命令。
```

前提：Agent 所在设备已经安装 GitHub CLI、uv、Python 3.12+、Node.js 22+ 与 npm，并已通过 `gh auth login` 登录一个具有仓库读取权限的账号。

安装后先执行 `omnigent-zh platform-info`。它会明确告诉 Agent 当前是 Windows 原生降级模式、WSL2/Linux 完整模式，还是 macOS 原生模式。
