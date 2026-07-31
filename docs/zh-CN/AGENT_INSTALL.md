# 交给 Agent 的安装指令

本项目是公开仓库，且是完整源码发行版。不要额外安装官方 Omnigent，也不要把 API Key、`.env`、数据库或会话日志写入仓库。

将下面文字直接交给已具备本机终端权限的 Agent：

```text
执行 uv tool install --force --python 3.12 "git+https://github.com/professoryu06/omnigent-zh-cn.git"，随后运行 omnigent-zh platform-info 和 omnigent-zh setup。Windows 需要 tmux 多 CLI 协作时，请在 WSL2 内执行同一命令；不要提交任何凭据、.env、数据库、日志或构建缓存。
```

## 前置条件

- Python 3.12+、`uv`、Node.js 22+、npm。
- Linux/WSL2 原生 CLI：`tmux` 与 `bubblewrap`。
- macOS 原生 CLI：`tmux`；使用系统 seatbelt，不要求 `bwrap`。
- 各模型 CLI 已按其官方方式安装和登录；本项目不绕过账户、地区或服务商权限。

安装后先执行 `omnigent-zh platform-info`。它会说明当前是 Windows 原生 Web/SDK 模式、WSL2/Linux 完整模式，还是 macOS 原生模式。
