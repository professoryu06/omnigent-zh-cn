# Omnigent 中文版

> Omnigent 的简体中文私有发行版：默认中文界面、保留英文切换，并为 Windows、WSL2 与 macOS 写明真实可用边界。

本仓库是基于 [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent) 源码快照的私有派生发行版，不是官方项目，也不替代官方支持渠道。许可证和第三方声明见 [LICENSE](LICENSE)、[NOTICE](NOTICE) 与 [UPSTREAM.md](UPSTREAM.md)。

## 适合什么场景

- 通过浏览器管理本地或远程的 AI 编码会话。
- 在一个项目中编排 Claude、Kimi、Qwen、Hermes 等不同 harness。
- 默认使用简体中文界面，需要时可在设置中切换英语。
- 在 Windows 上使用 Web/SDK 模式，或通过 WSL2 使用 tmux 原生 CLI 模式。

## 一句话让 Agent 安装

前提：设备已执行 `gh auth login`，且该 GitHub 账号拥有本私有仓库读取权限。

```text
先执行 gh auth setup-git；随后用 uv tool install --force --python 3.12 "git+https://github.com/professoryu06/omnigent-zh-cn.git"，安装后运行 omnigent-zh setup；Windows 需要多 CLI/tmux 时在 WSL2 内执行同一命令。
```

安装后使用的命令是 `omnigent-zh` 和 `omni-zh`，不会覆盖官方 Omnigent 的 `omnigent` / `omni` 命令。

## 快速开始

### 1. 前置条件

- Python 3.12+ 与 [uv](https://docs.astral.sh/uv/)
- Git 与 GitHub CLI（私有安装需要）
- Node.js 22 LTS+ 与 npm（源码安装会构建中文 Web UI）
- 需要原生编码 CLI 时：`tmux`
- Linux/WSL2 原生 CLI：`bubblewrap` / `bwrap`

### 2. 安装

```bash
gh auth setup-git
uv tool install --force --python 3.12 "git+https://github.com/professoryu06/omnigent-zh-cn.git"
omnigent-zh platform-info
omnigent-zh setup
```

如果你已 clone 仓库，需要预检和本地安装：Windows PowerShell 执行 `scripts/install-zh.ps1`；macOS、Linux、WSL2 执行 `sh scripts/install-zh.sh`。

### 3. 启动

```bash
omnigent-zh
```

首次启动完成模型或 CLI 凭据配置后，会启动本地服务和中文 Web UI。若浏览器刷新后无法连接，先执行：

```bash
omnigent-zh server status
omnigent-zh server start
```

## 平台支持

| 平台 | Web/SDK harness | tmux 原生 CLI | 沙箱 | 推荐方式 |
|---|---:|---:|---|---|
| Windows 原生 | 支持 | 不支持 | Windows Job Object，不隔离文件/网络 | Web 或 SDK harness |
| Windows + WSL2 | 支持 | 支持 | Linux bubblewrap | Windows 上的完整多 CLI 模式 |
| macOS | 支持 | 支持 | macOS seatbelt | 原生完整模式 |
| Linux | 支持 | 支持 | Linux bubblewrap | 原生完整模式 |

Windows 原生无法提供 tmux/PTY 包装器，因此 Claude、Kimi、Qwen、Hermes 的完整原生 CLI 协作必须在 WSL2 内运行。运行 `omnigent-zh platform-info` 可查看当前机器的实际模式。

## 模型和团队

使用 `omnigent-zh setup` 配置模型提供方和 harness 凭据。密钥仅保存在系统密钥链或本机配置中；不要把密钥、`.env`、数据库或会话日志提交到仓库。

推荐团队分工：主理人负责任务拆解与汇总；Claude/Kimi 负责实现或研究；Qwen 负责独立核验；Hermes 负责风险审查。生产任务不要仅因某个子智能体显示“完成”就接受结论，应检查其实际产物、来源和会话记录。

## 重要限制

- Hermes 原生首条消息在当前上游运行链中可能只形成 `resource_event`。在该问题彻底修复前，不应让 Hermes 成为唯一阻塞审批者；首次派发必须确认会话历史出现真实任务文本。
- 本发行版不会绕过模型服务商的地区、账号、授权或 API 使用限制。
- 从私有 Git 源安装需要 GitHub CLI 已授权；`gh auth setup-git` 失败时通常意味着 Git 凭据代理尚未配置。

## 文档

- [安装总览](docs/zh-CN/INSTALL.md)
- [Windows 与 WSL2](docs/zh-CN/WINDOWS_WSL2.md)
- [macOS](docs/zh-CN/MACOS.md)
- [故障排查](docs/zh-CN/TROUBLESHOOTING.md)
- [供 Agent 使用的安装指令](docs/zh-CN/AGENT_INSTALL.md)
- [上游与许可说明](UPSTREAM.md)

## 更新

```bash
gh auth setup-git
uv tool install --force --python 3.12 "git+https://github.com/professoryu06/omnigent-zh-cn.git"
```

本仓库保持 Private，不发布到 PyPI 或 npm。

## 许可证

本发行版遵循 Apache License 2.0；必须保留原始 [LICENSE](LICENSE) 和 [NOTICE](NOTICE)。中文化、安装脚本和发布文档的改动也在同一许可证下提供。
