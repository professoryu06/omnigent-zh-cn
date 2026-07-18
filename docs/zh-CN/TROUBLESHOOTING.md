# 故障排查

## 私有仓库无法安装

症状：Git 要求用户名、无法读取私有仓库或 `uv tool install` 拉取失败。

处理：确认 `gh auth status` 已显示正确账号，再执行 `gh auth setup-git`。不要把 PAT 放进 URL、Shell 历史、README 或 `.env` 后提交。

## 网页未启动或刷新后拒绝连接

```bash
omnigent-zh server status
omnigent-zh server start
```

如果从源码安装时网页构建失败，检查 `node --version` 是否为 22+，以及 `npm` 是否能访问依赖源。

## Windows 原生启动 CLI 失败

这是设计边界，不是安装遗漏。Windows 原生不支持 tmux/PTY；请切换到 WSL2，安装 `tmux` 与 `bubblewrap` 后在 WSL2 内运行。

## Hermes 首次派发没有真实任务文本

当前已知现象是首次派发可能只出现 `resource_event`。确认子会话历史中是否有真实用户任务文本；在上游完全修复前，Hermes 不得作为项目唯一的阻塞审批人。记录重试事件，不要创建无关的重复任务。

## 凭据安全

使用 `omnigent-zh setup` 或系统密钥链管理模型凭据。发布前运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/audit-release.ps1
```

审计会阻断常见密钥模式、`.env`、数据库、虚拟环境、构建产物和本地验收文件。
