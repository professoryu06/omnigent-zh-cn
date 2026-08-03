# HERMES_COMPLETION_5 — #2853 Phase 2: codex-native system prompt apply

日期：2026-07-28
分支：`docs/fix-plans-core-secondary`（HEAD `dc83140c73ceb12fa165753c1880c19f68da86f4`，未 commit）
工作树：`F:\codex-ai\git项目部署\tmp\omnigent-review`

---

## 初始保护检查

| 项 | 值 |
|---|---|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| 阶段 1 workspace 测试 blob | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` |
| 阶段 3 model 测试 blob | `be43ec45816e8ece4192822506df8072580910e0` |
| 阶段 3 idle 测试 blob | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` |
| 阶段 3 serve 测试 blob | `6116218097f2352c467524fd0ddf0838315aa524` |
| PR #5 Phase 1 ref | `1f42a898fbd07e358f87de5cba391a93af1f43b9` |

---

## Phase 1 — fail-loud 语义移植

### RED 1

```
PYTHONPATH="" uv run pytest -q tests/inner/test_native_system_prompt_delivery.py
```

结果：**1 error**（collection error），exit 1。
原因：`ModuleNotFoundError: No module named 'omnigent.inner.native_prompt_delivery'`。

### FIX 1

1. 创建 `omnigent/inner/native_prompt_delivery.py`：
   - `PromptDeliveryMode = Literal["apply", "warn", "error"]`
   - `NATIVE_PROMPT_CAPABILITY_MATRIX`：11 个 harness，仅 `codex-native` 为 `apply`，其余 10 个为 `warn`
   - `strict_prompt_enabled()`：读 `OMNIGENT_STRICT_PROMPT` 环境变量
   - `note_native_system_prompt()`：非空 prompt + `applied=False` → warning（只含 `chars=N`）；strict 时抛 `ValueError`
   - prompt 正文不进入 log/exception/receipt

2. 在 11 个 executor 入口接线（`del tools, system_prompt` 前插入 try/except）：
   - `claude_native_executor.py`、`cursor_native_executor.py`、`goose_native_executor.py`、`hermes_native_executor.py`、`kimi_native_executor.py`、`kiro_native_executor.py`、`pi_native_executor.py`、`qwen_native_executor.py`、`antigravity_native_executor.py`、`codex_native_executor.py`、`native_server_harness.py`

### GREEN 1

```
PYTHONPATH="" uv run pytest -q tests/inner/test_native_system_prompt_delivery.py
```

结果：**6 passed**，exit 0。

---

## Phase 2 — codex-native safe apply

### RED 2

```
PYTHONPATH="" uv run pytest -q tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
```

结果：**1 error**（collection error），exit 1。
原因：`ImportError: cannot import name 'read_prompt_receipt' from 'omnigent.inner.native_prompt_delivery'`。

### FIX 2

1. **`native_prompt_delivery.py`** 扩展 receipt API：
   - `write_prompt_receipt()`：写 `prompt_delivery.receipt.json`（只含 harness_id/channel/chars/sha256，无正文）；空 prompt 不写；写前清理旧 receipt
   - `read_prompt_receipt()`：缺失/损坏返回 None，不抛异常
   - `receipt_matches_prompt()`：SHA-256 精确匹配

2. **`codex_native_app_server.py`**：
   - 新增 `_upsert_developer_instructions()`：symlink materialize → JSON 编码 → 顶层 `developer_instructions` 写入 → best-effort 0600
   - `CodexNativeAppServer` 新增 `developer_instructions` 字段
   - `start()` 中 model pin 后调用 upsert + 写 receipt
   - `build_codex_native_server()` 新增 `developer_instructions` 参数并传递

3. **`runner/app.py`**：
   - 新增 `_codex_native_developer_instructions()`：从 AgentSpec/ResolvedSpec 提取 instructions，None/空白/非字符串 → None
   - `_auto_create_codex_terminal()` 中仅当 `external_session_id is None`（fresh thread）时传给 builder

4. **`codex_native_executor.py`**：
   - 不再无条件 `applied=False`
   - 读 bridge dir receipt，用 `receipt_matches_prompt()` 做 digest 匹配
   - 匹配时 `applied=True`；不匹配/缺失/resume 保持 `applied=False`（Phase 1 warn/error）
   - strict mismatch 在任何 RPC 前返回 sole `ExecutorError`

### GREEN 2

```
PYTHONPATH="" uv run pytest -q tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
```

结果：**16 passed**，exit 0。

---

## 受影响套件

```
PYTHONPATH="" uv run pytest -q tests/inner/test_native_system_prompt_delivery.py tests/inner/test_claude_native_executor.py tests/inner/test_codex_native_executor.py
```

结果：**36 passed**，exit 0。

```
PYTHONPATH="" uv run pytest -q tests/test_codex_native_app_server.py tests/inner/test_codex_native_executor.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
```

结果：**57 passed**，exit 0。

---

## 阶段 1/3 保护回归

```
PYTHONPATH="" uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries tests/runner/test_app_codex_native_model.py tests/runner/test_runner_idle_active_work.py tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

结果：**17 passed**，exit 0。

---

## Ruff

```
PYTHONPATH="" uv run ruff check --fix <19 files>
```

结果：18 auto-fixed（unused imports），0 remaining。

## git diff --check

结果：无输出，exit 0。

## 保护 blob hash（最终）

| 文件 | Hash |
|---|---|
| `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` ✅ |
| `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` ✅ |
| `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` ✅ |
| `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` ✅ |

---

## Capability Matrix

| Harness | 策略 | 通道 |
|---|---|---|
| `codex-native` | **apply**（仅 fresh thread） | 私有 `CODEX_HOME/config.toml` 顶层 `developer_instructions` + digest receipt |
| `claude-native` | warn / strict error | 无安全通道（argv 不安全） |
| `cursor-native` | warn / strict error | 无已证实安全通道 |
| `hermes-native` | warn / strict error | 无已证实安全通道 |
| `opencode-native` | warn / strict error | session-init apply 未证实 |
| `goose-native` | warn / strict error | 无已证实安全通道 |
| `kimi-native` | warn / strict error | 无已证实安全通道 |
| `kiro-native` | warn / strict error | 无已证实安全通道 |
| `qwen-native` | warn / strict error | 无已证实安全通道 |
| `antigravity-native` | warn / strict error | 无已证实安全通道 |
| `pi-native` | warn / strict error | 无已证实安全通道 |

---

## Prompt 正文无泄漏检查

- receipt 文件只含 `harness_id`/`channel`/`chars`/`sha256`，测试断言 `SENTINEL not in raw`
- `note_native_system_prompt()` 日志只含 `chars=N`，测试断言 sentinel 不出现在 caplog
- `build_codex_native_server` 的 `config_overrides`（argv）和 `env` 不含 sentinel（测试断言）
- executor 不拼接 prompt 到 user input

## Fresh/Resume 边界

- `_auto_create_codex_terminal` 仅当 `external_session_id is None` 时传 `developer_instructions`
- resume/fork 路径传 `None`，不写 receipt，executor 保持 Phase 1 warn/error

## 可选真实 CLI smoke

**未运行**。本机无可用 Codex 认证配置，不满足任务卡 §10 条件。不阻塞 deterministic channel tests。

## Grok §9 阶段 3 信心复跑

**未执行**（可选项，非阶段 5 强制）。

---

## 最终 git status

```
## docs/fix-plans-core-secondary...origin/docs/fix-plans-core-secondary
 M docs/fixes/POST_FIX_HANDOFF_PROMPT.md
 M docs/fixes/PRE_MERGE_GATES.md
 M docs/fixes/STATUS.md
 M omnigent/codex_native_app_server.py
 M omnigent/host/connect.py
 M omnigent/inner/antigravity_native_executor.py
 M omnigent/inner/claude_native_executor.py
 M omnigent/inner/codex_native_executor.py
 M omnigent/inner/cursor_native_executor.py
 M omnigent/inner/goose_native_executor.py
 M omnigent/inner/hermes_native_executor.py
 M omnigent/inner/kimi_native_executor.py
 M omnigent/inner/kiro_native_executor.py
 M omnigent/inner/loader.py
 M omnigent/inner/pi_native_executor.py
 M omnigent/inner/qwen_native_executor.py
 M omnigent/native_server_harness.py
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
?? omnigent/inner/native_prompt_delivery.py
?? tests/inner/test_codex_native_system_prompt_apply.py
?? tests/inner/test_native_system_prompt_delivery.py
?? tests/runner/test_app_codex_native_model.py
?? tests/runner/test_app_codex_native_prompt_delivery.py
?? tests/runner/test_runner_idle_active_work.py
?? tests/runner/test_session_workspace_cache.py
```

---

## 风险与未完成项

- 真实 AgentCenter E2E **未验证**（Gate 2 未执行）
- 其余 10 个 native harness 的 prompt **未送达**，仅 fail-loud 保护
- 可选真实 CLI smoke 未运行（无认证）
- `codex-native` apply 仅覆盖 fresh thread；resume/fork 保持 warn/error

---

## 禁止项遵守声明

- 未执行 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean
- 未 commit/push/merge/tag、发版或编辑 PR/Issue
- 未通过 argv/环境变量/日志/exception/receipt/user message 暴露 prompt 正文
- 未把 system prompt 拼进首条用户消息或 turn/start.input
- 未为 Claude/Cursor/Hermes/OpenCode/Goose/Kimi/Kiro/Qwen/Antigravity/Pi 发明 apply 通道
- 未改阶段 1 cache 函数、阶段 3 实现或测试（四个 blob 已验证）
- 未修改 r05 文档、STATUS.md、PRE_MERGE_GATES.md、POST_FIX_HANDOFF_PROMPT.md 或既有 handoff
- 未声称 #2853 对全部 native harness 完整 fixed
- 未声称阶段 4 approve 等于可 merge
- Gate 1 / Gate 2 **仍未执行、未判定**
