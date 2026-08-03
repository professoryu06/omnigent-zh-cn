# CODEX_TASK_22_PLAN — BUG-1/BUG-2/BUG-3 修复方案（只排查，不实施）

状态：方案交付；本文件不包含源码补丁，不代表 Gate 2 签字。

## 1. 结论摘要

本 RUN 的失败发生在 Omnigent 的 harness/terminal 路由层，而不是 Codex CLI、模型或 TUN 本身。证据中的 runner 已经创建 session、接受用户消息并开始 turn，随后进入：

`omnigent/terminals/registry.py:221` → `omnigent/inner/terminal.py:1882`

Windows 在 `create_terminal_instance()` 明确拒绝 tmux/PTY，于是 runner 崩溃，Codex CLI 从未 spawn，CLI 最终只看到 240s idle watchdog。这个分类可以确认是 BUG-2，但要注意下面的语义边界：

| 配置 | 设计上的实现 | Windows 适用性 |
|---|---|---|
| `executor.config.harness: codex` | `harness_plugins.py` 映射到 `omnigent.inner.codex_harness`，再由 `CodexExecutor` 启动 Codex app-server/子进程 | 适用 |
| `executor.config.harness: codex-native` | `omnigent.inner.codex_native_harness` → `CodexNativeExecutor`，需要 native terminal/TUI | Windows 当前不适用 |

因此，任务卡中“`harness: codex` 是否应走 `codex_native_executor.py`”的答案是：**不应走**。`codex_native_executor.py` 只属于显式的 `codex-native`；把二者合并会把 Windows 的终端限制重新引入 SDK 路径。

本方案同时纳入 BUG-1 与 BUG-3，因为二者分别会造成 host 隧道反复断线，以及 multipart 创建 session 后永远没有 runner，任何一个都足以让 full-run 无法到达 `CONTROLLER_OK`。

## 2. 审计范围与证据

- 任务卡：`docs/fixes/handoffs/CODEX_TASK_22.md`
- 诊断：`docs/fixes/handoffs/HERMES_DIAGNOSIS_21.md`
- Evidence：`C:\Users\Administrator\omnigent-diagnostics\20260730-172454-dc83140-hermes-d2-run-cli0146-r2\`
- RUN_ID：`20260730-172454-dc83140-hermes-d2-run-cli0146-r2`
- 固定模型：`gpt-5.6-sol`
- 固定 native CLI：`0.146.0`（后续验证必须继续使用任务卡约定的 native 路径/SHA）
- 产品 idle watchdog：`240s`，修复和验证均不得改变
- 凭据：本方案不记录任何凭据，统一使用 `[REDACTED]`

诊断报告及 runner 日志表明：runner PID `20864` 已启动；session、user message、turn 均已出现；之后出现 Windows native terminal RuntimeError；没有 assistant event，也没有 Codex child process。r2 evidence 应持久保留，不能用旧 RUN 拼接结论。

## 3. BUG-2 根因确认

### 3.1 配置解析本身不是把 `codex` 变成 native

静态路径核对结果：

1. `omnigent/spec/parser.py` 的 `_parse_executor()`（约 613–650 行）保留 `executor.config`，没有把 `codex` 改写为 `codex-native`。
2. `omnigent/spec/types.py` 的 `ExecutorSpec.harness_kind` 从 `config["harness"]` 取值；`executor.type: omnigent` 不会自动产生 native harness。
3. `omnigent/harness_plugins.py:538–545` 明确区分：
   - `codex` → `omnigent.inner.codex_harness`
   - `codex-native` → `omnigent.inner.codex_native_harness`
4. `harness_plugins.py:581–605` 的 native 集合包含 `codex-native`/`native-codex`，不包含裸 `codex`。
5. `omnigent/inner/codex_harness.py:1–11, 95–99` 包装的是 `CodexExecutor`；`omnigent/inner/codex_native_harness.py:1–9` 才包装 `CodexNativeExecutor`。

所以 `inner/loader.py` 不是本 BUG 的路由断点，它只负责读取 executor；也没有证据支持“loader 缺少 codex 映射”这个假设。

### 3.2 运行时已具备正确的 SDK 分支，但 native terminal 路径仍被触发

`omnigent/runner/app.py` 中可核对到：

- `8900–8901`：session 创建时从 `spec.executor.config["harness"]` 读取并 canonicalize；
- `9035–9038`：把解析后的 harness 交给 `process_manager.get_client()`；
- `13711–13716`：turn dispatch 再次遵循 `harness_override → config.harness → executor.type` 优先级；
- `18964–18968`：HTTP/配置解析路径同样保留该优先级；
- `9220–9288`：Codex native terminal 自动创建分支明确写着 `if harness_name == "codex-native"`；
- `16440–16465`：`_ensure_native_terminal_for_turn()` 通过 `native_terminal_name()`，裸 `codex` 正常应返回无 terminal 的 no-op。

但本 RUN 的真实 traceback 已到达 `terminals/registry.py:221`，再由 `inner/terminal.py:1882` 在 Windows 抛错。这证明运行时的某个 session/turn/terminal 入口把本应是 SDK `codex` 的请求带入了 native terminal 创建路径。当前最具体的越界入口是 `omnigent/runner/app.py:15870–15904`：只要请求带 `ensure_native_terminal=true` 且 `terminal=codex`，就直接调用 `_auto_create_codex_terminal()`；该入口本身没有先核对 session 的 resolved harness 是否确为 `codex-native`。正常的 SDK `codex` session 不应发出这个 marker，但一旦上游分类/复用状态错误，就会绕过 `9220` 的 native-only guard。持久 runner 日志是 traceback 尾部，缺少发出该请求的完整外层 frame；因此不能不负责任地声称“`runner/app.py:8900` 这一行必然漏读配置”。**可确认的根因是 harness 语义在 runtime terminal 边界发生了不一致/错误激活，具体应优先修复 `15870–15904` 的 resolved-harness 护栏，并用一次受控、可审计的日志/断言补齐调用者链。**

### 3.3 BUG-2 修复方案

后续实施卡应按以下顺序改动，当前不实施：

1. **集中解析，单一事实源**：在 runner 内提供一个共享的 `resolve_harness_dispatch(spec, override)`（可放在现有 runner harness 解析模块），返回 `raw_harness`、`canonical_harness`、`is_native`、`module`、`dispatch_mode`。session 创建、turn dispatch、session reattach、terminal endpoint 都调用同一解析结果，不再各自重算。
2. **保持语义分离**：
   - canonical `codex` 只能选择 `omnigent.inner.codex_harness`/`CodexExecutor`，只能构造 SDK/app-server client；
   - canonical `codex-native` 才能选择 `codex_native_harness`/`CodexNativeExecutor` 和 native terminal；
   - 不增加 `codex → codex-native` alias，不用 Windows 判断偷偷改写配置。
3. **加硬护栏**：`create_session_terminal()` 的 `15870–15904` 分支、`_auto_create_codex_terminal()`、`_ensure_native_terminal_for_turn()` 进入 terminal registry 前验证 resolved session harness 的 `is_native=True` 且 canonical id 为 `codex-native`（以及现有其他 native harness）。若裸 `codex` 到达此处，应记录结构化错误并立即返回，不得 fallback 到 tmux/PTY；上游也不得给 SDK session 发送 `ensure_native_terminal` marker。
4. **补足可审计日志/断言**：在 `app.py` 的 session、turn、process-manager、terminal 入口记录 `(executor.type, config.harness, canonical_harness, is_native, module, dispatch_mode, session_id)`；记录一次实际子进程 argv/模块，不记录 token。这样下一次 RUN 能直接证明“codex 未进入 registry”。
5. **保持 Windows native 禁止逻辑**：`inner/terminal.py:1882` 的拒绝不可删除或改成伪成功；可将错误信息改为结构化、可操作的“请使用 `harness: codex`”提示，但不能让 native TUI 在 Windows 假装支持。

建议涉及文件/影响面：

| 文件 | 后续改动意图 | 影响 |
|---|---|---|
| `omnigent/runner/app.py` | 统一 dispatch、`15870–15904` native ensure 护栏、审计字段 | 影响所有 harness 的 session/turn/terminal 生命周期；需回归 claude-native 与 codex-native |
| `omnigent/harness_plugins.py`、`omnigent/harness_aliases.py` | 仅在需要时补齐共享 resolver 所需的 canonical/capability API；不改变 `codex` 语义 | 影响 harness 注册与 alias；禁止引入裸 codex native alias |
| `omnigent/inner/codex_harness.py`、`codex_executor.py` | 原则上不改业务实现；仅补可验证的启动标识/测试 seam | 确认 `HARNESS_CODEX_PATH`、模型和 app-server 子进程继承 |
| `omnigent/terminals/registry.py`、`inner/terminal.py` | 保留 Windows 拒绝；必要时增加调用者/结构化错误 | 防止错误路径静默崩溃；不扩大终端支持范围 |
| `tests/` 中 runner/harness 测试 | 覆盖 codex 与 codex-native 分流及 Windows invariant | 防止回归；不改变 Gate 2 政策 |

### 3.4 BUG-2 测试要点

- parser/loader snapshot：`type=omnigent + config.harness=codex` 保留为 `codex`。
- dispatch snapshot：裸 `codex` 解析到 `omnigent.inner.codex_harness`/`CodexExecutor`，`is_native=False`；`codex-native` 解析到 native 模块，`is_native=True`。
- Windows guard：模拟裸 `codex` 的 session/turn，断言不会调用 `TerminalRegistry.launch`；模拟显式 `codex-native`，断言在 Windows 得到清晰的不支持错误，而不是启动半截 runner。
- Terminal ensure guard：对 `create_session_terminal()` 发送 `terminal=codex` 的请求，若 session resolved harness 为裸 `codex`，断言拒绝/不调用 `_auto_create_codex_terminal()`；显式 `codex-native` 才允许进入 native 分支。
- spawn-env：断言 `HARNESS_CODEX_PATH`、`HARNESS_CODEX_MODEL=gpt-5.6-sol` 在 server → host → runner → Codex child 链上可见；凭据只验证存在性/脱敏，不落盘值。

## 4. BUG-1 方案：选择自定义 D（B + A，窄化 C）

### 4.1 根因

`omnigent/host/connect.py:1878` 的连接成功消息包含 Unicode `✓`。Windows 中文代码页下，host daemon 子进程 stdout 仍可能是 GBK；而 `connect.py:261` 的 `_RUNNER_ENV_ALLOWLIST`、`omnigent/cli.py:354` 的 `_LOCAL_DAEMON_ENV_ALLOWLIST` 都没有转发 `PYTHONUTF8`，父进程设置无法稳定传给 daemon，于是打印阶段触发 `UnicodeEncodeError`，WS/tunnel 断开并进入重连循环。

### 4.2 方案

选 **自定义 D = B + A**，并只在必要处采用窄化的 C：

1. 将 `PYTHONUTF8` 加入 `connect.py` 的 runner env allowlist 与 `cli.py` 的 local-daemon allowlist。
2. 同时加入 `PYTHONIOENCODING`（值由调用环境提供时才转发），覆盖显式 stdout/stderr 编码配置；不扩大到任意环境变量。
3. 把用户可见的连接 banner 从 `✓`、长破折号等非 ASCII 字符改为 `[OK]` 和 ASCII 标点。这样即使父进程未设置 UTF-8，也不会在成功路径崩溃。
4. 不采用全局 `errors="replace"` 作为主要修复；它会掩盖诊断日志损坏。若未来确需兼容第三方输出，只能在明确的用户界面包装层局部使用，并保留原始结构化日志。

### 4.3 影响与测试

影响仅限 host/local daemon 的环境传递与连接提示，不改变认证、代理、TUN 或模型请求。测试应覆盖：allowlist 包含两项、子进程在 GBK locale 下连接 banner 不崩、Unicode 诊断文本不被静默替换、敏感环境变量仍被排除。

## 5. BUG-3 方案：本轮纳入，但与 BUG-2 分阶段实施

### 5.1 根因

`omnigent/server/routes/sessions.py:14212–14222` 的 multipart 分支调用 `_create_bundled_session_from_multipart()` 后直接授予权限、广播并返回。`14489–14553` 解析了 `SessionCreateMetadata`（其中已有 `host_id`），但只在有 `parent_session_id` 时继承 runner；没有复用 JSON 路径 `14384–14482` 的 host authorization、原子 `runner_id` 绑定、`HostLaunchRunnerFrame` 发送和 30s 结果等待。因此 multipart `POST /v1/sessions` 可以返回 201，却永远没有 runner/turn。

### 5.2 方案

推荐实现方案 A：当 multipart metadata 带 `host_id` 时，执行与 JSON 路径一致的 host launch 语义；不静默忽略该字段。建议把 JSON 路径现有逻辑抽成共享 helper，至少包含：

1. `resolve_host_launch()` 权限/归属校验；
2. `conversation_store.set_runner_id()` 的 `WHERE runner_id IS NULL` 原子绑定；
3. 发出 `HostLaunchRunnerFrame`，传递 session/workspace/harness；
4. 等待 host launch future，设置明确的 30s 超时；
5. 失败时写入可见的 session/launch error，不返回“看似成功、实际 idle”的 201；
6. 与 parent-session runner inheritance、managed host、重复请求并发保持现有语义。

如果产品最终不希望 multipart 自动 launch，则必须采用方案 B：schema/API 文档明确禁止带 `host_id`，并在请求时返回 4xx；不能继续接受 `host_id` 后静默返回 idle session。本项目 full-run 需要 host launch，故本方案选择 A。

### 5.3 BUG-3 测试要点

- multipart + `host_id`：201 后恰好一次 launch、session 绑定正确 runner、host 收到 frame。
- host 不存在/无权限/超时/重复绑定：返回结构化错误，不能伪装成成功 idle。
- multipart 无 `host_id`、parent inheritance、JSON 旧路径：保持原行为。
- 并发两次创建/重试：只有一次 `runner_id` 成功绑定，不能重复 spawn。

## 6. 后续实施顺序与验证计划

本文件不执行以下步骤；它们应由后续独立实施/验证任务卡安排。

### 阶段 1：静态与定向测试

1. 先实施 BUG-1 的 allowlist/banner 修复并运行 host/CLI 定向测试。
2. 实施 BUG-2 resolver 与 terminal guard，运行 parser、runner dispatch、Windows guard、Codex executor spawn-env 测试。
3. 实施 BUG-3 multipart host-launch helper 与 API 并发/错误测试。
4. 运行 `py_compile`/`node --check`（如变更涉及对应脚本）及定向 pytest；不改变 240s watchdog，不启动完整 Gate 2 六轮。

### 阶段 2：一次全链路 full-run（新 RUN_ID）

使用全新 evidence 根，继续固定：

- 模型 `gpt-5.6-sol`；native CLI 0.146.0、任务卡约定的绝对路径与 SHA；
- `HARNESS_CODEX_PATH` 在 server/host/C 启动前注入，并记录子进程继承结果；
- 240s idle watchdog 原值；TUN 只观察 start/end，不开关；
- 凭据全部 `[REDACTED]`，旧 evidence 不拼接。

执行顺序：

1. precheck 结束并确认无竞争 Codex 进程/端口；冻结 source/binary identity。
2. 启动 server，等待 READY；启动 host，确认 online 且连接 banner 不发生 GBK 崩溃。
3. 用一次真实 `omnigent run <agent_dir> -p "Reply with CONTROLLER_OK and stop." --server <url>`，不重试、不跑完整 Gate 2。
4. 实时记录 multipart/JSON session 创建、`host_id`、runner launch frame、runner_id 绑定、runner PID、resolved harness、module、terminal guard、Codex child PID/path/version/SHA、turn terminal 与 assistant sentinel。
5. 业务验收必须同时满足：
   - multipart（若使用）不再停留在只有 201 的 idle；host launch 恰好一次；
   - resolved harness 为 `codex`，module 为 `omnigent.inner.codex_harness`，`is_native=False`；
   - runner 日志中无 `terminals.registry.launch`/`inner.terminal.create_terminal_instance`；
   - `HARNESS_CODEX_PATH` 子进程确实为固定 native 0.146.0，且出现真实 Codex child；
   - 产生真实 assistant item/final sentinel `CONTROLLER_OK`、`turn/completed`，C exit=0，未触发 240s idle。
6. 失败时按边界分类：若仍无 runner，优先查 BUG-3；若 runner 已启动但进入 terminal，查 BUG-2 resolver/guard；若 host 断线，查 BUG-1；只有三者均通过后才继续判断认证、网络、relay 或模型问题。
7. finally 后执行 PID dead、端口释放、runtime 删除、`.codex-tmp`、required-check、manifest、最后 leak-scan；evidence 持久保留，报告只能在 final-check/leak-scan 后写入。

### 阶段 3：回归与 Gate 边界

补跑 SDK harness、显式 native harness、JSON session、multipart session、Windows host reconnect 的回归集合。即使 full-run 得到 `CONTROLLER_OK`，也只能说明本修复链路通过；Gate 1 仍是相对 main 的 PASS，Gate 2 r4 仍需独立验收，不能据此 merge。

## 7. 风险、回滚与交付边界

- 不要把 `codex` alias 到 `codex-native`，否则会把 Windows 不支持的 tmux/PTY 再次引入。
- 不要删除 `inner/terminal.py:1882` 的平台拒绝；应让错误更早、更清晰、更可审计。
- BUG-3 helper 若改变 JSON 路径，必须保持原子绑定和 managed-host 分支；建议先抽共享逻辑，再分别覆盖两种 content type。
- 本文仅为排查确认与修复方案；不改 `omnigent/`、`tests/`、政策、STATUS、配置、TUN 或认证，不重跑 D0/D1/D2/full Gate 2，不 commit/push/merge/tag。后续实施必须另发任务卡并独立生成 evidence。
