# HERMES COMPLETION 1 — #3016 workspace 投影缓存修复

**执行者：** Hermes（Qwen3.8）
**日期：** 2026-07-28
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_1.md`
**阶段：** 仅阶段 1（#3016）
**分支：** `docs/fix-plans-core-secondary`（未切换、未 checkout）

---

## 根因

`_session_snapshot()` 本身不缓存失败 snapshot，但 workspace 投影层破坏了重试语义：

1. **`_session_workspace_value()`**：无条件将 `snapshot.workspace`（失败时为 `None`）写入 `_session_workspace_cache`，导致一次瞬时 503 永久钉住 `workspace=None`。
2. **`_ensure_session_registered()`**：无条件投影 workspace，且 `_session_start_cache` 已存在即短路返回，阻止后续补取 workspace。
3. **`_clear_session_agent_caches()`**：不清理 `_session_workspace_cache` 和 `_session_fs_registries`，agent-cache reset 后旧 workspace 投影和 per-session filesystem registry 仍然存活。

---

## 修改文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `omnigent/runner/app.py` | 修改 | 三个函数最小修复（+11 −4） |
| `tests/runner/test_session_workspace_cache.py` | 新建 | 两个回归测试，语义与 PR #3 test-first `6fd9ef4` 一致 |
| `docs/fixes/handoffs/HERMES_COMPLETION_1.md` | 新建 | 本报告 |

未改动：`docs/fixes/STATUS.md`、`docs/fixes/PRE_MERGE_GATES.md`、`docs/fixes/POST_FIX_HANDOFF_PROMPT.md`、其他 handoff、依赖锁、配置、CI。

---

## 关键 diff（omnigent/runner/app.py）

### `_session_workspace_value()`（~L8622）

```diff
         if session_id not in _session_workspace_cache:
             snapshot = await _session_snapshot(session_id)
-            _session_workspace_cache[session_id] = snapshot.workspace
+            if snapshot.ok:
+                _session_workspace_cache[session_id] = snapshot.workspace
+            else:
+                return None
         return _session_workspace_cache.get(session_id)
```

### `_ensure_session_registered()`（~L17345）

```diff
-        if session_id in _session_start_cache:
+        if session_id in _session_start_cache and session_id in _session_workspace_cache:
             return
         snapshot = await _session_snapshot(session_id)
-        _session_start_cache[session_id] = snapshot.created_at
-        _session_workspace_cache[session_id] = snapshot.workspace
+        if session_id not in _session_start_cache:
+            _session_start_cache[session_id] = snapshot.created_at
+        if snapshot.ok:
+            _session_workspace_cache[session_id] = snapshot.workspace
```

### `_clear_session_agent_caches()`（~L17944）

```diff
         _session_snapshot_cache.pop(session_id, None)
+        _session_workspace_cache.pop(session_id, None)
+        _session_fs_registries.pop(session_id, None)
         if agent_id:
```

---

## RED 证据（修复前）

### 测试 1：`test_failed_snapshot_does_not_poison_workspace_cache`

```
命令：PYTHONPATH="" uv run pytest -q tests/runner/test_session_workspace_cache.py::test_failed_snapshot_does_not_poison_workspace_cache
结果：1 failed in 4.24s
断言：AssertionError: expected session worktree change after snapshot recovery;
      got paths=[] status_first=200 snapshot_count=1.
      Missing agent_change.py means workspace cache stayed poisoned
      and the runner used the global workspace.
```

### 测试 2：`test_reset_agent_cache_evicts_workspace_projection`

```
命令：PYTHONPATH="" uv run pytest -q tests/runner/test_session_workspace_cache.py::test_reset_agent_cache_evicts_workspace_projection
结果：1 failed in 2.32s
断言：AssertionError: after agent-cache reset, expected workspace B changes;
      got ['only_a.py']. Missing only_b.py means workspace and/or
      per-session fs registry projection survived reset.
```

> 注：运行 pytest 需 `PYTHONPATH=""` 清除 hermes-agent venv 路径污染（`PYTHONPATH` 被设为 hermes-agent site-packages，导致 PIL/pydantic_core 导入失败）。此为环境问题，不影响测试语义。

---

## GREEN 证据（修复后）

| 命令 | 结果 |
|------|------|
| `PYTHONPATH="" uv run pytest -q tests/runner/test_session_workspace_cache.py` | **2 passed** in 2.63s |
| `PYTHONPATH="" uv run pytest -q tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries` | **1 passed** in 1.19s |
| `PYTHONPATH="" uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries` | **3 passed** in 2.37s |
| `PYTHONPATH="" uv run ruff check omnigent/runner/app.py tests/runner/test_session_workspace_cache.py` | **All checks passed!** |
| `git diff --check` | 无输出，退出码 0 |

---

## 风险

1. **环境依赖**：pytest 运行需 `PYTHONPATH=""` 前缀；CI/Linux 环境无此问题。
2. **`_ensure_session_registered` 短路条件变更**：现在需要 `_session_start_cache` 和 `_session_workspace_cache` 同时存在才短路。若某 session 的 snapshot 始终失败（`ok=False`），每次调用都会重新 fetch snapshot。这与 PR #3 语义一致（失败不缓存 → 允许重试），但高频调用场景下可能增加 server 请求量。
3. **成功 snapshot 的 `workspace=None`**：仍会缓存（`snapshot.ok` 为真时），保持原有"成功解析但没有显式 workspace"语义。

---

## 未完成项

| 项 | 状态 |
|----|------|
| Gate 1 Linux 全仓 pytest | **未由本阶段执行或判定** |
| Gate 2 AgentCenter C/E/R smoke | **未由本阶段执行或判定** |
| PR #3 merge | OPEN 未 merge（本阶段不操作） |
| #2853 Phase2 / #2539 / #2854 / #2967 | 不在本阶段范围 |

---

## 约束遵守

- [x] 未 checkout/switch/rebase/cherry-pick
- [x] 未 commit / push / merge / tag / 发版
- [x] 未编辑 PR/Issue
- [x] 未修改密钥、账号、模型凭据
- [x] 未改动 r05 文档改动（STATUS.md / PRE_MERGE_GATES.md / POST_FIX_HANDOFF_PROMPT.md 保持原样）
- [x] 未跨阶段修复或顺手重构
- [x] 未声称 Gate 1/2 已执行或通过
- [x] 未声称 PR #3 可合并或 Issue 已关闭

---

## 最终 Git 状态

```
## docs/fix-plans-core-secondary...origin/docs/fix-plans-core-secondary
 M docs/fixes/POST_FIX_HANDOFF_PROMPT.md
 M docs/fixes/PRE_MERGE_GATES.md
 M docs/fixes/STATUS.md
 M omnigent/runner/app.py
?? docs/fixes/handoffs/
?? tests/runner/test_session_workspace_cache.py
```

`git diff --stat -- omnigent/runner/app.py`：1 file changed, 11 insertions(+), 4 deletions(-)
