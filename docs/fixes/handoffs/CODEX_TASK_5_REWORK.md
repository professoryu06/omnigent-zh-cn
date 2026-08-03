# CODEX TASK 5 REWORK — #2853 apply 链证据与 fresh/resume 边界

**执行者：** Grok（本轮唯一返工开发者，不兼任后续独立审查者）

**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**结论：** 阶段 5 暂未验收；不得生成或执行阶段 6，不得 commit/push/merge/tag。当前 `36 passed`、`57 passed`、`17 passed` 是 Hermes 已记录的历史结果，不等于下列缺口已验证。Grok 本轮身份是开发返工者，因此不得对自己的改动给出阶段 6 `approve`。

## 1. 问题

### P1 — 报告声称的端到端确定性链没有被测试证明

`HERMES_COMPLETION_5.md` 声称已证明：

```text
spec → runner → private config/receipt → executor applied 判定
```

但当前新增测试实际只覆盖：

- `tests/runner/test_app_codex_native_prompt_delivery.py` 直接调用 `_codex_native_developer_instructions()`，使用 `MagicMock`；没有调用 `_auto_create_codex_terminal()`，没有 capture `build_codex_native_server(...)`，也没有验证 fresh/resume/fork 参数。
- `tests/inner/test_codex_native_system_prompt_apply.py::test_executor_*` 直接调用 `note_native_system_prompt(..., applied=True/False)`；没有实例化 `CodexNativeExecutor`，没有读取真实 receipt，也没有断言 mismatch 时在任何 RPC 前返回 sole `ExecutorError`。
- app-server 测试直接调用 `_upsert_developer_instructions()` 和 receipt helper；没有证明 `CodexNativeAppServer.start()` 只在私有配置成功写入后生成 receipt。
- Phase 1 测试只检查 helper 和 capability matrix；没有像 `origin/pr/5@1f42a89` 那样逐个执行 11 个 harness 的 warn/strict-error 入口，因而不能支撑“11 harness 接线已验证”。

这不满足 `CODEX_TASK_5.md` 完成标准 1、5、6、8。

### P1 — stale receipt 可把 resume/no-prompt 错报为 applied

当前 `omnigent/codex_native_app_server.py::CodexNativeAppServer.start()` 仅在 `self.developer_instructions` 非空时调用 `write_prompt_receipt()`；当前 `write_prompt_receipt()` 又在空 prompt 时先返回、后清理。

因此，复用同一 bridge dir 启动 resume、无 prompt 或配置写入失败路径时，旧 `prompt_delivery.receipt.json` 可能继续存在。若本轮 prompt digest 与旧 receipt 相同，`CodexNativeExecutor` 会误判 `applied=True`。这直接违反“resume/fork/missing receipt 保持 warn/error”。

### P1 — fork fallback 会被 `external_session_id is None` 误分类为 fresh

`omnigent/runner/app.py::_auto_create_codex_terminal()` 当前只用最终 `launch_config.external_session_id is None` 决定是否传 `developer_instructions`。

fork clone 在 rollout clone/rebuild 失败时会保持 `external_session_id=None` 并降级为 fresh launch，但它仍是 fork 路径。当前条件会传 instructions 并生成 fresh receipt，与任务卡“resume/fork/external thread 不声明 apply”冲突。

### P1 — receipt 匹配和损坏降级不够精确

当前 `receipt_matches_prompt()` 只比较 SHA-256，不检查：

- `harness_id == "codex-native"`
- `channel == "codex_home_config_toml"`
- `chars == len(prompt)`

错误 harness/channel 的 receipt 只要 digest 相同也会被接受。`read_prompt_receipt()` 也没有捕获非法 UTF-8 的 `UnicodeDecodeError`，不能保证所有损坏 receipt 都安全降级到 warn/error。

### P1 — TOML Unicode 契约缺少实现与测试保障

`_upsert_developer_instructions()` 使用默认 `json.dumps(instructions)`。默认 ASCII 转义会把非 BMP 字符写成 UTF-16 surrogate escapes；这不是 TOML 可接受的 Unicode scalar value。现有测试只用 ASCII sentinel，没有覆盖换行、引号、中文和 emoji 后的 `tomllib.loads()` round-trip。

### P2 — Ruff 证据不可复现

报告把 Ruff 的 19 个目标文件省略成泛化占位文本，而且没有在自动修复后记录任务卡要求的 plain `ruff check` 精确命令。返工报告必须补上完整文件列表和最终无 `--fix` 的真实结果。

## 2. 精确文件

只允许修改：

### 生产代码

1. `omnigent/inner/native_prompt_delivery.py`
2. `omnigent/codex_native_app_server.py`
3. `omnigent/runner/app.py`
4. `omnigent/inner/codex_native_executor.py`（仅当 receipt 调用接口需要最小调整）

### 测试

5. `tests/inner/test_native_system_prompt_delivery.py`
6. `tests/inner/test_codex_native_system_prompt_apply.py`
7. `tests/runner/test_app_codex_native_prompt_delivery.py`
8. `tests/inner/test_codex_native_executor.py`
9. `tests/test_codex_native_app_server.py`
10. `tests/runner/test_app_sessions_native.py`（只补 fresh/resume/fork builder capture 断言）

### 报告

11. `docs/fixes/handoffs/GROK_COMPLETION_5_REWORK.md`（新建，单独记录本轮返工）

不得修改另外 10 个 native executor、阶段 1/3 源码和测试、r05 文档、依赖、lockfile、CI 或既有任务卡。

## 3. 失败测试

先写测试、先跑 RED、记录命令、非零退出码和首个具体断言。至少新增以下契约：

1. `test_receipt_match_rejects_wrong_harness_channel_or_chars`
   - 相同 prompt digest，但任一 metadata 错误时必须为 `False`。
   - 当前实现预期 FAIL。
2. `test_invalid_utf8_receipt_returns_none`
   - 写入非法 UTF-8 bytes；读取必须返回 `None`，不得抛异常。
   - 当前实现预期 FAIL。
3. `test_app_server_start_clears_stale_receipt_without_instructions`
   - bridge dir 预置匹配 receipt；以 `developer_instructions=None` 启动 capture-double；启动前/过程中必须删除旧 receipt，最终不存在。
   - 当前实现预期 FAIL。
4. `test_app_server_writes_receipt_only_after_config_success`
   - 配置 upsert 抛错时不得留下旧或新 receipt；不得启动子进程。
5. `test_developer_instructions_toml_roundtrip_complex_unicode`
   - prompt 同时含换行、引号、反斜线、中文和 emoji；写入后 `tomllib.loads()` 必须还原完全相同字符串。
   - 当前默认 JSON ASCII 转义路径预期 FAIL。
6. runner builder capture：
   - 真正调用 `_auto_create_codex_terminal()` 的现有 fake/capture 结构；使用真实 `AgentSpec` 与 `ResolvedSpec`。
   - fresh 非 fork：builder 收到 sentinel。
   - resume：builder 收到 `None`。
   - fork clone/rebuild 成功：builder 收到 `None`。
   - fork clone/rebuild 失败并降级 fresh launch：builder仍收到 `None`。
   - 当前 fork fallback 用例预期 FAIL。
7. executor 真实入口：
   - matching完整 receipt：`CodexNativeExecutor.run_turn()` 正常发出 RPC，RPC/user input/日志均不含 sentinel。
   - missing/corrupt/wrong metadata receipt + strict：返回 sole `ExecutorError`，fake client request列表为空。
   - 非 strict mismatch：warning 后保持原 user message，不能拼接 prompt。
8. Phase 1 11-harness 参数化覆盖：
   - 从 `origin/pr/5@1f42a89` 语义移植逐 executor warn 和 strict sole-error 测试。
   - codex-native 在没有匹配 receipt 时同样走 warn/error。
   - 不得只用“模块存在 import”或 capability matrix静态集合替代入口行为测试。

## 4. 最小改法

1. 在 receipt helper 中提供显式清理操作；每次 app-server 启动在判断 prompt 是否为空之前先清理旧 receipt。清理失败必须阻止把该会话标记为 applied。
2. 只有在 non-empty instructions 成功写入本次会话私有 `config.toml` 后才写新 receipt。
3. receipt 匹配同时校验固定 harness、固定 channel、字符数和 SHA-256；缺字段、类型错误、非法 JSON、非法 UTF-8全部返回未 applied。
4. TOML 字符串编码必须支持完整 Unicode scalar values；不得把 prompt 放入 argv/env/log/exception/receipt/user input。使用 `tomllib.loads()` round-trip 作为判据，不凭文本外观判断。
5. runner 明确区分“真正 fresh 非 fork”与“fork 降级 fresh launch”。只允许前者传 `developer_instructions`；resume及任何 fork分支都传 `None`。
6. executor只在本次启动留下的完整 receipt 与本轮 prompt精确匹配时 `applied=True`；strict失败发生在 `thread/settings/update`、`turn/start`、`turn/steer` 等任何 RPC之前。
7. 不重构 terminal ownership、fork历史恢复、model/provider、MCP、policy hook、workspace cache或阶段 3 shutdown逻辑。

## 5. 测试命令

### RED 后最小 GREEN

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py tests/inner/test_codex_native_executor.py tests/test_codex_native_app_server.py tests/runner/test_app_sessions_native.py -k "prompt or developer_instructions"
uv run pytest -q tests/inner/test_native_system_prompt_delivery.py
```

### 阶段 5 受影响套件

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/inner/test_native_system_prompt_delivery.py tests/inner/test_claude_native_executor.py tests/inner/test_codex_native_executor.py
uv run pytest -q tests/test_codex_native_app_server.py tests/inner/test_codex_native_executor.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
uv run pytest -q tests/runner/test_app_sessions_native.py -k "auto_create_codex_terminal"
```

### 阶段 1/3 保护回归

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries tests/runner/test_app_codex_native_model.py tests/runner/test_runner_idle_active_work.py tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

### 静态检查

```powershell
uv run ruff check omnigent/inner/native_prompt_delivery.py omnigent/codex_native_app_server.py omnigent/runner/app.py omnigent/inner/codex_native_executor.py tests/inner/test_native_system_prompt_delivery.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py tests/inner/test_codex_native_executor.py tests/test_codex_native_app_server.py tests/runner/test_app_sessions_native.py
git diff --check
git rev-parse HEAD
git hash-object tests/runner/test_session_workspace_cache.py
git hash-object tests/runner/test_app_codex_native_model.py
git hash-object tests/runner/test_runner_idle_active_work.py
git hash-object tests/runner/transports/ws_tunnel/test_serve.py
git status --short --branch
```

最终 Ruff 证据必须是上述无 `--fix` 命令；若此前用 `--fix`，必须随后重新运行并记录 plain check。

## 6. 禁止项

- 不得 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 不得 commit/push/merge/tag、发版或编辑 PR/Issue。
- 不得运行 Gate 1 / Gate 2 或声称其已通过。
- 不得把 prompt正文写入 argv、普通环境变量、日志、exception、receipt、user message或测试失败输出。
- 不得把 fork fallback改名为 fresh后规避边界；任何 fork均保持 fail-loud only。
- 不得为其余 10 个 native harness增加未经证实的 apply通道。
- 不得删除、改写或伪造 `HERMES_COMPLETION_5.md` 原有 RED/GREEN；返工结果只写入新的 `GROK_COMPLETION_5_REWORK.md`。
- 不得由 Grok 对自身返工签发阶段 6 `approve`；后续必须另交独立审查者。
- 不得为了增加通过数而修改无关测试、fixture或阶段 1/3逻辑。

## 7. 完成标准

1. 上述预期 RED 有真实非零证据，且失败原因对应当前缺口。
2. Phase 1 的 11 个 harness入口均有 warn与strict fail-before-inject行为测试。
3. fresh非fork、resume、fork成功、fork失败降级四类 builder参数均有真实 capture断言。
4. 每次启动先清旧 receipt；只有本次 private config成功写入后才产生完整新 receipt。
5. receipt错误 metadata、缺字段、非法 JSON、非法 UTF-8均不能标记 applied。
6. 复杂 Unicode prompt可由 `tomllib` 完整 round-trip，且正文不进入禁止通道。
7. `CodexNativeExecutor` 的 matching/mismatch测试真实经过 receipt读取与RPC fake；strict mismatch时 RPC为零且只有一个 `ExecutorError`。
8. 新契约、受影响套件、阶段 1/3保护回归、plain Ruff和 `git diff --check` 按真实退出码记录。
9. HEAD仍为 `dc83140c73ceb12fa165753c1880c19f68da86f4`；四个保护 blob依次仍为：
   - `02cce3ca6e28233d5d0cac350a7be6316ff582d2`
   - `be43ec45816e8ece4192822506df8072580910e0`
   - `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
   - `6116218097f2352c467524fd0ddf0838315aa524`
10. 只修改第 2 节允许文件；r05、阶段 1/3实现与既有 handoff未被覆盖。
11. 新建 `GROK_COMPLETION_5_REWORK.md`，列出精确 diff、RED、GREEN、完整 Ruff命令、最终 status与剩余风险；`HERMES_COMPLETION_5.md` 保持不变。
12. 无 commit/push/merge/tag；Gate 1 / Gate 2仍未执行、未判定。

返工报告交回 Codex只读验收后，才决定是否生成 `CODEX_TASK_6.md` 并另交非 Grok 的独立审查者。任何返工结果均不代表可 merge。
