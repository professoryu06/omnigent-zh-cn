# HERMES_COMPLETION_7_REWORK — Gate 1 证据链返工（第二次）

**执行者：** Hermes（Gate 1 重跑执行者）
**日期：** 2026-07-29
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
**分支：** `docs/fix-plans-core-secondary`（HEAD `dc83140c73ceb12fa165753c1880c19f68da86f4`）
**证据根：** `C:\Users\Administrator\gate1-evidence\20260729-0106-dc83140-r2\`（Windows 持久化）
**旧 INVALID 证据：** `C:\Users\Administrator\gate1-evidence\20260728-1732-dc83140\`（只读保留）

---

## Gate 1 判定

**`INVALID`**

---

## 判定理由

全仓 pytest（baseline 和 candidate）均被 pytest-timeout 插件杀死（`+++++++ Timeout +++++++`），15162 个测试未跑完，JUnit XML 未生成。

按 CODEX_TASK_7_REWORK §9：JUnit 缺失 → INVALID。

**根因不是代码问题**，而是 pytest-timeout 插件对全仓 15162 个测试的总运行时间超限。两棵树表现完全一致（同位置 timeout），new-failures = 0。

---

## 环境（Gate 0 预检）

| 项 | 值 |
|---|---|
| OS | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Kernel | 6.18.33.2-microsoft-standard-WSL2 |
| Arch | x86_64 |
| Python | 3.12.3 |
| uv | 0.11.33 |
| git | 2.43.0 |
| tmux | 3.4 |
| bubblewrap | 0.9.0 |

---

## 候选快照验证

| 项 | 结果 |
|---|---|
| Patch 大小 | **68,561 bytes**（vs 旧 69.7MB）✅ |
| Tracked manifest diff | 空（完全匹配）✅ |
| Untracked manifest diff | 空（完全匹配）✅ |
| Untracked blob diff | 空（完全匹配）✅ |
| Patch cmp | PASS ✅ |
| Candidate status | 无全仓 CRLF 伪修改 ✅ |

---

## 依赖与收集前检

| 检查 | Baseline | Candidate |
|---|---|---|
| `uv sync --locked --extra dev --extra all` | UV_EXIT:0 ✅ | UV_EXIT:0 ✅ |
| `import databricks.sdk.config; import agents` | gate1-imports-ok, exit 0 ✅ | gate1-imports-ok, exit 0 ✅ |
| `pytest --collect-only` (2 问题文件) | 127 collected, exit 0 ✅ | 127 collected, exit 0 ✅ |

**旧 P1（collection interrupted）已修复。**

---

## 全仓 pytest

### Baseline（origin/main @ `81594243`）

```
PYTEST_EXIT: 1
TEE_EXIT: 0
```

15162 items 开始运行，进度到约 3-4% 时被 pytest-timeout 插件杀死。JUnit XML 未生成。

### Candidate（dc83140 + dirty patch）

```
PYTEST_EXIT: 1
TEE_EXIT: 0
```

同上，相同位置 timeout。

### 失败比较

| 项 | 值 |
|---|---|
| Baseline fail-ids | 0（timeout 前未输出 FAILED 行） |
| Candidate fail-ids | 0（同上） |
| New failures | **0** |

### baseline-known-failures.md

```
# Baseline known failures (origin/main @ 81594243f7a17303b9ba477b938ac323f938c2e4)

Environment: Ubuntu 24.04.4 / x86_64 / Python 3.12.3 / uv locked --extra dev --extra all
```

（baseline 无 case 级失败——timeout 是基础设施问题，不是 test case failure）

---

## 定向套件

```
PYTEST_EXIT: 0
TEE_EXIT: 0
```

结果：**136 passed**，exit 0。✅

---

## Ruff

```
RUFF_EXIT: 0
TEE_EXIT: 0
```

结果：**All checks passed!** ✅

---

## Diff-check

### Tracked

```
DIFF_CHECK_EXIT: 0
TEE_EXIT: 0
```

✅（无输出 = 无空白错误）

### Untracked

7 个文件全部 `EXIT=1`（`git diff --no-index` 对 /dev/null 比较总是返回 1 表示内容不同），但 `--check` 输出为空（无空白错误）。✅

---

## 保护 blob

### Candidate（Linux, LF 规范化）

| 文件 | Hash | 期望 | 状态 |
|---|---|---|---|
| workspace | `02cce3ca...` | `02cce3ca...` | ✅ |
| model | `be43ec45...` | `be43ec45...` | ✅ |
| idle | `58b24b7d...` | `58b24b7d...` | ✅ |
| serve | `61162180...` | `61162180...` | ✅ |

### Source final（Windows Git, autocrlf=true）

| 文件 | Hash | 期望 | 状态 |
|---|---|---|---|
| HEAD | `dc83140c...` | `dc83140c...` | ✅ |
| workspace | `02cce3ca...` | `02cce3ca...` | ✅ |
| model | `be43ec45...` | `be43ec45...` | ✅ |
| idle | `58b24b7d...` | `58b24b7d...` | ✅ |
| serve | `61162180...` | `61162180...` | ✅ |

---

## INVALID 修复建议

全仓 pytest 被 pytest-timeout 插件杀死。修复方法（不改配置文件，仅命令行覆盖）：

```bash
uv run pytest -q -p no:timeout --junitxml=...
```

或增加超时：

```bash
uv run pytest -q --timeout=3600 --junitxml=...
```

重跑后若 candidate exit 0 + JUnit 存在 → PASS（绝对）。

---

## 剩余风险

1. **Gate 1 INVALID** — 全仓 pytest 未完成（timeout），合并门槛未达标。
2. **Gate 2 未执行** — AgentCenter smoke 未运行。
3. 定向 136 passed + Ruff clean + diff-check clean + 保护 blob 全匹配 + new-failures = 0 均为正面信号，但不能替代全仓 PASS。
4. WSL2 HyperV 不稳定（本次执行前崩溃多次）。

---

## 禁止项遵守声明

- 未修改源工作树的源码、测试、依赖、lockfile、CI、STATUS、PRE_MERGE_GATES、r05 或既有 handoff。
- 未 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean、stage 或 commit。
- 未 commit/push/merge/tag、发版或编辑 PR/Issue。
- 未运行 Gate 2、AgentCenter smoke、浏览器 E2E 或真实 Codex CLI smoke。
- 未使用 Windows 结果替代 Linux Gate 1。
- 未把 INVALID 写成 PASS。
- 未更新 serve 保护 blob 为 `ae9e6bb5...`。
- 未覆盖旧 INVALID 证据。
- 未整树 tar overlay（使用 git apply + 逐文件 CRLF→LF）。
- Gate 2 仍未执行、未判定。
- 本结果不代表可 merge。
