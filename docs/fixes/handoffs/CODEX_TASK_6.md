# CODEX TASK 6 — Hermes 独立审查阶段 5 #2853

**执行者：** Hermes（独立审查者；未参与 Grok 的阶段 5 返工）

**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**阶段边界：** 只审查 Hermes 阶段 5 初始实现与 Grok 返工后的累计结果。不得修改源码、测试、fixture、既有 handoff 或 r05 文档。阶段 6结论只能是 `approve` 或 `request-changes`；`approve` 仅允许进入后续 Gate策划，不代表可 merge。

## 1. 问题与审查目标

阶段 5为 #2853 建立两层契约：

1. 11 个 native harness 对未送达的 non-empty system prompt实施 warn/strict-error，禁止静默丢弃。
2. 仅 fresh、非 fork 的 `codex-native` 可通过每会话私有 `CODEX_HOME/config.toml` 顶层 `developer_instructions` + metadata/digest receipt标记 `applied=True`。

Hermes 初始实现后，Codex发现测试链与 fresh/resume边界不足；Grok根据 `CODEX_TASK_5_REWORK.md` 修复 stale receipt、fork fallback、receipt完整校验、非法UTF-8和复杂Unicode，并补真实入口测试。

阶段 6必须独立判断：

- Grok返工是否真实关闭任务卡中的 P1/P2缺口。
- cumulative阶段 5实现是否保持 Phase 1 fail-loud、Phase 2仅 codex-native fresh apply的边界。
- prompt正文是否只进入私有 config通道，不进入 argv、普通env、日志、exception、receipt或user message。
- 阶段 1/3、r05与既有 handoff是否保持。
- 当前证据是否足以进入 Gate策划；不得把任何定向测试当成 Gate 1/2或merge许可。

## 2. 必读材料

1. `docs/fixes/handoffs/CODEX_TASK_5.md`
2. `docs/fixes/handoffs/HERMES_COMPLETION_5.md`（只读历史报告）
3. `docs/fixes/handoffs/CODEX_TASK_5_REWORK.md`
4. `docs/fixes/handoffs/GROK_COMPLETION_5_REWORK.md`
5. `docs/fixes/handoffs/CODEX_TASK_4.md`
6. `docs/fixes/handoffs/GROK_REVIEW_4.md`
7. `docs/fixes/STATUS.md`
8. `docs/fixes/PRE_MERGE_GATES.md`

Phase 1本地语义来源：`origin/pr/5@1f42a898fbd07e358f87de5cba391a93af1f43b9`。只允许读取本地对象；不得 fetch、cherry-pick或覆盖文件。

## 3. 精确审查文件

### 3.1 阶段 5生产代码

1. `omnigent/inner/native_prompt_delivery.py`
2. `omnigent/codex_native_app_server.py`
3. `omnigent/runner/app.py`（仅 #2853 instructions/fresh/fork相关 diff；阶段 1/3累计 diff是保护项）
4. `omnigent/inner/codex_native_executor.py`
5. `omnigent/inner/antigravity_native_executor.py`
6. `omnigent/inner/claude_native_executor.py`
7. `omnigent/inner/cursor_native_executor.py`
8. `omnigent/inner/goose_native_executor.py`
9. `omnigent/inner/hermes_native_executor.py`
10. `omnigent/inner/kimi_native_executor.py`
11. `omnigent/inner/kiro_native_executor.py`
12. `omnigent/inner/pi_native_executor.py`
13. `omnigent/inner/qwen_native_executor.py`
14. `omnigent/native_server_harness.py`

### 3.2 阶段 5测试

15. `tests/inner/test_native_system_prompt_delivery.py`
16. `tests/inner/test_codex_native_system_prompt_apply.py`
17. `tests/runner/test_app_codex_native_prompt_delivery.py`
18. `tests/inner/test_codex_native_executor.py`（只审查新增 receipt/RPC用例及其对既有测试的影响）
19. `tests/test_codex_native_app_server.py`
20. `tests/runner/test_app_sessions_native.py`（只审查新增 builder capture用例及其对既有测试的影响）

### 3.3 保护项

21. `tests/runner/test_session_workspace_cache.py`
22. `tests/runner/test_app_codex_native_model.py`
23. `tests/runner/test_runner_idle_active_work.py`
24. `tests/runner/transports/ws_tunnel/test_serve.py`
25. `docs/fixes/STATUS.md`
26. `docs/fixes/PRE_MERGE_GATES.md`
27. `docs/fixes/POST_FIX_HANDOFF_PROMPT.md`
28. `docs/fixes/handoffs/HERMES_COMPLETION_5.md`

阶段 6只允许新建 `docs/fixes/handoffs/HERMES_REVIEW_6.md`。

## 4. 失败测试（RED）与既有证据的审查边界

只审查已有记录，不得回退源码或伪造 RED：

- `HERMES_COMPLETION_5.md` 记录 Phase 1真实 RED：collection error / exit 1；Phase 2真实 RED：缺 receipt API / exit 1。
- `GROK_COMPLETION_5_REWORK.md` §3记录返工前静态失败根因，但没有逐项给出实际 pre-fix RED命令和退出码。报告明确没有伪造 RED。
- 审查报告必须把“初始 Phase 1/2真实 RED”和“Grok返工的静态 pre-fix根因”分开；不得把后者写成已实跑 RED。
- 独立审查者需判断该历史证据限制是 P1、P2还是可接受剩余风险，并说明理由；不得通过修改/回退工作树重建 RED。

## 5. 最小改法：只读静态审查方法

### 5.1 Phase 1 fail-loud

确认：

- capability matrix恰好覆盖 11 harness，只有 `codex-native` 是 `apply`能力目标。
- 11 个入口均在用户消息注入前调用共享 helper。
- unsupported路径 non-empty prompt会 warning；strict时只返回一个 `ExecutorError`并停止注入。
- warning/error只含 harness和 `chars=N`，不含正文。
- 其余 10 个 harness没有新增 argv或伪 apply通道。

### 5.2 receipt与app-server

确认：

- 每次 app-server启动均在本次 apply判定前清 stale receipt。
- 空 prompt、resume、fork、config upsert失败不会留下可匹配 receipt。
- 新 receipt只在 private config成功写入后产生，只含固定 harness、固定 channel、chars、SHA-256。
- matcher同时验证四项；缺字段、错误类型、非法JSON、非法UTF-8都不能 applied。
- config symlink被materialize，不修改用户共享配置；复杂Unicode由 `tomllib`精确round-trip。
- prompt正文不进入argv/env/log/exception/receipt/user message。

### 5.3 runner fresh/resume/fork

确认真实 `_auto_create_codex_terminal()` builder capture覆盖：

- fresh非fork传 non-empty instructions。
- resume传 `None`。
- fork clone/rebuild成功传 `None`。
- fork clone/rebuild失败、降级fresh launch仍传 `None`。
- `ResolvedSpec`和普通 `AgentSpec`语义一致；blank/non-string均不传。

### 5.4 executor真实入口

确认：

- 完整matching receipt时正常走原 `turn/start`/steer语义，RPC参数只有原user input，不含prompt。
- missing/corrupt/wrong metadata + strict在任何RPC前返回sole `ExecutorError`。
- 非strict mismatch只warning并发送原user message，不拼接prompt。
- 不改变model/effort、active turn、steering、attachment、MCP startup或bridge lock语义。

### 5.5 范围与报告真实性

确认：

- Grok返工只触及 `CODEX_TASK_5_REWORK.md`允许文件和 `GROK_COMPLETION_5_REWORK.md`。
- `HERMES_COMPLETION_5.md`未被覆盖；Grok没有自签 approve。
- 报告中的 `29 / 29 / 62 / 70 / 8 / 17 passed`、plain Ruff和 `git diff --check`均明确标为Grok运行结果，不得写成Codex或Hermes此前已运行。
- HEAD与四个保护blob保持下列值。

## 6. 独立验证命令

Hermes必须独立运行以下命令；这些是阶段 6定向复验，不是 Gate 1或Gate 2：

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py tests/inner/test_codex_native_executor.py tests/test_codex_native_app_server.py tests/runner/test_app_sessions_native.py -k "prompt or developer_instructions"
uv run pytest -q tests/inner/test_native_system_prompt_delivery.py
uv run pytest -q tests/inner/test_native_system_prompt_delivery.py tests/inner/test_claude_native_executor.py tests/inner/test_codex_native_executor.py
uv run pytest -q tests/test_codex_native_app_server.py tests/inner/test_codex_native_executor.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py
uv run pytest -q tests/runner/test_app_sessions_native.py -k "auto_create_codex_terminal"
uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries tests/runner/test_app_codex_native_model.py tests/runner/test_runner_idle_active_work.py tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown
uv run ruff check omnigent/inner/native_prompt_delivery.py omnigent/codex_native_app_server.py omnigent/runner/app.py omnigent/inner/codex_native_executor.py tests/inner/test_native_system_prompt_delivery.py tests/inner/test_codex_native_system_prompt_apply.py tests/runner/test_app_codex_native_prompt_delivery.py tests/inner/test_codex_native_executor.py tests/test_codex_native_app_server.py tests/runner/test_app_sessions_native.py
git diff --check
git rev-parse HEAD
git hash-object tests/runner/test_session_workspace_cache.py
git hash-object tests/runner/test_app_codex_native_model.py
git hash-object tests/runner/test_runner_idle_active_work.py
git hash-object tests/runner/transports/ws_tunnel/test_serve.py
git status --short --branch
```

保护值：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- workspace blob：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model blob：`be43ec45816e8ece4192822506df8072580910e0`
- idle blob：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve blob：`6116218097f2352c467524fd0ddf0838315aa524`

任一命令非零必须如实记录并判断是否阻断；不得改测试让结果变绿。不得运行全仓、浏览器E2E、真实Codex CLI smoke、AgentCenter smoke或任何Gate。

## 7. 输出要求

只新建 `docs/fixes/handoffs/HERMES_REVIEW_6.md`，必须包含：

1. 结论：`approve` 或 `request-changes`。
2. P0/P1/P2逐级问题；无则逐项写“无”。
3. Phase 1 11-harness、receipt/app-server、runner边界、executor RPC逐项结论。
4. prompt正文泄漏面审计。
5. Grok返工范围、Hermes原报告、r05和四个保护blob核对。
6. 对Grok返工缺少真实pre-fix RED退出码的证据评级。
7. 每条独立命令、summary、退出码；不得复制Grok数字冒充独立运行。
8. 必须修改项、剩余风险和是否允许进入Gate策划。
9. 明确写明Gate 1 / Gate 2未执行、未判定；`approve`不代表可merge。
10. 最终 `git status --short --branch`。

## 8. 禁止项

- 不得修改 `omnigent/`、`tests/`、fixture、依赖、lockfile、CI、r05或任何既有handoff。
- 不得修复审查发现的问题；只能在报告中列出并退回Codex决定返工。
- 不得由Grok撰写、修改或签发本审查报告。
- 不得checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 不得commit/push/merge/tag、发版或编辑PR/Issue。
- 不得运行Gate 1、Gate 2、全仓测试、浏览器E2E或真实AgentCenter/Codex smoke。
- 不得把定向GREEN、阶段4 approve或阶段6 approve写成可merge。
- 不得泄漏prompt sentinel正文到报告；只可记录测试名、字符数或digest已验证。

## 9. 完成标准

阶段 6只有在以下全部满足时完成：

1. 审查者不是Grok，且没有修改被审查实现、测试或既有文档。
2. 已独立检查累计阶段 5 diff和Grok返工报告，不仅复述summary。
3. 已逐项判断11 harness、receipt、app-server、fresh/resume/fork和executor RPC契约。
4. 已独立执行第6节全部定向命令并记录真实结果。
5. 所有问题按P0/P1/P2分类，必须修改项与剩余风险完整。
6. 已诚实区分Hermes初始真实RED、Grok静态pre-fix根因和本轮独立GREEN。
7. 只创建 `HERMES_REVIEW_6.md`；工作树其他内容保持。
8. 无commit/push/merge/tag；Gate 1 / Gate 2仍未执行、未判定。

若结论为 `approve`，只允许Codex进入Gate策划；若为 `request-changes`，只列缺陷并交Codex决定返工。两种结论均不表示可merge。
