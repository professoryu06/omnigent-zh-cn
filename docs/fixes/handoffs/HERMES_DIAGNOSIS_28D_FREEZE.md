# HERMES_DIAGNOSIS_28D_FREEZE — Gate 2 基线冻结方案（只读规划）

- 执行者：Hermes 3.8（只读基线冻结规划执行者，非 Gate 2 签字人）
- 运行模型：`deepseek-v4-flash` via `deepseek`
- 规划日期：2026-08-03 19:13
- 任务卡：`CODEX_TASK_28D_FREEZE`
- 基线仓库：`https://github.com/professoryu06/omnigent-zh-cn.git`
- 基线分支：`docs/fix-plans-core-secondary`
- 基线 HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- 约束遵守：未修改/未 stage/未 commit/未 merge/未删除任何文件；未跑测试；凭据全部 `[REDACTED]`

---

## 0. 盘点基准

- 工作树 dirty 总数：**58 条目** = 37 tracked（36 M + 1 A）+ 21 untracked（含 `docs/fixes/handoffs/` 整个目录 + `evidence/` 目录）
- 前置审查：`HERMES_DIAGNOSIS_28D.md`（基线=omnigent-review、两树非同仓、dirty 分类 A/B/C/D 框架）
- **配置/凭据检查**：dirty 中**无** config.toml/.env/凭据/代理配置混入（git diff 中的 config.toml 引用均为代码内对私有 CODEX_HOME 的消毒逻辑，非仓库配置）；`~/.codex/config.toml` 属用户级不在仓库

## 1. 逐文件分类（58 条目）

### A. 已验收 BUG-1/2/3/24 修复 → 建议纳入候选基线（30 文件）

**源码（16）**：
| 文件 | 变更 | 归属 |
|---|---|---|
| `omnigent/inner/codex_executor.py` | +183 | OpenCodex 隔离（10100/OPENAI_BASE_URL/OPENAI_API_BASE 禁令）+ prompt 消毒 |
| `omnigent/inner/native_prompt_delivery.py` | untracked 新文件 | system_prompt fail-loud 交付策略（#2853 相关） |
| `omnigent/codex_native_app_server.py` | +66 | native app-server 修复 |
| `omnigent/runner/app.py` | +180 | runner 会话/资源修复 |
| `omnigent/runner/transports/ws_tunnel/serve.py` | +169 | ws_tunnel 修复 |
| `omnigent/runner/_entry.py` | +33 | runner 入口修复 |
| `omnigent/server/routes/sessions.py` | +322/− | sessions 路由修复 |
| `omnigent/server/routes/_workspace_validation.py` | +95 | 工作区校验修复 |
| `omnigent/host/connect.py` | +59 | host 连接修复 |
| `omnigent/harness_aliases.py` | +67 | harness 别名 |
| `omnigent/cli.py` | +5 | CLI 修复 |
| `omnigent/native_server_harness.py` | +6 | prompt 提示统一（`note_native_system_prompt`） |
| `omnigent/inner/loader.py` | +10 | loader 修复 |
| `omnigent/inner/antigravity_native_executor.py` | +6 | prompt 提示统一 |
| `omnigent/inner/claude_native_executor.py` | +6 | prompt 提示统一（A 类，非 B 类功能） |
| `omnigent/inner/cursor_native_executor.py` / `goose_native_executor.py` / `hermes_native_executor.py` / `kimi_native_executor.py` / `kiro_native_executor.py` / `pi_native_executor.py` / `qwen_native_executor.py` | 各 +6 | prompt 提示统一（A 类） |
| `omnigent/inner/codex_native_executor.py` | +15 | codex-native executor 修复 |

**测试（11）**：
`tests/cli/test_backend.py`、`tests/e2e_ui/chat/test_chat_file_path_links.py`、`tests/e2e_ui/conftest.py`、`tests/host/test_connect.py`、`tests/inner/test_codex_native_executor.py`、`tests/inner/test_loader.py`、`tests/runner/test_app_sessions_native.py`、`tests/runner/transports/ws_tunnel/test_serve.py`、`tests/server/integration/test_session_mcp_servers.py`、`tests/server/routes/test_workspace_validation.py`、`tests/server/routes/test_workspace_validation_helpers.py`

**untracked 测试（8，配套 A 类源码）**：
`tests/inner/test_codex_native_system_prompt_apply.py`、`tests/inner/test_codex_runtime_isolation.py`、`tests/inner/test_native_system_prompt_delivery.py`、`tests/runner/test_app_codex_native_model.py`、`tests/runner/test_app_codex_native_prompt_delivery.py`、`tests/runner/test_codex_terminal_ensure_guard.py`、`tests/runner/test_runner_idle_active_work.py`、`tests/runner/test_session_workspace_cache.py`、`tests/server/test_multipart_host_launch.py`、`tests/test_harness_dispatch.py`（10 个）

> 注：claude/qwen 等 executor 的 +6 行是 `note_native_system_prompt(...)` 统一修复（A 类），**不是** B 类中文/Grok 功能新增；grok 相关代码在本仓库**不存在**（在 zh-next 工作树）。

### B. Grok/WSL/中文扩展功能 → 暂缓，需单独确认（0 文件 in 本仓库）

- 本仓库（omnigent-review）dirty **无** grok 功能代码（grok_native*.py 在 `omnigent-zh-next`，另一仓库，28D 已确认）
- 但 `evidence/grok-native-01/`（untracked，8-3 新产生 5 文件：acceptance.log、agentcenter.log 等）是 **grok 功能的验收 evidence** —— 归属 B 类，**不删**，但**不入本基线**，随 grok 功能卡另行处理

### C. 必要的 STATUS/Gate/handoff/进度文档 → 建议纳入（9 文件）

| 文件 | 归属 |
|---|---|
| `docs/fixes/PRE_MERGE_GATES.md`（+255/−） | Gate 规格（核心） |
| `docs/fixes/STATUS.md`（+11/−） | Gate 状态载体 |
| `docs/fixes/POST_FIX_HANDOFF_PROMPT.md` | 交接模板 |
| `docs/fixes/PROJECT_OWNER_WORKFLOW_20260731.md`（A 新增） | 工作流文档 |
| `AGENTS.md`（+21） | Agent 指南 |
| untracked：`docs/fixes/CLEANUP_COMPLETION_20260731.md`、`CLEANUP_MANIFEST_20260731.md`、`PROJECT_PROGRESS_20260731.md`、`TEST_PROGRESS_20260731.md`、`WSL_PROXY_BRIDGE_20260731.md`、`WSL_REPAIR_20260731.md` | 进度/交接文档 |
| untracked：`docs/fixes/handoffs/`（~110 文件，含 27/28A/28B/28C/28D 报告与全部历史任务卡） | 完整 handoff 链 |

> 注：handoffs 目录较大（110+ 文件），建议**整目录纳入**（它是可审计交接链的权威副本）；若 Codex 认为过大，可拆分为"仅 27/28 系列 + 最新任务卡"的精简集，但需用户/Codex 明确取舍。

### D. 异常文件 → 不静默清理，另列清理卡（3 条目）

| 文件 | 判定 | 建议 |
|---|---|---|
| `nul`（30B，内容 `bash: chcp: command not found`） | 命令误重定向垃圾产物（7-31） | 清理卡：`rm nul`（低风险，但不静默做） |
| `evidence/`（含 grok-native-01/） | 未跟踪 evidence 目录，8-3 新写入 | **不删**（任务卡：evidence 不得删除）；纳入 .gitignore 或随 grok 卡归档 |
| `docs/fixes/handoffs/` 部分历史文件（若 Codex 选择精简集） | 未跟踪 | 不删，仅不入本提交 |

## 2. 确认项

- ✅ **无 config.toml/.env/凭据/代理配置混入**（见 §0）
- ✅ **evidence 未删除**（`evidence/grok-native-01/` 保留）
- ✅ **D 类不静默清理**（`nul` 另列清理卡，evidence 不删）
- ✅ **不整体提交 58 条目**（A+C 分组提交，B/D 排除）
- ✅ **Gate 2 只对应一个 commit**（§4 顺序）

## 3. 暂缓 / 另开任务清单

1. **grok 功能**（在 omnigent-zh-next，本仓无）→ 独立功能卡（28D 已定）
2. **`evidence/grok-native-01/`** → 随 grok 卡归档或 gitignore（B 类）
3. **`nul` 清理** → 独立清理卡（D 类，`rm nul`）
4. **handoffs 精简取舍**（如 Codex 要求）→ 用户确认后执行

## 4. 建议 commit 顺序与 message

**顺序（3 个 commit，全部落在 `docs/fix-plans-core-secondary`，最后一个是 Gate 2 基线）：**

```text
# Commit 1 — C 类文档（先固化 Gate 规格与状态载体）
git add docs/fixes/PRE_MERGE_GATES.md docs/fixes/STATUS.md \
        docs/fixes/POST_FIX_HANDOFF_PROMPT.md docs/fixes/PROJECT_OWNER_WORKFLOW_20260731.md \
        AGENTS.md docs/fixes/CLEANUP_COMPLETION_20260731.md docs/fixes/CLEANUP_MANIFEST_20260731.md \
        docs/fixes/PROJECT_PROGRESS_20260731.md docs/fixes/TEST_PROGRESS_20260731.md \
        docs/fixes/WSL_PROXY_BRIDGE_20260731.md docs/fixes/WSL_REPAIR_20260731.md
git commit -m "docs(fixes): freeze gate specs, status, and progress handoff chain"

# Commit 2 — A 类修复（源码 + 配套测试 + handoffs 文档）
git add omnigent/ tests/ docs/fixes/handoffs/
git commit -m "fix(core): codex isolation, prompt delivery fail-loud, ws_tunnel, session and workspace fixes (#2853, BUG-1/2/3/24)"

# Commit 3 — 无（可选）或合并进 Commit 2
```

> 若 handoffs 整目录过大，Commit 2 的 `git add docs/fixes/handoffs/` 改为精确文件清单（27/28 系列 + 相关任务卡），由用户/Codex 定。

**基线冻结后**：`git rev-parse HEAD` 记录新 SHA 于 STATUS.md；工作树需 clean（`nul`/`evidence/` 先按清理卡处置或 gitignore）。

## 5. 提交前必须等待用户批准

**本方案不产生任何提交。** 所有 `git add`/`git commit` 均为**建议命令**，须经：
1. 用户/Codex 审核本文件分类（尤其 A/B 交叠的 executor 与 handoffs 取舍）；
2. 明确批准后，由**有提交权的执行者**（Codex 或用户指定）执行；
3. 提交后以实际 SHA 回填本文件。

## 6. 基线未冻结前禁止开始 Gate 2

**在 Commit 2 落地、工作树 clean、冻结 SHA 记录于 STATUS.md 之前，禁止开始 Gate 2。** 当前 HEAD `dc83140c…` + 58 dirty 条目**不是**可审计基线。

## 7. 边界声明

- 不宣称 Gate 2 PASS、全仓 GREEN 或 mergeable。
- 本报告纯只读规划：未修改/stage/commit/merge/tag 任何内容；未跑测试。
- 凭据全部 `[REDACTED]`；10100/OpenCodex/`~/.codex/config.toml`/TUN/Clash 未触碰。
