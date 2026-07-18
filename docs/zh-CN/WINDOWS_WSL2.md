# Windows 与 WSL2

## Windows 原生模式

Windows 原生支持本地服务、网页界面和 SDK harness。它使用 Windows Job Object 管理进程树，但不提供 Linux/macOS 那样的文件系统和网络隔离。

Windows 原生不支持 tmux/PTY 包装器，因此不要在 PowerShell 中运行依赖原生终端的 Claude、Kimi、Qwen 或 Hermes 多 CLI 协作。需要该能力时，请使用 WSL2。

## WSL2 完整模式

在 Ubuntu WSL2 中安装：

```bash
sudo apt-get update
sudo apt-get install -y tmux bubblewrap git
gh auth setup-git
uv tool install --force --python 3.12 "git+https://github.com/professoryu06/omnigent-zh-cn.git"
omnigent-zh platform-info
```

`platform-info` 应显示 Linux、WSL2 和 `native_cli`。之后在 WSL2 内完成 CLI 登录与 `omnigent-zh setup`。

## 常见误区

- PowerShell 命令不能直接在 Bash 使用；进入 WSL2 后先执行 `source ~/.profile`。
- Bash 的 `cd` 后必须有空格，例如 `cd /mnt/f/...`。
- 复制长 API Key 时优先使用终端右键粘贴或 Windows Terminal 的粘贴设置；不要把 Key 写入项目文件。
