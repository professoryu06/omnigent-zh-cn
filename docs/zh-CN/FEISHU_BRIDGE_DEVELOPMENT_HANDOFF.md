# Omnigent 飞书通道开发交接方案

> 状态：待开发。本文是交给实现 Agent 的唯一范围说明；最后代码审查与是否进入下一阶段
> 由 Codex 负责。

## 1. 目标与边界

建立独立的飞书桥接服务，使飞书项目群成为人类的任务入口、进度面板与审批面板；
Omnigent + tmux + CLI 仍是唯一的执行面。

```text
飞书项目群 <-> 飞书桥接服务 <-> 项目状态存储 <-> Omnigent/tmux <-> 多个 CLI
                                  |
                                  +-> Obsidian（人工可读项目记忆）
```

桥接服务必须放在独立项目 `F:\\codex-ai\\omnigent-feishu-bridge`，不得修改
`F:\\codex-ai\\omnigent-zh-cn` 的调度核心，也不得复制其内部实现。

### MVP 目标

1. 一个飞书群绑定一个项目。
2. 桥接服务将项目的结构化执行事件同步为简洁中文消息。
3. 仅白名单群和白名单用户的消息可被接收与审计；MVP 不执行任何入站控制动作。
4. Omnigent、tmux、模型 API Key、VPN 凭据不通过飞书传输或显示。
5. 飞书故障不能阻断 Omnigent 任务；桥接服务重启不能重复投递已确认事件。

### 非目标

- 不引入 OpenClaw runtime；它只能作为飞书 WebSocket 接入模式的参考。
- 不做飞书下发 Shell、tmux、Git、CLI 或任意代码执行命令。
- 不做动态安装 CLI、创建模型凭据、远程公网控制或腾讯云部署。
- 不做多群路由、图谱记忆、Obsidian 双向编辑、Redis、消息队列或 Docker 编排。

## 2. 当前项目进度（2026-07-20）

### 已完成并已验证

| 项目 | 状态 | 证据/说明 |
|---|---|---|
| Omnigent 中文发行版 | 已完成 | 仓库：`F:\\codex-ai\\omnigent-zh-cn`；公开发行与中文文档已完成。 |
| 中文 UI 回归 | 已完成 | 历史验收为 4,000+ 测试通过；仅保留上游 `AgentInfo` 的 `1K` 格式化基线失败。 |
| WSL2 完整运行环境 | 已现场复核 | `tmux 3.4`、`bubblewrap 0.9.0`、Omnigent 服务 `127.0.0.1:6767` 运行中。 |
| Omnigent 宿主守护进程 | 已现场复核 | 后台服务运行，当前报告 10 个 live sessions，host daemon attached。 |
| Kimi K3 团队试点 | 已存在 | `F:\\codex-ai\\omnigent-teams\\kimi-k3-team-pilot` 有团队配置、诊断报告和试点报告。 |
| 多 CLI 角色定义 | 已存在 | Kimi 主理人、Claude Code、Kimi Researcher、Qwen Verifier、Hermes Reviewer。 |
| 飞书桥接服务 | 未开始 | `F:\\codex-ai\\omnigent-feishu-bridge` 尚未创建。 |

### 已确认的架构决策

- 主理人由创建项目的人显式选择，不能由系统随机猜测。
- 当前可选主理人默认为已配置的 Kimi K3；后续可增加 Claude、Qwen、Codex 等。
- Obsidian 是人工可读、可审计的知识主库；飞书不是长期技术记忆库。
- Omnigent Graph 只作为后续实验性记忆索引候选，不属于本项目 MVP。
- 固定出口网络/VPN 是独立基础设施工作项，不能在飞书桥接项目中实现或存放凭据。

## 3. 目标架构

### 3.1 组件职责

| 组件 | 职责 | 禁止事项 |
|---|---|---|
| 飞书工作台机器人 | 接收群事件、发送状态卡片/消息 | 不直接运行 CLI 或保存模型密钥。 |
| Bridge API | 验签、白名单、事件去重、项目映射、状态转发 | 不包含 Omnigent 调度逻辑。 |
| Project Registry | 保存群、项目、会话、tmux 标识的映射 | 不保存 API Key、VPN 订阅或完整对话文本。 |
| Event Store | 追加式保存标准化事件和投递状态 | 不把飞书投递成功作为任务完成条件。 |
| Omnigent Adapter | 从受控 JSONL/文件读取项目事件；未来才接稳定 API | 不读取或修改 Omnigent 私有数据库。 |
| Obsidian | 项目简报、Todo、审计与最终报告 | 不被飞书直接编辑。 |

### 3.2 必须使用的事件契约

第一版只接受下列事件类型。所有事件均使用 JSONL 追加写入，便于离线恢复。

```json
{
  "event_id": "uuid",
  "project_id": "kimi-k3-team-pilot",
  "occurred_at": "2026-07-20T10:00:00Z",
  "type": "task_started",
  "actor": {"id": "claude_code", "display_name": "Claude Code"},
  "task": {"id": "task-03", "title": "实现飞书消息格式", "status": "running"},
  "summary": "开始处理消息格式化。",
  "severity": "info",
  "metadata": {}
}
```

允许的 `type`：`project_created`、`plan_proposed`、`task_started`、`task_progress`、
`task_blocked`、`task_completed`、`review_completed`、`runner_error`、`project_completed`。

`event_id` 是全局幂等键；`project_id` 是工作区标识；`metadata` 必须经过脱敏处理。

### 3.3 飞书消息策略

- 对外只有一个“AI 开发工作台”机器人；不同 CLI 以角色标签显示，不能各自注册机器人。
- 普通进度消息合并并限流，避免群刷屏。
- `task_blocked`、`runner_error`、`plan_proposed`、`review_completed` 必须即时发送。
- 第一版仅发送纯文本或简单卡片；审批操作卡片留给 P4-P6。

## 4. 开发阶段与 Todo

### P0：人工前置配置（不写程序）

**负责人：用户。**

- [ ] 在飞书开放平台创建“AI 开发工作台”企业自建应用。
- [ ] 创建机器人并将其加入测试项目群。
- [ ] 配置事件接收方式；本机开发优先选择 WebSocket 长连接模式，避免暴露公网回调。
- [ ] 仅申请 MVP 所需的最小消息接收和发送权限。
- [ ] 建立专用测试群，记录 `chat_id`，不在真实工作群先试。
- [ ] 通过本机受控 `.env` 保存 App ID/App Secret；不得发到聊天、Git 或截图中。

**验收：** 机器人可加入测试群；凭据只存在本机 `.env`；没有广泛通讯录、云盘或管理员权限。

### P1：项目骨架、配置与安全基础（写程序）

**实现：DS。审查：Codex。**

- [ ] 创建 `F:\\codex-ai\\omnigent-feishu-bridge` 独立 Git 仓库。
- [ ] 定义 Python 3.12 服务、依赖锁定、格式检查、单元测试和中文 README。
- [ ] 建立 `.env.example`，只列变量名，禁止真实值。
- [ ] 实现严格配置校验：缺失密钥、非法群 ID、无效工作目录时启动失败且输出中文可操作提示。
- [ ] 实现 `GET /health`，只返回版本、服务状态和非敏感依赖状态。
- [ ] 实现结构化日志与敏感字段脱敏。
- [ ] 增加 `.gitignore`、提交前密钥扫描和 SQLite/日志排除规则。

**验收：** 空配置无法启动；合法测试配置可启动；日志、测试快照和 Git 暂存区均无密钥。

### P2：项目注册与事件存储（写程序）

**实现：DS。审查：Codex。**

- [ ] 实现 `ProjectRegistry`：`project_id`、工作目录、飞书 `chat_id`、Omnigent conversation ID、tmux session 名称。
- [ ] 使用 SQLite 保存映射、事件、投递回执和失败重试状态。
- [ ] 实现只允许受控项目根目录的路径校验，禁止任意本机路径读取。
- [ ] 实现上述事件 JSON Schema 的解析、校验和 JSONL 追加读取。
- [ ] 以 `event_id` 保证事件幂等；重启后仍不能重复投递。
- [ ] 增加测试：白名单路径、重复事件、损坏 JSONL、并发读取、重启恢复。

**验收：** 可注册一个测试项目并写入事件；同一事件重复输入仅保留一次投递记录。

### P3：飞书只读监控适配器（写程序）

**实现：DS。审查：Codex。**

- [ ] 实现飞书连接适配器，接收事件但 MVP 不执行入站指令。
- [ ] 实现允许 `chat_id` 和允许用户白名单；其他来源只写脱敏审计日志。
- [ ] 实现事件到中文飞书消息的格式化器。
- [ ] 实现优先级、限流和合并：进度消息可合并，阻塞和错误不可延迟。
- [ ] 实现发送失败的指数退避重试与最终失败状态。
- [ ] 实现一个本地模拟飞书客户端，所有自动化测试禁止依赖真实飞书账号。
- [ ] 为 `kimi-k3-team-pilot` 创建不含敏感数据的演示 JSONL，完成本地端到端冒烟。

**验收：** 从演示 JSONL 读到 `task_started`、`task_blocked`、`review_completed` 时，模拟客户端收到正确中文事件；重复运行不重复发送；飞书模拟失败会重试且不阻塞事件读取。

### P3.5：Codex 审查闸门（不由 DS 合并）

**负责人：Codex。**

- [ ] 审查事件契约是否足以支持未来审批与多 CLI 状态。
- [ ] 审查飞书输入是否能间接触发路径遍历、命令执行或提示注入。
- [ ] 审查密钥脱敏、SQLite 文件权限、日志保留和失败降级。
- [ ] 审查 WSL2 本地运行、服务重启、网络中断和 Omnigent 不可用时的行为。
- [ ] 仅在 P1-P3 自动化测试、手动模拟和安全检查均通过后批准 P4。

### P4：飞书发起项目与选择主理人（后续，写程序）

- [ ] 实现“新项目”命令/卡片；不接受自由文本作为 Shell 命令。
- [ ] 从受版本管理的成员名册中选择主理人：Kimi、Claude、Qwen、Hermes、后续 Codex。
- [ ] 创建项目工作目录和基础项目元数据。
- [ ] 将飞书群、项目、主理人、工作目录写入 Registry。

### P5：自动计划与审批（后续，写程序）

- [ ] 主理人生成 `PROJECT_BRIEF.md`、`TEAM_PLAN.md`、`TASKS.md`、`RUN_STATE.md`。
- [ ] 主理人只能从预配置成员名册提出团队建议，不能创建未知 harness、模型或权限。
- [ ] 在飞书发送计划摘要和“批准/退回修改”卡片。
- [ ] 卡片回调必须验签、幂等、绑定原始项目和授权用户。
- [ ] 未批准时绝不启动 CLI 团队。

### P6：批准后执行与状态闭环（后续，写程序）

- [ ] 将已批准的 `TEAM_PLAN` 校验并物化为 Omnigent 团队运行配置。
- [ ] 通过受限启动器启动既有 Omnigent/tmux 团队，禁止拼接任意 Shell 字符串。
- [ ] 回传子任务状态、阻塞、审查和最终结果。
- [ ] 把最终项目摘要和 Todo 状态写入 Obsidian。

### V2：远程访问与高级能力（明确延期）

- [ ] 腾讯云部署、安全隧道、HTTPS、远程身份认证。
- [ ] 固定出口网络与 tmux 的独立基础设施方案。
- [ ] 多飞书群、多项目并发、配额与队列。
- [ ] Omnigent Graph 实验性共享记忆索引。
- [ ] 飞书文件/图片上下文、Obsidian 双向同步、可视化运行面板。

## 5. 实现 Agent 工作规则

1. 先在独立仓库完成 P1-P3；不改 Omnigent 核心，不改现有 Kimi 团队 YAML。
2. 使用 Superpowers 流程：`brainstorming` -> 设计文档 -> `writing-plans` ->
   `subagent-driven-development` -> `test-driven-development` -> 验证。
3. 所有飞书输入均视为不可信数据；禁止将其拼接为路径、Shell、tmux、Git 或模型提示词。
4. 不提交 `.env`、API Key、App Secret、VPN 配置、SQLite 数据库、日志、真实消息样本。
5. 每一阶段结束写 handoff：`ops/handoffs/pN-<name>-completion.md`，包含文件列表、
   测试命令、结果、已知限制和下一阶段接口。
6. P1-P3 完成后停止，等待 Codex 审查；不得自行开始 P4。

## 6. P1-P3 最终验收清单

- [ ] 单元测试覆盖配置、事件 Schema、幂等、路径白名单、白名单群、重试和脱敏。
- [ ] 本地模拟飞书端到端测试通过，不需要真实账号。
- [ ] 使用测试群手动验证一条状态消息可到达群内。
- [ ] 服务重启后不会重复发送同一 `event_id`。
- [ ] 飞书不可用时 Omnigent/JSONL 事件不会丢失，且任务执行不受阻断。
- [ ] `git diff --check`、格式检查、测试、密钥扫描通过。
- [ ] README 说明 Windows/WSL2 边界、配置步骤、运行命令、故障排查和数据边界。
- [ ] Codex 完成安全、接口和可维护性审查并明确批准。

## 7. 交付顺序

1. 用户完成 P0 飞书应用与测试群准备。
2. DS 按本文完成 P1-P3，提交 handoff，不进入 P4。
3. Codex 审查 P1-P3；修复通过后才决定是否开始 P4。
4. P4-P6 单独重新设计和拆包，避免动态团队、审批和 tmux 启动混入 MVP。
