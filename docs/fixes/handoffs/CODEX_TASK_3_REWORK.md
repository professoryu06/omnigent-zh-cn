# CODEX TASK 3 REWORK — 上游回移验收缺口

**执行者：** Hermes（Qwen3.8，唯一开发者）

**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**结论：** 阶段 3 暂未验收；不得进入阶段 4，不得 commit/push/merge/tag

## 1. 必须修复的实现问题

### P1 — idle tunnel 等待未保持上游的有界语义

当前 `omnigent/runner/_entry.py` 使用：

```python
await asyncio.wait_for(
    tunnel_task,
    timeout=_GRACEFUL_SHUTDOWN_TUNNEL_TIMEOUT_S,
)
```

Python 3.12 的 `asyncio.wait_for()` 超时后会取消并继续等待 task 实际完成取消，总等待时间可以超过 timeout；这不满足任务卡“最多 15 秒等待 graceful drain，然后进入 finally backstop”的要求。上游 #3060 merge commit `23e498521f88fb9145512a7449f6fa603ce9ee11` 使用 `asyncio.wait({tunnel_task}, timeout=...)`，超时只返回 pending task，再由 finally 统一取消。

最小修复：

- 把该分支改成上游等价的 `asyncio.wait({tunnel_task}, timeout=...)`。
- 不在此处用 `wait_for()`，不提前取消 tunnel task。
- 保持 signal/parent-death 的 `stop_event` 路径、finally 清理和 15 秒常量不变。

### P1 — graceful recv loop 与上游最终异常语义不一致

当前 `omnigent/runner/transports/ws_tunnel/serve.py::_recv_loop_with_shutdown()` 使用 `asyncio.ensure_future()`，并在 shutdown 获胜时用 `suppress(asyncio.CancelledError, Exception)` 吞掉所有 recv 异常。

按上游 `23e4985` 收敛：

- 使用 `asyncio.create_task()`。
- shutdown 获胜时：
  - `CancelledError` 视为正常取消；
  - 同 tick 已发生的 `WebSocketException` 记录 debug（含 `exc_info=True`），不得用裸 `Exception` 全吞；
  - 然后继续 graceful drain。
- recv 获胜时单独把 `ConnectionClosedOK` 当正常 close；其他异常保持既有上抛/重连语义。
- 不改变 auth refresh、close-code 分类、frame dispatch 或 terminal channel 清理。

### P2 — 生产注释违反仓库规范

`omnigent/inner/loader.py` 新增注释含 `(#3178)`。仓库 `AGENTS.md` 禁止在源码注释中引用 PR/Issue 编号。

最小修复：删除编号，只描述“bundle-style nesting in single-file executor specs”的场景；错误行为和测试断言不变。

## 2. 验收证据缺口

### 2.1 loader 全套不能写成已通过

`HERMES_COMPLETION_3.md` 只记录了三个定向 loader 测试和 `tests/spec/test_load.py`，没有记录任务卡要求的完整命令：

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/inner/test_loader.py tests/spec/test_load.py
```

Codex 在当前 PowerShell/Windows 环境复跑得到 exit 3：`TestLoadFromYAML::test_load_yaml_file` 因 Windows 对仍打开的 `NamedTemporaryFile` 执行 `os.unlink` 返回 `WinError 32`，随后 pytest 插件产生 internal error。该失败位于未修改的既有测试路径，不是 #3178 定向契约失败，但报告必须如实记录，不能省略或称全套 GREEN。

返工要求：

- 重跑并记录完整命令、环境、退出码、首个失败 nodeid 和 `WinError 32` 根因。
- 三个 #3178 定向测试仍必须 GREEN。
- 不得顺手修改 `test_load_yaml_file`、pytest 插件或 Windows 测试基础设施。

### 2.2 host 全套缺少可审计的同环境说明

Hermes 报告为 `25 failed / 45 passed`；Codex 在当前 PowerShell 环境复跑为 `36 failed / 34 passed`，主要差异来自 `sh`/`sleep` 不在 PATH、Windows tilde/path 行为和既有连接 mock。说明失败数依赖执行 shell，不能仅写“全部 pre-existing”而不列环境。

返工要求：

- 记录实际执行 shell、`where.exe sh`、`where.exe sleep`、Python/pytest 版本及完整命令。
- 重新记录 full-suite summary 和失败 nodeid 列表。
- 单独证明以下三个 watcher 用例在同一个具备 `sh`/`sleep` 的环境 GREEN：
  - `test_watch_runner_silent_on_clean_exit`
  - `test_watch_runner_reports_unexpected_exit`
  - `test_watch_runner_silent_on_intentional_stop`
- 不得为了让 Windows 全套变绿而跨范围重写 host 测试或实现。

## 3. 允许修改的文件

仅允许修改：

1. `omnigent/runner/_entry.py`
2. `omnigent/runner/transports/ws_tunnel/serve.py`
3. `omnigent/inner/loader.py`（只删除 issue 编号）
4. `tests/runner/transports/ws_tunnel/test_serve.py`（仅当对齐上游异常语义需要调整既有阶段 3 测试）
5. `docs/fixes/handoffs/HERMES_COMPLETION_3.md`（补充返工 diff 与证据）

不得修改其他源码、测试、fixture、r05 文档、阶段 1 结果或既有任务卡。

## 4. 必跑验证

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py tests/runner/transports/ws_tunnel/test_serve_extended.py
uv run pytest -q tests/runner/test_runner_entry.py
uv run pytest -q tests/inner/test_loader.py::TestLoadFromDict::test_executor_bundle_nesting_rejected tests/inner/test_loader.py::TestLoadFromDict::test_executor_extra_keys_tolerated tests/inner/test_loader.py::TestLoadFromDict::test_tools_agent_executor_bundle_nesting_rejected
uv run pytest -q tests/inner/test_loader.py tests/spec/test_load.py
uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries
uv run ruff check omnigent/runner/_entry.py omnigent/runner/transports/ws_tunnel/serve.py omnigent/inner/loader.py tests/runner/transports/ws_tunnel/test_serve.py
git diff --check
git hash-object tests/runner/test_session_workspace_cache.py
git status --short --branch
```

对平台既有失败必须记录为非零，不得伪写 GREEN。阶段 1 测试 blob 仍必须是 `02cce3ca6e28233d5d0cac350a7be6316ff582d2`。

## 5. 完成标准

1. `_entry.py` 使用上游等价 `asyncio.wait()`，不再用 `wait_for()` 等待 graceful tunnel task。
2. recv/shutdown race 使用 `create_task()`；异常分支不再裸吞所有 `Exception`，并正确区分 `ConnectionClosedOK`。
3. loader 生产注释不含 issue/PR 编号，行为不变。
4. 阶段 3 定向测试、serve 全套、runner entry、阶段 1 回归、Ruff、`git diff --check` 通过。
5. loader/host 平台全套结果按实际退出码记录；既有 Windows 失败有环境与 nodeid 证据，不冒充 GREEN。
6. `HERMES_COMPLETION_3.md` 新增“返工轮次”章节，列出修复 diff、全部命令和真实结果。
7. 无 checkout/fetch/rebase/cherry-pick/commit/push/merge/tag；Gate 1 / Gate 2 仍为未执行、未判定。

返工报告交回 Codex 验收后，才决定是否生成 `CODEX_TASK_4.md` 交给 Grok。
