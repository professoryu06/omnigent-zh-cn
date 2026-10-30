# CODEX_TASK_29：Codex 直连重规划与事故记录

## 1. 本轮范围与结论

本轮仅由当前 Codex 订阅直连会话执行项目级规划、只读状态核对和文档归档，不启动 Claude、Qwen、Grok、Pi 或其他模型 CLI，不重新发送模型任务。

上一次 Claude-DS 子任务状态标记为 `BLOCKED`。该状态只描述子任务的环境阻塞，不代表 Task 29 代码修复完成，也不代表 Codex 直连链路回退。

## 2. 事故记录

- Claude-DS 调用失败的直接原因是 WSL 无法访问 Windows CCSwitch 的 `127.0.0.1:15721`。
- WSL 与 Windows 的 localhost/网络边界使该 CCSwitch 路径不可达；本轮不重试网络、不调用 CCSwitch，也不调整网络桥接。
- 此次失败发生在 Claude-DS 外部调用路径，不是已经修复的 Omnigent → Codex CLI → Codex 订阅直连路径发生回退。
- `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds` 尚未创建。
- 失败请求没有产生有效模型输出，因此不存在可审查候选、候选 SHA、语义补丁或有效实施结论。
- 旧 evidence、旧报告和旧 RUN_ID 全部保留；不得删除、覆盖、拼接或复制为本轮证据。
- 禁止把该失败误写成代码修复完成、TARGETED_IMPLEMENTATION、Gate 1 PASS、Gate 2 PASS、全仓 GREEN 或 mergeable。

## 3. P0：停止错误的 Claude 重试

- 当前会话只使用 Omnigent → Codex CLI → Codex 订阅直连路径。
- 不再从 Codex 内启动 Claude、Qwen、Grok、Pi CLI，也不执行 `cc-switch`。
- Claude-DS 上一次任务保持 `BLOCKED`，不重试。
- 不读取或加载 `/mnt/c/Users/Administrator/.claude/settings.json`。
- 不调用 CCSwitch，不修改 TUN、Clash、OpenCodex、10100、认证或相关配置。

## 4. P1：确认 Codex 直连链路

本轮只进行了本机、只读、无连接的状态核对：

- 当前 Codex 会话：`AVAILABLE`。当前对话与仓库只读命令可继续执行；这证明当前会话可用，不等同于重新发送模型任务或完整链路 Gate。
- Omnigent server/host/runner：`NOT_OBSERVED`。本轮进程筛选未发现可确认的 server、host 或 runner 进程；未启动、停止或连接任何进程。
- tmux：`BLOCKED_BY_ENVIRONMENT`。查询 `/tmp/tmux-1000/default` 返回 `Operation not permitted`，因此不能据此判定 tmux 会话存在或不存在。
- Claude target worktree：`ABSENT`。
- Git 基线登记：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged` 在 worktree 元数据中记录为 `8ef79ac348711d523053019cdb2f36e8cbbfef7e`；元数据同时提示 Windows gitdir 路径在当前 WSL 视角为 prunable，后续创建新 worktree 前必须在获批实施轮次重新验证。

本轮未连接 `10100`，未读取或修改 OpenCodex `config.toml`，未运行完整 Gate 1/Gate 2，也未进行网络重试。

## 5. P2：Task 29 重新拆分

### Codex

- 负责主计划、必要实现、最终代码审查与证据归档。
- 若当前 Codex 能完成实现，则在用户批准后，从干净基线创建新的独立 Codex worktree，逐 hunk 重建四文件候选。
- 实施、验证和审查必须分别使用可追溯的新 RUN_ID；不得复用旧 evidence。

### Claude-DS

- 当前为 `BLOCKED`，不重试旧请求。
- 如未来确需启用，必须另发独立任务卡，明确选择 Windows 侧 CCSwitch 执行或已验证的 WSL 网络桥接方案。
- 新任务卡生成和执行均须先取得用户批准；使用独立 worktree、独立 RUN_ID 和独立 evidence。

### Qwen

- 仅负责低成本定向验证，不实施代码、不补造上游交付。
- 只有有效候选、独立任务卡和用户批准齐全后才能启动。
- 必须使用独立 worktree、独立 RUN_ID 和独立 evidence；定向结果不得写成 Gate PASS。

### Grok

- 仅负责独立代码审查，默认只读，不直接修复。
- 只有有效候选、验证证据、独立任务卡和用户批准齐全后才能启动。
- 必须使用独立 worktree、独立 RUN_ID 和独立 evidence。

### Pi

- 本轮无角色、无任务卡、不得启动。

## 6. P3：代码实施原则

- 当前 Codex 可完成的工作优先由当前 Codex 直接完成。
- 如必须交给其他模型，先生成独立任务卡并等待用户明确批准，批准前不启动任务。
- 禁止在 `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review` 历史脏树直接修改源码或测试。
- 任何实现必须从固定干净基线新建独立 worktree，并在创建前验证实际 HEAD 和路径不存在。
- 历史四文件只能逐 hunk 重建，禁止整文件复制；禁止复制旧 evidence。
- 每个实施、验证、审查阶段使用独立的新 RUN_ID 和独立 evidence 根。
- 定向 pytest、Ruff、compileall、稳定性检查或单次冒烟只能标记为定向结果，禁止写成 Gate 1/Gate 2 PASS。
- 未经单独授权不得提交、push、merge 或创建 PR。

## 7. P4：当前项目 TODO

### 已完成

- Codex 直连状态：当前订阅会话可继续进行规划和只读仓库操作；未通过其他 CLI 中转。
- 事故归档：已记录 Claude-DS 失败原因、失败边界和 `BLOCKED` 状态。
- evidence 和文档归档：旧 evidence/报告保持原状；本文件作为本轮新规划文档，不冒充测试 evidence。

### 阻塞

- Claude-DS：`BLOCKED`；WSL 无法访问 Windows CCSwitch `127.0.0.1:15721`，且没有有效模型输出或目标 worktree。
- Qwen/Grok/Pi：未启动；当前会话禁止调用，且缺少获批任务卡/有效上游候选。
- Task 29 代码移植：尚未开始；没有候选 SHA 或实施 evidence。
- WSL/tmux：tmux socket 查询受当前沙箱权限阻塞，状态未知。
- Omnigent server/host/runner：本轮未观察到可确认进程，且没有启动或网络探测授权。

### 下一步

1. 由用户决定是否授权当前 Codex 从固定基线创建独立实现 worktree，接管 Task 29 四文件逐 hunk 移植。
2. 获批后先验证 `/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged` 的实际 HEAD、worktree 可用性和新目标路径不存在。
3. 为 Codex 实施生成全新 RUN_ID/evidence，只运行获批的定向测试、目标 Ruff、目标 compileall 和有限稳定性检查。
4. Codex 对实际 diff 和 evidence 做最终审查；任何 Qwen/Grok 外部验证均需另行生成任务卡并再次等待批准。
5. Gate 1 保持既有严格状态 `FAIL`；Gate 2 历史冻结不视为当前验收。完整 Gate 1/Gate 2 暂不运行。
6. 候选和定向 evidence 完整后，再单独决定 PR、提交、push 或 merge；当前均未执行。

### 等待用户操作

- 批准或拒绝由 Codex 新建独立 worktree并实施 Task 29 四文件移植。
- 若仍要求 Claude-DS，批准单独的新任务卡，并在 Windows CCSwitch 或 WSL 网络桥接方案之间作出明确选择；未批准前保持 `BLOCKED`。
- 若要求 Qwen 或 Grok，分别批准其独立任务卡；当前不得从本会话启动。
- 决定未来是否以及何时运行完整 Gate 1/Gate 2。
- 在候选通过定向验证和最终审查后，另行批准是否提交、创建 PR、push 或 merge。

## 8. 交接约束

下一执行者首先读取本文件、`CODEX_TASK_29_ORCHESTRATION.md`、`MODEL_ROLE_MATRIX_20260806.md`、`AGENTS.md` 和 `CONTRIBUTING.md`。在用户批准前只允许只读规划；不得触碰历史脏树源码/测试、旧 evidence、Windows Claude 配置、CCSwitch、TUN、Clash、OpenCodex、10100 或认证。
