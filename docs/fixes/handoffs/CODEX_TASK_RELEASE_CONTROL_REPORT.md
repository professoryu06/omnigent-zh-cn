# CODEX_TASK — Release Control Report（Omnigent 第一版唯一 release 线盘点）

- 日期：2026-08-06（UTC+8）
- 执行者：Hermes（发布控制 / 版本管理操作员，只读盘点 + 文档交接）
- RUN_ID / Evidence：`20260806-160933-8ef79ac-hermes-release-control`（`C:\Users\Administrator\omnigent-diagnostics\20260806-160933-8ef79ac-hermes-release-control\`）
- 基线：**`8ef79ac348711d523053019cdb2f36e8cbbfef7e`**（GitHub main，PR #3/#4 已合并，"Merge PR #4: honor nested harness and model"）
- 配套文档：[RELEASE_BUG_LEDGER.md](../RELEASE_BUG_LEDGER.md)、[RELEASE_ROLLBACK_PLAN.md](../RELEASE_ROLLBACK_PLAN.md)、[CODEX_TASK_30_INTEGRATION_MANIFEST_20260806.md](./CODEX_TASK_30_INTEGRATION_MANIFEST_20260806.md)
- **本报告不得被解读为 Gate 1 PASS、Gate 2 PASS、全仓 GREEN 或 mergeable。未 commit / push / merge / tag。**

## 1. 模型与隔离约束记录（强制）

| 项 | 值 |
|---|---|
| codex_model（本项目 Codex 唯一允许） | `gpt-5.6-luna` |
| reasoning_effort | `max`（固定） |
| 禁止模型 | `gpt-5.6-sol`、mini、任何 fallback |
| OpenCodex ↔ Omnigent Codex | **必须隔离**（私有 CODEX_HOME，不共享 config/认证） |
| 端口 10100 | **不得连接、占用或释放**（OpenCodex bun proxy dashboard 专属） |

**待处理差异（只记录，不改测试凑绿）**：现有测试硬编码 `gpt-5.6-sol` 作为订阅默认模型：
- `tests/harness_bench/test_bench.py:602,612,624,637,650,660`
- `tests/harness_bench/__main__.py:32`、`tests/harness_bench/README.md:23,27`
- `tests/runner/test_codex_terminal_ensure_guard.py:27`
- `tests/inner/test_codex_runtime_isolation.py` 中 `sol` 为订阅默认、`luna` 为用户覆盖（隔离语义，属有意设计，单独评审）

按任务约束：这些差异**记入台账，不在本轮修改**；是否把 harness_bench 的默认示例改为 luna 由 Codex 另发专项卡决策。

## 2. 五棵工作树盘点（只读）

| # | 工作树 | HEAD | 分支 | staged | 工作区 | 角色 |
|---|---|---|---|---|---|---|
| 1 | `F:\codex-ai\git项目部署\tmp\omnigent-main-merged` | `8ef79ac` | detached（clean） | 0 | clean | **main 干净副本，release 基线参照** |
| 2 | `F:\codex-ai\git项目部署\tmp\omnigent-task30-grok-integrate` | `8ef79ac` | `codex/task30-integrate` | **42**（10 A + 32 M） | staged 之外无脏文件 | Task30 整合候选（未 commit） |
| 3 | `F:\codex-ai\git项目部署\tmp\omnigent-task29-codex-direct` | worktree gitdir 损坏（指向 WSL `/mnt/f/...` 路径，Windows git 不可读） | `task29/codex-direct` = `8ef79ac`（与基线同 SHA，**零新增 commit**），被 git 标记 `prunable` | — | 文件树完整但 git 元数据断裂 | Task29 Route-A 隔离区（见 §4） |
| 4 | `F:\codex-ai\git项目部署\tmp\omnigent-review` | `5c8b9ce` | `docs/fix-plans-core-secondary` | 0 | 4 M（Grok R5 修复文件，ISOLATE）+ 35 untracked（交接文档/evidence/nul，KEEP-EVIDENCE） | 文档仓 + 本地修复候选源 |
| 5 | `F:\codex-ai\omnigent-zh-next` | `c2982266` | `integration/omnigent-zh-20260731` | 0 | 5 M + 15 ??（Grok native 实验、WSL 脚本、异常目录 `C\uff0f/`） | 上游官方仓（omnigent-ai/omnigent）实验运行树；**6767 现网跑此树**；`8ef79ac` 在该仓不存在（非同仓） |

祖先关系（实测）：
- `8ef79ac` **不是** review HEAD `5c8b9ce` 的祖先（review 分支在 PR #3/#4 合入 main 之前分叉，两线并行）。
- `task29/codex-direct` **即** `8ef79ac` 本身（无新增提交）。
- `zh-next` 是上游仓，`8ef79ac` 对象不存在于该仓——**不得与中文交付仓互当基线**。

## 3. 唯一推荐 release worktree

**推荐：新建 `omnigent-release-v1`，从 `origin/main` @ `8ef79ac` 检出**（命令模板见回滚方案 §3）。

理由：
1. `omnigent-main-merged` 虽是 `8ef79ac` 干净副本，但它是 detached 参照树，且已被多轮诊断引用；release 线应独占一棵新树，避免与参照树互相污染。
2. Task30 候选（42 staged）必须**逐文件移植**进新树，而非把 task30 树直接改名成 release 树——其中 7 个文件与 e691d08 blob 不同（rebase 到 8ef79ac 后含 PR #3/#4 基线的 MIXED-HUNK），需逐 hunk 审查。
3. `8ef79ac` 是中文交付仓当前唯一权威发布基线；release 线必须从它单点出发。

## 4. Task30 是否准入第一版：有条件准入（35 直接 + 7 审查 + 4 隔离）

Task30 staged 42 文件清单已逐文件核验（evidence：`task30-staged-files.txt`）：**35 个文件 blob 与 `e691d08` 完全一致**（FIRST-V1 直接移植），**7 个文件 blob 不同**（rebase 到 8ef79ac 基线产生差异，必须逐 hunk 审查，不得整文件覆盖）：

| DIFF 文件 | 原因 |
|---|---|
| `omnigent/cli.py` | 基线已含后续改动 |
| `omnigent/host/connect.py` | 同上 |
| `omnigent/inner/codex_executor.py` | MIXED-HUNK：只纳入私有 CODEX_HOME/OpenCodex 隔离 hunk；Route-A/proxy hunk 隔离 |
| `omnigent/runner/app.py` | PRESERVE-MAIN：保留 PR #3/#4，只补已审查 hunk |
| `tests/host/test_connect.py` | 随实现逐 hunk |
| `tests/inner/test_codex_runtime_isolation.py` | MIXED-HUNK：基础隔离测试纳入，R5 proxy/NO_PROXY 段隔离 |
| `tests/runner/test_codex_terminal_ensure_guard.py` | 逐 hunk |

**禁止进入第一版的 4 个未提交文件**（review 树 Grok R5 修复，manifest §5 ISOLATE）：`omnigent/inner/codex_executor.py`（proxy/Route-A 段）、`tests/inner/test_codex_executor.py`、`tests/inner/test_codex_runtime_isolation.py`（R5 新增段）、`tests/server/integration/test_session_host_launch.py`（relaunch 竞态修复——定向 50× 通过，但 r6 全量 Gate 1 仍 candidate-only 失败，须独立决策）。

## 5. Task29 Route-A 为什么隔离

1. **Route-A 已实现但未被接受为修复**（TASK_24_PLAN §10）：child-only proxy 边界落地后，4 个 full-run（`20260731-152542…r1` ~ `…154130…r4`）全部在真实 assistant 响应之前失败（Rust 10106/11003），未观察到 10100 连接，leak 为零。结论原文："Route A is therefore implemented but **not accepted as a fix**"。
2. **task29 分支对基线零贡献**：`task29/codex-direct` == `8ef79ac`，无任何新增 commit——第一版从它拿不到任何东西。
3. **worktree 元数据损坏**：gitdir 指向 WSL 风格 `/mnt/f/...` 路径，Windows git 报 not a git repository，且已被标记 prunable。禁止 prune（保留现场），但也不得作为任何整合来源。
4. **环境根因未解决**：Codex 0.146.0 + Clash proxy 兼容性问题（Rust 10106/11003）仍需独立的 CLI 版本/上游决策，不属于第一版范围。

## 6. Gate 现状（如实记录，不宣称通过）

| 门槛 | 状态 |
|---|---|
| Gate 1 Linux 全仓 pytest（第一版候选） | **候选尚未生成，未执行** |
| Gate 1 r6（历史候选 5c8b9ce+R5 vs clean main 8159424） | 完成：`shared=137 only_main=1 only_cand=1`；严格规则下 **GATE1_FAIL**（relaunch candidate-only，定向 20× 通过不豁免）。该结果针对旧候选，不是第一版 release 线的判定 |
| Gate 2 AgentCenter smoke | 由 Codex 专属签字；本轮不涉及 |
| 第一版 release 线 | **未建立、未验证、未合并** |

## 7. Obsidian 同步（vault 路径已确认）

Vault：`E:\ob zhishiku\本地知识库`（实测发现 `.obsidian`；`OBSIDIAN_VAULT_PATH` 未设置，非猜测）。既有 `Omnigent/` 目录。**待同步清单**（本轮只生成清单，不写 vault）：

1. `Omnigent/Omnigent-Release线盘点-20260806.md` ← 本报告摘要（基线、推荐 worktree、Task30/29 准入结论）
2. `Omnigent/Omnigent-Release-Bug台账-20260806.md` ← RELEASE_BUG_LEDGER.md 全文
3. `Omnigent/Omnigent-Release-回滚方案-20260806.md` ← RELEASE_ROLLBACK_PLAN.md 全文
4. 更新 `Omnigent/Omnigent-资料索引.md`：追加以上 3 篇链接
5. 更新 `Omnigent/Omnigent-源码整合清单-20260806.md`：追加"Task30 staged 42 文件 blob 核验结果（35 SAME / 7 DIFF）"

## 8. 下一张实施卡建议

建议 Codex 发布 **CODEX_TASK_31 — 第一版 release 线整合实施卡**：
1. 从 `origin/main` @ `8ef79ac` 新建 worktree `omnigent-release-v1`（命令模板在回滚方案 §3）；
2. 按 manifest §4 移植 35 个 SAME 文件（FIRST-V1），7 个 DIFF 文件逐 hunk 审查后移植；
3. 明确排除：manifest §5 的 4 个 ISOLATE 文件、Task29 Route-A、zh-next Grok native 实验、PR #5；
4. 移植后跑 BUG-1/2/3/4 + Codex 隔离 + prompt fail-loud 定向测试（Windows 定向 ≠ Gate 1）；
5. 候选 commit 后由 Hermes 以全新 RUN_ID 跑 Gate 1 r7 双树全量对照（重点观察 relaunch 是否仍在 new-failures）；
6. Gate 1 对照通过后，Gate 2 / 合并 / tag 仍归 Codex 专属决策。

## 9. 本轮边界声明

未修改任何源码、测试、配置、STATUS、PRE_MERGE_GATES、TUN、Clash、OpenCodex、10100、240s watchdog；未 commit / push / merge / tag；未删除任何 evidence、nul、VHDX、历史 worktree；未触碰 6767 现网服务；凭据一律 `[REDACTED]`。
