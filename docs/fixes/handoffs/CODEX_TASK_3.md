# CODEX TASK 3 — 回移上游 #3175 / #3178 / #3060

**执行者：** Hermes（Qwen3.8，唯一开发者）

**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**阶段边界：** 仅阶段 3；把三项已合入上游 v0.7 的语义适配到当前 `0.6.0.dev0+zhcn.1` 二开，不开始阶段 4 审查

**阶段 2 记录：** Grok 结论为 `approve`；P0/P1 无，必须修改项无。该结论只允许进入阶段 3，不批准 merge；阶段 1 不返工。

## 1. 官方上游依据

只以以下官方 GitHub PR/commit 为语义来源：

1. #3175：`https://github.com/omnigent-ai/omnigent/pull/3175`
   - 上游源提交：`a8433fb7cfb7e7e07d74f28b7a277cd7a7bce1a4`
   - 上游 merge commit：`131db6276b6c7670195d8346fd03070e01b71d2d`
2. #3178：`https://github.com/omnigent-ai/omnigent/pull/3178`
   - loader 提交：`e4fdfb0c13887e3ebcff0fd644c2d7fb71c38880`
   - fixture 迁移提交：`0c30cadf9bbf03befd6ff7d90d0f43b891cfa337`
   - 上游 merge commit：`af3d18ba16bb777ff3229b2d8d814e732f64a427`
3. #3060：`https://github.com/omnigent-ai/omnigent/pull/3060`
   - 上游 merge commit：`23e498521f88fb9145512a7449f6fa603ce9ee11`

允许使用 `gh pr view` / `gh api` / `git show` 做只读核对。不得 `git fetch`、新增 remote、cherry-pick 或整文件覆盖；当前二开与上游 v0.7 文件布局不同，必须做语义回移。

## 2. 开始前基线保护

先记录但不要清理：

```powershell
git status --short --branch
git rev-parse HEAD
git diff --stat
git diff -- omnigent/runner/app.py
git hash-object tests/runner/test_session_workspace_cache.py
```

必须保持：

- HEAD 为 `dc83140c73ceb12fa165753c1880c19f68da86f4`，不切分支。
- 阶段 1 的 `omnigent/runner/app.py` 三处 workspace cache 修复原样保留。
- `tests/runner/test_session_workspace_cache.py` blob 仍为 `02cce3ca6e28233d5d0cac350a7be6316ff582d2`。
- r05 三份文档和既有 handoff 原样保留。
- Grok 的 P2 docstring 建议不是阶段 3 必改项；不得借机返工阶段 1。

## 3. 精确文件范围

阶段 3 只允许修改或创建以下文件。

### 3.1 生产代码

1. `omnigent/runner/app.py`
   - `_codex_native_model_from_spec()`（当前约第 4813 行，#3175）
   - `_has_active_work()` 后新增 session stream drain hook（当前约第 8058 行，#3060）
   - 不得改阶段 1 的 `_session_workspace_value()`、`_ensure_session_registered()`、`_clear_session_agent_caches()`
2. `omnigent/inner/loader.py`
   - `_parse_executor_spec()`（当前约第 613 行，#3178）
3. `omnigent/host/connect.py`
   - `_watch_runner()`（当前约第 1192 行，#3060）
4. `omnigent/runner/_entry.py`
   - graceful tunnel timeout 常量及 `_run_tunnel_from_env()` 的 idle shutdown 编排（#3060）
5. `omnigent/runner/transports/ws_tunnel/serve.py`
   - `serve_tunnel()`、`_serve_tunnel_once()`、新增 `_graceful_drain()` 及相关常量/import（#3060）

### 3.2 测试与 fixture

6. 创建 `tests/runner/test_app_codex_native_model.py`
7. 修改 `tests/inner/test_loader.py`
8. 修改 `tests/e2e_ui/chat/test_chat_file_path_links.py`
9. 修改 `tests/e2e_ui/conftest.py`
10. 修改 `tests/server/integration/test_session_mcp_servers.py`
11. 修改 `tests/host/test_connect.py`
12. 创建 `tests/runner/test_runner_idle_active_work.py`
13. 修改 `tests/runner/transports/ws_tunnel/test_serve.py`
14. 完成后创建 `docs/fixes/handoffs/HERMES_COMPLETION_3.md`

不得修改依赖、lockfile、CI、STATUS、PRE_MERGE_GATES、POST_FIX、阶段 1 测试或其他 handoff。

## 4. 3A — #3175 codex-native model 读取

### 4.1 RED

先创建 `tests/runner/test_app_codex_native_model.py`，按上游 `a8433fb` 覆盖以下精确行为：

- `executor.model="gpt-5.4-mini"` 返回该值。
- `databricks-gpt-5-4-mini` 原样通过。
- `None` / 空字符串返回 `None`。
- canonical `executor.model` 缺失时回退 `executor.config["model"]`。
- 两处同时存在时 canonical 字段优先。
- 非字符串 config model 被忽略。
- `None` spec 返回 `None`。
- `ResolvedSpec` 正确解包。

生产代码未改前运行：

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/runner/test_app_codex_native_model.py
```

预期至少 canonical-field、canonical-wins 和 ResolvedSpec canonical 用例真实 FAIL；记录命令、非零退出码和具体断言。若全部通过，停止 3A 并报告基线已变化。

### 4.2 最小改法

上游 v0.7 函数位于 `omnigent/runner/native/orchestration.py`，但当前二开对应函数仍在 `omnigent/runner/app.py`；不得创建缺失的上游模块。

仅修改当前 `_codex_native_model_from_spec()`：

1. 解包 `ResolvedSpec`。
2. 优先返回非空字符串 `spec.executor.model`。
3. canonical 缺失/空时，回退非空字符串 `spec.executor.config.get("model")`。
4. 其他输入返回 `None`；不改两个现有调用点。

### 4.3 GREEN

```powershell
uv run pytest -q tests/runner/test_app_codex_native_model.py
uv run pytest -q tests/runner/test_app_codex_native_model.py tests/runner/test_app_claude_native_model.py tests/runner/test_app_cursor_native_model.py tests/runner/test_codex_native_launch_config.py
```

## 5. 3B — #3178 单文件 executor 嵌套 fail-loud

### 5.1 RED

先在 `TestLoadFromDict` 中加入上游三个测试：

- `test_executor_bundle_nesting_rejected`
- `test_executor_extra_keys_tolerated`
- `test_tools_agent_executor_bundle_nesting_rejected`

精确契约：

- 单文件 YAML/dict 中 `executor.type` 和/或 `executor.config` 必须抛 `ValueError`。
- 错误消息必须指出这些键属于 bundle `config.yaml` 格式，并展示扁平示例 `executor: {harness: codex-native, model: gpt-5.4-mini}`。
- inline AgentTool 的 executor 走相同拒绝逻辑。
- 其他 compat raw keys（至少 `use_responses`）仍可加载，不能改成“拒绝所有未知键”。

生产代码未改前运行：

```powershell
uv run pytest -q tests/inner/test_loader.py::TestLoadFromDict::test_executor_bundle_nesting_rejected tests/inner/test_loader.py::TestLoadFromDict::test_executor_extra_keys_tolerated tests/inner/test_loader.py::TestLoadFromDict::test_tools_agent_executor_bundle_nesting_rejected
```

预期两个 rejection 测试真实 FAIL（没有抛异常），extra-keys 测试 PASS。记录每项结果；不得为了全红而破坏 extra-keys 正向保护。

### 5.2 最小改法

在 `_parse_executor_spec()` 的 dict 分支最前面：

1. 只收集 `("config", "type")` 中实际出现的键并排序。
2. 非空时抛出上游等价 `ValueError` 和扁平拼写提示。
3. 其余解析逻辑、`auth`、`model/harness/profile` 和 compat extra keys 保持原样。

不得采用 PR #4 的“兼容并吸收错误嵌套”长期语义；阶段 3 必须采用上游 fail-loud。

### 5.3 迁移恰好六处 compat 单文件 fixture

把以下 `executor.config.harness: openai-agents` 改为扁平 `executor.harness: openai-agents`：

- `tests/e2e_ui/chat/test_chat_file_path_links.py`：1 处 `_agent_bundle` YAML。
- `tests/e2e_ui/conftest.py`：4 处 `_TEST_AGENT_YAML`、`_FILES_PROBE_NO_ENV_AGENT_YAML`、`_FILES_PROBE_ENV_AGENT_YAML`、`_TERMINAL_AGENT_YAML`。
- `tests/server/integration/test_session_mcp_servers.py`：1 处 single YAML bundle。

必须保留 `tests/e2e_ui/conftest.py` 中两个严格 `spec_version: 1` / `config.yaml` fixture 的嵌套：

- `_APPROVAL_AGENT_YAML`
- `_CUSTOM_AGENT_YAML`

不得机械替换仓库中所有 `executor.config`；严格 bundle 与直接构造 `ExecutorSpec` 的嵌套仍合法。

### 5.4 GREEN

```powershell
uv run pytest -q tests/inner/test_loader.py::TestLoadFromDict::test_executor_bundle_nesting_rejected tests/inner/test_loader.py::TestLoadFromDict::test_executor_extra_keys_tolerated tests/inner/test_loader.py::TestLoadFromDict::test_tools_agent_executor_bundle_nesting_rejected
uv run pytest -q tests/inner/test_loader.py tests/spec/test_load.py
uv run pytest -q tests/server/integration/test_session_mcp_servers.py
```

再用 `rg` 报告六处已扁平化及两个 strict fixture 仍嵌套；不得把未运行的浏览器 E2E 写成已通过。

## 6. 3C — #3060 idle runner 安静退出

### 6.1 RED：先加六个上游回归测试

1. `tests/host/test_connect.py`
   - 新增 `test_watch_runner_silent_on_clean_exit`。
   - runner 仍在 `_runners` 中但进程以 code 0 结束时，不发送 `host.runner_exited`，也不进入 `_unreported_exits`。
   - 既有 non-zero unexpected exit 与 intentional stop 测试必须保留。
2. 创建最小 `tests/runner/test_runner_idle_active_work.py`
   - 只移植本阶段需要的 `_scaffold_app()` helper 和 `test_drain_session_streams_enqueues_done_sentinel`，不要顺手复制与当前阶段无关的整套上游 active-work 测试。
   - 两个 `_session_event_queues_ref` 队列调用 drain hook 后各收到且只收到一个 `None` sentinel，并在 finally 清理全局队列。
3. `tests/runner/transports/ws_tunnel/test_serve.py`
   - `test_graceful_drain_fires_hook_and_awaits_inflight_task`
   - `test_graceful_drain_bounded_when_task_never_finishes`
   - `test_serve_tunnel_once_graceful_shutdown_returns_and_closes`
   - `test_serve_tunnel_stops_reconnecting_after_graceful_shutdown`
   - 按上游为本文件现有 `_serve_once` stubs 增加 `**_kwargs: Any`，只解决新增可选参数的测试兼容性。

在改生产代码前分别运行并保留 RED：

```powershell
uv run pytest -q tests/host/test_connect.py::test_watch_runner_silent_on_clean_exit
uv run pytest -q tests/runner/test_runner_idle_active_work.py::test_drain_session_streams_enqueues_done_sentinel
uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

预期分别暴露：code 0 仍被报告；app 没有 drain hook；serve 模块缺少 graceful drain/shutdown 参数或仍重连。记录命令、退出码与关键失败，不得先改实现再补写 RED。

### 6.2 最小改法：host 路径

`omnigent/host/connect.py::_watch_runner()` 在确认 handle 仍被跟踪后：

- `returncode == 0` 记录普通 info 并直接返回，不发送 crash report。
- 非零退出继续执行现有 `_runner_exit_error()` 与 `_report_runner_exit()`。
- intentional stop 的现有提前返回保持不变。

### 6.3 最小改法：session stream drain

在 `omnigent/runner/app.py` 的 `app.state.has_active_work` 赋值之后增加同步 hook：

- 对 `list(_session_event_queues.values())` 快照逐个 `put_nowait(None)`。
- 暴露为 `app.state.drain_session_streams`。
- 不改 event generator、单 session delete 或阶段 1 cache 函数。

### 6.4 最小改法：WebSocket graceful drain

在 `omnigent/runner/transports/ws_tunnel/serve.py` 按上游 `23e4985` 的契约适配：

- 引入 `ConnectionClosedOK`。
- graceful close timeout = 5 秒；dispatch drain timeout = 5 秒；普通 reconnect close timeout 仍为 0.25 秒。
- `serve_tunnel()` 新增可选 `shutdown_event` 与 `on_graceful_shutdown`；event 在连接前/连接后已 set 时直接返回，不再重连。
- `_serve_tunnel_once()` 在有 shutdown event 时 race `ws.recv()` 与 event；event 获胜时取消并 settle recv、调用 `_graceful_drain()` 后正常返回。
- clean close 保持安静；异常 close 仍走既有错误/重连语义。
- `_graceful_drain()` 先调用 hook，再有界等待所有 dispatch task；超时任务留给既有 finally 的 `_cancel_dispatch_tasks()`，不能让 shutdown 永久卡住。
- hook 异常只记录，不阻止退出；保留上游同 tick 最后一帧可能丢弃的明确注释。
- 不改变 tunneled terminal channel 的既有取消语义、auth refresh、close-code 分类或 frame 协议。

### 6.5 最小改法：idle entry 编排

当前 v0.6 的 `_entry.py` 没有上游后续 `_record_exit_reason` 结构，禁止为套 patch 引入无关重构。只适配本地现有控制流：

- 新增 `_GRACEFUL_SHUTDOWN_TUNNEL_TIMEOUT_S = 15.0`。
- 为 idle reaper 创建独立 `tunnel_shutdown_event`，传给 `serve_tunnel()`，并传 `app.state.drain_session_streams` hook。
- idle monitor 的 `request_shutdown` 只 set tunnel shutdown event；signal/parent-death 仍走现有 `stop_event` 快速终止路径。
- idle task 完成且 graceful event 已 set 时，有界等待 tunnel task 最多 15 秒，再进入既有 finally backstop。
- tunnel 自发结束、signal、parent death 和异常退出行为不得被静默化。

### 6.6 GREEN

先跑新增用例：

```powershell
uv run pytest -q tests/host/test_connect.py::test_watch_runner_silent_on_clean_exit tests/host/test_connect.py::test_watch_runner_reports_unexpected_exit tests/host/test_connect.py::test_watch_runner_silent_on_intentional_stop
uv run pytest -q tests/runner/test_runner_idle_active_work.py
uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

再跑受影响套件：

```powershell
uv run pytest -q tests/host/test_connect.py
uv run pytest -q tests/runner/test_runner_entry.py
uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py tests/runner/transports/ws_tunnel/test_serve_extended.py
```

这些只验证组件契约；不运行真实 AgentCenter smoke，不得声称端到端 UI banner 已验证。

## 7. 阶段 1 回归、Ruff 与最终检查

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries
uv run ruff check omnigent/runner/app.py omnigent/inner/loader.py omnigent/host/connect.py omnigent/runner/_entry.py omnigent/runner/transports/ws_tunnel/serve.py tests/runner/test_app_codex_native_model.py tests/inner/test_loader.py tests/e2e_ui/chat/test_chat_file_path_links.py tests/e2e_ui/conftest.py tests/server/integration/test_session_mcp_servers.py tests/host/test_connect.py tests/runner/test_runner_idle_active_work.py tests/runner/transports/ws_tunnel/test_serve.py
git diff --check
git status --short --branch
```

最后确认阶段 1 测试 blob 未变：

```powershell
git hash-object tests/runner/test_session_workspace_cache.py
```

期望仍为 `02cce3ca6e28233d5d0cac350a7be6316ff582d2`。

## 8. 禁止项

- 不得 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean 或整文件覆盖。
- 不得 commit、push、merge、创建/移动 Tag、发版或编辑 PR/Issue。
- 不得修改阶段 1 三个 cache 函数、阶段 1 测试、r05 文档或既有 handoff。
- 不得把 PR #4 的错误嵌套兼容语义带入 #3178；本阶段采用上游 fail-loud。
- 不得直接覆盖升级 v0.7、创建 `runner/native/orchestration.py` 或顺手迁移无关模块。
- 不得实施 #2853 Phase 2、#2539、#2854、#2967 或其他问题。
- 不得引入依赖、调整 websockets 版本、修改密钥/账号/模型凭据。
- 不得声称阶段 2 approve 等于可 merge。
- 不得声称 Gate 1 / Gate 2 已执行、已判定或已通过。

## 9. 完成标准

仅当以下全部满足，Hermes 才可报告阶段 3 完成：

1. 3A、3B、3C 均有实现前真实 RED：命令、非零退出码、关键失败齐全。
2. #3175 canonical model 优先、config fallback 与边界用例全部 GREEN。
3. #3178 只拒绝单文件 `type/config` 嵌套；extra keys 仍兼容；六处 compat fixture 已扁平化，两个 strict fixture 保持嵌套。
4. #3060 的 code-0 host 静默、stream sentinel、graceful bounded drain、正常 close 和停止重连全部 GREEN；non-zero crash 仍报告。
5. 所有定向/受影响套件、阶段 1 回归、目标 Ruff 与 `git diff --check` 通过；未运行项必须诚实列出。
6. 只改第 3 节允许文件；阶段 1 app hunks和测试 blob、r05 文档、Grok 报告均保持原样。
7. 创建 `docs/fixes/handoffs/HERMES_COMPLETION_3.md`，逐项记录：
   - 三个上游来源与本地适配位置；
   - 初始 HEAD/status；
   - 3A/3B/3C RED 与 GREEN 命令、退出码、结果；
   - 精确文件和关键 diff；
   - fixture 迁移/保留清单；
   - 风险、未运行项、未完成项；
   - 最终 `git status --short --branch`。
8. 报告明确写明：无 commit/push/merge/tag；Gate 1 / Gate 2 **未由本阶段执行或判定**；阶段 3 结果只供阶段 4 Grok 审查。

Hermes 交付后，Codex 只验收 `HERMES_COMPLETION_3.md` 及其报告证据；不自行修源码。
