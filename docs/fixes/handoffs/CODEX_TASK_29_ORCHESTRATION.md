# CODEX_TASK_29：WSL 代码移植、定向验证与独立审查编排

## 1. 总协调角色

Codex / GPT-5.6 Luna 是 Task 29 的 Controller C，负责维护任务边界、执行顺序、证据契约和最终只读验收。Codex 不替执行角色伪造测试结果，也不把定向验证升级为 Gate 结论。

本任务严格串行：

1. Claude-DS 完成实现、定向检查和交付后，Qwen3.8 才能启动。
2. Qwen3.8 完成独立验证和 evidence 后，Grok 才能启动。
3. Grok 只做独立审查；只有发现可复现且明确归因于 Claude 候选的缺陷，才能提出新的修复卡和独立修复 worktree。
4. Grok 完成后，由 Codex 汇总并做最终验收。是否提交、创建 PR、push 或 merge 均不属于本任务卡自动授权范围。

## 2. 路径映射

所有 WSL 命令必须使用 `/mnt/...` 路径。Windows 路径仅用于人工定位，不得复制到 WSL 命令中。

| 用途 | Windows 说明路径 | WSL 可执行路径 |
|---|---|---|
| 历史文档/脏树 | `F:\codex-ai\git项目部署\tmp\omnigent-review` | `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review` |
| 干净代码基线 | `F:\codex-ai\git项目部署\tmp\omnigent-main-merged` | `/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged` |
| Claude worktree | `F:\codex-ai\git项目部署\tmp\omnigent-task29-claude-ds` | `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds` |
| Qwen worktree | `F:\codex-ai\git项目部署\tmp\omnigent-task29-qwen-verify` | `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-qwen-verify` |
| Grok worktree | `F:\codex-ai\git项目部署\tmp\omnigent-task29-grok-review` | `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review` |
| Evidence 根 | `C:\Users\Administrator\omnigent-diagnostics` | `/mnt/c/Users/Administrator/omnigent-diagnostics` |

基线 SHA 固定为：

`8ef79ac348711d523053019cdb2f36e8cbbfef7e`

执行者必须验证实际 HEAD；路径存在不等于 SHA 正确。若 WSL Git 无法解析 worktree，必须报告 BLOCKED，不得修改 `.git` 指针或改用 Windows 路径命令绕过。

## 3. 必读文档

所有角色都必须先完整读取：

1. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/AGENTS.md`
2. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/CONTRIBUTING.md`
3. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/CODEX_TASK_29_ORCHESTRATION.md`
4. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/MODEL_ROLE_MATRIX_20260806.md`
5. 与本角色任务卡列出的诊断报告和上游交付。

如果文档不在当前候选 main 中，只能从历史树的上述 WSL 路径只读获取；不得创建替代文档。

## 4. 当前事实和 Gate 边界

- PR #3、#4 已合并；PR #2、#5 仍开放。历史 `STATUS.md` 是时间快照，不得用它回退当前 PR 状态。
- 历史树中的 4 个待审文件必须逐 hunk 重建，禁止整体复制：
  - `omnigent/inner/codex_executor.py`
  - `tests/inner/test_codex_executor.py`
  - `tests/inner/test_codex_runtime_isolation.py`
  - `tests/server/integration/test_session_host_launch.py`
- `evidence/`、`nul`、旧 handoff 和旧 RUN_ID 全部保留，不得删除、覆盖、拼接或提交。
- Gate 1 严格结论仍为 FAIL；项目级豁免不是 Gate 1 PASS。
- Gate 2 冻结记录属于历史基线，不是当前 main 的新验收。
- 定向 pytest、目标 Ruff、目标 compileall、多轮稳定性检查、CLI sentinel 或单次产品冒烟都不得写成 Gate 1 PASS 或 Gate 2 PASS。

## 5. 角色与交付

### 5.1 Codex / Luna：总协调与最终验收

- 维护本文件、角色矩阵和三张任务卡。
- 确认每个角色使用独立可写 worktree 和全新 RUN_ID。
- 只根据实际 diff、命令退出码、时间线、cleanup 和 leak-scan 验收。
- 最终输出 ACCEPT、REWORK 或 INCONCLUSIVE 建议，不自动 push 或 merge。

### 5.2 Claude Code / DeepSeek V4 Flash：实施者

- 使用 `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds`。
- 仅处理获批的 4 个源码/测试文件。
- 逐 hunk 重建 Codex/OpenCodex 隔离、代理环境清理和 relaunch 测试同步。
- 交付本地候选 SHA、`semantic-diff.patch`、`implementation-report.md` 和 TARGETED_IMPLEMENTATION evidence。

### 5.3 Qwen3.8：独立验证者

- 仅在 Claude 完成交付后启动。
- 使用 `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-qwen-verify`。
- 应用 Claude 候选但不再修改源码或测试。
- 运行定向检查，盘点 WSL 工具、五类模型 CLI、登录状态和端口。
- 交付 TARGETED_VALIDATION evidence；未知登录状态只能写 UNKNOWN 或 LOGIN_REQUIRED。

### 5.4 Grok：独立审查者

- 仅在 Qwen 完成交付后启动。
- 使用 `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review`。
- 审查 Claude diff 和 Qwen evidence，不修改 Claude 或 Qwen worktree。
- 输出 ACCEPT、REWORK 或 INCONCLUSIVE。
- 只有可复现、可明确归因的候选缺陷才能触发另一张修复卡；审查卡本身不授权直接修复。

## 6. 全局硬规则

- Claude、Qwen、Grok 不得共享同一个可写 worktree。
- 历史 `omnigent-review` 源码和测试保持不变。
- 不修改 TUN、Clash、OpenCodex、10100、用户认证或 240s watchdog。
- 10100 只允许观察监听状态，不连接、不占用、不释放、不杀进程。
- 所有新 evidence 写入 `/mnt/c/Users/Administrator/omnigent-diagnostics/<RUN_ID>/`。
- 每个角色使用独立的新 RUN_ID；不得把旧 RUN_ID 当作本轮结果。
- token、cookie、密钥、`auth.json` 内容和认证配置一律写为 `[REDACTED]`。
- 不运行完整 Gate 1 或 Gate 2。
- 不提交 evidence、`nul` 或无关文件；不 push、不 merge。

## 7. 独立任务卡

- Claude：`docs/fixes/handoffs/CODEX_TASK_29_CLAUDE_DS.md`
- Qwen：`docs/fixes/handoffs/CODEX_TASK_29_QWEN_VERIFY.md`
- Grok：`docs/fixes/handoffs/CODEX_TASK_29_GROK_REVIEW.md`

三张卡必须按 Claude → Qwen → Grok 顺序执行，最后回到 Codex 验收。
