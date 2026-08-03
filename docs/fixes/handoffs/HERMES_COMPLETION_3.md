# HERMES_COMPLETION_3 — CODEX_TASK_3 阶段 3 完成报告

日期：2026-07-28
分支：`docs/fix-plans-core-secondary`（HEAD `dc83140`，未 commit）
工作树：`F:\codex-ai\git项目部署\tmp\omnigent-review`

---

## 3A — #3175 Codex native model canonical-first

### RED

```
PYTHONPATH="" uv run pytest -q tests/runner/test_app_codex_native_model.py
```

结果：4 failed, 5 passed。`_codex_native_model_from_spec()` 只读 `config["model"]`，不读 `executor.model`（canonical 字段）。

### FIX

`omnigent/runner/app.py::_codex_native_model_from_spec()`：先读 `spec.executor.model`（canonical），若为 `None` 再回退 `spec.executor.config.get("model")`。

### GREEN

```
PYTHONPATH="" uv run pytest -q tests/runner/test_app_codex_native_model.py
```

结果：**9 passed**。

组合套件（含 claude/cursor native model + codex launch config）：

```
PYTHONPATH="" uv run pytest -q tests/runner/test_app_codex_native_model.py tests/runner/test_app_claude_native_model.py tests/runner/test_app_cursor_native_model.py tests/runner/test_codex_native_launch_config.py
```

结果：**47 passed**。

---

## 3B — #3178 executor bundle nesting fail-loud

### RED

```
PYTHONPATH="" uv run pytest -q tests/inner/test_loader.py::TestLoadFromDict::test_executor_bundle_nesting_rejected tests/inner/test_loader.py::TestLoadFromDict::test_executor_extra_keys_tolerated tests/inner/test_loader.py::TestLoadFromDict::test_tools_agent_executor_bundle_nesting_rejected
```

结果：2 个 rejection 测试未抛 `ValueError`（RED），1 个 toleration 测试通过。

### FIX

`omnigent/inner/loader.py::_parse_executor_spec()` dict 分支最前面加入 fail-loud 检查：若 `data` 包含 `"config"` 或 `"type"` 键，抛出 `ValueError`（提示 #3178 和扁平化要求）。

6 处 compat fixture 扁平化（`executor: {config: {harness: ...}}` → `executor: {harness: ...}`）：
- `tests/e2e_ui/chat/test_chat_file_path_links.py`（1 处）
- `tests/e2e_ui/conftest.py`（4 处）
- `tests/server/integration/test_session_mcp_servers.py`（1 处）

2 处 strict fixture 保留嵌套不变。

### GREEN

```
PYTHONPATH="" uv run pytest -q tests/inner/test_loader.py::TestLoadFromDict::test_executor_bundle_nesting_rejected tests/inner/test_loader.py::TestLoadFromDict::test_executor_extra_keys_tolerated tests/inner/test_loader.py::TestLoadFromDict::test_tools_agent_executor_bundle_nesting_rejected
```

结果：**3 passed**。

受影响套件：

```
PYTHONPATH="" uv run pytest -q tests/server/integration/test_session_mcp_servers.py
```

结果：**6 passed**。

```
PYTHONPATH="" uv run pytest -q tests/spec/test_load.py
```

结果：**6 passed**。

---

## 3C — #3060 idle runner 安静退出

### RED

```
PYTHONPATH="" uv run pytest -q tests/host/test_connect.py::test_watch_runner_silent_on_clean_exit
```

结果：**1 failed** — code 0 退出仍被报告为 crash。

```
PYTHONPATH="" uv run pytest -q tests/runner/test_runner_idle_active_work.py::test_drain_session_streams_enqueues_done_sentinel
```

结果：**1 failed** — `app.state.drain_session_streams` 不存在。

```
PYTHONPATH="" uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

结果：**4 failed** — `_graceful_drain` 不存在、`shutdown_event` 参数不存在。

### FIX（四处）

1. **`omnigent/host/connect.py::_watch_runner()`**：`returncode == 0` 记 info 并直接返回，不发 crash report，不进入 `_unreported_exits`。

2. **`omnigent/runner/app.py`**：在 `app.state.has_active_work` 赋值后新增 `_drain_session_streams()`，对 `list(_session_event_queues.values())` 快照逐个 `put_nowait(None)`，暴露为 `app.state.drain_session_streams`。

3. **`omnigent/runner/transports/ws_tunnel/serve.py`**：
   - 新增常量 `_GRACEFUL_CLOSE_TIMEOUT_S = 5.0`、`_GRACEFUL_DRAIN_TIMEOUT_S = 5.0`。
   - `serve_tunnel()` 新增可选 `shutdown_event` 与 `on_graceful_shutdown`；event 在连接前/连接后已 set 时直接返回，不再重连。
   - `_serve_tunnel_once()` 新增 `shutdown_event`/`on_graceful_shutdown` 参数；有 shutdown event 时调用 `_recv_loop_with_shutdown()` race `ws.recv()` 与 event。
   - 新增 `_recv_loop_with_shutdown()`：event 获胜时取消并 settle recv、调用 `_graceful_drain()` 后正常返回。
   - 新增 `_graceful_drain()`：先调用 hook（异常只记录不阻止退出），再有界等待所有 dispatch task；超时任务留给既有 finally 的 `_cancel_dispatch_tasks()`。

4. **`omnigent/runner/_entry.py`**：
   - 新增 `_GRACEFUL_SHUTDOWN_TUNNEL_TIMEOUT_S = 15.0`。
   - 为 idle reaper 创建独立 `tunnel_shutdown_event`，传给 `serve_tunnel()` 的 `shutdown_event`，并传 `app.state.drain_session_streams` 作为 `on_graceful_shutdown`。
   - idle monitor 的 `request_shutdown` 改为 `tunnel_shutdown_event.set`；signal/parent-death 仍走 `stop_event` 快速终止路径。
   - `asyncio.wait(FIRST_COMPLETED)` 后新增分支：idle_task 完成且 `tunnel_shutdown_event.is_set()` 时，`asyncio.wait_for(tunnel_task, timeout=15s)` 有界等待 tunnel drain 完成，超时记 warning 后进入 finally 强制取消。

### GREEN — 新增用例

```
PYTHONPATH="" uv run pytest -q tests/host/test_connect.py::test_watch_runner_silent_on_clean_exit tests/host/test_connect.py::test_watch_runner_reports_unexpected_exit tests/host/test_connect.py::test_watch_runner_silent_on_intentional_stop
```

结果：**3 passed**。

```
PYTHONPATH="" uv run pytest -q tests/runner/test_runner_idle_active_work.py
```

结果：**1 passed**。

```
PYTHONPATH="" uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

结果：**4 passed**。

### GREEN — 受影响套件

```
PYTHONPATH="" uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py tests/runner/transports/ws_tunnel/test_serve_extended.py
```

结果：**54 passed**。

```
PYTHONPATH="" uv run pytest -q tests/runner/test_runner_entry.py
```

结果：**69 passed**。

---

## 阶段 1 回归

```
PYTHONPATH="" uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries
```

结果：**3 passed**。

---

## Ruff

```
PYTHONPATH="" uv run ruff check omnigent/runner/app.py omnigent/inner/loader.py omnigent/host/connect.py omnigent/runner/_entry.py omnigent/runner/transports/ws_tunnel/serve.py tests/runner/test_app_codex_native_model.py tests/inner/test_loader.py tests/e2e_ui/chat/test_chat_file_path_links.py tests/e2e_ui/conftest.py tests/server/integration/test_session_mcp_servers.py tests/host/test_connect.py tests/runner/test_runner_idle_active_work.py tests/runner/transports/ws_tunnel/test_serve.py
```

结果：**All checks passed!**

---

## git diff --check

结果：**无输出，exit 0**（无空白错误）。

---

## git status --short --branch

```
## docs/fix-plans-core-secondary...origin/docs/fix-plans-core-secondary
 M docs/fixes/POST_FIX_HANDOFF_PROMPT.md
 M docs/fixes/PRE_MERGE_GATES.md
 M docs/fixes/STATUS.md
 M omnigent/host/connect.py
 M omnigent/inner/loader.py
 M omnigent/runner/_entry.py
 M omnigent/runner/app.py
 M omnigent/runner/transports/ws_tunnel/serve.py
 M tests/e2e_ui/chat/test_chat_file_path_links.py
 M tests/e2e_ui/conftest.py
 M tests/host/test_connect.py
 M tests/inner/test_loader.py
 M tests/runner/transports/ws_tunnel/test_serve.py
 M tests/server/integration/test_session_mcp_servers.py
?? docs/fixes/handoffs/
?? tests/runner/test_app_codex_native_model.py
?? tests/runner/test_runner_idle_active_work.py
?? tests/runner/test_session_workspace_cache.py
```

---

## 阶段 1 测试 blob hash

```
git hash-object tests/runner/test_session_workspace_cache.py
```

结果：`02cce3ca6e28233d5d0cac350a7be6316ff582d2` ✅（与期望一致，未被修改）。

---

## test_connect.py 25 个 pre-existing Windows 失败说明

`tests/host/test_connect.py` 全套运行有 25 failed / 45 passed。全部失败均为 Windows 环境 pre-existing 问题（tilde 展开 `~` 在 Windows 不生效、login redirect mock 路径差异等），与本次 3C 修改无关。本次修改涉及的 3 个 watcher 测试（`test_watch_runner_silent_on_clean_exit`、`test_watch_runner_reports_unexpected_exit`、`test_watch_runner_silent_on_intentional_stop`）全部通过。

---

## 禁止项遵守声明

- 未执行 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 未 commit、push、merge、创建/移动 Tag、发版或编辑 PR/Issue。
- 未修改阶段 1 三个 cache 函数、阶段 1 测试（blob `02cce3ca` 已验证）、r05 文档或既有 handoff。
- 未把 PR #4 的错误嵌套兼容语义带入 #3178；采用上游 fail-loud。
- 未覆盖升级 v0.7、未创建 `runner/native/orchestration.py`、未迁移无关模块。
- 未实施 #2853 Phase 2、#2539、#2854、#2967 或其他问题。
- 未运行真实 AgentCenter smoke，不声称端到端 UI banner 已验证。
- 未声称 Gate 1/2 已执行或通过。

---

## 返工轮次 — CODEX_TASK_3_REWORK

日期：2026-07-28（同日）
任务卡：`docs/fixes/handoffs/CODEX_TASK_3_REWORK.md`

### P1 — `_entry.py`：`wait_for()` → 上游等价 `asyncio.wait()`

**问题**：Python 3.12 的 `asyncio.wait_for()` 超时后会取消并继续等待 task 实际完成取消，总等待时间可超过 timeout。上游 `23e4985` 使用 `asyncio.wait({tunnel_task}, timeout=...)`，超时只返回 pending task，再由 finally 统一取消。

**修复 diff**：

```diff
-            try:
-                await asyncio.wait_for(
-                    tunnel_task,
-                    timeout=_GRACEFUL_SHUTDOWN_TUNNEL_TIMEOUT_S,
-                )
-            except asyncio.TimeoutError:
+            _drain_done, _drain_pending = await asyncio.wait(
+                {tunnel_task},
+                timeout=_GRACEFUL_SHUTDOWN_TUNNEL_TIMEOUT_S,
+            )
+            if _drain_pending:
                 _logger.warning(
```

### P1 — `serve.py`：recv/shutdown race 对齐上游异常语义

**问题**：使用 `asyncio.ensure_future()` 而非 `create_task()`；shutdown 获胜时用 `suppress(asyncio.CancelledError, Exception)` 吞掉所有 recv 异常；recv 获胜时裸 `except Exception: raise` 未区分 `ConnectionClosedOK`。

**修复 diff**：

```diff
-        recv_task = asyncio.ensure_future(ws.recv())
-        shutdown_waiter = asyncio.ensure_future(shutdown_event.wait())
+        recv_task = asyncio.create_task(ws.recv())
+        shutdown_waiter = asyncio.create_task(shutdown_event.wait())
```

```diff
             recv_task.cancel()
-            with contextlib.suppress(asyncio.CancelledError, Exception):
+            try:
                 await recv_task
+            except asyncio.CancelledError:
+                pass  # normal cancellation — expected path
+            except WebSocketException:
+                _logger.debug(
+                    "recv settled with WebSocketException during "
+                    "shutdown race",
+                    exc_info=True,
+                )
```

```diff
         try:
             raw = recv_task.result()
-        except Exception:
-            # Connection closed or errored — let it propagate to the
-            # caller's except/finally handling.
-            raise
+        except ConnectionClosedOK:
+            # Normal close — the server hung up cleanly.
+            return
```

### P2 — `loader.py`：删除生产注释中的 issue 编号

**修复 diff**：

```diff
-        # Reject bundle-style nesting in single-file executor specs (#3178).
+        # Reject bundle-style nesting in single-file executor specs.
```

行为不变，三个定向测试仍 GREEN。

### 返工验证 — 全部命令与真实结果

**执行环境**：
- Shell：`/usr/bin/bash`（Git Bash / MSYS）
- `where.exe sh`：`C:\Program Files\Git\usr\bin\sh.exe`
- `where.exe sleep`：`C:\Program Files\Git\usr\bin\sleep.exe`
- Python：3.11.15
- pytest：9.0.3
- OS：Windows 10

**3C 定向 4 测试**：

```
PYTHONPATH="" uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

结果：**4 passed**，exit 0。

**serve 全套**：

```
PYTHONPATH="" uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py tests/runner/transports/ws_tunnel/test_serve_extended.py
```

结果：**54 passed**，exit 0。

**runner entry**：

```
PYTHONPATH="" uv run pytest -q tests/runner/test_runner_entry.py
```

结果：**69 passed**，exit 0。

**loader 定向 3 测试**：

```
PYTHONPATH="" uv run pytest -q tests/inner/test_loader.py::TestLoadFromDict::test_executor_bundle_nesting_rejected tests/inner/test_loader.py::TestLoadFromDict::test_executor_extra_keys_tolerated tests/inner/test_loader.py::TestLoadFromDict::test_tools_agent_executor_bundle_nesting_rejected
```

结果：**3 passed**，exit 0。

**loader 全套（含平台既有失败）**：

```
PYTHONPATH="" uv run pytest -q tests/inner/test_loader.py tests/spec/test_load.py
```

结果：**1 failed, 38 passed, 2 warnings**，exit 3（INTERNALERROR）。

- 失败 nodeid：`tests/inner/test_loader.py::TestLoadFromYAML::test_load_yaml_file`
- 根因：Windows 对仍打开的 `NamedTemporaryFile` 执行 `os.unlink` 返回 `WinError 32`（文件被占用），随后 pytest-unittest 插件 `pytest_runtest_makereport` 中 `call.excinfo` 为 tuple 而非 ExceptionInfo，触发 `AttributeError: 'tuple' object has no attribute 'value'` INTERNALERROR。
- 该失败位于未修改的既有测试路径，非 #3178 定向契约失败。
- 单独运行该测试（`pytest tests/inner/test_loader.py::TestLoadFromYAML::test_load_yaml_file`）通过——失败依赖测试执行顺序/文件句柄竞争。
- 未修改 `test_load_yaml_file`、pytest 插件或 Windows 测试基础设施。

**阶段 1 回归**：

```
PYTHONPATH="" uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries
```

结果：**3 passed**，exit 0。

**Ruff**：

```
PYTHONPATH="" uv run ruff check omnigent/runner/_entry.py omnigent/runner/transports/ws_tunnel/serve.py omnigent/inner/loader.py tests/runner/transports/ws_tunnel/test_serve.py
```

结果：**All checks passed!**

**git diff --check**：无输出，exit 0。

**blob hash**：

```
git hash-object tests/runner/test_session_workspace_cache.py
```

结果：`02cce3ca6e28233d5d0cac350a7be6316ff582d2` ✅

**host 全套（含平台既有失败）**：

```
PYTHONPATH="" uv run pytest -q tests/host/test_connect.py
```

结果：**25 failed, 45 passed, 42 warnings**，**exit 1**（`HOST_FULL_EXIT=1`，捕获自 `$LASTEXITCODE` / 进程退出码）。

Codex 在 Windows、Python 3.11.15、pytest 9.0.3，并将 `C:\Program Files\Git\usr\bin` 加入 `PATH`（提供 `sh.exe` / `sleep.exe`）后独立复跑同一套件，确认：`25 failed, 45 passed, 42 warnings`，`HOST_FULL_EXIT=1`。本记录与该真实退出状态一致；**不得**写成 exit 0，也**不得**把 host 全套表述为 GREEN。

失败 nodeid 列表（全部 pre-existing Windows 环境问题）：

1. `test_handle_launch_prints_exact_runner_log_path`
2. `test_handle_launch_immediate_exit_reports_exit_code_and_log_tail`
3. `test_reap_orphans_reaps_orphaned_children`
4. `test_reap_orphans_never_steals_tracked_runner_exit_code`
5. `test_handle_stat_expands_tilde`
6. `test_handle_list_dir_expands_tilde`
7. `test_handle_create_dir_parent_is_file_returns_error`
8. `test_handle_create_dir_expands_tilde`
9. `test_run_retries_on_login_redirect`
10. `test_login_redirect_prints_warning_to_terminal`
11. `test_fresh_host_fails_loud_after_persistent_login_redirects`
12. `test_login_redirect_streak_resets_on_other_transient_errors`
13. `test_connected_host_retries_login_redirects_indefinitely`
14. `test_run_fails_loud_on_permanent_4xx[401-HTTP 401]`
15. `test_run_fails_loud_on_permanent_4xx[403-HTTP 403]`
16. `test_run_fails_loud_on_permanent_4xx[404-permanent]`
17. `test_auth_rejection_suggests_omnigent_login[401]`
18. `test_auth_rejection_suggests_omnigent_login[403]`
19. `test_non_auth_permanent_4xx_omits_login_hint`
20. `test_run_reconnects_on_transient_upgrade_failure[408]`
21. `test_run_reconnects_on_transient_upgrade_failure[429]`
22. `test_run_reconnects_on_transient_upgrade_failure[500]`
23. `test_run_reconnects_on_transient_upgrade_failure[503]`
24. `test_run_host_process_exits_nonzero_on_fatal`
25. `test_run_host_process_announces_session_log_dir_on_start`

主要失败类别：Windows tilde `~` 展开不生效、login redirect mock 路径差异、`sh`/`sleep` 依赖（本环境 Git Bash 提供 `sh.exe`/`sleep.exe`，故失败数 25 而非 Codex PowerShell 环境的 36）。

**3 个 watcher 用例单独 GREEN**（同一环境）：

```
PYTHONPATH="" uv run pytest -q tests/host/test_connect.py::test_watch_runner_silent_on_clean_exit tests/host/test_connect.py::test_watch_runner_reports_unexpected_exit tests/host/test_connect.py::test_watch_runner_silent_on_intentional_stop
```

结果：**3 passed**，exit 0。

### 最终 git status

```
## docs/fix-plans-core-secondary...origin/docs/fix-plans-core-secondary
 M docs/fixes/POST_FIX_HANDOFF_PROMPT.md
 M docs/fixes/PRE_MERGE_GATES.md
 M docs/fixes/STATUS.md
 M omnigent/host/connect.py
 M omnigent/inner/loader.py
 M omnigent/runner/_entry.py
 M omnigent/runner/app.py
 M omnigent/runner/transports/ws_tunnel/serve.py
 M tests/e2e_ui/chat/test_chat_file_path_links.py
 M tests/e2e_ui/conftest.py
 M tests/host/test_connect.py
 M tests/inner/test_loader.py
 M tests/runner/transports/ws_tunnel/test_serve.py
 M tests/server/integration/test_session_mcp_servers.py
?? docs/fixes/handoffs/
?? tests/runner/test_app_codex_native_model.py
?? tests/runner/test_runner_idle_active_work.py
?? tests/runner/test_session_workspace_cache.py
```

### 返工禁止项遵守声明

- 未执行 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 未 commit、push、merge、创建/移动 Tag、发版或编辑 PR/Issue。
- 未修改允许文件范围外的任何源码、测试、fixture、r05 文档、阶段 1 结果或既有任务卡。
- 未修改 `test_load_yaml_file`、pytest 插件或 Windows 测试基础设施。
- 未声称 Gate 1/2 已执行或通过。
- 未声称 loader/host 全套 GREEN。平台既有失败按真实非零退出码记录：
  - **loader 全套：`exit 3`**（INTERNALERROR；1 failed, 38 passed, 2 warnings）
  - **host 全套：`exit 1`**（`HOST_FULL_EXIT=1`；25 failed, 45 passed, 42 warnings）
  - 两者均**未**冒充 GREEN；定向 watcher 3 passed（exit 0）与全套非零退出不矛盾。

---

## 返工轮次 2 — CODEX_TASK_3_REWORK_2（Grok 文档纠错）

日期：2026-07-28（同日）
任务卡：`docs/fixes/handoffs/CODEX_TASK_3_REWORK_2.md`
执行者：Grok（用户授权；仅改本交接报告，未跑测试、未改源码）

### 纠正内容

| 项 | 纠正前（错误） | 纠正后（事实） |
|----|----------------|----------------|
| host 全套退出码 | `exit 0` | **`exit 1` / `HOST_FULL_EXIT=1`** |
| 错误说明 | 「pytest 不因既有失败返回非零」 | **已删除**；pytest 在 25 failed 时返回非零 |
| 计数 | 25 failed / 45 passed / 42 warnings | **不变**（与 Codex 复跑一致） |
| loader 全套 | exit 3 已记录 | **保留**；与 host 一并在总结中标明未冒充 GREEN |

### 总结（exit 码，均未冒充 GREEN）

| 套件 | 结果摘要 | 退出码 | 是否 GREEN |
|------|----------|--------|------------|
| loader 全套 `tests/inner/test_loader.py tests/spec/test_load.py` | 1 failed, 38 passed, 2 warnings | **loader exit 3** | **否** |
| host 全套 `tests/host/test_connect.py` | 25 failed, 45 passed, 42 warnings | **host exit 1**（`HOST_FULL_EXIT=1`） | **否** |
| host watcher 定向 3 用例 | 3 passed | exit 0 | 定向 GREEN only |

**Gate 1 / Gate 2：仍未执行、未判定。** 本轮不声称阶段 3 已获 approve、可 merge。

### REWORK_2 禁止项遵守

- 仅修改 `docs/fixes/handoffs/HERMES_COMPLETION_3.md`。
- 未运行 pytest / Ruff / 构建 / 集成测试 / Gate。
- 未修改 `omnigent/`、`tests/`、fixture、r05、既有任务卡；未创建 `CODEX_TASK_4.md` / `GROK_REVIEW_4.md`。
- 未 commit / push / merge / tag。
