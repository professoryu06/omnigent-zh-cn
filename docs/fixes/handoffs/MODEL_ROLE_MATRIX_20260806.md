# Omnigent Task 29 模型角色矩阵（2026-08-06）

## 1. 目标与基线

Task 29 以 SHA `8ef79ac348711d523053019cdb2f36e8cbbfef7e` 为唯一代码基线，串行完成四文件补丁重建、定向验证、环境盘点和独立审查。

WSL 执行路径：

- 基线：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged`
- 历史只读树：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-review`
- Evidence 根：`/mnt/c/Users/Administrator/omnigent-diagnostics`

Windows 映射仅供人工定位：

- `F:\codex-ai\git项目部署\tmp\...` 对应 `/mnt/f/codex-ai/git项目部署/tmp/...`
- `C:\Users\Administrator\omnigent-diagnostics` 对应 `/mnt/c/Users/Administrator/omnigent-diagnostics`

任何 WSL 命令都只能使用 `/mnt/f/...` 或 `/mnt/c/...`。历史树保持脏状态，禁止 reset、checkout、清空、整体复制或整体 `git add`。

## 2. 串行依赖

| 阶段 | 角色 | 启动条件 | 主要输出 | 下一阶段条件 |
|---|---|---|---|---|
| 0 | Codex / Luna | 本文档和任务卡已冻结 | 三张独立任务卡 | Claude 可启动 |
| 1 | Claude-DS | 基线 SHA 已验证 | 候选 SHA、semantic diff、TARGETED_IMPLEMENTATION evidence | Claude 交付完整后 Qwen 才可启动 |
| 2 | Qwen3.8 | Claude 三项输入齐全 | TARGETED_VALIDATION evidence、WSL/CLI 矩阵 | Qwen 交付完整后 Grok 才可启动 |
| 3 | Grok | Claude 与 Qwen 完整交付 | ACCEPT、REWORK 或 INCONCLUSIVE | 返回 Codex |
| 4 | Codex / Luna | Grok 结论可审计 | 最终验收建议 | 另行决定后续动作 |

禁止跳过依赖、并行写同一 worktree，或由后置角色替前置角色补造 evidence。

## 3. 角色职责

### Codex / GPT-5.6 Luna：Controller C

- 维护编排、任务边界、路径映射和证据清单。
- 只读复核 Claude、Qwen、Grok 的真实交付。
- 最终判定候选是否 ACCEPT、REWORK 或 INCONCLUSIVE。
- 不把项目级 Gate 1 豁免写成 Gate 1 PASS。
- 不把定向测试、CLI sentinel 或单次冒烟写成 Gate 2 PASS。
- 本任务不直接授权 Codex 提交、push 或 merge。

### Claude Code / CCSwitch DeepSeek V4 Flash：实施者

- 独立 worktree：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds`
- 仅允许处理：
  - `omnigent/inner/codex_executor.py`
  - `tests/inner/test_codex_executor.py`
  - `tests/inner/test_codex_runtime_isolation.py`
  - `tests/server/integration/test_session_host_launch.py`
- 从基线逐 hunk 重建，不整体复制历史文件。
- 聚焦 Codex/OpenCodex 隔离、代理环境清理和 offline runner relaunch 测试同步。
- 执行定向 pytest、目标 Ruff、目标 compileall。
- 报告类型只能是 TARGETED_IMPLEMENTATION。

### Qwen3.8：独立验证与 WSL 操作员

- 独立 worktree：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-qwen-verify`
- 必须等待 Claude 候选 SHA、`semantic-diff.patch` 和 `implementation-report.md`。
- 应用 Claude 候选后不得再修改源码或测试。
- 执行定向检查，盘点 WSL、Python、uv、Node、tmux、bwrap、git。
- 检查 Claude-DS、Qwen、Grok、Codex、Pi 的 path、version、help 和非交互 auth-status。
- 登录状态无法证实时写 UNKNOWN 或 LOGIN_REQUIRED，不得猜测。
- 报告类型只能是 TARGETED_VALIDATION。

### Grok：独立只读审查者

- 独立 worktree：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review`
- 必须等待 Claude 和 Qwen 的完整交付。
- 审查 diff 边界、代理串线、Codex/OpenCodex 隔离、relaunch 竞态、Windows/WSL 边界和 Qwen evidence。
- 不得修改 Claude 或 Qwen worktree。
- 输出 ACCEPT、REWORK 或 INCONCLUSIVE。
- 只有缺陷可复现且明确归因于 Claude 候选时，才能提出新的修复卡；审查阶段不得直接盲改。

## 4. Worktree 隔离矩阵

| 角色 | 可写 worktree | 其他树权限 |
|---|---|---|
| Claude-DS | `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds` | 基线和历史树只读 |
| Qwen3.8 | `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-qwen-verify` | Claude、基线和历史树只读 |
| Grok | `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review` | Claude、Qwen、基线和历史树只读 |
| Codex / Luna | 本轮仅维护 handoff 文档 | 所有代码 worktree 只读 |

任何角色不得复用另一角色的可写 worktree。Grok 若获得独立修复卡，必须使用一个不同于上述三个路径的新 worktree 和新 RUN_ID。

## 5. Evidence 与安全契约

- 所有新 evidence：`/mnt/c/Users/Administrator/omnigent-diagnostics/<RUN_ID>/`。
- 每个执行阶段使用全新 RUN_ID，不覆盖或拼接旧目录。
- Evidence 至少保留环境、SHA、命令、stdout/stderr、真实 exit code、时间线、cleanup 和 leak-scan。
- `evidence/`、`nul` 和旧 handoff 不删除、不覆盖、不提交。
- 凭据、token、cookie、密钥和 `auth.json` 内容一律 `[REDACTED]`。
- Codex subscription 使用私有 `CODEX_HOME`；不得读取或改写 OpenCodex `config.toml`。
- 10100 只观察，不连接、不占用、不释放、不杀进程。
- 不修改 TUN、Clash、OpenCodex、认证、全局代理或 240s watchdog。

## 6. Gate 措辞

- Gate 1 严格状态保持 FAIL；项目级豁免不能记为 PASS。
- 历史 Gate 2 冻结不构成当前 main 的新 Gate 2 验收。
- 本任务禁止运行完整 Gate 1 或 Gate 2。
- TARGETED_IMPLEMENTATION、TARGETED_VALIDATION、单节点多轮测试和独立审查均不是 Gate 1/Gate 2 PASS，也不是全仓 GREEN 或 mergeable。
