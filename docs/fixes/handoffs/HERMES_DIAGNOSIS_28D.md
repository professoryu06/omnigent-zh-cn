# HERMES_DIAGNOSIS_28D — Gate 2 基线盘点（只读）

- 执行者：Hermes 3.8（只读基线审查执行者，非 Gate 2 签字人）
- 运行模型：`deepseek-v4-flash` via `deepseek`
- 审查日期：2026-08-03 18:58
- 任务卡：`CODEX_TASK_28D`（Gate 2 前代码基线选择）
- 约束遵守：未修改/未提交/未删除任何文件；未跑测试；凭据全部 `[REDACTED]`

---

## 1. 两个工作树全景

| 项 | 工作树 1（Gate 2 候选） | 工作树 2（参考/实验） |
|---|---|---|
| 路径 | `F:\codex-ai\git项目部署\tmp\omnigent-review` | `F:\codex-ai\omnigent-zh-next` |
| 远端仓库 | `github.com/professoryu06/omnigent-zh-cn.git`（**中文版**） | `github.com/omnigent-ai/omnigent.git`（**上游官方**） |
| 当前分支 | `docs/fix-plans-core-secondary` | `integration/omnigent-zh-20260731` |
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` | `c2982266f1d702d83d47f9352bbe5e0aa8c987f9` |
| HEAD 提交 | `docs(fixes): define pre-merge gates with runnable Linux and AgentCenter procedures` | `Record Windows and WSL test progress` |
| dirty 条目 | **58**（38 tracked + 20 untracked） | **17**（3 tracked + 14 untracked） |
| dirty 源码量 | 22 文件 +1139/−125 | 3 文件 +76/−0 |
| dirty 测试量 | 11 文件 +1064/−31 | 0（未跟踪 5 个测试文件） |

**关键关系**：两树**非同仓**。`omnigent-review` 是中文版仓库的特性分支集成树（PRE_MERGE_GATES.md 的 #3/#4/#5 功能 PR 门槛正是为其设计）；`omnigent-zh-next` 是上游官方仓库的集成分支，含 WSL/Grok 实验功能。HEAD `dc83140` **不在** `origin/main` 祖先链上（特性分支）；`c2982266` 与上游 `omnigent-ai` 同源。

## 2. dirty 文件分类

### 工作树 1 `omnigent-review`（58 条目）

**A. 已验收 BUG 修复**（核心，源码 22 文件中的主力）：
- `omnigent/inner/codex_executor.py`（+183）— **OpenCodex 污染隔离**：`_CODEX_ENV_DENY_EXACT` 增 `OPENAI_BASE_URL`/`OPENAI_API_BASE`、`_CODEX_CONFIG_POLLUTION_KEYS`（openai_base_url/openai_api_base/model）、`_CODEX_CONFIG_FORBIDDEN_ENDPOINT=127.0.0.1:10100` —— 即 CODEX_TASK_23/24 系列修复落点（git diff 含 5 处 10100/隔离相关）
- `omnigent/codex_native_app_server.py`（+66）、`omnigent/runner/app.py`（+180）、`omnigent/runner/transports/ws_tunnel/serve.py`（+169）、`omnigent/server/routes/sessions.py`（+322/−）、`omnigent/host/connect.py`（+59）、`omnigent/runner/_entry.py`（+33）、`omnigent/server/routes/_workspace_validation.py`（+95）等
- 配套测试 11 文件 +1064/−31（test_connect、test_codex_native_executor、test_app_sessions_native、test_serve、test_workspace_validation 等）

**B. 中文版/WSL 功能**（与 A 交叠）：
- `omnigent/inner/` 下 8 个 native executor（antigravity/claude/cursor/goose/hermes/kimi/kiro/pi/qwen）+6 行/文件（可能是统一枚举/注册扩展）；`omnigent/harness_aliases.py`（+67）
- 未跟踪：`omnigent/inner/native_prompt_delivery.py` + 配套测试（test_codex_native_system_prompt_apply 等 8 个）

**C. 文档/evidence**（未跟踪 + tracked）：
- tracked：`AGENTS.md`、`docs/fixes/POST_FIX_HANDOFF_PROMPT.md`、`docs/fixes/PRE_MERGE_GATES.md`、`docs/fixes/STATUS.md`、`docs/fixes/PROJECT_OWNER_WORKFLOW_20260731.md`（A）
- untracked：`docs/fixes/CLEANUP_COMPLETION_20260731.md`、`CLEANUP_MANIFEST_20260731.md`、`PROJECT_PROGRESS_20260731.md`、`TEST_PROGRESS_20260731.md`、`WSL_PROXY_BRIDGE_20260731.md`、`WSL_REPAIR_20260731.md`、`docs/fixes/handoffs/`（27/28A/28B/28C 报告 + 任务卡）

**D. 未授权/异常**：
- **`nul`**（untracked，工作树根）— Windows 保留名误创建，**异常文件**
- `evidence/`（untracked 目录）— 需确认内容后决定入库/忽略

### 工作树 2 `omnigent-zh-next`（17 条目）

**B. 中文版/WSL/Grok 功能**（全部）：
- tracked 3 文件：`omnigent/_wrapper_labels.py`（+4）、`omnigent/harness_plugins.py`（+19）、`omnigent/server/app.py`（+53）
- untracked：`omnigent/grok_native.py`、`omnigent/grok_native_bridge.py`、`omnigent/inner/grok_native_executor.py`、`omnigent/inner/grok_native_harness.py`、`scripts/start_omnigent_claude_direct.sh`、`scripts/start_omnigent_wsl_backend.sh`、`scripts/start_qwen_direct.sh`、WSL/QWEN 文档 2 篇、grok 测试 5 个、`tests/test_harness_dispatch.py`

**D. 未授权/异常**：
- **`C\357\200\272/Users/Administrator/omnigent-diagnostics/r27-observer-...`** — **r27 路径 bug 残留**（Windows 路径 `C:/` 被 WSL 当相对路径创建的怪路径副本，含 r27 evidence 副本）。正式 evidence 在 `C:\Users\Administrator\omnigent-diagnostics\` 完好，此为**重复副本，必须排除出基线**

**配置混入检查**：两树 dirty **均无** `config.toml`/`.env`/`.ini` 等配置类文件（grep 零命中）——`~/.codex/config.toml` 属用户级，不在仓库内。**源码/测试/文档混入存在但归属清晰**（A/B/C 可归因）。

## 3. 两个 HEAD 代码差异

两树**非同源可比**（不同仓库）。`omnigent-review` 的 dirty 是中文版仓库特性分支上的 BUG 修复 + 中文功能；`omnigent-zh-next` 的 dirty 是上游集成分支上的 grok/WSL 实验。二者**不互为 baseline**，Gate 2 只能针对其中一个。

## 4. 唯一建议（Gate 2 基线）

1. **选择 `omnigent-review`（工作树 1）作为 Gate 2 基线**。
   - 理由：它是中文版交付仓库（`omnigent-zh-cn`），PRE_MERGE_GATES.md 的 #3/#4/#5 功能 PR 合并门槛（Gate 0/1/2 全程）**专门针对此仓库设计**；dirty 改动为已验收 BUG 修复 + 中文功能 + 文档；`docs/fixes/STATUS.md` 即 Gate 状态载体。
   - `omnigent-zh-next` 为上游参考 + WSL/Grok 实验场，**不作为 Gate 2 基线**（其改动属 B 类功能开发，未验收）。

2. **需保留的改动**：工作树 1 的 A 类（BUG 修复）+ B 类（中文功能）+ C 类（文档/evidence）全部保留并入库。

3. **必须另开 Hermes/Grok 卡的改动**：
   - 工作树 1：`nul`（异常文件，删除卡）；`evidence/`（内容确认后归档/忽略卡）
   - 工作树 2：grok 全套（grok_native*.py + 测试 + harness）+ WSL 脚本 + `C\357\200\272/` 怪路径清理——属 B 类功能开发，需独立功能卡验收后另行入库

4. **需要用户批准后再 commit**：是。所有 dirty 文件在提交前须经用户/Codex 确认归属（尤其 A/B 交叠的 `omnigent/inner/*_executor.py` 统一改动与 C 类文档）。

5. **冻结后要求**：commit 落在 `omnigent-review` 的 `docs/fix-plans-core-secondary` 分支（或 Codex 指定的 #3/#4/#5 集成分支），工作树**必须 clean**（`git status` 无 dirty、无 untracked 残留，`nul` 与 `evidence/` 先处置），冻结 SHA 以 `git rev-parse HEAD` 记录于 STATUS.md。

6. **在基线未冻结前，明确禁止开始 Gate 2。**

## 5. 边界声明

- **不宣称 Gate 2 PASS、全仓 GREEN 或 mergeable。**
- 本报告为只读盘点：未修改/未提交/未删除/未移动任何文件；未跑 pytest/full-run。
- 凭据全部 `[REDACTED]`；10100/OpenCodex/`~/.codex/config.toml` 未触碰。

## 6. 证据位置

- 工作树状态：git status 输出（本会话记录）
- 分类依据：`omnigent/inner/codex_executor.py` diff（10100 隔离）、`docs/fixes/STATUS.md`、`docs/fixes/PRE_MERGE_GATES.md`、`docs/fixes/handoffs/`（27/28A/28B/28C）
- 异常文件：`nul`（工作树 1 根）、`C\357\200\272/`（工作树 2 根，r27 路径 bug 副本）
