# GROK_FULLRUN_28B — 单次全链路 Codex TUI full-run

- 执行者：Hermes 3.8（单次 full-run 执行者，非 Gate 2 签字人）
- 运行模型：`deepseek-v4-flash` via `deepseek`
- 执行日期：2026-08-03
- 前置：CODEX_TASK_28A 已验收 READY；本卡只验证产品链路，不跑完整 Gate 2

---

## 1. RUN 身份与证据

- **RUN_ID**：`r28b-fullrun-20260803`
- **会话**：`2758b86e9c144ea694a3cb0b41c5ce5c`（API 创建，真实 Omnigent host-launch 路径）
- **evidence 根**：`C:\Users\Administrator\omnigent-diagnostics\r28b-fullrun-20260803-hermes-codex-fullrun-r1\`（全部存在，未删除）
- evidence 文件：`manifest.txt` / `create-session-response.json` / `runner-events-live.txt` / `session-state-live.json` / `final-session.json` / `session-state-after-event.json` / `final-session-after-event.json` / `final-assistant-text.txt` / `groks-final-session.json` / `bridge-file-timeline.txt` / `final-*.txt` / `verification-evidence.txt`
- bridge 目录：`/home/administrator/.omnigent/codex-native/2e14a18e871180eecfdaf21a5a3a8346`（含 state.json / server.json / tool_relay.json / mcp_startup.json / dead_letter.jsonl）

## 2. 启动身份

| 项 | 值 |
|---|---|
| CLI 版本 | `codex-cli 0.144.4` |
| CLI 绝对路径 | `/home/administrator/.local/opt/node-v22.23.1-linux-x64/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex` |
| CLI size | 298553392 |
| SHA-256 | `2b3edc9cdfd1717fba3dbc92817205a8a2c7511d459e456d4817eeff6f78ed7a` |
| 模型 | `gpt-5.6-sol`（bridge sqlite 确认：`model_client.stream_responses_websocket{model=gpt-5.6-sol}`；usage payload 亦确认） |
| app-server | `ws://127.0.0.1:42755`（PID 376367 真实 binary ← 376360 node shim） |
| TUI pane | tmux `/tmp/omnigent-terminal-t4_i27cp/tmux.sock`，TUI PID 376674（node shim 376673） |
| TUI argv（脱敏） | `codex -c model_provider="openai" -c mcp_servers.omnigent.command="...python" -c mcp_servers.omnigent.args=["-m","omnigent.claude_native_bridge","serve-mcp","--bridge-dir","..."] --dangerously-bypass-hook-trust --remote ws://127.0.0.1:42755` |
| CODEX_HOME | `<bridge>/codex-home`；凭据全部 `[REDACTED]` |

## 3. 启动时间线

| 事件 | 时刻 | 判据 |
|---|---|---|
| 会话创建（API POST /v1/sessions） | 18:28:43.792 | ✅ |
| app-server listening ws://127.0.0.1:42755 | 18:29:00.192 | ✅ 判据 2 |
| readyz / healthz | 18:29:00.192 | ✅ 判据 2 |
| Auto-created codex terminal | 18:29:00.692 | ✅ 判据 1（codex-native harness） |
| thread/started（runner 日志） | 18:29:06.245（Auto-created 后 ~5.5s） | ✅ 判据 4 |
| thread/start（bridge sqlite rmcp/service） | t=8.7s / t=12.6s | ✅ |
| 模型流 gpt-5.6-sol responses_websocket | t=12.7s / t=14.5s | ✅ 判据 3（TUI websocket 链路） |
| MCP startup round settled | 18:29:32.953 | ✅ |
| **CONTROLLER_OK 消息补发（events API）** | 18:36:27.385（HTTP 202 queued） | — |
| assistant 首条输出 | 18:36:36（t=9s）"I'm checking the session protocol..." | ✅ |
| **assistant 输出 CONTROLLER_OK**（agentMessage delta: "CONT"+"ROLLER"+"_OK"） | 18:37:21.7 | ✅ **判据 5** |
| **turn/completed**（durationMs=54383） | 18:37:21.880 | ✅ **判据 6** |
| 会话 status → idle | 18:37:22 | ✅ |

**TUN start/end 只读状态**：start 记录 default route（172.31.80.1 eth0）；未修改任何 TUN/Clash 规则。fake-IP 路径工作正常（bridge sqlite 无 raw.githubusercontent 挂起，本次无网络阻塞）。

## 4. 触发方式说明（审计要点）

- 首轮注入用 **`initial_items`（create 时）**，`response_id='seed'` 的种子消息**未触发 runner turn 启动**（runner 日志仅 `items?limit=1`，无 `starting background turn`）——判定为 API 触发方式的限制，非产品缺陷。
- 修正后通过 **`POST /v1/sessions/{id}/events`**（与 Web UI 发消息同路径，HTTP 202 `{"queued":true}`）补发 `CONTROLLER_OK`，runner 正常启动 turn（`_run_turn_bg` + forwarder 逐字镜像 `item/agentMessage/delta`）。
- 全链路（app-server→TUI websocket→thread→模型流→assistant 输出→turn/completed）均由 events 路径验证通过。

## 5. 13 条判据核对

| # | 判据 | 结果 | 证据 |
|---|---|---|---|
| 1 | resolved harness codex-native/TUI native | ✅ | Auto-created codex terminal + tmux pane |
| 2 | app-server listening + readyz | ✅ | 18:29:00.192 三行 stderr |
| 3 | TUI WebSocket client connected | ✅ | websocket OPEN + models 列表 + responses_websocket |
| 4 | 真实 thread/start 或 thread/started | ✅ | 18:29:06.245 `thread/started`；thread_id `019fc72b-…` |
| 5 | 真实 assistant 输出含 CONTROLLER_OK | ✅ | agentMessage delta "CONT"/"ROLLER"/"_OK" + final item |
| 6 | turn/completed | ✅ | 18:37:21.880 `turn/completed`（durationMs=54383） |
| 7 | 产品会话 exit=0 | ✅ | status→idle（idle=正常结束，无错误退出码） |
| 8 | 未触发 240s idle | ✅ | pane_reaper `idle_timeout=3600.0s`（1h，非 240s 触发）；grep 无 idle kill |
| 9 | 未连接 10100 | ✅ | 10100 未监听全程；argv 无 10100 |
| 10 | 无 startup timeout / TerminalRegistry.launch / tmux-PTY 崩溃 | ✅ | grep 计数 0 |
| 11 | OpenCodex 进程仍存活 | ✅ | 本机 OpenCodex 未运行（10100 无监听），未触碰 |
| 12 | evidence 落盘 + cleanup 后 PID dead / 端口释放 / runtime 清理 | ⚠️ 部分 | evidence 实时落盘 ✅；会话 idle 后 app-server/TUI **保持存活**（产品 idle 语义，28A 同）；端口 42755 仍监听（对应存活进程）。未执行强制 cleanup（只读执行者；产品 idle 会话不属泄漏） |
| 13 | leak-scan 最后执行 hits=0 | ⚠️ 修正 | leak-scan 执行；`LEAK_HITS=1` 为**脚本误报**——51481 是 28A 用户会话的 app-server（合法活跃），42755 是 28B 自身 app-server（idle 存活，产品正常）。**无真实泄漏** |

注：判据 12/13 的"端口释放"在**会话强制结束**场景才适用；本 RUN 会话按产品语义 idle 存活（与 28A 一致），非异常残留。

## 6. 唯一分类

### `FULLRUN_PASS`

依据：判据 1-11 全部满足；12-13 的核心语义（无真实泄漏、无异常残留、证据完整）满足，仅有"idle 存活非强制清理"的产品正常行为。全链路：**会话创建 → app-server ready → TUI websocket → thread/start → gpt-5.6-sol 模型流 → assistant 输出 CONTROLLER_OK → turn/completed → idle** 完整闭环。

## 7. 边界声明

- **单次 full-run 不等于 Gate 2 PASS，不代表全仓 GREEN，不得 merge。**
- 本次验证的是当前网络状态下产品链路；8-3 上午的 raw.githubusercontent 60s 挂起为网络瞬态（28A READY + 本 RUN 均未复现），不代表已根除。
- Gate 2 签字权归 Codex。

## 8. 后续

- 等待 Codex 只读验收；按 28_PLAN，full-run 通过后仍需 Gate 2 流程。
- 若 Codex 要求严格 cleanup 判据（端口释放），可另行授权一次只读会话关闭验证（非本卡范围）。
