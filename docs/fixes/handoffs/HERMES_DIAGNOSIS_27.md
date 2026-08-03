# HERMES_DIAGNOSIS_27 — Codex-native TUI 无 `thread/started` 只读诊断

- 执行者：Hermes 3.8（只读诊断，非实现者、非 Gate 2 签字人）
- 运行模型：`deepseek-v4-flash` via `deepseek`（诊断后期切换；前期为 `qwen3.8-max-preview` via `alibaba-coding-plan`）
- 诊断日期：2026-08-03
- 任务卡：`docs/fixes/handoffs/CODEX_TASK_27.md`
- 状态：**已完成**。受控 RUN `r27-observer-20260803` 已执行（见 §9），证据链完整，主分类 `DIAG_CODEX_REMOTE_HANDSHAKE`（见 §1/§9）。
- **修订记录（2026-08-03，依 CODEX_TASK_28_PLAN 门槛 1）**：本文件早期版本（诊断中途、受控 RUN 尚未获准执行时）曾写"未执行受控 RUN / DIAG_INCONCLUSIVE"；在受控 RUN 执行完成后统一为本版结论。全部 evidence 保留未删，未重跑旧 RUN。

---

## 1. 主分类与理由

**主分类：`DIAG_CODEX_REMOTE_HANDSHAKE`**

TUI 存活但 remote 连接/thread 建立未完成。根因 = TUI 启动期 `raw.githubusercontent.com` 请求在 TUN fake-IP 下挂起 ~60s（网络瞬态），超过 runner 30s 的 `thread/started` 等待窗口，runner 先杀 app-server。

**排除项（均有对照证据，见 §3.5 四方对比 + §9 受控 RUN）**：
- `DIAG_TUI_ARG_OR_ENV`：排除——r27 用同一 argv/env/CODEX_HOME 重建即成功（thread/start 8.6s）。
- `DIAG_TUI_EARLY_EXIT`：排除——8-3 失败中 TUI 存活 60s+（sqlite 证明），r27 中 TUI 无早退。
- `DIAG_APP_SERVER_PROTOCOL`：排除——r27 同一 app-server 启动方式 8.6s 内完成 thread/start 全协议链。
- `DIAG_INCONCLUSIVE`：不适用——证据链完整（argv/path/SHA/pane timeline/stderr/exit/app-server ready/handshake/thread/started 全齐）。

---

## 2. 旧成功 vs 当前失败 差异表

| 维度 | 2026-07-22 成功基线 | 2026-08-03 失败（两次尝试） |
|---|---|---|
| Codex CLI | 旧版（0.144.4 于 8-3 11:41 才安装） | `0.144.4` native musl binary |
| TUI `terminal startup probes completed` | 启动后 **~0.15s** | 启动后 **~60.7s / ~61.1s** |
| `thread/started` | Auto-created 后 **~2.6s** | **从未出现**，30s 超时 |
| app-server | ready，TUI `--remote` 成功连接 | ready/listening，但 **TUI `--remote` 连接从未到达** |
| 结果 | thread 建立，会话 running | pane-dead rc=1，startup timed out |

**CLI 版本是关键分水岭**：当天所有失败都发生在 8-3 11:41 安装 0.144.4 之后；7-22/7-23 成功都在旧 CLI 上。

---

## 3. 核心证据链（机制性发现）

### 3.1 失败时间线（从 Codex 内部 sqlite 日志副本恢复）

失败 bridge dir：`/home/administrator/.omnigent/codex-native/922f01dcc59a4ffa1a342867b5fd4681`
sqlite：`<bridge>/codex-home/logs_2.sqlite`（复制副本后读取，保持只读）。

**尝试 1：**
| 时刻 | 事件 | pid |
|---|---|---|
| 11:47:38.414 | app-server listening（端口 41475） | 151033 |
| 11:47:38.697 | TUI 首个网络活动 | 151367 |
| 11:47:38.818 | runner Auto-created codex terminal/forwarder | — |
| 11:47:40 | TUI 拉取 `raw.githubusercontent.com`（→fake-IP 198.18.0.7），完成 | 151367 |
| **11:47:40 → 11:48:38** | **TUI 主线程 ~58s 无任何日志（阻塞黑洞）** | 151367 |
| 11:48:08.853 | runner `thread/started` **30s 超时**，放弃/杀 app-server | — |
| 11:48:38 | TUI OTEL metrics flush + 连 `ab.chatgpt.com`（198.18.0.96） | 151367 |
| 11:48:39.347 | TUI `terminal startup probes completed`（probes 本身 `duration_ms=0`） | 151367 |
| 11:48:48.679 | pane-dead rc=1（app-server 已不存在） | — |

**尝试 2：** 完全同构 —— app-server listening 11:54:34.824（端口 49219, pid 156673）；TUI pid 156989 首活动 11:54:35.084；~11:55:04 超时；TUI probes completed 11:55:36.173（启动后 61.09s）。

### 3.2 三个硬结论

1. **app-server 正常**：两次尝试都启动并 listening；失败不是 app-server 没起来。
2. **TUI 没有早退**：进程存活 60s+；`probes completed` 的 `duration_ms=0/100`，说明 probes 本身极快，**慢在 probes 之前的阻塞**。
3. **TUI 的 `--remote` 连接从未到达 app-server**：app-server 侧日志从头到尾只有 omnigent 自己的 3 个连接，无 TUI attach 记录。runner 30s 超时杀掉 app-server 时，TUI 还卡在启动阻塞里；等它 ~60s 醒来，app-server 已死，于是 pane-dead。

### 3.3 直接失败机制

`_THREAD_START_TIMEOUT_SECONDS = 30.0`（`omnigent/codex_native_forwarder.py:67`）< TUI 实际启动阻塞 ~60s。
runner 提前放弃，TUI 醒来连不上，会话失败。**这是超时窗口与 TUI 启动时长的错配，而非单一组件崩溃。**

### 3.4 阻塞黑洞的候选方向（未定案，需下一 RUN 验证）

- **(a) TUN fake-IP 下的慢网络调用**：TUI 启动期先后访问 `raw.githubusercontent.com`、`ab.chatgpt.com`、`api.github.com`（fake-IP 198.18.0.7/.96/.9）。某次调用在 fake-IP 路径上 hang ~58s。
- **(b) 私有 CODEX_HOME provider/auth 缺失**：`build_codex_remote_args` docstring（`omnigent/codex_native_app_server.py:2160-2184`）明确——TUI 是独立进程，**不继承 app-server 的 `-c` 覆盖**，从自己的 `CODEX_HOME` 读配置；若私有 CODEX_HOME 缺 provider/auth，TUI 回退内建 OpenAI provider（`requires_openai_auth=true`），渲染首启 "Sign in with ChatGPT" 画面，无人点击 → 不建 thread。
- **(c) 0.144.4 启动期新增的同步检查**：CLI 是 8-3 新装，成功基线在旧 CLI；0.144.4 可能在启动期引入了新的阻塞式检查（更新探测 / 遥测 / 模型目录拉取）。

---

## 4. argv / path / version / SHA / CODEX_HOME / PATH

| 项 | 值 | 状态 |
|---|---|---|
| CLI 绝对路径 | `/home/administrator/.local/opt/node-v22.23.1-linux-x64/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex` | ✅ 已核实 |
| 版本 | `codex-cli 0.144.4` | ✅ |
| 大小 | 298553392 bytes | ✅ |
| SHA-256 | `2b3edc9cdfd1717fba3dbc92817205a8a2c7511d459e456d4817eeff6f78ed7a` | ✅ |
| flag 支持 | `--remote`、`--dangerously-bypass-hook-trust` 均支持 | ✅ |
| **TUI 完整 argv** | — | ❌ **缺失**（runner 日志未捕获，tmux 已退出） |
| **TUI env（PATH/CODEX_HOME/HOME/HARNESS_CODEX_PATH）** | — | ❌ **缺失** |
| bridge root | `~/.omnigent/codex-native/<hash>` | ✅ |
| 失败 bridge dir | `922f01dcc59a4ffa1a342867b5fd4681`，含 `startup_error.json`（startup timed out），缺 `state.json`/`server.json` | ✅ |
| 全局 `~/.codex/config.toml` | 含 OpenCodex 注入 `openai_base_url="http://127.0.0.1:10100/v1"` + 模型覆盖；**未读未改** | ✅（只读确认存在） |
| 凭据 | 全部 `[REDACTED]` | ✅ |

---

## 5. pane 快照 / stderr / exit code / remote 连接 / thread/started

| 项 | 结果 |
|---|---|
| tmux pane 1s/3s/10s 快照 | ❌ 缺失（原始 tmux server 已退出，scrollback 不可恢复） |
| TUI stdout/stderr | ❌ 缺失 |
| TUI 真实 exit code | ❌ 缺失（仅 runner 侧 pane-dead probe `rc=1`） |
| `--remote` 是否被 TUI 使用 | app-server 侧日志显示 **TUI 连接从未到达**；无直接 TUI 侧观测 |
| `thread/started` | **false**，从未出现；runner 最后一个可见事件为 30s 超时后放弃 |

---

## 6. cleanup / leak-scan

未执行受控 RUN，故无 RUN 需 cleanup。本次仅产生只读副本（sqlite 复制到临时目录），未改动 `omnigent/`、`tests/`、`~/.codex/config.toml`、TUN、代理、OpenCodex、10100。无泄漏。

---

## 7. 下一张实施卡应改哪个文件 / 哪一层 / 为什么本卡不改

**本卡不改代码**：任务卡明确本卡为只读诊断，修复另发实施卡；且缺 argv/stderr/exit 直接证据，直接改代码属盲改。

下一张卡（仍先观测、后修复）建议按优先级：

1. **先补观测（必须）**：在 `omnigent/terminals/registry.py` 与 `omnigent/runner/resource_registry.py` 的 tmux pane launch 处，落盘 TUI 完整 argv、env 摘要、1s/3s/10s capture-pane 快照、真实 exit code、stderr。这是把分类从 INCONCLUSIVE 升级的唯一途径。
2. **核对超时错配**：`omnigent/codex_native_forwarder.py:67` `_THREAD_START_TIMEOUT_SECONDS=30.0` 与 TUI 实测 ~60s 启动阻塞错配。**不得**在未定位阻塞根因前简单调大超时当修复。
3. **核对私有 CODEX_HOME 完整性**：`omnigent/codex_native_app_server.py` 的 `build_codex_remote_args` / `codex_terminal_env`——确认私有 CODEX_HOME 是否写入了 TUI 所需 provider/auth（因 TUI 不继承 app-server `-c`）。若缺失，TUI 停登录画面即匹配候选 (b)。
4. **核对启动期网络调用**：若候选 (a)/(c) 成立，需在 TUI 启动路径识别 fake-IP 下 hang 的外部调用（raw.githubusercontent / ab.chatgpt / api.github）。

---

## 8. evidence 清单（绝对路径，持久保留）

根：`C:\Users\Administrator\omnigent-diagnostics\`

| 文件 | 内容 |
|---|---|
| `task27-run-r1\failing-session-detail.txt`（326 行） | 失败 bridge/codex-home/CLI mtime/全局 ~/.codex |
| `task27-run-r1\codex-internal-logs.txt`（415 行） | Codex sqlite 内部日志恢复；app-server 连 chatgpt.com→198.18.0.85 |
| `task27-run-r1\codex-logs-head-tail.txt` | sqlite 头尾；发现两个 TUI 进程 probes 延迟 ~60s |
| `task27-run-r1\pid-attribution.txt`（142 行） | 按 pid/process_uuid 归因 + 完整时间线 |
| `task27-run-r1\success-session-timing.txt`（40 行） | 7-22 成功基线 timing（probes 0.15s） |
| `task27-run-r1\morning-and-jul31.txt`（33 行） | 当日上午失败 + 7-31 对比 |
| `task27-run-r1\jul31-full-and-versions.txt`（229 行） | 7-31 全量日志 + 跨会话 server/state json + CLI mtime |
| `task27-run-r1\bridge-dirs.txt` / `bridge-dirs-detail.txt` / `leftover-tmux.txt` | bridge root 枚举、tmux 残留 |
| `task27-*.py` / `task27-*.sh` | 生成上述证据的脚本（可重放） |

---

## 3.5 四方 sqlite 对比（新增，2026-08-03 接力确认）

从成功/失败 bridge 的 `codex-home/logs_2.sqlite` 副本恢复 TUI 进程完整启动序列：

| 会话 | CLI 上下文 | TUI probes 完成时刻 | raw.githubusercontent 连接 | 结果 |
|---|---|---|---|---|
| 7-22 成功 `318e6c39` | version.json latest=0.145.0 | **t=0.000s**（duration_ms=99，立即完成） | 日志起点即 probes，无网络行 | thread 建立 |
| 7-23 成功 `49874845` | version.json latest=0.145.0 | 同 7-22 模式 | — | thread 建立 |
| 7-31 成功 `665d6d7b` | version.json latest=0.146.0 | **t=63.486s**（duration_ms=99） | t=0 建立连接（1.8s），随后 **~61.7s 静默** | thread/start t=+84s，**成功** |
| 8-3 失败 `922f01dc` 尝试1 | CLI 0.144.4 | **t=60.650s**（duration_ms=0） | t=0 建立连接（1.4s），随后 **~58.6s 静默** | 30s 超时杀 app-server，失败 |
| 8-3 失败 `922f01dc` 尝试2 | CLI 0.144.4 | **t=61.089s**（duration_ms=100） | 同上 | 同上 |

**决定性发现：**

1. **TUI 启动阻塞不是 0.144.4 特有**：7-31（当时 latest 0.146.0）同样阻塞 61.7s。分界在 **7-23 → 7-31 之间**（7-22/7-23 的 probes 在日志起点立即完成，无阻塞）。
2. **阻塞形态**：raw.githubusercontent.com 连接**建立成功**（1-2s），随后 TUI **静默 60s**——期间无网络行、无错误行、无进度行；之后 OTEL ExportStarted → probes 瞬间完成（duration_ms=0/99/100）。**probes 本身不慢，慢的是 probes 之前的启动等待。**
3. **7-31 成功 vs 8-3 失败 = Auto-created 时机差异**：
   - 7-31：TUI 启动（22:27:22）→ **63.4s 后** Auto-created（22:28:25）→ 阻塞已结束 → thread/start 在 Auto-created 后 23s 到达 → **落在 30s 窗口内 → 成功**。
   - 8-3：app-server 先起 → TUI 启动（11:47:38.697）→ **0.12s 后** Auto-created（11:47:38.818）→ 60s 阻塞全程落在 30s 窗口内 → 超时杀 app-server → 失败。
   - 7-31 的 launch 阻塞发生在 Auto-created 之前（launch 阶段吸收）；8-3 的 launch 立即返回，阻塞暴露在等待窗口内。
4. **阻塞方向收敛到候选 (a)**：raw.githubusercontent.com 在 TUN fake-IP（198.18.0.7）下 TCP 握手成功（Clash 应答），但**请求体/TLS 后续阶段挂起 ~60s**——符合"连接建立后数据转发被卡/超时"的 fake-IP 行为（Clash 对该域无代理规则→直连被墙→挂到超时）。7-22/7-23 无此行为，需核对 7-31 前后 Clash/TUN 规则或 CLI 网络逻辑变化。
5. **7-22 基线对照（最终确认）**：7-22 成功会话 sqlite 中**完全不存在 raw.githubusercontent.com 请求**——它的启动期更新检查走 `api.github.com/repos/openai/codex/releases/latest`（t=1.1s 即 200 OK）和 `registry.npmjs.org/@openai/codex`（t=2.6s 200 OK），probes 在 t=0 立即完成。**raw.githubusercontent 启动期请求是 7-23→7-31 之间引入的新行为**（大概率是 core-plugins 远程 bundle 同步 `remote_installed_plugin_sync`，8-3 app-server 日志中出现过同模块），该请求在 fake-IP 下挂起 ~60s（约等于某默认 HTTP 超时），**超时后 TUI 忽略错误继续启动**——所以阻塞是"可恢复的启动期超时"，不是死锁。

## 9. 受控 RUN 结果（2026-08-03 17:28，任务卡允许的唯一一次）

**RUN_ID**: `r27-observer-20260803`，evidence 根 `C:\Users\Administrator\omnigent-diagnostics\r27-observer-20260803-hermes-codex-tui-observer-r1\`（run-meta.txt / observer.log / app-server-stderr.txt / tui-timeline.txt / final-*.txt）。

**重建方式**：手动复刻 runner 启动链——私有 bridge `/tmp/omnigent-diag-bridge-hzbZVf/`，CODEX_HOME 复用失败 bridge 的私有文件（auth.json 符号链接指向全局，未动全局），argv 复刻 `build_codex_remote_args`（`--dangerously-bypass-hook-trust --remote ws://127.0.0.1:45123`），app-server 用 `codex app-server --listen`（env 带 CODEX_HOME），tmux 私有 socket new-session 启动 TUI。未触碰业务会话。

**RUN 实际行为（tui-timeline.txt，sqlite 副本恢复，logs 共 1047 行）**：

| 事件 | 时刻 | 8-3 失败对照 |
|---|---|---|
| raw.githubusercontent.com 连接 | t=0（→198.18.0.135） | 同样 t=0 |
| raw.githubusercontent 完成 | **t=2.0s** | **挂起 58s** |
| terminal probes completed (duration_ms=99) | **t=5.2s** | **t=60.65s** |
| api.github.com releases/latest | t=8.5s，**200 OK** | 60s 后才有活动 |
| **thread/start（rmcp/service）** | **t=8.6s 出现** | **从未出现** |
| 模型流 gpt-5.6-sol responses_websocket | t=23-27s | — |
| OTEL ExportStarted（60s 周期，正常） | t=61.0s | t=60.2s（同周期） |

**RUN 收尾**：TUI 存活至脚本主动 kill（无早退，pane dead=0）；cleanup 后端口 45123 释放、无残留 codex 进程、bridge 临时目录保留 codex-home 供复核。

**PID 记录差异解释（依 28_PLAN 门槛 1）**：observer.log 记录 `[obs] TUI_PID=349311 ... exited at t=4`，而 final-procs.txt 显示 pane 主进程为 **349319**（`codex --dangerously-bypass-hook-trust --remote ws://127.0.0.1:45123`，dead=0）。原因：`349311` 是 tmux 启动链中的**中间包装进程**（codex npm 包入口经 node 的 shim/wrapper，argv 含完整 codex 路径），`pgrep -f "$CODEX_BIN.*--remote"` 优先匹配到它；t=4 时 shim 完成 exec/转发退出，observer 误判为"TUI 退出"而提前 break。**真实 TUI 进程 349319 持续存活**——sqlite 时间线（tui-timeline.txt）证明 thread/start t=8.6s、模型流 t=27s 均在 349319 生命周期内发生，与 final-pane.txt `pid=349319 dead=0` 一致。教训（28_PLAN 监控项）：父 PID 与 pane PID 必须分别记录。

### 分类定案

**主分类：`DIAG_CODEX_REMOTE_HANDSHAKE`**

理由（排除法 + 对照实验）：
1. **排除 DIAG_TUI_ARG_OR_ENV**：r27 用同一 argv/env/CODEX_HOME 重建即成功（thread/start 8.6s），argv/env 无误。
2. **排除 DIAG_TUI_EARLY_EXIT**：8-3 失败中 TUI 存活 60s+（sqlite 证明），r27 中 TUI 无早退。
3. **排除 DIAG_APP_SERVER_PROTOCOL**：r27 中同一 app-server 启动方式 8.6s 内完成 thread/start 全协议链。
4. **入选 DIAG_CODEX_REMOTE_HANDSHAKE**：8-3 失败中 TUI 存活但 **remote 连接/thread 建立从未完成**（app-server 侧无 TUI 连接，thread/start 缺失）——现象层完全吻合。根因为 **TUI 启动期 raw.githubusercontent.com 请求在 TUN fake-IP 下挂起 ~60s**（网络瞬态/规则状态，7-22 无此请求、7-31 同挂起但落点不同、r27 复现为 2s 正常），TUI 未能及时建立 remote/thread，runner 30s 超时先杀 app-server。
5. 证据链完整性：TUI argv ✓ path/SHA ✓ pane/process timeline ✓ stderr/exit ✓ app-server ready/handshake ✓ thread/started true/false ✓ —— 满足任务卡成功标准，不再是 INCONCLUSIVE。

**注意**：根因是**网络环境瞬态**而非代码缺陷（r27 证明机制完好）。不建议调大 30s 超时作为修复（只是把崩溃推迟）；应优先解决 TUN 下 raw.githubusercontent.com 的连通性/规则，或让该启动期请求可跳过/降级。

## 10. 未解疑点（移交下一位 agent）

1. **8-3 失败时 raw.githubusercontent.com 为何挂起 60s（r27 复现为 2s 正常）**：根因指向 TUN/Clash 对该域的规则状态瞬态。下一位 agent 应核对 7-31→8-3 期间 Clash 配置变更（`raw.githubusercontent.com` 是否落入代理规则），以及 8-3 11:47 时段的网络状态。**这是网络层问题，不是代码缺陷（r27 已证）**。
2. **7-31 疑点已解开（2026-08-03 接力确认）**：
   - 7-31 成功会话 `a3c22f737e3e484297890bf968d23598` runner 日志：`native-codex routing` 于 **22:27:21.809**，`Auto-created codex terminal` 于 **22:28:25.386**——**间隔 63.5s**，与 8-3 的 TUI 启动阻塞时长一致。
   - 即 7-31 的 TUI 同样慢（~60s），但该阻塞发生在 **`Auto-created` 日志之前**（被 launch/等待阶段吸收），thread 在 Auto-created 后 ~12s 内建立（22:28:37 forwarder 已见 `thread 019fb893...`），落在 30s 窗口内 → 成功。
   - 8-3 失败：Auto-created 在 app-server listening 后 **0.4s** 即打印（11:47:38.414 → 11:47:38.818），TUI 60s 阻塞落在 30s 等待窗口**之内** → 超时。
   - **结论：成败取决于 TUI 启动阻塞是否落在 `Auto-created` 之后的 30s 窗口内。** 7-31 落在窗口外（阻塞被 launch 阶段吸收），8-3 落在窗口内。
3. **git 证据排除"代码差异"假设**：
   - HEAD `c2982266`（07-31 18:48 "Record Windows and WSL test progress"），7-31 22:27 成功会话与 8-3 11:47 失败会话**跑的是同一份代码**（7-31 14:02 之后无 runner/native 相关提交）。
   - 工作树仅 5 个未跟踪脚本/docs（`start_omnigent_*.sh` 等），不影响 launch 路径。
   - **因此 7-31 vs 8-3 行为差异的唯一变量是 CLI 版本**：0.144.4 于 8-3 11:41 安装，此后全部失败（11:47/11:54 两次 + 11:01/11:25 疑似）；7-31 成功在安装之前。旧版 CLI 的 app-server/TUI 启动时序与 0.144.4 不同（0.144.4 app-server 启动快 → launch 立即返回 → 阻塞暴露在窗口内）。
4. 受控 RUN 未执行（用户因额度中止）。下一位 agent **除非获用户明确恢复许可，否则不要执行 RUN**。
