# CODEX TASK 5 — #2853 Phase 2：codex-native 真实 system prompt apply

**执行者：** Hermes（Qwen3.8，唯一开发者）

**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**阶段边界：** 仅阶段 5。先把 PR #5 的 Phase 1 fail-loud 契约语义移植到当前累积工作树，再为 `codex-native` 实现首个安全、可审计的 `apply` 通道。其他 native harness 继续 `warn` / strict `error`，不得冒充已送达。

## 1. 阶段 4 结论记录与问题

Grok 阶段 4 结论：`approve`。

- #3175 / #3178 / #3060：均可接受。
- P0：无；P1：无；必须修改项：无。
- 不强制阶段 3 返工。
- `approve` 只允许进入阶段 5，不代表可 merge。
- Grok 阶段 4 未运行测试。
- Gate 1 / Gate 2 仍未执行、未判定。

当前工作树未包含 PR #5 `origin/pr/5@1f42a898fbd07e358f87de5cba391a93af1f43b9` 的 Phase 1 代码：`native_prompt_delivery.py` 不存在，native executor 仍直接丢弃 `system_prompt`。阶段 5 必须在保留阶段 1/3 累积 diff 的前提下语义移植 Phase 1，禁止整文件覆盖或 cherry-pick。

#2853 Phase 2 的真实目标不是把 prompt 拼到首条用户消息，也不是把 fail-loud warning 改名为“已送达”。本阶段只把 `codex-native` 定义为 `apply` 目标：把 agent-spec `instructions` 写入每会话私有 `CODEX_HOME/config.toml` 的顶层 `developer_instructions`，并用不含正文的 delivery receipt 证明 executor 收到的 prompt 与启动通道一致。

本机 `codex-cli 0.142.5`；当前代码已为每个 native Codex session 创建私有 `CODEX_HOME` 并在启动 app-server 前写 `config.toml`。Codex 官方配置契约说明 `developer_instructions` 会作为独立 developer-role message 注入；官方源：

- `https://github.com/openai/codex/blob/main/codex-rs/config/src/config_toml.rs`
- `https://github.com/openai/codex/blob/main/codex-rs/core/src/config/mod.rs`

`claude-native` 本机只明确暴露 prompt argv 参数；敏感角色 prompt 不得放入进程列表可读 argv。本阶段不为 Claude 或其他 TUI 发明不安全通道。

## 2. 目标 harness 能力矩阵

Phase 1 覆盖的 11 个 harness 必须进入可执行矩阵：

| Harness | 阶段 5 策略 | 通道 / 原因 |
| --- | --- | --- |
| `codex-native` | `apply`（仅 fresh thread） | 私有 `CODEX_HOME/config.toml` 顶层 `developer_instructions` + digest receipt |
| `claude-native` | `warn` / strict `error` | 已知通道是 argv；本阶段判为不安全，不 apply |
| `cursor-native` | `warn` / strict `error` | 无已证实安全 system channel |
| `hermes-native` | `warn` / strict `error` | 无已证实安全 system channel |
| `opencode-native`（`NativeServerHarness`） | `warn` / strict `error` | session-init apply 未在当前契约证实 |
| `goose-native` | `warn` / strict `error` | 无已证实安全 system channel |
| `kimi-native` | `warn` / strict `error` | 无已证实安全 system channel |
| `kiro-native` | `warn` / strict `error` | 无已证实安全 system channel |
| `qwen-native` | `warn` / strict `error` | 无已证实安全 system channel |
| `antigravity-native` | `warn` / strict `error` | 无已证实安全 system channel |
| `pi-native` | `warn` / strict `error` | 当前 native executor 仍无已证实 system channel；不要与非-native `pi` harness 混淆 |

`codex-native` 的 apply 只覆盖由当前 runner 创建的 fresh native Codex thread。已有 external thread 的 resume/fork 不得仅因 config 文件被写入就声称 prompt 已进入既有上下文；没有 fresh receipt 时必须保留 Phase 1 warn/error。

## 3. 精确文件范围

### 3.1 Phase 1 语义移植

允许创建：

1. `omnigent/inner/native_prompt_delivery.py`
2. `tests/inner/test_native_system_prompt_delivery.py`

允许最小修改以下 Phase 1 接线文件：

3. `omnigent/inner/antigravity_native_executor.py`
4. `omnigent/inner/claude_native_executor.py`
5. `omnigent/inner/codex_native_executor.py`
6. `omnigent/inner/cursor_native_executor.py`
7. `omnigent/inner/goose_native_executor.py`
8. `omnigent/inner/hermes_native_executor.py`
9. `omnigent/inner/kimi_native_executor.py`
10. `omnigent/inner/kiro_native_executor.py`
11. `omnigent/inner/pi_native_executor.py`
12. `omnigent/inner/qwen_native_executor.py`
13. `omnigent/native_server_harness.py`

PR #5 只能作为语义来源；不得整文件复制覆盖当前版本。当前代码在 PR #5 后已有大量 native bridge 变化，必须只移植 `note_native_system_prompt()` 接线和测试契约。

### 3.2 Phase 2 codex-native apply

允许最小修改：

14. `omnigent/codex_native_app_server.py`
15. `omnigent/runner/app.py`

允许创建：

16. `tests/inner/test_codex_native_system_prompt_apply.py`
17. `tests/runner/test_app_codex_native_prompt_delivery.py`

必要时可在不改变既有断言语义的前提下最小修改：

18. `tests/inner/test_codex_native_executor.py`
19. `tests/test_codex_native_app_server.py`

完成后创建：

20. `docs/fixes/handoffs/HERMES_COMPLETION_5.md`

不得修改其他源码、测试、依赖、lockfile、CI、r05 文档、阶段 1/3 测试或既有 handoff。

## 4. 开始前保护检查

只记录，不清理工作树：

```powershell
git status --short --branch
git rev-parse HEAD
git diff --stat
git hash-object tests/runner/test_session_workspace_cache.py
git hash-object tests/runner/test_app_codex_native_model.py
git hash-object tests/runner/test_runner_idle_active_work.py
git hash-object tests/runner/transports/ws_tunnel/test_serve.py
git rev-parse origin/pr/5
```

保护值：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- 阶段 1 workspace 测试：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- 阶段 3 model 测试：`be43ec45816e8ece4192822506df8072580910e0`
- 阶段 3 idle 测试：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- 阶段 3 serve 测试：`6116218097f2352c467524fd0ddf0838315aa524`
- PR #5 Phase 1 ref：`1f42a898fbd07e358f87de5cba391a93af1f43b9`

不得切换分支或清理阶段 1/3/r05/handoff 累积改动。

## 5. 失败测试 RED 1 — Phase 1 不再静默丢弃

先从 `origin/pr/5` 的测试契约语义创建 `tests/inner/test_native_system_prompt_delivery.py`，但暂不创建 helper、不改生产代码。

测试必须覆盖：

- helper 对非空、未 apply 的 prompt 发 warning，日志只含 `chars=N`，不含正文。
- `OMNIGENT_STRICT_PROMPT=1` 时在用户消息注入前产生 `ExecutorError`。
- 空 prompt 不 warning。
- applied path 不 warning、不 strict-error。
- 上表 11 个 harness 全部接入同一 helper；unsupported harness 为 warn/error。

使用唯一 sentinel，例如：

```text
OMNIGENT_PROMPT_SENTINEL_C2853_PHASE2_7f3a9c
```

生产代码未改时运行：

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/inner/test_native_system_prompt_delivery.py
```

预期真实 RED：至少因 `omnigent.inner.native_prompt_delivery` 不存在而 collection error，或因 native executor 未接线而断言失败。记录命令、非零退出码和首个具体错误；不得先复制 Phase 1 实现再伪造 RED。

## 6. 最小改法 1 — 语义移植 Phase 1

以 `origin/pr/5@1f42a89` 为语义来源，创建共享 helper并在 11 个 harness入口调用：

1. `PromptDeliveryMode = Literal["apply", "warn", "error"]`。
2. `OMNIGENT_STRICT_PROMPT` 仅接受既有 truthy 集合。
3. 非空 prompt + `applied=False`：warning；strict 时抛 `ValueError`，各 executor 转为 sole `ExecutorError` 后立即返回。
4. prompt 正文不得进入 log、exception、receipt、状态文档或测试失败消息。
5. 非 Codex native harness全部 `applied=False`。
6. helper 中加入完整 11 项 capability matrix；矩阵不得把未证实 harness 标为 apply。

不得改变各 executor 的消息抽取、附件、锁、steering、model、tool、resume 或 terminal 语义。

## 7. 失败测试 RED 2 — codex-native safe apply

在任何 Phase 2 生产改动前创建：

- `tests/inner/test_codex_native_system_prompt_apply.py`
- `tests/runner/test_app_codex_native_prompt_delivery.py`

必须包含以下确定性 capture-double 断言：

1. **spec → runner：** `AgentSpec.instructions=SENTINEL` 经 `ResolvedSpec`/普通 spec 解析后，被传给 `build_codex_native_server(..., developer_instructions=...)`；`None` / 空白不传。
2. **private config channel：** app-server 启动前把 sentinel 写入每会话私有 `codex_home/config.toml` 顶层 `developer_instructions`；共享/符号链接源 config 原样不变。
3. **不走 argv/user message：** app-server argv、terminal args、`turn/start.input` 都不含 sentinel。
4. **receipt：** fresh thread 成功写私有 config 后，在 bridge dir 写只含 `harness_id`、channel、`chars`、SHA-256 digest 的 receipt；文件和日志不含正文。
5. **executor核对：** `CodexNativeExecutor.run_turn()` 仅当 receipt digest 与本轮 `system_prompt` 匹配时调用 `note_native_system_prompt(..., applied=True)`；无 receipt、digest 不同、resume/fork 路径均保持 warn/error。
6. **strict applied：** `OMNIGENT_STRICT_PROMPT=1` 对匹配 receipt 不报错并继续正常 `turn/start`；不匹配时在注入前 sole `ExecutorError`。
7. **无重复/污染：** 多轮相同 prompt 不追加到 user input；空 prompt 不生成 receipt。

运行 RED：

```powershell
uv run pytest -q tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
```

预期真实 FAIL：当前 app-server builder/runner没有 `developer_instructions` 通道，executor也没有 receipt apply 判定。记录非零退出码和关键断言。

## 8. 最小改法 2 — fresh codex-native 配置通道

### 8.1 `native_prompt_delivery.py`

在 Phase 1 helper上增加最小 receipt API：

- receipt 文件位于 per-session bridge dir，名称固定且不导出正文。
- 写入前先清理旧 receipt；只在 non-empty prompt 已成功写入私有 Codex config 后写 fresh receipt。
- receipt 保存 SHA-256 digest、字符数、`harness_id="codex-native"`、channel标识；不得保存 prompt。
- 提供精确匹配函数供 executor调用；损坏/缺失 receipt 返回未 apply，不抛出导致静默跳过。

### 8.2 `codex_native_app_server.py`

最小扩展 `CodexNativeAppServer` / `build_codex_native_server()`：

- 新增 `developer_instructions: str | None` 参数/字段。
- app-server process 启动前，在 `_populate_codex_home_config()`、MCP config注入和 model pin 的同一私有 config生命周期中 upsert顶层 `developer_instructions`。
- 使用 TOML/JSON安全字符串编码支持换行、引号和 Unicode。
- 与 `_pin_codex_config_model()` 相同，先 materialize symlink，绝不修改用户共享 `~/.codex/config.toml`。
- private `CODEX_HOME` 保持目录 0700；含 prompt 的 config在 POSIX 尽力设为 0600。
- 配置写成功后才写 receipt；失败必须阻止 fresh native session启动，不能记录 applied。
- prompt 正文不得出现在 logger、exception、argv、环境变量或 receipt。

### 8.3 `runner/app.py`

新增一个小型 spec helper，语义为：

```text
ResolvedSpec → spec.instructions
AgentSpec → instructions
None / 非字符串 / 全空白 → None
```

在 `_auto_create_codex_terminal()` 中：

- 仅当 `launch_config.external_session_id is None`（fresh thread）时把 non-empty instructions 传给 app-server builder。
- resume/fork/external thread 不写 fresh receipt，不宣称 apply，继续由 Phase 1 warn/error保护。
- 不改 `_codex_native_model_from_spec()`、workspace cache、stream drain、terminal ownership、model/provider、MCP 或 policy hook逻辑。

### 8.4 `codex_native_executor.py`

- 不再无条件 `del system_prompt`。
- 在读取到 bridge state后，用 bridge dir receipt 与 `system_prompt` 做 digest 匹配。
- 匹配时 `note_native_system_prompt("codex-native", system_prompt, applied=True)`；不匹配时 `applied=False`。
- strict mismatch 必须在任何 `thread/settings/update`、`turn/start`、`turn/steer` 之前返回 sole `ExecutorError`。
- user input保持原样；不得前缀/拼接 prompt；不得把正文放入 JSON-RPC user input。

## 9. 测试命令：GREEN 与受影响套件

先跑新契约：

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/inner/test_native_system_prompt_delivery.py
uv run pytest -q tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
```

再跑 Phase 1/目标 harness受影响套件：

```powershell
uv run pytest -q tests/inner/test_native_system_prompt_delivery.py tests/inner/test_claude_native_executor.py tests/inner/test_codex_native_executor.py
uv run pytest -q tests/test_codex_native_app_server.py tests/inner/test_codex_native_executor.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
```

再保护阶段 1/3：

```powershell
uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries
uv run pytest -q tests/runner/test_app_codex_native_model.py
uv run pytest -q tests/runner/test_runner_idle_active_work.py
uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

目标 Ruff：

```powershell
uv run ruff check omnigent/inner/native_prompt_delivery.py omnigent/inner/antigravity_native_executor.py omnigent/inner/claude_native_executor.py omnigent/inner/codex_native_executor.py omnigent/inner/cursor_native_executor.py omnigent/inner/goose_native_executor.py omnigent/inner/hermes_native_executor.py omnigent/inner/kimi_native_executor.py omnigent/inner/kiro_native_executor.py omnigent/inner/pi_native_executor.py omnigent/inner/qwen_native_executor.py omnigent/native_server_harness.py omnigent/codex_native_app_server.py omnigent/runner/app.py tests/inner/test_native_system_prompt_delivery.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py tests/inner/test_codex_native_executor.py tests/test_codex_native_app_server.py
git diff --check
```

不得把 skipped real-CLI test、模型碰巧遵循 sentinel、warning消失或 capture-double以外的随机回复当成 prompt delivery证明。

## 10. 可选真实 CLI 信心证据（不是 Gate 2）

只有在本机已有可用 Codex认证且不需要修改凭据时，Hermes可以追加一次真实 native Codex smoke。必须同时满足：

- 使用测试 agent的非敏感 sentinel prompt。
- 通过 Codex rollout/app-server可审计输入证明 developer instruction进入上下文；模型回复仅作辅助，不能是唯一断言。
- 保存命令、Codex版本、非零/零退出码和脱敏证据位置。
- 不得把该 smoke称为 AgentCenter C/E/R Gate 2。

环境不满足时写“未运行”，不阻塞阶段 5 的 deterministic channel tests，也不得编造。

Grok §9 的阶段 3信心复跑为可选，不是阶段 5 开始前强制项。若执行，必须单独标为历史修复信心复验，不得改写 Gate状态。

## 11. 禁止项

- 不得 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean或整文件覆盖。
- 不得 commit/push/merge/tag、发版或编辑 PR/Issue。
- 不得通过 argv、环境变量、日志、exception、receipt或user message暴露 prompt正文。
- 不得把 system prompt拼进首条用户消息、`turn/start.input` 或 steering message后声称 system delivery。
- 不得为 Claude/Cursor/Hermes/OpenCode/Goose/Kimi/Kiro/Qwen/Antigravity/Pi 发明未证实 apply通道。
- 不得把 Phase 1 warning、strict error或 capture失败当成成功送达。
- 不得改阶段 1 cache函数、阶段 3 #3175/#3178/#3060实现或测试。
- 不得修改 r05 文档、`STATUS.md`、`PRE_MERGE_GATES.md`、`POST_FIX_HANDOFF_PROMPT.md` 或既有 handoff。
- 不得声称 #2853 对全部 native harness完整 fixed；本阶段仅 `codex-native fresh` 为 apply目标。
- 不得声称阶段 4 approve等于可 merge。
- 不得声称 Gate 1 / Gate 2 已执行、已判定或已通过。

若实现只能依赖不安全 argv、只能靠模型随机输出断言、无法区分 fresh/resume receipt，或必须重构 native terminal ownership，停止 Phase 2实现并在报告中写明阻塞；不得用降级语义冒充完成。

## 12. 完成标准

仅当以下全部满足，Hermes才可报告阶段 5 完成：

1. Phase 1 有真实 RED，11 个 native harness 全部进入共享 fail-loud helper和可执行 capability matrix。
2. Phase 2 有真实 RED，证明当前 runner/app-server/executor没有 codex-native安全 apply通道。
3. fresh `codex-native` 的 non-empty agent instructions写入私有 `CODEX_HOME/config.toml` 顶层 `developer_instructions`，不进入 argv/env/log/user input。
4. delivery receipt只含 metadata/digest，无正文；executor仅在 digest匹配时标记 applied。
5. strict applied正常继续；missing/mismatch/resume路径在注入前保持 Phase 1 warn/error。
6. deterministic capture tests证明 spec → runner → private config/receipt → executor判定链；不依赖模型随机回复。
7. 其余 10 个 native harness继续 warn/error，报告不得称其 prompt已送达。
8. 新测试、受影响套件、阶段 1/3保护回归、目标 Ruff和 `git diff --check` 按实际结果记录。
9. HEAD和四个保护 blob不变；r05、阶段 1/3结果和既有 handoff未被覆盖。
10. 只修改第 3 节允许文件并创建 `HERMES_COMPLETION_5.md`。
11. 报告区分：`codex-native fresh apply verified`、`其他 native fail-loud only`、`真实 AgentCenter E2E未验证`。
12. 无 commit/push/merge/tag；Gate 1 / Gate 2仍未执行、未判定。

`HERMES_COMPLETION_5.md` 必须逐项记录：初始 HEAD/status、Phase 1/2 RED命令和失败、最小 diff、capability matrix、所有 GREEN命令与真实退出码、prompt正文无泄漏检查、fresh/resume边界、可选 smoke是否运行、保护 hash、最终 status、风险和未完成项。

Hermes交付后，Codex只验收报告与证据；通过后才生成阶段 6 Grok审查卡。阶段 5结果不代表可 merge。
