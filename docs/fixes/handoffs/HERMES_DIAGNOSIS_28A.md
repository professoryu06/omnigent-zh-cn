# HERMES_DIAGNOSIS_28A — Codex TUI 启动期网络监控（用户重试 RUN）

- 执行者：Hermes 3.8（只读监控执行者，非实现者、非 Gate 2 签字人）
- 运行模型：`deepseek-v4-flash` via `deepseek`
- 监控日期：2026-08-03
- 任务卡：`docs/fixes/handoffs/CODEX_TASK_28A_MONITOR.md`
- 前置：`docs/fixes/handoffs/CODEX_TASK_28_PLAN.md`（门槛 1 修订已完成，见 §7）

---

## 1. RUN 身份与证据

- **RUN_ID**：`r28a-observer-20260803`
- **用户重试会话**：`24385a29eafb46f1a2d88066f928e391`（Web UI 创建）
- **evidence 根**：`C:\Users\Administrator\omnigent-diagnostics\r28a-observer-20260803-hermes-codex-tui-monitor-r1\`（**全部存在，未删除**）
- evidence 文件：
  - `manifest.txt`（RUN 元数据 + 检测日志）
  - `tui-timeline-28a.txt`（TUI 启动时间线，sqlite 副本恢复，logs 共 1133 行）
  - `runner-events.txt`（runner 日志关键事件 60KB）
  - `proc-samples.txt`（进程采样 146KB，PID 链）
  - `ports-during.txt`（端口采样）
  - `bridge-file-timeline.txt` / `final-*.txt` / `pre-*.txt` / `verification-evidence.txt`
- 前置说明：本卡曾有两个待命窗口——窗口 1（17:52–18:08）无用户重试，按任务卡记该窗口 `DIAG_INCONCLUSIVE`；窗口 2（18:09 起）检测到用户重试，**本报告基于窗口 2**。

## 2. 启动身份

| 项 | 值 |
|---|---|
| CLI 版本 | `codex-cli 0.144.4` |
| CLI 绝对路径 | `/home/administrator/.local/opt/node-v22.23.1-linux-x64/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex` |
| CLI size | 298553392 bytes |
| SHA-256 | `2b3edc9cdfd1717fba3dbc92817205a8a2c7511d459e456d4817eeff6f78ed7a` |
| app-server 端口 | `51481`（ws://127.0.0.1:51481） |
| app-server PID | **363209**（真实 binary）← 父 363201（node shim） |
| TUI pane PID | **363553**（真实 binary）← 父 363526（node shim）← 363525（tmux） |
| TUI 完整 argv（脱敏） | `codex -c model_provider="openai" -c mcp_servers.omnigent.command=".../python" -c mcp_servers.omnigent.args=["-m","omnigent.claude_native_bridge","serve-mcp","--bridge-dir","<bridge>"] --dangerously-bypass-hook-trust --remote ws://127.0.0.1:51481` |
| CODEX_HOME | `/home/administrator/.omnigent/codex-native/6ec25c30fefea53604e03a0af29c2c35/codex-home` |
| bridge 目录 | `/home/administrator/.omnigent/codex-native/6ec25c30fefea53604e03a0af29c2c35` |
| 凭据 | 全部 `[REDACTED]` |

注：真实 runner 的 TUI argv 含 `-c model_provider="openai"` 等 config_overrides（r27 手动重建未含，但不影响启动结论）。

## 3. 启动时间线（sqlite 副本恢复，相对 TUI 启动 t=0）

| 事件 | 相对时刻 | 绝对时刻（CST） | 判定阈值 |
|---|---|---|---|
| raw.githubusercontent.com 连接开始 | t=0.000s | 18:09:21.615 | — |
| raw.githubusercontent.com **完成**（checkout dropped） | **t=1.090s** | 18:09:22.705 | ≤10s ✅ |
| terminal probes **completed**（duration_ms=99） | **t=5.193s** | 18:09:26.808 | ≤10s ✅ |
| api.github.com releases/latest | t=7.144s，**200 OK** | 18:09:28.759 | ✅ |
| initial frame scheduled（bootstrap_ms=825） | t=6.094s | 18:09:27.709 | ✅ |
| **thread/start**（rmcp/service，app-server 侧） | **t=9.198s** | 18:09:30.813 | ≤30s ✅ |
| runner 侧 `thread/started` 事件 | Auto-created 后 ~6s | **18:09:27.786** | ≤30s ✅ |
| 模型流 gpt-5.6-sol responses_websocket | t=18.587s | 18:09:40.203 | ✅ |
| 用户输入分发（thread 019fc719-…） | t=24.9s | 18:09:46.483 | ✅ |
| websocket client connected（另一个 peer） | t=37.2s | 18:09:58.819 | ✅ |
| plugin 远程同步 completed（不阻塞启动） | t=86.0s / 95.2s | 18:10:47 / 18:10:56 | ✅ |

**runner 侧关键事件（runner 日志）**：
- 18:09:20.774 `native-codex routing: Codex CLI login (subscription provider 'codex'; Codex is logged in)`
- 18:09:21.261 app-server stderr `listening on: ws://127.0.0.1:51481` + `readyz` + `healthz`
- 18:09:21.799 `Auto-created codex terminal + forwarder for session 24385a29…`
- **18:09:27.786 `thread/started`**（Auto-created 后 **5.99s**）
- 无 TimeoutError、无 startup_error、无 pane dead

## 4. Clash/TUN 只读状态

- 本 RUN 期间**未修改**任何 TUN/Clash/代理规则（任务卡硬约束）。
- 观察事实：raw.githubusercontent.com 解析到 TUN fake-IP 段（198.18.0.x），TCP/TLS 连接**建立并完成请求 t=1.09s**——与 8-3 失败时（挂起 58s）形成对照，与 r27 受控 RUN（2s 完成）一致。fake-IP 路径本身工作正常，本次无网络侧阻塞证据。
- 未读取 Clash 配置内容（任务卡只要求记录命中规则/代理直连/fake-IP 的观察；本次请求正常完成，无规则异常信号）。

## 5. Bridge 与 cleanup

| 文件 | 状态 |
|---|---|
| `state.json` | ✅ 存在（thread_id `019fc719-8aa5-7731-b6e3-757003c7f77c`，socket ws://127.0.0.1:51481） |
| `server.json` | ✅ 存在（url http://127.0.0.1:42419，pid 363787） |
| `startup_error.json` | ❌ **不存在**（成功信号） |
| `bridge.json` / `mcp_startup.json` / `tool_relay.json` | ✅ 存在 |

**cleanup / leak-scan**：用户会话**仍在活跃运行**（监控窗口结束时 TUI 363553 与 app-server 363209 存活 ~3 分钟，keepalive 正常；端口 51481 持续监听；runner 无退出记录）。因此本 RUN **无 cleanup 事件**（会话未结束），leak-scan 意义上无残留异常——所有进程/端口均为用户当前活动会话的正常组成部分。监控者未执行任何 kill/cleanup 操作（只读纪律）。

## 6. 唯一分类

### 主分类：`READY`

依据（对照任务卡判定标准）：
1. **raw 请求完成且 ≤10s**：t=1.09s ✅
2. **probes 完成且 ≤10s**：t=5.19s ✅
3. **thread/start 在 30s 内出现**：app-server 侧 t=9.20s、runner 侧 Auto-created 后 5.99s ✅
4. **bridge 出现正常 state/server**：state.json + server.json 存在，无 startup_error ✅
5. **无 app-server 协议错误**：无 TimeoutError/ERROR 事件 ✅

排除项：
- `NETWORK_STALL`：排除——raw 请求 1.09s 完成，远未超 30s。
- `PROTOCOL_OR_LAUNCH`：排除——TUI WebSocket/thread 均在 30s 内建立，无早退。
- `DIAG_INCONCLUSIVE`：不适用——本 RUN 为用户真实重试（窗口 2），时间线完整，无历史证据顶替。

**结论**：8-3 失败的 60s raw.githubusercontent 挂起在本 RUN **未复现**，网络瞬态已消失，TUI 在 30s 窗口内正常建立 thread/start。**无代码修复必要**；按 28_PLAN 后续路由，`READY` 可由 Codex 另发单次 full-run 卡。

## 7. 附：CODEX_TASK_28_PLAN 门槛 1 完成说明

- `HERMES_DIAGNOSIS_27.md` 头部已修订：状态统一为"已完成，受控 RUN r27-observer-20260803 已执行，主分类 DIAG_CODEX_REMOTE_HANDSHAKE"，删除旧的"未执行受控 RUN / DIAG_INCONCLUSIVE"矛盾文本，并附修订记录。
- §9 已补充 PID 记录差异解释：observer 的 `[obs] TUI_PID=349311 exited at t=4` 是 node shim 包装进程（argv 含 codex 路径，被 pgrep 匹配），真实 TUI 进程 349319 持续存活（final-pane dead=0 + sqlite 时间线交叉验证）。
- 全部 evidence 保留未删，未重跑旧 RUN。

## 8. 边界声明

- 不宣称 Gate 2 PASS、全仓 GREEN 或 mergeable。
- Gate 1 状态不受本卡影响；Codex 只读验收后按 28_PLAN §4 路由（READY → 单次 full-run 卡）。
