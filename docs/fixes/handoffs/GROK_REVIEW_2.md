# GROK REVIEW 2 — 独立审查 #3016 workspace 投影缓存修复

**执行者：** Grok（独立代码审查者）  
**日期：** 2026-07-28  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_2.md`  
**阶段：** 仅阶段 2（独立审查阶段 1 候选）  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**分支：** `docs/fix-plans-core-secondary`（未切换、未 checkout）

---

## 1. 结论

**`approve`**

阶段 1 的实现与证据可接受，**可以进入阶段 3 策划**。

明确边界（非 merge 批准）：

- 本结论 **不** 批准 merge / push / tag / 发版。
- **Gate 1 Linux 全仓 pytest：未由本阶段执行或判定**
- **Gate 2 AgentCenter C/E/R smoke：未由本阶段执行或判定**
- Windows 定向 GREEN 仅是定向证据，**不等于** Gate 1 或 Gate 2。
- PR #3 仍为 OPEN 未 merge；Issue #3016 关闭状态不由本阶段声称。

---

## 2. 审查基线

| 项 | 值 |
|----|-----|
| 工作树 HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| `origin/docs/fix-plans-core-secondary` | `dc83140c73ceb12fa165753c1880c19f68da86f4`（一致） |
| PR #3 参照 HEAD | `744e3a04a9b041b7bf3c2ae25cd22f96f5945038` |
| PR #3 分支 | `fix/core-workspace-3016` |
| PR #3 test-first | `6fd9ef440ac9aadbb965904d6378f7072243d230` |
| 远端 PR #2 | OPEN，`headRefOid=dc83140…`，`mergedAt=null` |
| 远端 PR #3 | OPEN，`headRefOid=744e3a0…`，`mergedAt=null` |
| 远端 tags（抽样） | 仅见 `v0.6.0-zhcn.1`；无本轮新建 tag |

### 实际文件范围

| 文件 | 归属 | 说明 |
|------|------|------|
| `omnigent/runner/app.py` | 阶段 1 源码 | +11 / −4；仅三函数 |
| `tests/runner/test_session_workspace_cache.py` | 阶段 1 测试（untracked） | 两回归测试；blob 与 test-first 一致 |
| `docs/fixes/handoffs/HERMES_COMPLETION_1.md` | 阶段 1 报告（untracked） | 只读审计 |
| `docs/fixes/STATUS.md` | **r05 既有** | 非阶段 1；LastWriteTime 2026-07-24 |
| `docs/fixes/PRE_MERGE_GATES.md` | **r05 既有** | 非阶段 1；LastWriteTime 2026-07-24 |
| `docs/fixes/POST_FIX_HANDOFF_PROMPT.md` | **r05 既有** | 非阶段 1；LastWriteTime 2026-07-24 |
| 其他 `docs/fixes/handoffs/*` | 前置 handoff | 非阶段 1 改动 |

`git rev-parse HEAD` / `origin/docs/fix-plans-core-secondary` 均为 `dc83140…`。  
`git reflog -10`：自 2026-07-24 起无 stage-1 产生的 commit / merge / tag；近期均为历史 checkout。未发现禁止操作痕迹。

---

## 3. RED 证据审计结果

**判定：RED 证据链充分、可接受。** 未回退源码重演 RED（任务禁止）。

### 3.1 测试 blob 同一性

```text
git rev-parse 6fd9ef4…:tests/runner/test_session_workspace_cache.py
→ 02cce3ca6e28233d5d0cac350a7be6316ff582d2

git hash-object tests/runner/test_session_workspace_cache.py
→ 02cce3ca6e28233d5d0cac350a7be6316ff582d2
```

两 blob **完全相同**，与任务卡预期一致。

### 3.2 test-first 父基线三处根因（`6fd9ef4^:omnigent/runner/app.py`）

| 函数 | 基线缺陷（已确认） |
|------|-------------------|
| `_session_workspace_value` | 无条件 `_session_workspace_cache[session_id] = snapshot.workspace`（失败 `None` 被永久缓存） |
| `_ensure_session_registered` | `if session_id in _session_start_cache: return` 直接短路；且无条件写 workspace |
| `_clear_session_agent_caches` | 仅清 spec/tool/snapshot；**无** workspace / fs registry 清理 |

### 3.3 HERMES_COMPLETION_1.md 记录的 RED

| 测试 | 报告命令 | 失败断言关键词 |
|------|----------|----------------|
| `test_failed_snapshot_does_not_poison_workspace_cache` | `PYTHONPATH="" uv run pytest -q …::test_failed_snapshot…` | `Missing agent_change.py means workspace cache stayed poisoned` |
| `test_reset_agent_cache_evicts_workspace_projection` | `PYTHONPATH="" uv run pytest -q …::test_reset_agent_cache…` | `Missing only_b.py means workspace and/or per-session fs registry projection survived reset` |

报告同时给出非零失败（1 failed）与上述根因断言文本。  
**RED 缺口：无。** 本审查未独立重跑 RED（禁止改源/回退）；blob 对齐 + 父基线根因 + 报告断言三者闭环。

### 3.4 测试语义覆盖

- **poison 测试：** 503→200 后 `/changes` 必须见 `agent_change.py` → 覆盖“失败 `workspace=None` 不得钉死缓存”。
- **reset 测试：** A→reset→B 后 `/changes` 必须见 `only_b.py` → 覆盖 workspace 投影 + per-session fs registry 双清。
- 与 PR #3 test-first 文件字节级一致，无断言弱化。

---

## 4. 实现语义检查结果

`git diff --stat -- omnigent/runner/app.py`：`1 file changed, 11 insertions(+), 4 deletions(-)`。

仅变更行（`git diff -U3` 过滤）：

```diff
-            _session_workspace_cache[session_id] = snapshot.workspace
+            if snapshot.ok:
+                _session_workspace_cache[session_id] = snapshot.workspace
+            else:
+                return None

-        if session_id in _session_start_cache:
+        if session_id in _session_start_cache and session_id in _session_workspace_cache:

-        _session_start_cache[session_id] = snapshot.created_at
-        _session_workspace_cache[session_id] = snapshot.workspace
+        if session_id not in _session_start_cache:
+            _session_start_cache[session_id] = snapshot.created_at
+        if snapshot.ok:
+            _session_workspace_cache[session_id] = snapshot.workspace

+        _session_workspace_cache.pop(session_id, None)
+        _session_fs_registries.pop(session_id, None)
```

### 4.1 契约逐项

| # | 契约 | 结果 |
|---|------|------|
| 1 | 失败 snapshot 的 `workspace=None` 不进 `_session_workspace_cache`；后续可重试 | **通过**（`snapshot.ok` 才写；else `return None`） |
| 2 | start cache 已有但 workspace 未解析时，`_ensure_session_registered` 不得永久短路 | **通过**（双条件短路；缺 workspace 时重新 snapshot） |
| 3 | 成功 snapshot 的 `workspace=None` 仍可缓存 | **通过**（仅判 `snapshot.ok`，不要求 workspace 非空） |
| 4 | agent-cache reset 同时清 workspace cache 与 per-session fs registry | **通过**（两处 `pop`） |
| 5 | 最小改动：仅三函数 + 两精确回归测试；无新依赖/跨阶段 | **通过** |

### 4.2 与 PR #3（`origin/fix/core-workspace-3016`）行为等价

| 函数 | 等价性 | 差异性质 |
|------|--------|----------|
| `_session_workspace_value` | 等价 | PR #3 用 `if not ok: return` + 注释；当前用 `if ok: cache else return` — 控制流等价 |
| `_ensure_session_registered` | 等价 | PR #3 为“start 存在时内嵌补 workspace 再 return”；当前为“双 cache 均在才 return，否则统一路径且不覆盖已有 created_at” — 可达状态与写库条件等价 |
| `_clear_session_agent_caches` | 等价 | 同两 `pop`；PR #3 注释/docstring 更完整，当前更短 — 允许范围内 |

**未发现：** sleep、retry loop、异常吞噬、断言弱化、强制 worktree、公开接口变化、跨阶段逻辑。

### 4.3 created_at 保护

`if session_id not in _session_start_cache` 保证后续 retry **不覆盖** 已闩住的 `created_at`。与任务卡一致。

---

## 5. 独立 GREEN / Ruff / `git diff --check`

环境：`$env:PYTHONPATH=''`（进程内，避免 hermes-agent 污染）。  
**以下均为 Windows 定向证据，绝非 Gate 1 / Gate 2。**

| # | 命令 | 退出码 | 结果 |
|---|------|--------|------|
| 1 | `uv run pytest -q tests/runner/test_session_workspace_cache.py` | **0** | `2 passed in 2.73s` |
| 2 | `uv run pytest -q tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries` | **0** | `1 passed in 1.26s` |
| 3 | 组合：`…test_session_workspace_cache.py` + `…::test_failed_session_snapshot_is_not_cached_and_retries` | **0** | `3 passed in 2.79s` |
| 4 | `uv run ruff check omnigent/runner/app.py tests/runner/test_session_workspace_cache.py` | **0** | `All checks passed!` |
| 5 | `git diff --check` | **0** | 无输出 |

---

## 6. r05 文档保护核对

| 文件 | LastWriteTime | 判定 |
|------|---------------|------|
| `docs/fixes/STATUS.md` | 2026-07-24 18:20:31 | 保持 r05 日戳 |
| `docs/fixes/PRE_MERGE_GATES.md` | 2026-07-24 18:19:59 | 保持 r05 日戳 |
| `docs/fixes/POST_FIX_HANDOFF_PROMPT.md` | 2026-07-24 18:21:01 | 保持 r05 日戳 |

真实性 / 未执行标记（只读检索仍存在）：

- `fixrun-20260724-target-v0.6.0-zhcn.2-r05`
- `pipeline_status` / `PYTEST_EXIT` / `TEE_EXIT` / `INVALID`
- `baseline-fail-ids.txt` / `integrate-fail-ids.txt` / `new-failures.txt`
- Gate 1 / Gate 2 **未执行 / 未达标** 措辞

`git diff --check --` 上述三文档：通过（整体 `git diff --check` exit 0）。  
**本阶段未整理或修改 r05 文档。**

---

## 7. P0 / P1 / P2 分级发现

### P0

**无**

### P1

**无**

### P2

1. **`_ensure_session_registered` docstring 未同步双 cache 短路条件**  
   仍写 “Subsequent calls … short-circuit immediately”，实际需 start + workspace 均在。PR #3 亦未完全对齐 docstring。  
   **建议后续处理：是（可在后续文档/注释清理中改；不阻塞本阶段）。**

2. **相对 PR #3 注释更少**  
   任务卡允许“更少注释或等价控制流”。可读性略降，契约不改。  
   **建议后续处理：可选。**

3. **持续失败 snapshot 的请求放大**  
   失败不缓存 → 每次访问重拉 server（与 PR #3 及 Hermes 风险说明一致，属预期权衡）。  
   **建议后续处理：否（当前契约正确）；若生产出现风暴再单独设计限流。**

---

## 8. 必须修改项

**无**

（无 P0/P1；不退回 Hermes 返工。）

---

## 9. 剩余风险

1. **Gate 1 / Gate 2 仍未执行** — 合并门槛未达标；本 `approve` 仅放行进入阶段 3 策划。
2. **Windows 定向 3 passed ≠ Linux 全仓** — 未覆盖 fcntl/pexpect 等路径与全量回归。
3. **agent-cache reset 不清理 `_session_start_cache`** — 与 PR #3 一致且符合 “created_at 不覆盖”；若未来 reset 语义要“完全空白 session 注册态”，需另开契约（非本缺陷）。
4. **瞬时/持续 503 下的重复 GET** — 正确重试语义的成本；极端高频调用可能增加 server 压力。
5. **未验证真实 AgentCenter multi-worktree 编排** — 单测 mock 已覆盖投影契约，生产路径仍依赖后续 Gate 2。

---

## 10. Gate 1 / Gate 2

| 门槛 | 本阶段状态 |
|------|------------|
| Gate 1 Linux 全仓 pytest | **未由本阶段执行或判定** |
| Gate 2 AgentCenter C/E/R smoke | **未由本阶段执行或判定** |

不得将上述定向 GREEN 表述为任一 Gate 通过。

---

## 11. 禁止项遵守（审查侧）

- [x] 未修改 `omnigent/`、`tests/`、r05 文档、Hermes 报告或既有任务卡  
- [x] 未 checkout / switch / rebase / cherry-pick / stash / reset / clean  
- [x] 未 commit / push / merge / tag / 发版 / 编辑 PR·Issue  
- [x] 发现问题仅记录，未自行修复  
- [x] 未开始阶段 3  
- [x] 未将 `approve` 表述为允许合并  
- [x] 未声称 Gate 1/2 已执行或通过  

**唯一写入文件：** `docs/fixes/handoffs/GROK_REVIEW_2.md`（本文件）

---

## 12. 最终 `git status --short --branch`

（写入本报告后预期状态；以交付时现场命令为准复述如下。）

```text
## docs/fix-plans-core-secondary...origin/docs/fix-plans-core-secondary
 M docs/fixes/POST_FIX_HANDOFF_PROMPT.md
 M docs/fixes/PRE_MERGE_GATES.md
 M docs/fixes/STATUS.md
 M omnigent/runner/app.py
?? docs/fixes/handoffs/
?? tests/runner/test_session_workspace_cache.py
```

说明：`docs/fixes/handoffs/` 下现含本审查文件 `GROK_REVIEW_2.md` 及既有 handoff/任务卡/Hermes 报告；除本文件新建外无其它工作树改动。
