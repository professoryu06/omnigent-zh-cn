# Omnigent Linux tmux Host 接入方案

日期：2026-07-15
状态：设计中，尚未部署。

## 目标

将原生 CLI 的 PTY/tmux 执行从 Windows Host 移到 Linux Host，同时复用现有 Omnigent Web UI、会话控制层、Agent 定义和中文化工作。

## 第一性原理

Web UI 负责控制与展示；Host 负责在本机执行 CLI。tmux 是 Linux Host 的执行细节，不应进入前端或 i18n 的业务逻辑。因此中文化、会话 UI、审批 UI 与 tmux Host 可以独立演进。

## 复用边界

可直接复用：

- Web UI、i18n Provider、中文词典与前端测试。
- Omnigent Server 的会话、Agent、审批、文件和终端 API。
- 用户的提示词、Skill、任务记录与 Agent 角色定义。

需要按 Linux Host 重新配置：

- `tmux`、`bubblewrap`、Node/uv/Python 和各 CLI 的安装。
- Hermes、Claude Code、Codex 的登录态和 API/模型路由环境变量。
- Host 可见的工作目录与 Git 凭据。
- Linux 专用 Agent YAML 与策略路径。

不会直接迁移：

- Windows 原生终端会话及其 PTY 历史。
- Windows 本机的 CLI 登录令牌或密钥。

## 两阶段实施

### 阶段 A：本机 WSL2 验证

目的：不暴露公网、不配置 HTTPS，先验证 tmux/PTY、Hermes 和一个简单 CLI 会话。

1. 安装 WSL2 Ubuntu，并启用 systemd。
2. 在 WSL 安装 `tmux`、`bubblewrap`、Git、Node、uv/Python 与 Omnigent。
3. 在 WSL 安装 Hermes CLI；仅使用一个专用测试目录和测试 Git 仓库。
4. Windows 上的 Omnigent Server 保持本机运行；WSL Host 通过明确的 Server URL 连接。
5. 创建 Linux Host 专用 Agent，启动 Hermes 原生会话，验证终端输出、停止、重连、文件面板。

验收：Web 端能看到 Linux Host；Hermes 会话不再出现 Windows PTY 错误；tmux session 可在 WSL 中查看。

### 阶段 B：腾讯云 Ubuntu Host

目的：获得持续运行的 tmux 会话，为后续远程访问 Beta 做准备。

1. 先在腾讯云部署 Omnigent Server，再让 Linux Host 以出站连接方式注册。
2. 配置域名、HTTPS、反向代理与最小防火墙规则后，才开放 Web UI。
3. 安装 tmux、bubblewrap、Git、Omnigent 和经过单独登录的 CLI。
4. 使用非 root 专用用户运行 Host；每个项目限定工作目录和 Git 权限。
5. 设置服务自启动、日志轮转、Host 心跳和磁盘阈值监控。

验收：服务器重启后 Host 自动回连；新会话可以创建、停止和恢复；不暴露 CLI 凭据到浏览器或 Windows 本机。

## 安全边界

- Server 只接收 HTTPS；Host 使用出站连接，避免为 Host 开放入站 SSH 以外的端口。
- CLI 登录态与模型密钥仅保存在各自 Linux Host，不写入前端、聊天记录或 Obsidian。
- 默认使用最小权限的 Linux 用户；不以 root 运行 tmux 或 Agent CLI。
- 先使用测试仓库；生产项目按目录与 Git 凭据隔离。
- `bubblewrap` 是 Linux 原生终端的基础隔离，不把它当作完整多租户沙箱。

## 决策顺序

1. 先做阶段 A 的 WSL2 验证。
2. 验证通过后再处理腾讯云域名、HTTPS 和部署。
3. Linux Host 稳定后继续 P2B-P5 中文化，不阻塞前端翻译，但不把 Windows 原生 Hermes 当作验收环境。
