# HERMES REVIEW 6 — 独立审查阶段 5 #2853 累计实现

**审查者：** Hermes（独立审查者；未参与 Grok 阶段 5 返工）
**日期：** 2026-07-28
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
**分支：** `docs/fix-plans-core-secondary`（HEAD `dc83140c73ceb12fa165753c1880c19f68da86f4`）

---

## 1. 结论

**`approve`**

阶段 5 累计实现（Hermes 初始 + Grok 返工）满足任务卡契约：Phase 1 fail-loud 覆盖 11 harness，Phase 2 仅 codex-native fresh 非 fork 通过私有 config.toml + digest receipt 标记 applied。Prompt 正文不进入 argv/env/log/exception/receipt/user message。阶段 1/3 保护完整。

明确边界：
- 本结论 **不** 批准 merge / push / tag / 发版。
- **Gate 1 Linux 全仓 pytest：未执行、未判定。**
- **Gate 2 AgentCenter C/E/R smoke：未执行、未判定。**
- 定向 GREEN 仅是定向证据，不等于 Gate 1 或 Gate 2。
- 其余 10 个 native harness 的 prompt **未送达**，仅 fail-loud 保护。

---

## 2. P0 / P1 / P2

### P0（阻断）

无。

### P1（必须修改）

无。

### P2（可接受剩余风险）

1. **Grok 返工缺少实际 pre-fix RED 退出码**：`GROK_COMPLETION_5_REWORK.md` §3 列出了 8 项静态根因，明确写"未伪造 RED 退出码"和"最终记录以 GREEN 实测为准"。返工在同一开发会话内完成测试补齐与修复，没有逐项保存 pre-fix 非零退出码。这是证据完整性限制，不是正确性问题——测试存在且通过，实现经独立静态审查确认正确。评级 P2：不阻断 approve，但后续审计应注明此限制。

2. **真实 Codex CLI smoke 未运行**：本机无可用认证，不满足 §10 条件。不阻塞 deterministic channel tests。

3. **`HERMES_COMPLETION_5.md` 中"端到端确定性链已证明"措辞过宽**：Grok 返工报告 §8.6 已标注此问题。以返工报告与新测试为准。

---

## 3. Phase 1 — 11 harness fail-loud

### 3.1 Capability matrix

`NATIVE_PROMPT_CAPABILITY_MATRIX` 恰好 11 项，仅 `codex-native` 为 `"apply"`，其余 10 个为 `"warn"`。✅

### 3.2 入口接线

独立 grep 确认 11 个文件均在 `del tools, system_prompt` 前调用 `note_native_system_prompt(..., applied=False)`（codex-native 为 `applied=_applied`）：

| 文件 | 行号 | harness_id |
|---|---|---|
| claude_native_executor.py | 125 | `"claude-native"` |
| cursor_native_executor.py | 89 | `"cursor-native"` |
| goose_native_executor.py | 83 | `"goose-native"` |
| hermes_native_executor.py | 84 | `"hermes-native"` |
| kimi_native_executor.py | 87 | `"kimi-native"` |
| kiro_native_executor.py | 61 | `"kiro-native"` |
| pi_native_executor.py | 97 | `"pi-native"` |
| qwen_native_executor.py | 126 | `"qwen-native"` |
| antigravity_native_executor.py | 230 | `"antigravity-native"` |
| codex_native_executor.py | 212 | `"codex-native"` |
| native_server_harness.py | 133 | `self._harness_id` |

所有入口在用户消息注入前执行；strict 时 `ValueError` → sole `ExecutorError` → return。✅

### 3.3 日志安全

`note_native_system_prompt()` 只输出 `chars=N`，不插值 prompt 正文。测试 `_assert_logs_never_contain_sentinel` 断言 sentinel 不出现在 caplog。✅

### 3.4 无伪 apply

10 个 non-codex harness 均硬编码 `applied=False`，无新增 argv 或通道。✅

---

## 4. Receipt 与 app-server

### 4.1 Stale receipt 清理

`CodexNativeAppServer.start()` 第 589 行无条件调用 `clear_prompt_receipt(self.bridge_dir)`，在 apply 判定前执行。Resume/no-prompt 不会继承旧 receipt。✅

### 4.2 Receipt 写入时序

`write_prompt_receipt()` 仅在 `_upsert_developer_instructions()` 成功后调用（第 597-602 行）。Config upsert 失败（异常）→ 无 receipt → executor 保持 warn/error。✅

### 4.3 Receipt 内容

只含 `harness_id`/`channel`/`chars`/`sha256`。测试断言 `SENTINEL not in raw`。✅

### 4.4 Matcher 四项校验

`receipt_matches_prompt()` 校验 harness_id == `"codex-native"`、channel == `"codex_home_config_toml"`、chars == len(prompt)、sha256 精确匹配。缺字段/错误类型/非法 JSON/非法 UTF-8 均返回 False。✅

### 4.5 Symlink materialization

`_upsert_developer_instructions()` 与 `_pin_codex_config_model()` 相同模式：`is_symlink()` → resolve → unlink → copy2。不修改用户共享 config。✅

### 4.6 Unicode

`json.dumps(instructions)` 用于 TOML 值编码（Grok 返工改为 `ensure_ascii=False`）；`tomllib.loads` round-trip 测试覆盖复杂 Unicode。✅

---

## 5. Runner fresh/resume/fork 边界

### 5.1 Fork 判定

```python
is_fork_launch = bool(
    launch_config.fork_source_id
    or launch_config.fork_source_external_id
    or launch_config.fork_carry_history
)
```

第 3498-3502 行。✅

### 5.2 Builder 传参

```python
developer_instructions=(
    _codex_native_developer_instructions(agent_spec)
    if (launch_config.external_session_id is None and not is_fork_launch)
    else None
),
```

第 3740-3747 行。Fresh 非 fork 传 instructions；resume 传 None；fork（含失败降级）传 None。✅

### 5.3 Builder capture 测试

`tests/runner/test_app_sessions_native.py -k "auto_create_codex_terminal"` 独立运行 8 passed，覆盖 fresh/resume/fork 成功/fork fallback。✅

---

## 6. Executor RPC 契约

### 6.1 Receipt 匹配 → applied

`codex_native_executor.py` 第 209-212 行：读 receipt → `receipt_matches_prompt` → `applied=_applied`。匹配时正常走 `turn/start`/steer。✅

### 6.2 Strict mismatch → sole ExecutorError

`note_native_system_prompt` 在 strict + non-empty + `applied=False` 时抛 `ValueError`，executor 捕获后 yield sole `ExecutorError` 并 return，在任何 RPC 前。✅

### 6.3 Non-strict mismatch → warn + 原 user message

不拼接 prompt，不修改 user input。✅

### 6.4 不改变既有语义

Model/effort overrides、active turn、steering、attachment、MCP startup、bridge lock 均未被 receipt 逻辑触及。✅

---

## 7. Prompt 正文泄漏面审计

| 通道 | 审计结果 |
|---|---|
| argv / config_overrides | 测试断言 sentinel 不在 `server.config_overrides` ✅ |
| 环境变量 | 测试断言 sentinel 不在 `server.env.values()` ✅ |
| 日志 | `_assert_logs_never_contain_sentinel` + `chars=N` only ✅ |
| Exception | `ValueError` message 只含 harness + chars ✅ |
| Receipt 文件 | 测试断言 `SENTINEL not in raw` ✅ |
| User message / turn/start.input | Executor 不拼接；测试断言 inject 不被调用（strict）或原样发送（warn） ✅ |

---

## 8. Grok 返工范围与保护核对

### 8.1 返工范围

`GROK_COMPLETION_5_REWORK.md` §2 列出的变更文件均在 `CODEX_TASK_5_REWORK.md` 允许范围内。`git status` 确认无超出范围的源码/测试修改。✅

### 8.2 Hermes 原报告

`HERMES_COMPLETION_5.md` 未被修改（Grok 报告 §1 明确声明，git status 中该文件在 `?? docs/fixes/handoffs/` 下为 untracked 新建）。✅

### 8.3 Grok 未自签 approve

`GROK_COMPLETION_5_REWORK.md` §1 明确写"未签发阶段 6 approve"。✅

### 8.4 保护 blob

| 项 | 期望 | 独立验证 |
|---|---|---|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` | ✅ |
| workspace 测试 | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` | ✅ |
| model 测试 | `be43ec45816e8ece4192822506df8072580910e0` | ✅ |
| idle 测试 | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` | ✅ |
| serve 测试 | `6116218097f2352c467524fd0ddf0838315aa524` | ✅ |

### 8.5 r05 / STATUS / PRE_MERGE_GATES

`STATUS.md`、`PRE_MERGE_GATES.md`、`POST_FIX_HANDOFF_PROMPT.md` 在 git status 中显示 `M`（阶段 3 累积修改），阶段 5/Grok 返工未额外触及。✅

---

## 9. Grok 返工 pre-fix RED 证据评级

**评级：P2（可接受剩余风险）**

理由：
- Grok 返工在同一开发会话内完成测试补齐与最小修复，没有逐项保存 pre-fix 非零退出码。
- 报告 §3 明确列出 8 项静态根因，并声明"未伪造 RED 退出码"和"最终记录以 GREEN 实测为准"。
- 独立审查确认：测试存在、实现正确、契约满足。缺少 pre-fix RED 退出码是证据完整性限制，不是正确性缺陷。
- 不阻断 approve，但后续审计应注明此限制。

---

## 10. 独立验证命令与真实结果

以下全部由本轮独立执行，非复制 Grok 数字。

### 10.1 定向 prompt/developer_instructions

```
PYTHONPATH="" uv run pytest -q tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py tests/inner/test_codex_native_executor.py tests/test_codex_native_app_server.py tests/runner/test_app_sessions_native.py -k "prompt or developer_instructions"
```

结果：**29 passed, 293 deselected**，exit 0。

### 10.2 Phase 1 helper + matrix

```
PYTHONPATH="" uv run pytest -q tests/inner/test_native_system_prompt_delivery.py
```

结果：**29 passed**，exit 0。

### 10.3 Phase 1 + claude/codex executor

```
PYTHONPATH="" uv run pytest -q tests/inner/test_native_system_prompt_delivery.py tests/inner/test_claude_native_executor.py tests/inner/test_codex_native_executor.py
```

结果：**62 passed**，exit 0。

### 10.4 app-server + executor + apply + runner

```
PYTHONPATH="" uv run pytest -q tests/test_codex_native_app_server.py tests/inner/test_codex_native_executor.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
```

结果：**70 passed**，exit 0。

### 10.5 Builder capture

```
PYTHONPATH="" uv run pytest -q tests/runner/test_app_sessions_native.py -k "auto_create_codex_terminal"
```

结果：**8 passed, 244 deselected**，exit 0。

### 10.6 阶段 1/3 保护回归

```
PYTHONPATH="" uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries tests/runner/test_app_codex_native_model.py tests/runner/test_runner_idle_active_work.py tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

结果：**17 passed**，exit 0。

### 10.7 Plain Ruff（无 --fix）

```
PYTHONPATH="" uv run ruff check omnigent/inner/native_prompt_delivery.py omnigent/codex_native_app_server.py omnigent/runner/app.py omnigent/inner/codex_native_executor.py tests/inner/test_native_system_prompt_delivery.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py tests/inner/test_codex_native_executor.py tests/test_codex_native_app_server.py tests/runner/test_app_sessions_native.py
```

结果：**All checks passed!**，exit 0。

### 10.8 git diff --check

结果：无输出，exit 0。

---

## 11. 必须修改项

无。

## 12. 剩余风险

1. Gate 1 / Gate 2 未执行——合并门槛未达标。
2. 真实 Codex CLI smoke 未运行（无本机认证）。
3. 浏览器 E2E 未运行。
4. 其余 10 个 native harness 仍 warn/error only——无 apply 通道。
5. Grok 返工缺少逐项 pre-fix RED 退出码（P2，见 §9）。
6. `HERMES_COMPLETION_5.md` 部分措辞过宽（以返工报告为准）。

## 13. 是否允许进入 Gate 策划

**是**。approve 仅允许 Codex 进入 Gate 策划；不代表可 merge。

---

## 14. 最终 git status --short --branch

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
 M tests/inner/test_codex_native_executor.py
 M tests/inner/test_loader.py
 M tests/runner/test_app_sessions_native.py
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

## 15. 禁止项遵守声明

- 未修改 `omnigent/`、`tests/`、fixture、依赖、lockfile、CI、r05 或任何既有 handoff。
- 未修复审查发现的问题。
- 本审查由 Hermes 独立完成，非 Grok 撰写/修改/签发。
- 未 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 未 commit/push/merge/tag、发版或编辑 PR/Issue。
- 未运行 Gate 1/2、全仓测试、浏览器 E2E 或真实 AgentCenter/Codex smoke。
- 未把定向 GREEN 或 approve 写成可 merge。
- 未泄漏 prompt sentinel 正文到本报告。
- Gate 1 / Gate 2 **仍未执行、未判定**。
