# Grok Native 部署、测试与使用经验

更新时间：2026-08-04

## 结论先说

Grok Native 已通过专项最终验收，可在 Omnigent 中正常使用，也可以被其他 Agent 通过 AgentCenter 唤起。当前结论仅针对 Grok，不代表 Claude、Codex、Qwen、Pi 或全局 Gate 2 已通过。

## 1. 运行架构

Grok Native 采用 WSL/Linux 中的 CLI subprocess/headless 路径：

```text
Omnigent AgentCenter
  -> grok-native-ui
  -> per-session GROK_HOME
  -> Grok CLI
  -> grok-4.5
```

关键设计：

- `grok-native` 是 headless CLI_SUBPROCESS，不是 Windows native TUI。
- 首次调用不创建 Windows tmux/PTY，也不进入 `TerminalRegistry.launch`。
- 每个 Omnigent 会话使用独立的 `GROK_HOME` 和 leader socket。
- 认证材料通过隔离目录引用，不把真实凭据复制进项目或 evidence。
- 子进程环境采用 deny-by-default；不会继承 Claude、Codex、OpenAI、Qwen 等其他模型的密钥或配置。
- 默认强制 `NO_PROXY=127.0.0.1,localhost`；只有显式设置 `OMNIGENT_GROK_PROXY` 时才注入 Grok 代理。
- AgentCenter 调用通过 caller → target 和 `parent_session_id` 建立父子关系。

## 2. WSL 部署要点

环境建议：

- WSL 发行版：Ubuntu-24.04
- Grok CLI：在 WSL 内安装并确认版本
- 认证目录：使用 Grok 专用目录，不使用 OpenCodex、Codex 或 Claude 的配置目录
- Omnigent server/host：启动后确认 host online，再创建会话

认证时在 WSL 中执行设备码登录。示例：

```bash
GROK_HOME="$HOME/.grok-omnigent" grok login --device-code
GROK_HOME="$HOME/.grok-omnigent" grok models
```

看到 `You are logged in with grok.com.` 后才开始测试。任何文档、截图、日志和 evidence 都不得记录 token、auth 内容或设备码。

## 3. 日常使用流程

1. 启动 WSL 和 Omnigent server/host。
2. 在 Web UI 中选择 Grok Native（显示名通常为 `Grok` 或 `grok-native-ui`）。
3. 新建会话发送简单指令，例如要求返回唯一 sentinel。
4. 看到真实 assistant 回复且会话进入 idle 后，再进行多轮或 AgentCenter 调用。
5. 需要其他 Agent 调用时，让调用方通过 AgentCenter 指定 `grok-native-ui`；不要手工复制 Grok 会话目录。

## 4. 专项验收标准

### G1：认证

- 私有 `GROK_HOME` 存在。
- `grok models` 明确显示已登录。
- auth 文件存在，但其内容不进入报告。

### G2：单轮

- assistant item 中出现预设 sentinel。
- 会话最终状态为 `idle`。
- resources 只有一个 `environment`。
- 不出现 `terminal_tui_main`、`tmux_socket` 或 `terminal_transport=control`。

### G3：同会话双轮

- 第一轮使用 `--session-id` 创建。
- 第二轮使用 `--resume` 复用同一 Grok session。
- 两轮都必须有真实 assistant item，不能用 user 回显当作成功。
- 两轮最终都进入 idle。
- evidence 应记录不含凭据的 session id、时间范围和摘要。

### G4：AgentCenter

- 记录 caller session 与 target session。
- target 带正确的 `parent_session_id` 和 sub-agent 关系。
- target 返回真实 assistant sentinel。
- target 不创建 tmux/PTY 资源。

### G5：代理隔离

在父环境故意放入 HTTP/HTTPS/ALL_PROXY 等变量后，Grok spawn 环境仍应满足：

```text
NO_PROXY=127.0.0.1,localhost
HTTP_PROXY/HTTPS_PROXY/ALL_PROXY 不继承
OMNIGENT_GROK_PROXY 未设置时不出现
```

### G6：清理与泄漏

- 旧失败 harness 要逐 PID 终止并确认 dead。
- vendor Grok CLI 泄漏数为 0。
- 常驻 harness 要单独标记为产品 idle 语义，不能误报为泄漏。
- 观察脚本进程单列。
- OpenCodex 的 10100 不应被 Grok Native 连接或占用。
- leak-scan 必须最后执行，evidence 持久保留。

## 5. 已验证结果

最终专项 RUN：`grok-native-final-01-20260804T0110Z`

- G1 认证通过。
- G2 单轮 `GROK_NATIVE_FINAL_OK` 通过。
- G3 双轮 `ROUND1_OK` / `ROUND2_OK`，同一 Grok session 复用通过。
- G4 AgentCenter `GROK_AGENTCENTER_FINAL_OK` 通过。
- G5 代理负向隔离通过。
- G6 清理、端口和 leak-scan 通过。
- evidence 根目录保留 20 个文件。

## 6. 常见故障与处理

### 显示未认证

先在 WSL 中用同一个私有 `GROK_HOME` 执行 `grok models`。若认证失效，重新 `grok login --device-code`，然后使用全新 RUN_ID 重测，不要把旧 failed 会话拼进新结果。

### 出现 tmux/PTY 或 terminal_tui_main

这通常表示旧 server/host 未加载 headless 注册、旧会话复用，或路由错误。应先确认当前 server/host 已重启并加载最新代码，再新建全新会话。不要把这类旧会话当作当前 Grok Native 结果。

### Grok 被其他代理影响

检查 spawn 环境是否剥离大小写形式的 HTTP/HTTPS/ALL_PROXY。不要修改 OpenCodex 的 10100，也不要把 OpenCodex 的 `config.toml` 复制到 Grok HOME。需要代理时只通过 `OMNIGENT_GROK_PROXY` 显式设置。

### 只有用户消息，没有 assistant

不能算通过。必须看到真实 assistant item、正确 sentinel 和最终 idle；仅标题、用户回显或创建成功都不构成模型成功。

## 7. Evidence 与文档纪律

- 每次诊断使用全新 RUN_ID 和独立 evidence 目录。
- evidence 不删除、不拼接旧 RUN。
- 报告中的 token、auth、设备码和代理凭据统一写 `[REDACTED]`。
- `sessions.txt` 应列出 G2、G3、G4 的 caller/target；若漏记，只能作为审计文档修正，不要改写业务 evidence。
- 单次 Grok 专项通过不等于全局 Gate 2 通过，也不自动允许 merge。

## 当前状态

Grok Native 可以投入日常使用，并可由其他 Agent 通过 AgentCenter 调用。后续若要签全局 Gate 2，需要另开独立验收卡，不能复用本专项结论。
