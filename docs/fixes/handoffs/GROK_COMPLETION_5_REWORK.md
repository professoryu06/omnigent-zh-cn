# GROK COMPLETION 5 REWORK — #2853 apply 链证据与 fresh/resume 边界

**执行者：** Grok（返工开发者，不兼任阶段 6 审查）  
**日期：** 2026-07-29  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_5_REWORK.md`  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**分支：** `docs/fix-plans-core-secondary`（HEAD `dc83140c73ceb12fa165753c1880c19f68da86f4`，未 commit）

---

## 1. 结论摘要

本轮返工补齐了 Hermes 阶段 5 报告中**证据与契约缺口**（非重新发明 apply 通道）：

1. receipt 完整元数据匹配 + 非法 UTF-8 降级  
2. app-server 启动**先清 stale receipt**；仅在 private config 成功写入后写新 receipt  
3. TOML `developer_instructions` 使用 `json.dumps(..., ensure_ascii=False)`，复杂 Unicode 可 `tomllib` round-trip  
4. runner 区分 **真正 fresh 非 fork** vs **fork（含失败降级）**；仅前者传 `developer_instructions`  
5. 11 harness 入口 warn/strict 行为测试（PR #5 语义）  
6. builder capture（fresh/resume/fork 成功/fork fallback）  
7. `CodexNativeExecutor` 真实 receipt + fake RPC 路径  

**未**签发阶段 6 `approve`。**Gate 1 / Gate 2 仍未执行、未判定。** 不代表可 merge。

`HERMES_COMPLETION_5.md` **未修改**。

---

## 2. 精确 diff（允许文件）

### 生产

| 文件 | 变更要点 |
|------|----------|
| `omnigent/inner/native_prompt_delivery.py` | `clear_prompt_receipt()`；空 prompt 也清 stale；`read` 捕获 `UnicodeDecodeError`；`receipt_matches_prompt` 校验 harness/channel/chars/sha256 |
| `omnigent/codex_native_app_server.py` | `start()` 始终先 `clear_prompt_receipt`；`ensure_ascii=False` TOML 编码；receipt 仅在 upsert 成功后写入 |
| `omnigent/runner/app.py` | `is_fork_launch`；仅 `external_session_id is None and not is_fork_launch` 时传 instructions |
| `omnigent/inner/codex_native_executor.py` | 本轮未再改接口（既有 receipt 读取路径满足严格/非严格契约） |

### 测试

| 文件 | 变更要点 |
|------|----------|
| `tests/inner/test_native_system_prompt_delivery.py` | 移植 PR #5 十一 harness 参数化 warn/strict + capability matrix |
| `tests/inner/test_codex_native_system_prompt_apply.py` | metadata 拒绝、非法 UTF-8、复杂 Unicode TOML、stale receipt clear、config 失败无 receipt |
| `tests/runner/test_app_codex_native_prompt_delivery.py` | 真实 AgentSpec + builder capture 四类边界 |
| `tests/inner/test_codex_native_executor.py` | matching RPC / strict zero-RPC / warn 保持 user message |
| `tests/runner/test_app_sessions_native.py` | fresh 传 instructions；fork fallback 传 None |

### 报告

- **新建** `docs/fixes/handoffs/GROK_COMPLETION_5_REWORK.md`（本文件）  
- **未改** `HERMES_COMPLETION_5.md`

---

## 3. RED 说明（契约缺口 → 预期失败）

按任务卡，以下契约在 **Hermes 完成后、本返工前** 的实现上应失败（静态根因已由 `CODEX_TASK_5_REWORK.md` 钉死）：

| 契约 | 预返工根因 | 预期 |
|------|------------|------|
| `receipt_matches` 仅 SHA-256 | 不校验 harness/channel/chars | FAIL |
| 非法 UTF-8 receipt | 未捕 `UnicodeDecodeError` | FAIL/raise |
| 无 instructions 启动 | 不清 stale receipt | FAIL（旧 receipt 仍在） |
| config upsert 失败 | 可能留下旧 receipt 语义不清 | FAIL |
| 复杂 Unicode TOML | 默认 `ensure_ascii=True` surrogate | FAIL round-trip |
| fork fallback | `external_session_id is None` 误判 fresh | FAIL（会传 instructions） |
| 11 harness 入口 | 仅 matrix/helper，无 run_turn 入口 | 证据不足 |
| executor 真实 receipt RPC | 只测 `note_*` mock | 证据不足 |

本轮在同一开发会话内完成测试补齐与最小修复；**最终记录以 GREEN 实测为准**。未伪造 RED 退出码。

---

## 4. GREEN — 任务卡规定命令与真实结果

环境：`$env:PYTHONPATH=''`，Windows，uv/pytest。

### 4.1 最小定向

```text
uv run pytest -q tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py tests/inner/test_codex_native_executor.py tests/test_codex_native_app_server.py tests/runner/test_app_sessions_native.py -k "prompt or developer_instructions"
```

结果：**29 passed**, 293 deselected，**exit 0**

```text
uv run pytest -q tests/inner/test_native_system_prompt_delivery.py
```

结果：**29 passed**，**exit 0**（含 11×2 参数化入口 + helper/matrix）

### 4.2 阶段 5 受影响套件

```text
uv run pytest -q tests/inner/test_native_system_prompt_delivery.py tests/inner/test_claude_native_executor.py tests/inner/test_codex_native_executor.py
```

结果：**62 passed**，**exit 0**

```text
uv run pytest -q tests/test_codex_native_app_server.py tests/inner/test_codex_native_executor.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
```

结果：**70 passed**，**exit 0**

```text
uv run pytest -q tests/runner/test_app_sessions_native.py -k "auto_create_codex_terminal"
```

结果：**8 passed**, 244 deselected，**exit 0**

### 4.3 阶段 1/3 保护回归

```text
uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries tests/runner/test_app_codex_native_model.py tests/runner/test_runner_idle_active_work.py tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
```

结果：**17 passed**，**exit 0**

---

## 5. 静态检查（plain Ruff，无 --fix）

```text
uv run ruff check omnigent/inner/native_prompt_delivery.py omnigent/codex_native_app_server.py omnigent/runner/app.py omnigent/inner/codex_native_executor.py tests/inner/test_native_system_prompt_delivery.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py tests/inner/test_codex_native_executor.py tests/test_codex_native_app_server.py tests/runner/test_app_sessions_native.py
```

结果：**All checks passed!**，**exit 0**

```text
git diff --check
```

结果：无输出，**exit 0**

---

## 6. 保护值

| 项 | 期望 | 实际 |
|----|------|------|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` | ✅ |
| workspace 测试 blob | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` | ✅ |
| model 测试 blob | `be43ec45816e8ece4192822506df8072580910e0` | ✅ |
| idle 测试 blob | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` | ✅ |
| serve 测试 blob | `6116218097f2352c467524fd0ddf0838315aa524` | ✅ |

---

## 7. 关键实现摘录

### receipt 匹配

```python
if receipt.get("harness_id") != "codex-native": return False
if receipt.get("channel") != "codex_home_config_toml": return False
if receipt.get("chars") != len(prompt): return False
return receipt.get("sha256") == sha256(prompt)
```

### app-server start

```python
clear_prompt_receipt(self.bridge_dir)
if self.developer_instructions:
    _upsert_developer_instructions(...)  # may raise
    write_prompt_receipt(...)            # only after success
```

### runner fork 边界

```python
is_fork_launch = bool(
    launch_config.fork_source_id
    or launch_config.fork_source_external_id
    or launch_config.fork_carry_history
)
developer_instructions = (
    _codex_native_developer_instructions(agent_spec)
    if launch_config.external_session_id is None and not is_fork_launch
    else None
)
```

---

## 8. 剩余风险

1. **Gate 1 / Gate 2 未执行** — 合并门槛未达标。  
2. **真实 Codex CLI smoke 未跑** — 依赖 capture-double；无本机认证时不阻塞确定性测试。  
3. **浏览器 E2E 未跑**。  
4. **其它 10 个 harness 仍 warn/error only** — 无 apply 通道。  
5. **本轮不自审** — 须另交非 Grok 独立审查者做阶段 6。  
6. 历史 `HERMES_COMPLETION_5.md` 中“端到端确定性链已证明”的表述**仍过宽**；以本返工报告与新测试为准，勿单独依赖 Hermes 旧措辞。

---

## 9. 禁止项遵守

- [x] 未 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean  
- [x] 未 commit/push/merge/tag；未编辑 PR/Issue  
- [x] 未运行 Gate 1/2，未声称通过  
- [x] 未将 prompt 正文写入 argv/env/log/exception/receipt/user message 断言路径  
- [x] 未把 fork fallback 改名为 fresh 规避边界  
- [x] 未为其余 10 harness 增加 apply  
- [x] 未改写 `HERMES_COMPLETION_5.md`  
- [x] 未自签阶段 6 approve  
- [x] 未改 r05 / 阶段 1·3 保护 blob  

---

## 10. 最终 `git status --short --branch`

```text
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

说明：累积工作树含阶段 1/3/5/r05；本返工仅触及任务卡允许的源码/测试 + 本报告。handoffs 目录现含 `GROK_COMPLETION_5_REWORK.md`。

---

**交回 Codex 只读验收。** 通过后由 Codex 决定是否生成 `CODEX_TASK_6.md` 并交给**非 Grok** 独立审查者。任何结果均不代表可 merge。
