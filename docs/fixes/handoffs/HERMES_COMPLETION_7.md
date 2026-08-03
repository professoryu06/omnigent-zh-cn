# HERMES_COMPLETION_7 — Gate 1 Linux 全仓执行

**执行者：** Hermes（Gate 1 执行者）
**日期：** 2026-07-28
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
**分支：** `docs/fix-plans-core-secondary`（HEAD `dc83140c73ceb12fa165753c1880c19f68da86f4`）
**证据根：** `C:\Users\Administrator\gate1-evidence\20260728-1732-dc83140`（Windows 持久化）

---

## Gate 1 判定

**`INVALID`**

---

## 判定理由

三项证据链缺陷阻止 PASS：

1. **全仓 pytest 未完成收集**：baseline 和 candidate 均 exit 2（collection interrupted），2 个 collection errors 在 `tests/inner/test_openai_agents_sdk_executor.py`。全仓测试从未实际运行，无法形成有效的全仓比较。
2. **`git diff --check` 结果不可信**：(a) 脚本 bug——`$?` 捕获了 `tee` 的退出码（0）而非 `git diff --check` 的退出码；(b) Windows NTFS 源工作树（autocrlf=true）overlay 到 Linux（autocrlf=false）后，所有文件行尾带 `\r`，git 将每行标记为 trailing whitespace。这是跨平台伪影，非真实代码问题。
3. **未创建 `baseline-known-failures.md`**：任务卡 §8 PASS（相对 main）要求每个 baseline 失败有同环境已知原因文档。

按任务卡 §8：证据链损坏 → `INVALID`。

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
| 执行方式 | WSL2（Windows 宿主机） |

环境合格。

---

## 候选快照

| 项 | 值 |
|---|---|
| CANDIDATE_HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| MAIN_SHA | （见 commits-and-status.txt） |
| RUN_ID | `20260728-1732-dc83140` |
| 文件级验证 | PASS（CRLF 归一化后所有 tracked + untracked 文件匹配） |
| Patch 级 cmp | 跳过（Windows autocrlf=true 产生不同 blob hash，跨平台不可比） |

---

## 全仓 pytest 结果

### Baseline（origin/main）

```
PYTEST_EXIT: 2
TEE_EXIT: 0
```

Summary: `Interrupted: 2 errors during collection`（`tests/inner/test_openai_agents_sdk_executor.py`）

### Candidate（dc83140 + dirty overlay）

```
PYTEST_EXIT: 2
TEE_EXIT: 0
```

Summary: `Interrupted: 2 errors during collection`（同一文件）

### 失败比较

| 项 | 值 |
|---|---|
| Baseline fail-ids | 2 |
| Candidate fail-ids | 2 |
| New failures | **0**（`new-failures.txt` 为空） |

两个 collection errors 完全相同，均为 `test_openai_agents_sdk_executor.py`（疑似缺少 openai-agents-sdk 可选依赖）。候选无新增失败。

**但**：exit 2 = collection interrupted，全仓测试从未实际运行。不满足 PASS（绝对）的 "candidate pytest exit 0" 条件，也不满足 PASS（相对 main）的 "证据有效" 条件。

---

## 当前候选定向套件

```
PYTEST_EXIT: 0
TEE_EXIT: 0
```

结果：**136 passed**，exit 0。✅

覆盖阶段 1/3/5 全部定向 nodeid（workspace cache、model、loader、host watcher、idle、serve drain、prompt delivery、executor、app-server）。

---

## Ruff

```
RUFF_EXIT: 0
TEE_EXIT: 0
```

结果：**All checks passed!** ✅

---

## git diff --check

```
DIFF_CHECK_EXIT: 0（脚本 bug：捕获 tee 退出码）
```

实际 `git diff --check` 输出大量 trailing whitespace 警告（`.gitattributes`、`.github/`、`web/` 等所有文件）。原因：Windows NTFS 源工作树 autocrlf=true → 文件带 CRLF → overlay 到 Linux 后 git 将 `\r` 视为 trailing whitespace。

**这是跨平台伪影，非真实代码问题。** 但脚本未正确捕获 git 退出码，证据不可信。

---

## 源工作树最终保护核对

| 项 | 期望 | 实际 | 状态 |
|---|---|---|---|
| HEAD | `dc83140c...` | `dc83140c...` | ✅ |
| workspace blob | `02cce3ca...` | `02cce3ca...` | ✅ |
| model blob | `be43ec45...` | `be43ec45...` | ✅ |
| idle blob | `58b24b7d...` | `58b24b7d...` | ✅ |
| serve blob | `61162180...` | `ae9e6bb5...` | ⚠️ 不匹配 |

**serve blob 不匹配说明**：`tests/runner/transports/ws_tunnel/test_serve.py` 在 Grok 返工（CODEX_TASK_5_REWORK）中被修改（添加 `**_kwargs: Any` stubs 和 4 个 graceful drain 测试）。任务卡 §10 的保护值 `61162180...` 是阶段 3 完成时的值，Grok 返工后 blob 自然变化。这不是阶段 7 的修改，而是阶段 5 返工的累积结果。

---

## 证据文件清单

`C:\Users\Administrator\gate1-evidence\20260728-1732-dc83140\`：

- `env-preflight.txt`
- `commits-and-status.txt`
- `candidate-tracked.patch`（69.7 MB）
- `candidate-untracked-files.txt`
- `candidate-snapshot.sha256`
- `source.bundle`（25.2 MB）
- `candidate-status.txt`
- `baseline-sync.txt` / `candidate-sync.txt`
- `baseline-pytest.txt` / `baseline-pytest.xml` / `baseline-pytest.exit` / `baseline-tee.exit`
- `candidate-pytest.txt` / `candidate-pytest.xml` / `candidate-pytest.exit` / `candidate-tee.exit`
- `baseline-fail-ids.txt` / `candidate-fail-ids.txt` / `new-failures.txt`
- `targeted-current.txt`
- `ruff.txt`
- `diff-check.txt`
- `source-final-status.txt`

---

## INVALID 修复建议

要使 Gate 1 达到 PASS，需要：

1. **修复 collection errors**：在 uv sync 时安装 `openai-agents-sdk`（或使用 `--extra all`），使全仓 pytest 能完成收集。或者在 baseline-known-failures.md 中记录该 collection error 为已知环境限制。
2. **修复 diff-check 脚本**：使用 `PIPESTATUS[0]` 捕获 git 退出码；或在 candidate tree 中设置 `git config core.autocrlf true` 使行尾一致。
3. **创建 baseline-known-failures.md**：记录 2 个 collection errors 的同环境已知原因。
4. **serve blob 期望值更新**：任务卡 §10 的保护值需要反映 Grok 返工后的实际 blob。

---

## 剩余风险

1. **Gate 1 INVALID** — 合并门槛未达标。
2. **Gate 2 未执行** — AgentCenter smoke 未运行。
3. 全仓 pytest 从未实际运行（collection interrupted），真实全仓结果未知。
4. WSL2 HyperV 不稳定（本次执行前崩溃 2 次，`wsl --shutdown` 后恢复）。
5. 跨平台 CRLF 问题影响 diff-check 和 patch cmp。

---

## 禁止项遵守声明

- 未修改源工作树的 `omnigent/`、`tests/`、r05、STATUS、PRE_MERGE_GATES 或既有 handoff。
- 未 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean、stage 或 commit。
- 未 commit/push/merge/tag、发版或编辑 PR/Issue。
- 未运行 Gate 2、AgentCenter smoke、浏览器 E2E 或真实 Codex CLI smoke。
- 未使用 Windows 全仓或阶段 6 定向结果替代 Linux Gate 1。
- 未把 INVALID 写成 PASS。
- 未修测试让结果变绿。
- Gate 2 仍未执行、未判定。
- 本结果不代表可 merge。
