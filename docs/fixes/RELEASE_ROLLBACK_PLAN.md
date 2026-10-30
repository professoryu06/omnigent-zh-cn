# RELEASE_ROLLBACK_PLAN — Omnigent 第一版发布回滚方案

- 日期：2026-08-06；基线：`8ef79ac348711d523053019cdb2f36e8cbbfef7e`
- Evidence：`20260806-160933-8ef79ac-hermes-release-control`
- 原则：**任何失败都通过"新建回滚 worktree + 指回已知好 SHA"解决，绝不 force-push、绝不重写历史、绝不删除既有 worktree/evidence。**
- 本方案不授权任何 commit/push/merge/tag；所有命令均为模板，实际执行需对应任务卡显式授权。

## 1. Release 分支命名

| 用途 | 名称 | 说明 |
|---|---|---|
| 第一版整合分支 | `release/v0.6.0-zhcn.2-rc1` | 从 `8ef79ac` 切出；rc 递增（rc2、rc3…）对应 Gate 对照轮次 |
| Tag（仅 Codex 授权后） | `v0.6.0-zhcn.2` | 单调递增（已有 `v0.6.0-zhcn.1`，禁止 fix-core/fix-scale 风格 tag） |
| 回滚分支 | `release/v0.6.0-zhcn.2-rollback-<日期>` | 失败时新建，不覆盖 rc 分支 |

## 2. Checkpoint / Tag 顺序（线性、只前进）

```
C0  8ef79ac  ──────────── 基线（main，PR#3/#4 已合并）★ 唯一权威起点
      │
C1  <sha-1>  release/v0.6.0-zhcn.2-rc1
      │        └─ Task30 移植：35 FIRST-V1 文件（blob=e691d08）一次性提交
      │           commit message: "release-v1: port FIRST-V1 fixes (BUG-1/2/3, NP-1, PROC-1) from e691d08"
      │
C2  <sha-2>  同分支第二个提交
      │        └─ Task30 移植：7 个 DIFF/MIXED-HUNK 文件逐 hunk 审查后提交
      │           commit message: "release-v1: port MIXED-HUNK hunks (cli/connect/codex_executor/runner_app + 3 tests)"
      │
C3  <sha-3>  （可选）harness_bench sol→luna 专项卡提交 —— 仅 Codex 显式授权后
      │
GATE-1  由 Hermes 以全新 RUN_ID 双树对照（rc1 候选 vs 8ef79ac clean）
      │
GATE-2  由 Codex 专属签字
      │
TAG   v0.6.0-zhcn.2  ── 仅 Gate1+Gate2 双通过后，由 Codex 授权打
```

**顺序铁律**：
1. C0 永远不动、不重写。
2. 每个 checkpoint 是一个独立 commit，可单独 `git checkout` 指回。
3. 任何 checkpoint 失败 → 指回上一个已知好 checkpoint（见 §4），而不是在原 checkpoint 上 amend。
4. Tag 只在最后、只由 Codex 授权、只单调递增。

## 3. 每张任务卡对应的 commit 边界

第一版整合把历史任务卡的成果收敛为两个提交边界：

| Commit 边界 | 归属任务卡（成果来源） | 文件范围 | 边界 SHA |
|---|---|---|---|
| **B1**（C1 提交） | CODEX_TASK_22/23（BUG-1/2/3 隔离+分流）、TASK_24（BUG-4 私有 CODEX_HOME）、#2853 NP-1 fail-loud phase-1、PROC-1 session/cleanup | 35 个 blob=e691d08 的 FIRST-V1 文件（源码 23 + 测试 12，见 manifest §4） | `<sha-1>` |
| **B2**（C2 提交） | CODEX_TASK_24 MIXED-HUNK、TASK_29 相关隔离 hunk（仅批准部分） | 7 个 DIFF 文件：`omnigent/cli.py`、`omnigent/host/connect.py`、`omnigent/inner/codex_executor.py`、`omnigent/runner/app.py`、`tests/host/test_connect.py`、`tests/inner/test_codex_runtime_isolation.py`、`tests/runner/test_codex_terminal_ensure_guard.py` | `<sha-2>` |

**明确排除在任何 commit 边界之外**（不进第一版）：
- manifest §5 的 4 个 ISOLATE 文件（Grok R5 proxy/relaunch 修复）
- Task29 Route-A proxy hunk（`task29/codex-direct` 分支对基线零新增 commit，且 worktree 元数据损坏）
- PR #5（`fix/core-2853-native-prompt`，OPEN）
- zh-next Grok native 实验、`start_omnigent_*.sh` 脚本
- `evidence/`、`nul`、异常目录 `C\uff0f/`（KEEP-EVIDENCE，另开清理卡）

> 注意：历史 `e691d08`（review 分支）是"本地修复候选"提交，**不是** release 线提交。第一版不复用它的 SHA，而是把其内容按 B1/B2 重新落到 `release/v0.6.0-zhcn.2-rc1` 上，产生全新 SHA。

## 4. 失败时如何新建回滚 worktree

### 4.1 触发条件（任一即触发回滚）
- Gate 1 对照出现新增失败（new-failures 非空）且无法归因豁免；
- Gate 2 Codex 判 FAIL；
- 第一版服务启动后出现 BUG-1/2/3/4 主链路回归；
- 现网 6767 受影响。

### 4.2 回滚步骤（新建 worktree，不破坏现状）
```bash
# 0) 定位"最近已知好 SHA"。第一版任何失败，最近已知好 SHA 都是基线 8ef79ac。
GOOD_SHA=8ef79ac348711d523053019cdb2f36e8cbbfef7e

# 1) 在 review 仓（主 worktree 所在仓）新建一个回滚 worktree，指回基线。
#    路径与名字都独立，绝不复用/覆盖既有树。
git -C "F:/codex-ai/git项目部署/tmp/omnigent-review" \
    worktree add \
    "F:/codex-ai/git项目部署/tmp/omnigent-rollback-$(date +%Y%m%d-%H%M%S)" \
    -b "release/v0.6.0-zhcn.2-rollback-$(date +%Y%m%d)" \
    "$GOOD_SHA"

# 2) 验证回滚树 HEAD 确实指回基线（必须打印 8ef79ac…）
git -C "<新回滚树路径>" rev-parse HEAD

# 3) 若需把现网 6767 切回基线：由 Codex 授权后，从回滚树重启产品；
#    不得直接改 omnigent-zh-next 运行树。
```

### 4.3 回滚边界约束
- **绝不** `git reset --hard`、`git push -f`、删除 rc 分支或既有 worktree。
- **绝不**删除任何 evidence、nul、VHDX、历史 worktree（含损坏的 task29 树——保留现场）。
- 回滚 worktree 建好后，原 rc 分支**保留不动**，供故障复盘。
- 回滚后必须重新走 Gate 1 对照，才能再次尝试前进。
- OpenCodex/10100/TUN/Clash/240s watchdog 在回滚过程中**一律不触碰**。

## 5. 回滚决策矩阵

| 失败点 | 指回目标 | 动作 |
|---|---|---|
| B1 移植后定向回归失败 | `8ef79ac` | 新建回滚树；B1 作废，重审 35 文件移植 |
| B2 移植后 Gate 1 新增失败 | `8ef79ac`（或已验证的 B1） | 新建回滚树；把 B2 的 MIXED-HUNK 逐 hunk 退回重审 |
| Gate 2 FAIL | `8ef79ac` | 新建回滚树；rc 分支整体冻结待 Codex 决策 |
| 现网回归 | `8ef79ac`（现网本应指回 zh-next 运行树或基线） | 由 Codex 授权切换运行树，不改源码 |

## 6. 本方案边界

本文件只提供回滚流程与边界定义，**不执行**任何 commit/push/merge/tag/worktree 创建。所有命令均为模板。实际回滚须由对应任务卡显式授权，且凭据一律 `[REDACTED]`。
