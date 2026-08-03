# GROK REVIEW 4 — 阶段 3 上游回移兼容性独立审查

**执行者：** Grok（只读审查者）  
**日期：** 2026-07-28  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_4.md`  
**阶段：** 仅阶段 4（审查 #3175 / #3178 / #3060 及两轮返工）  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**分支：** `docs/fix-plans-core-secondary`（未切换、未 checkout）

---

## 1. 结论

**`approve`**

当前工作树中的阶段 3 语义回移与两轮返工，**足以进入阶段 5 策划**。

明确边界（**非 merge 批准**）：

- `approve` **仅**允许 Codex 进入阶段 5 策划。
- **不**批准 merge / push / tag / 发版。
- **本轮未运行** pytest、Ruff、构建、AgentCenter smoke 或任何 Gate。
- **Gate 1 / Gate 2：未执行、未判定。**
- Windows 定向 GREEN ≠ Linux Gate 1；host watcher 三项 GREEN ≠ host 全套 GREEN。
- 阶段 2 的 `approve`、本阶段 `approve` 均不得写成可 merge。

---

## 2. P0 / P1 / P2

### P0

**无**

### P1

**无**

### P2

1. **上游 commit 对象本地不可用**  
   任务卡给出的 `a8433fb…` / `e4fdfb0…` / `23e4985…` 等在本工作树 `git cat-file` 失败（未 fetch）。兼容性判断依据任务卡语义 + 当前 diff + `HERMES_COMPLETION_3.md`，**非**与上游 blob 字节级 diff。  
   **建议后续：** 阶段 5/Gate 前在可联网只读环境核对上游对象（可选）；不阻塞进入阶段 5 策划。

2. **#3175 参数矩阵未覆盖「canonical 空串 + config 有值」**  
   代码对 `model == ""` 会走 config fallback（`isinstance(model, str) and model` 为假）；测试有 `empty-model`（空串→None）与 `config-fallback`（None→config），缺组合用例。行为静态正确。  
   **建议后续：** 可选补参；不阻塞。

3. **e2e 浏览器路径未在本流水线执行**  
   六处 compat fixture 已扁平化；浏览器 E2E 未跑、未声称通过。  
   **建议后续：** Gate 2 / 集成阶段再覆盖；不阻塞阶段 5 策划。

4. **`_register_extra_agent` 仍含 `executor.config` 嵌套**  
   不在任务卡「恰好六处扁平」清单内；默认 `arcname=config.yaml`，走 strict bundle 路径，与「不得机械替换全部 nesting」一致。  
   **建议后续：** 若改 single-file arcname 需同步扁平；当前低风险。

---

## 3. 三个上游回移分项结论

### 3.1 #3175 — canonical model 优先及 config fallback

| 检查项 | 结果 |
|--------|------|
| `ResolvedSpec` 解包 | **通过** — `agent_spec.spec if isinstance(..., ResolvedSpec)` |
| 非空字符串 `executor.model` 优先 | **通过** |
| canonical 缺失/`None`/空串时回退 `config["model"]` | **通过** |
| 非字符串 config model、空值、`None` 不当有效模型 | **通过**（`isinstance(..., str) and ...`） |
| 未破坏阶段 1 三 cache 函数 | **通过**（workspace 修复仍在 app.py） |

**兼容性结论：可接受。**  
测试文件 `tests/runner/test_app_codex_native_model.py`（untracked）覆盖 canonical / fallback / non-string / None / ResolvedSpec。报告 RED 4 failed/5 passed → GREEN 9 passed + 组合 47 passed（**历史证据，非本轮重跑**）。

### 3.2 #3178 — 单文件 executor bundle nesting fail-loud

| 检查项 | 结果 |
|--------|------|
| 仅对实际出现的 `config`/`type` fail-loud | **通过**（`sorted(k for k in ("config","type") if k in data)`） |
| 错误信息含 `config.yaml` 与扁平示例 | **通过** |
| `use_responses` 等 extra keys 仍可加载 | **通过**（测试 + 解析逻辑未拒未知键） |
| inline AgentTool 相同拒绝语义 | **通过**（共用 `_parse_executor_spec` + 测试） |
| 六处 compat fixture 扁平化 | **通过**（chat links 1 + conftest 4 + mcp 1） |
| `_APPROVAL_AGENT_YAML` / `_CUSTOM_AGENT_YAML` 仍嵌套 | **通过**（保留；bundle `config.yaml` 路径） |
| 生产注释无 PR/Issue 编号 | **通过**（返工后无 `#3178`） |

**兼容性结论：可接受。**  
定向 3 passed；server integration 6 passed（历史）。loader Windows 全套 **非 GREEN**（见 §6）。

### 3.3 #3060 — idle runner / stream drain / graceful tunnel

| 检查项 | 结果 |
|--------|------|
| host code 0 静默（仍 tracked） | **通过** — `_watch_runner` 在 intentional-stop 检查后 `returncode == 0` → info + return |
| non-zero 仍报告 | **通过**（既有路径未改） |
| intentional stop 仍静默 | **通过**（`self._runners.get` 句柄变更提前 return） |
| stream drain 快照逐队列一个 `None` | **通过** — `list(_session_event_queues.values())` + `put_nowait(None)`；`app.state.drain_session_streams` |
| 不改变阶段 1 cache | **通过** |
| recv/shutdown race 用 `create_task` | **通过**（无 `ensure_future`） |
| shutdown 胜：`CancelledError` + `WebSocketException`，不裸吞 `Exception` | **通过** |
| recv 侧 `ConnectionClosedOK` 正常关闭 | **通过**；其他异常上抛 |
| `_graceful_drain`：先 hook，再 `asyncio.wait(..., timeout=)` | **通过**；超时任务留给 finally 取消 |
| `_entry.py`：`asyncio.wait({tunnel_task}, timeout=15)`，不用 `wait_for` | **通过**（返工后） |
| idle → graceful event；signal/parent-death → `stop_event` | **通过** |
| shutdown 后不再连接 | **通过**（loop 入口与 once 正常返回后检查 event） |

**兼容性结论：可接受。**  
watcher 3 / drain 1 / graceful 4 / serve 54 / entry 69 为历史 GREEN 证据。

---

## 4. 两轮返工逐项结论

### 4.1 CODEX_TASK_3_REWORK（实现 + 证据）

| 项 | 结论 |
|----|------|
| P1 `_entry.py` `wait_for` → `asyncio.wait` | **已修复**；当前无 `wait_for` 等待 tunnel |
| P1 serve `create_task` + 异常语义 + `ConnectionClosedOK` | **已修复** |
| P2 loader 注释去 issue 编号 | **已修复** |
| loader 全套如实记录 exit 3 | **已记录**（1 failed / 38 passed / INTERNALERROR / WinError 32） |
| host 全套环境 + nodeid + watcher 同环境 GREEN | **已记录** |

### 4.2 CODEX_TASK_3_REWORK_2（纯文档）

| 项 | 结论 |
|----|------|
| host `25 failed, 45 passed, 42 warnings` | **保留正确** |
| `exit 1` / `HOST_FULL_EXIT=1` | **已纠正**（删除错误 exit 0 与「pytest 不因失败返回非零」） |
| 末尾 loader exit 3 + host exit 1 均未冒充 GREEN | **已写明** |
| 仅改 `HERMES_COMPLETION_3.md` | **符合**（本审查不重改） |

---

## 5. 范围、阶段 1、r05、工作树

### 5.1 阶段 3 相关 diff 范围（生产 + 测试）

生产：`omnigent/runner/app.py`、`inner/loader.py`、`host/connect.py`、`runner/_entry.py`、`runner/transports/ws_tunnel/serve.py`  
测试/fixture：任务卡 3.2 所列文件 + untracked `test_app_codex_native_model.py`、`test_runner_idle_active_work.py`、`test_session_workspace_cache.py`（阶段 1）

`app.py` 同时含阶段 1 workspace cache 修复与阶段 3 `#3175`/`drain`，符合串行累积；**未发现**阶段 3 回滚阶段 1 三函数语义。

### 5.2 阶段 1 保护

| 保护项 | 值 / 状态 |
|--------|-----------|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| `test_session_workspace_cache.py` blob | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` |
| 三函数语义 | 仍：`snapshot.ok` 才缓存；双 cache 短路；reset pop workspace+fs |

### 5.3 r05 文档

| 文件 | LastWriteTime | 状态 |
|------|---------------|------|
| `STATUS.md` | 2026-07-24 | 既有 r05；Gate 1/2 **未执行** 措辞仍在 |
| `PRE_MERGE_GATES.md` | 2026-07-24 | 同上 |
| `POST_FIX_HANDOFF_PROMPT.md` | 2026-07-24 | 同上 |

本阶段 **未修改** r05 或既有 handoff（仅新建本审查文件）。

### 5.4 `git diff --check`

**通过**（exit 0）。

---

## 6. RED/GREEN 与平台非零结果评价

**本轮评价方式：** 只读 `HERMES_COMPLETION_3.md` + 当前 diff 静态核对。**未独立重跑任何测试。**

| 范围 | 报告 RED | 报告 GREEN / 当前 | 评价 |
|------|----------|-------------------|------|
| #3175 | 4f/5p | 9p；组合 47p | 与实现一致；可支撑兼容判断 |
| #3178 | 2 reject FAIL + 1 toleration PASS | 定向 3p；mcp 6p | 契约覆盖充分 |
| #3060 host | clean exit FAIL | watcher 3p | 与 `_watch_runner` 一致 |
| #3060 stream | drain FAIL | 1p | 与 `drain_session_streams` 一致 |
| #3060 WS | 4 FAIL | 4p；serve 54p；entry 69p | 与 serve/_entry 一致 |
| 阶段 1 | — | 3p；blob 不变 | 保护有效 |
| loader Windows 全套 | — | **1f/38p，exit 3，非 GREEN** | 诚实；WinError 32 既有路径 |
| host Windows 全套 | — | **25f/45p/42w，exit 1 / HOST_FULL_EXIT=1，非 GREEN** | 诚实；25 nodeid 保留 |

**不得**将上表 GREEN 表述为本轮 Grok 运行结果，亦**不得**当作 Gate 1/2。

---

## 7. 必须修改项

**无**

（无 P0/P1；不退回 Hermes 实现返工。）

---

## 8. 剩余风险

1. Gate 1 / Gate 2 仍未执行 → **合并门槛未达标**。  
2. Windows 平台既有失败（loader exit 3、host exit 1）在 Linux 全仓表现未知。  
3. 上游 commit 本地不可达 → 无法做字节级上游 diff。  
4. 真实 AgentCenter idle/graceful/banner 路径未做端到端验证。  
5. 浏览器 E2E 在 fixture 扁平化后未跑。  
6. 持续失败 snapshot 仍会重复 GET（阶段 1 已知权衡）。  
7. 本审查依赖历史 RED/GREEN 记录 + 静态 diff，非独立复跑。

---

## 9. 是否需要 Hermes 补测

**否（进入阶段 5 策划不强制）。**

若 Codex 希望在阶段 5 前增加可选信心（**非本轮 Grok 代跑**），可交 Hermes：

```powershell
$env:PYTHONPATH=''
# 定向回归（期望全 exit 0）
uv run pytest -q tests/runner/test_app_codex_native_model.py
uv run pytest -q tests/inner/test_loader.py::TestLoadFromDict::test_executor_bundle_nesting_rejected tests/inner/test_loader.py::TestLoadFromDict::test_executor_extra_keys_tolerated tests/inner/test_loader.py::TestLoadFromDict::test_tools_agent_executor_bundle_nesting_rejected
uv run pytest -q tests/host/test_connect.py::test_watch_runner_silent_on_clean_exit tests/host/test_connect.py::test_watch_runner_reports_unexpected_exit tests/host/test_connect.py::test_watch_runner_silent_on_intentional_stop
uv run pytest -q tests/runner/test_runner_idle_active_work.py
uv run pytest -q tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries

# 平台全套（期望非零，不得冒充 GREEN）
uv run pytest -q tests/inner/test_loader.py tests/spec/test_load.py
# 期望：含既有失败时 exit 3 或等价非零；不得改测让其变绿
uv run pytest -q tests/host/test_connect.py
# 期望：HOST_FULL_EXIT=1 量级；watcher 定向仍 3 passed
```

**判据：** 定向套件 exit 0；平台全套按真实 exit 记录；blob 与 HEAD 保护值不变。  
**原因：** 纯信心复验，非本审查发现的契约缺口。

---

## 10. 明确声明

| 项 | 状态 |
|----|------|
| 本轮是否运行测试 | **未运行** |
| 本轮是否运行 Ruff / 构建 / smoke | **未运行** |
| Gate 1 Linux 全仓 | **未执行、未判定** |
| Gate 2 AgentCenter C/E/R | **未执行、未判定** |
| 是否可 merge | **否** — approve 仅进阶段 5 策划 |

---

## 11. 禁止项遵守（审查侧）

- [x] 未修改 `omnigent/`、`tests/`、fixture、r05、既有 handoff  
- [x] 未运行 pytest / Ruff / 构建 / Gate / AgentCenter smoke  
- [x] 未 checkout / switch / fetch / rebase / cherry-pick / stash / reset / clean  
- [x] 未 commit / push / merge / tag  
- [x] 未把 approve 写成可 merge  
- [x] 未实施 #2853 Phase 2 或自行修缺陷  

**唯一新建文件：** `docs/fixes/handoffs/GROK_REVIEW_4.md`（本文件）

---

## 12. 最终 `git status --short --branch`

```text
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

说明：`docs/fixes/handoffs/` 现含 `GROK_REVIEW_4.md` 及既有任务卡/完成报告；本轮除该新建审查文件外无其它写入。
