# HERMES_DIAGNOSIS_21 — D2 / Controller C / Native CLI 0.146.0 只读诊断

> Hermes 角色：只读诊断执行者。不是实现者，不是 Gate 2 签字人。
> 本报告不构成 Gate 2 PASS/FAIL 判定，不授权 merge。

---

## RUN 信息

| 项目 | 值 |
|---|---|
| RUN_ID | `20260730-152300-dc83140-hermes-d2-c-cli0146-r1` |
| Worktree | `F:\codex-ai\git项目部署\tmp\omnigent-review` |
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| Branch | `docs/fix-plans-core-secondary` |
| Evidence 根 | `C:\Users\Administrator\omnigent-diagnostics\20260730-152300-dc83140-hermes-d2-c-cli0146-r1\` |
| 模型 | `gpt-5.6-sol` |
| Native CLI | `0.146.0`（任务卡指定 SHA） |
| 日期 | 2026-07-30 |

---

## 结果摘要

| 阶段 | 结果 |
|---|---|
| Precheck | ✅ PASS（forbidden=0, port_free=True, codex_tmp=0） |
| Meta TUN | ✅ `Meta Tunnel` NetEnabled=TRUE |
| Agent bundle 预计算 | ✅ sha256=`c282ad92...`, size=248 |
| Observer sentinel 预检 | ✅ 正向 5/5, 负向 0 |
| Server READY | ✅ 12/12 HTTP 200, ordinal 1..12, UTC monotonic |
| Host online | ✅ 30 samples online, PID 4444 |
| Controller C POST | ✅ **201 Created** |
| Session 状态推进 | ❌ 停留在 `idle`，runner 未推进 |
| C 退出 | **IDLE_TIMEOUT_240S**（254.7s 总时长） |
| Observer 采样 | ✅ 258 samples, ordinal 1..258, server/host alive throughout |
| Cleanup | ✅ server/host killed, port released, runtime deleted |
| Leak scan | ✅ hits=0（2 false positive: `OPENAI_API_KEY_present=False` 变量名） |

---

## 诊断结论

**Outcome: `DIAG_COMPLETE / C_IDLE_TIMEOUT_240S`**

### 根因（经 Grok 交叉验证确认）

**Session 创建成功，但"分派到 host → 起 runner → 发消息 → 起 Codex"这条链根本没接上。**

1. Controller C 只执行了 multipart `POST /v1/sessions`（上传 agent + 建 session），未按任务卡意图执行完整的 `omnigent run … -p "Reply with CONTROLLER_OK and stop."` 或等价三步 API（建 session → `POST /hosts/{id}/runners` → 发消息）。
2. 产品代码中，multipart 建 session 路径直接 return，**不读 metadata 里的 host_id，不发 `host.launch_runner`**。Schema 文档写了"带 host_id 会启动 runner"，实现没做——这是产品缺口。
3. Session 从未绑定/启动真正的 runner，不会有 turn，native codex.exe 本来就不会出现。状态一直是 `idle`（无人上报时的默认值），不是"runner 认领了但 CLI 起不来"。
4. Observer 中 `runner_pid=22776` 不可信：它监控的是 server 子进程，而真正的 runner 应由 host 拉起；该 PID 在建 session 之前就存在，是误认。

### 本 RUN 无法回答的问题（需修好分派后复跑）

- 正确路径下 runner/CLI 是否仍失败
- `HARNESS_CODEX_PATH` 是否被 host→runner 环境白名单剥掉
- `gpt-5.6-sol` + TUN + 认证是否导致 CLI 卡死
- runtime 日志已删，无法对照 host/runner 日志二次确认
- 产品 240s turn idle 与诊断侧 idle 240s 是否同一机制

### 建议修复方向（供 Codex 决策，Hermes 不实施）

**产品修复（二选一）：**
- A（推荐）：multipart 若带 host_id，创建后像 JSON 路径一样：校验 workspace → 写 host → 发 `host.launch_runner`
- B：multipart 故意不 launch，则改文档，带 host_id 直接 400，禁止"写了 host_id 却当成功"

**诊断重跑（需新任务卡）：**
- C 必须用 `omnigent-zh.exe run <agent目录> -p "Reply with CONTROLLER_OK and stop." --server <地址>` 或等价三步 API
- Observer 应看 session 的 runner_id / runner_online 及 host 子进程，不要用 server 子进程当 runner

**真跑通 D2 后再加固：**
- 默认转发 `HARNESS_CODEX_PATH`（或要求 PATH 有 codex）
- `harness_is_configured` 要认显式路径，不只 `which codex`
- host launch 失败不要只 warning 仍 201 idle；要失败可见

---

## C 生命周期（逐秒落盘）

```json
{"ordinal": 1, "utc": "2026-07-30T15:56:04.547692Z", "event": "c_start", "session_id": "conv_d368e61a8a8f40f9864de92acbb41b64"}
{"ordinal": 2, "utc": "2026-07-30T15:56:18.820889Z", "event": "status_change", "status": "idle", "elapsed_s": 14.2}
{"ordinal": 3, "utc": "2026-07-30T16:00:19.196178Z", "event": "c_end", "exit": "IDLE_TIMEOUT_240S", "total_s": 254.7, "final_status": "idle"}
```

---

## 证据清单（57 文件）

持久保留于 `C:\Users\Administrator\omnigent-diagnostics\20260730-152300-dc83140-hermes-d2-c-cli0146-r1\`：

- `outcome.json` — 最终结果
- `run-summary.json` — 完整运行摘要
- `c-process-result.txt` — C 退出码/时长/状态
- `c-lifecycle-live.jsonl` — C 逐秒生命周期（3 records）
- `c-post-result.txt` — POST 201 响应
- `c-command-sanitized.txt` — 脱敏命令
- `d2-samples-live-sanitized.jsonl` — Observer 258 samples
- `d2-observer.mjs` — Observer 源码（frozen）
- `observer-source.mjs` — Observer 源码副本
- `observer-command-sanitized.txt` — Observer 启动命令
- `agent-bundle.tar.gz` — 冻结 bundle
- `agent-bundle-identity.txt` — Bundle SHA/size
- `server-ready-samples.jsonl` — Server READY 12 samples
- `host-online-samples.jsonl` — Host online 30 samples
- `precheck.json` — Precheck 结果
- `tun-check.json` — TUN 验证
- `environment-presence.txt` — 环境变量存在性（无值）
- `identity.json` — HEAD/branch/worktree
- `blob-hashes.txt` — 9 blob SHA 匹配
- `cleanup.txt` — Cleanup 记录
- `manifest.txt` — 全文件 SHA manifest
- `leak-scan.txt` — 泄漏扫描 hits=0

---

## 约束遵守

- [x] 一个全新 RUN_ID
- [x] 一次隔离 server
- [x] 一次 foreground host
- [x] 一次 Controller C
- [x] 模型 `gpt-5.6-sol`
- [x] Native CLI `0.146.0`
- [x] 240s idle watchdog 未修改
- [x] Precheck 只做一次
- [x] Observer 正向 sentinel + 零样本负向预检
- [x] Server/host/C 逐秒实时落盘
- [x] C exit 明确记录（IDLE_TIMEOUT_240S，非误标 300s）
- [x] 未重试 C
- [x] 未执行完整 Gate 2
- [x] 未改源码
- [x] 未 commit/push/merge/tag
- [x] Evidence 持久保留
- [x] 凭据一律 [REDACTED]

---

## Gate 状态

- **Gate 1**：仅"相对 main PASS"（此前任务结论）
- **Gate 2**：**未签 PASS**。Hermes 是只读诊断执行者，Gate 2 判定权归 Codex。
- **不可 merge**。

---

## 首次 RUN（已消耗）

| 项目 | 值 |
|---|---|
| RUN_ID | `20260730-151908-dc83140-hermes-d2-c-cli0146-r1` |
| Outcome | `DIAG_INCONCLUSIVE / PRECHECK_STOP` |
| 原因 | 检测到禁止进程 `codex.exe` PID 26964、`codex-code-mode-host.exe` PID 23756 |

---

---

## Full-Run r2（第二方式：完整 `omnigent run`）

> 用户授权后执行。目标：走完 `omnigent run … -p "Reply with CONTROLLER_OK and stop."` 全链路。

| 项目 | 值 |
|---|---|
| RUN_ID | `20260730-172454-dc83140-hermes-d2-run-cli0146-r2` |
| Evidence 根 | `C:\Users\Administrator\omnigent-diagnostics\20260730-172454-dc83140-hermes-d2-run-cli0146-r2\` |
| Server | `127.0.0.1:54721`，READY（1s） |
| Exit code | **1** |
| Exit reason | `IDLE_TIMEOUT_240S`（240s harness idle watchdog） |
| CONTROLLER_OK | ❌ 未产出 |

### 失败链（逐阶段）

| # | 阶段 | 结果 |
|---|---|---|
| 1 | Server READY | ✅ 1s |
| 2 | Host daemon 连接 | ✅（需临时修补 BUG-1，见下） |
| 3 | Runner started | ✅ pid=20864 |
| 4 | Session 创建 + 用户消息投递 | ✅ `conv_16b8d92d53824b9fa7d13da244931f9a` |
| 5 | Turn started, codex gateway routing | ✅ model=gpt-5.6-sol 已识别 |
| 6 | Runner 尝试 native terminal (tmux/PTY) | ❌ **RuntimeError: not supported on Windows** |
| 7 | Runner 崩溃，无事件输出 | ❌ |
| 8 | CLI 240s idle watchdog 触发 | ❌ exit=1 |

### 新发现的产品 Bug

**BUG-1（GBK 编码崩溃）：** Host daemon 环境白名单 `_RUNNER_ENV_ALLOWLIST`（`omnigent/host/connect.py:261`）不含 `PYTHONUTF8`。Daemon 子进程继承系统 GBK codepage，`connect.py:1878` 的 `✓`（U+2713）无法编码 → 异常 → tunnel 断开 → 10s 重连 → 无限崩溃循环。诊断时临时将 `✓` 改为 `[OK]` 后 daemon 稳定连接（已还原）。

**BUG-2（harness 路由错误）：** Agent config 已正确设置 `executor.config.harness: codex`，但 runner 仍路由到 native terminal（tmux/PTY）创建路径（`omnigent/inner/terminal.py:1882` → `omnigent/terminals/registry.py:221`），Windows 不支持 → RuntimeError。Codex harness 应走 SDK/subprocess 路径，不应走 tmux/PTY。

**BUG-3（已知，C-only r1）：** multipart `POST /v1/sessions` 带 `host_id` 不 launch runner。

### 关键结论

- **Native Codex CLI 从未被 spawn。** Runner 在 harness 路由阶段就崩溃了，根本没走到调用 `codex.exe` 的步骤。
- **不能将失败归咎于 Codex CLI。** 失败发生在产品内部的 harness 路由层。
- 即使修好 BUG-1（GBK），BUG-2 仍会阻塞 Windows 上的 full run。
- 需要 Codex 决策：修 BUG-2 的 harness 路由逻辑，或提供 Windows 兼容的 codex harness 路径。

### 证据清单（18 文件）

持久保留于 `C:\Users\Administrator\omnigent-diagnostics\20260730-172454-dc83140-hermes-d2-run-cli0146-r2\`：

- `run-summary.json` — 完整运行摘要 + 失败链 + bug 列表
- `agent-config.yaml` — 冻结的 agent 配置
- `logs/server/server-*.log` — Server 日志（130KB）
- `logs/host/host-*.log` — Host daemon 日志（含 GBK 崩溃 + 修补后稳定连接）
- `logs/runner/runner-conv_*.log` — Runner 日志（含 RuntimeError traceback）
- `logs/cli/cli-*.log` — CLI 日志
- `precheck.json`, `tun-check.json`, `identity.json`, `blob-hashes.txt` 等

### 临时修补记录（已还原）

- `omnigent/host/connect.py:1878`：`✓` → `[OK]`（DIAG-TEMP），诊断后已还原，`git diff` 确认 0 处残留。

---

*报告更新时间：2026-07-31T01:52Z*
*Hermes 只读诊断执行者 — 不实现、不签字、不 merge*
