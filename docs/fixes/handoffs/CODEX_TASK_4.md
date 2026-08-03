# CODEX TASK 4 — Grok 独立审查阶段 3 上游回移兼容性

**执行者：** Grok（只读审查者）

**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**阶段边界：** 只审查阶段 3 的 #3175 / #3178 / #3060 语义回移及两轮返工结果；不修改源码、测试或既有交接文档，不运行测试，不执行 Gate。

## 1. 问题与审查目标

Hermes 已完成阶段 3 实现和第一次返工，Grok 已完成第二次纯文档纠错。Codex 只读复验确认报告现记录：

- host 全套：`25 failed, 45 passed, 42 warnings`，`exit 1 / HOST_FULL_EXIT=1`；未冒充 GREEN。
- loader 全套：`1 failed, 38 passed, 2 warnings`，`exit 3`；未冒充 GREEN。
- host watcher 定向三项：`3 passed`、exit 0。
- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`。
- 阶段 1 测试 blob：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`。
- Gate 1 / Gate 2 仍未执行、未判定。

阶段 4 的目标是独立判断当前 diff 是否准确回移三个上游修复的语义、是否保持当前 v0.6 二开兼容边界，以及现有 RED/GREEN 报告是否足够支撑进入阶段 5。`approve` 只表示可进入阶段 5，不表示可 merge。

## 2. 必读材料

1. `docs/fixes/handoffs/CODEX_TASK_3.md`
2. `docs/fixes/handoffs/CODEX_TASK_3_REWORK.md`
3. `docs/fixes/handoffs/CODEX_TASK_3_REWORK_2.md`
4. `docs/fixes/handoffs/HERMES_COMPLETION_3.md`
5. `docs/fixes/handoffs/CODEX_TASK_1.md`
6. `docs/fixes/handoffs/HERMES_COMPLETION_1.md`
7. `docs/fixes/handoffs/CODEX_TASK_2.md`
8. `docs/fixes/handoffs/GROK_REVIEW_2.md`
9. `docs/fixes/STATUS.md`
10. `docs/fixes/PRE_MERGE_GATES.md`

上游语义依据：

- #3175：`a8433fb7cfb7e7e07d74f28b7a277cd7a7bce1a4`，merge `131db6276b6c7670195d8346fd03070e01b71d2d`
- #3178：`e4fdfb0c13887e3ebcff0fd644c2d7fb71c38880`、`0c30cadf9bbf03befd6ff7d90d0f43b891cfa337`，merge `af3d18ba16bb777ff3229b2d8d814e732f64a427`
- #3060：merge `23e498521f88fb9145512a7449f6fa603ce9ee11`

只允许使用本地已有对象和当前工作树做只读核对；不得 fetch、cherry-pick 或覆盖文件。若本地没有某个上游对象，以任务卡和完成报告中已有语义说明为审查依据，并在风险中注明。

## 3. 精确审查文件

### 3.1 生产代码

1. `omnigent/runner/app.py`
2. `omnigent/inner/loader.py`
3. `omnigent/host/connect.py`
4. `omnigent/runner/_entry.py`
5. `omnigent/runner/transports/ws_tunnel/serve.py`

### 3.2 测试与 fixture

6. `tests/runner/test_app_codex_native_model.py`
7. `tests/inner/test_loader.py`
8. `tests/e2e_ui/chat/test_chat_file_path_links.py`
9. `tests/e2e_ui/conftest.py`
10. `tests/server/integration/test_session_mcp_servers.py`
11. `tests/host/test_connect.py`
12. `tests/runner/test_runner_idle_active_work.py`
13. `tests/runner/transports/ws_tunnel/test_serve.py`

### 3.3 保护项

14. `tests/runner/test_session_workspace_cache.py`
15. `docs/fixes/STATUS.md`
16. `docs/fixes/PRE_MERGE_GATES.md`
17. `docs/fixes/POST_FIX_HANDOFF_PROMPT.md`

阶段 4 只能创建 `docs/fixes/handoffs/GROK_REVIEW_4.md`；不得修改上述任何文件。

## 4. 已有失败测试与证据边界

只审查以下已记录证据，不重新运行：

| 范围 | RED | GREEN / 当前结果 |
| --- | --- | --- |
| #3175 | 4 failed / 5 passed | 定向 9 passed；组合 47 passed |
| #3178 | 2 个 rejection FAIL、1 个 toleration PASS | 定向 3 passed；server integration 6 passed |
| #3060 host | clean exit 1 failed | watcher 三项 3 passed |
| #3060 stream | drain sentinel 1 failed | drain 1 passed |
| #3060 WebSocket | graceful shutdown 4 failed | 定向 4 passed；serve 54 passed；runner-entry 69 passed |
| 阶段 1 | — | 回归 3 passed；blob 保持 |
| loader Windows 全套 | — | 1 failed / 38 passed / exit 3，非 GREEN |
| host Windows 全套 | — | 25 failed / 45 passed / exit 1，非 GREEN |

不得把历史报告中的 GREEN 当成 Grok 本轮独立运行结果。若认为必须增加测试才能判断，只在 `GROK_REVIEW_4.md` 中列出需要 Hermes 执行的精确命令、预期判据和原因；Grok 不得代跑。

## 5. 最小审查方法

### 5.1 #3175 canonical model

确认：

- `ResolvedSpec` 正确解包。
- 非空字符串 `executor.model` 优先。
- canonical 缺失或为空时才回退 `executor.config["model"]`。
- 非字符串 config model、空值和 `None` 不被误当有效模型。
- 未改阶段 1 的 workspace cache 三个函数。

### 5.2 #3178 fail-loud

确认：

- 单文件 executor 只对实际出现的 `config` / `type` bundle key fail-loud。
- 错误信息说明 bundle `config.yaml` 与扁平单文件格式。
- `use_responses` 等兼容 raw key 仍可加载，不是拒绝所有未知键。
- inline AgentTool 走相同拒绝语义。
- 六处 compat fixture 已扁平化；两个 strict `spec_version: 1` / `config.yaml` fixture 仍保持嵌套。
- loader 生产注释不含 PR/Issue 编号。

### 5.3 #3060 idle runner 与 graceful tunnel

确认：

- host 中已跟踪 runner 的 code 0 退出静默返回，non-zero 意外退出仍报告，intentional stop 仍静默。
- session stream drain 对队列快照逐个放入一个 `None` sentinel，不改变阶段 1 cache 行为。
- tunnel recv/shutdown race 使用 `asyncio.create_task()`。
- shutdown 获胜时只处理预期取消和 WebSocket 异常，不裸吞所有 `Exception`。
- recv 正常关闭区分 `ConnectionClosedOK`；异常关闭仍沿既有错误/重连路径。
- graceful drain 先调用 hook，再用 `asyncio.wait(..., timeout=...)` 有界等待 dispatch tasks，超时任务留给 finally 取消。
- `_entry.py` 使用 `asyncio.wait({tunnel_task}, timeout=15)`，不使用 `wait_for()` 取消 graceful tunnel task。
- idle reaper 走 graceful event；signal / parent-death 保持快速停止语义。
- shutdown 后不再次连接；正常 tunnel 自行退出或异常退出没有被静默化。

### 5.4 范围与报告真实性

确认：

- 阶段 3 diff 仅涉及任务卡允许的代码、测试和 fixture；r05 与阶段 1 结果未被清理或覆盖。
- `HERMES_COMPLETION_3.md` 保留真实 RED、GREEN、平台非零退出码和 25 个 host 失败 nodeid。
- Windows 定向结果不等于 Linux Gate 1；watcher 定向 GREEN 不等于 host 全套 GREEN。
- 没有把阶段 2 approve、阶段 4 approve 或任何定向测试写成可 merge。

## 6. 只读检查命令

允许运行：

```powershell
git status --short --branch
git rev-parse HEAD
git diff --stat
git diff -- omnigent/runner/app.py omnigent/inner/loader.py omnigent/host/connect.py omnigent/runner/_entry.py omnigent/runner/transports/ws_tunnel/serve.py
git diff -- tests/runner/test_app_codex_native_model.py tests/inner/test_loader.py tests/e2e_ui/chat/test_chat_file_path_links.py tests/e2e_ui/conftest.py tests/server/integration/test_session_mcp_servers.py tests/host/test_connect.py tests/runner/test_runner_idle_active_work.py tests/runner/transports/ws_tunnel/test_serve.py
rg -n "_codex_native_model_from_spec|_parse_executor_spec|_watch_runner|drain_session_streams|asyncio.wait\(|asyncio.wait_for|create_task|ensure_future|ConnectionClosedOK|HOST_FULL_EXIT" omnigent tests docs/fixes/handoffs/HERMES_COMPLETION_3.md
git hash-object tests/runner/test_session_workspace_cache.py
git diff --check
```

禁止运行 pytest、Ruff、构建、集成测试、浏览器测试、真实 AgentCenter smoke 或任何 Gate 命令。

## 7. 输出格式

只创建 `docs/fixes/handoffs/GROK_REVIEW_4.md`，内容必须包含：

1. 结论：`approve` 或 `request-changes`。
2. P0 / P1 / P2 问题；无则逐项写“无”。
3. #3175、#3178、#3060 分项兼容性结论。
4. 两轮返工项逐项结论。
5. 任务范围、阶段 1 blob、r05 文档和工作树核对。
6. 对现有 RED/GREEN 与 Windows 平台非零结果的证据评价。
7. 必须修改项和剩余风险。
8. 若需补测：列出仅交 Hermes 执行的命令与判据；不得自行运行。
9. 明确写明未运行测试，Gate 1 / Gate 2 未执行、未判定。
10. 最终 `git status --short --branch`。

## 8. 禁止项

- 不得修改 `omnigent/`、`tests/`、fixture、依赖、lockfile、CI、r05 文档或既有 handoff。
- 不得运行 pytest、Ruff、构建、集成测试、AgentCenter smoke、Gate 1 或 Gate 2。
- 不得 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 不得 commit/push/merge/tag、发版或编辑 PR/Issue。
- 不得把 `approve` 写成可 merge；不得批准 merge。
- 不得实施 #2853 Phase 2 或修复审查中发现的问题。

## 9. 完成标准

阶段 4 仅在以下条件全部满足时完成：

1. Grok 已只读审查三个上游回移及两轮返工的实际 diff 和证据。
2. 报告对 #3175、#3178、#3060 分别给出明确兼容性判断。
3. 所有问题按 P0/P1/P2 分类，必须修改项和剩余风险完整。
4. 没有把 Windows 定向 GREEN、host watcher GREEN 或阶段 2 approve 当成 Gate 或 merge 许可。
5. 只创建 `GROK_REVIEW_4.md`，没有修改任何源码、测试或既有文档。
6. 未运行测试；若需要补测，已明确交 Hermes 而非自行执行。
7. 无 commit/push/merge/tag；Gate 1 / Gate 2 仍为未执行、未判定。

若结论为 `approve`，只允许 Codex进入阶段 5 策划；若为 `request-changes`，只列缺陷并由 Codex决定是否下发 Hermes 返工。任何结论均不代表可 merge。
