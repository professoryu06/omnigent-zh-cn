# HERMES_DIAGNOSIS_GROK_NATIVE_HEADLESS_PRECHECK — Grok headless 前置观察

- 执行者：Hermes 3.8（headless 前置观察执行者，非 Gate 2 签字人）
- 运行模型：`deepseek-v4-flash` via `deepseek`
- 观察日期：2026-08-03 16:33 UTC（本地 2026-08-04 00:33）
- 任务卡：`CODEX_TASK_GROK_NATIVE_HEADLESS_PRECHECK`
- 前置：GROK_NATIVE_FIX_02（两阻塞修复）→ CODEX_REVIEW_GROK_NATIVE_FIX_02（ACCEPT_WITH_NOTES，要求本观察卡）

---

## 1. RUN 身份与 evidence

- **RUN_ID**：`grok-native-headless-precheck-20260804T0015Z-r1`
- **evidence 根**：`C:\Users\Administrator\omnigent-diagnostics\grok-native-headless-precheck-20260804T0015Z-r1\`（9 文件：manifest.txt / create-session.json / event-post.json / session-poll.json / final-session.json / resources.json / assistant-text.txt）
- 工作树：`F:\codex-ai\omnigent-zh-next`，branch `integration/omnigent-zh-20260731`，HEAD `c2982266f1d702d83d47f9352bbe5e0aa8c987f9`
- server：`http://127.0.0.1:6767`；host：`27dc0e70add5450b9901c03fd9e9417c`（grok-native: true）
- agent：`grok-native-ui`（id `133499537450decf0a3fc425c686a02f`）
- **全新 session**：`13697c005389496bbc02738824a8ffcf`（不复用任何修复前 session）
- TUN start/end 只读：default via 172.31.80.1 dev eth0（未开关 TUN）

## 2. 时间线

| 事件 | 时刻（UTC） | 说明 |
|---|---|---|
| session 创建 | 16:33:10.35 | POST /v1/sessions → 202 |
| sentinel 发送 | 16:33:10.36 | `Reply with GROK_NATIVE_HEADLESS_OK and stop.`（唯一一条） |
| **assistant item 出现** | 16:33:24（t=14s） | 含 `GROK_NATIVE_HEADLESS_OK` |
| **session idle** | 16:33:24（t=14s） | status=idle |
| 资源/进程观察 | 16:33:57 | resources 仅 1 个 environment |
| final check + leak-scan | 16:34:49 | 见 §5 |

## 3. 成功判据核对（7 项全满足）

| # | 判据 | 结果 | 证据 |
|---|---|---|---|
| 1 | 真实 assistant item 含 GROK_NATIVE_HEADLESS_OK | ✅ | final-session.json items[1] = message assistant；assistant-text.txt 含 sentinel |
| 2 | session 最终 idle，无 runner error | ✅ | status=idle；无 error item |
| 3 | 无 terminal_tui_main / tmux / PTY / control / REPL tui-main | ✅ | **resources 仅 1 个：`default` type=environment transport=（空）**；无 terminal_tui_main、无 tmux_socket、无 terminal_transport=control、无 REPL tui/main |
| 4 | runner/host 无 native terminal launch / Windows tmux-PTY 错误 | ✅ | runner harness=`grok-native`（CLI subprocess 形态）；无 tmux/PTY 记录 |
| 5 | Grok 子进程代理负向规则 | ✅ | env 构造实测：父环境有 HTTP/HTTPS/ALL_PROXY 时，spawn env **仅 NO_PROXY**，`NO_PROXY=127.0.0.1,localhost` 严格相等；HTTP_PROXY/https_proxy/ALL_PROXY/OMNIGENT_GROK_PROXY 均不在 |
| 6 | evidence 实时落盘、RUN_ID 全新、无旧 RUN 拼接 | ✅ | 9 文件实时落盘；session 全新 |
| 7 | cleanup/leak-scan 可审计、凭据 [REDACTED] | ✅ | §5；本报告全值脱敏 |

## 4. 关键观察明细

### 4.1 资源负向（本卡核心）

```text
resource count: 1
 - default | type= environment | transport=
```

修复前证据（CODEX_REVIEW_GROK_NATIVE_01）出现过 `terminal_tui_main` + `metadata.tmux_socket=/tmp/omnigent-terminal-*/tmux.sock` + `terminal_transport=control`；**本次修复后全新 session 未出现任何 terminal/tmux/PTY 资源**——阻塞 1 修复的真机证据成立。

### 4.2 Grok 子进程（headless 语义）

- 观察时刻 `ps`：**无 `grok --single/--resume` CLI 子进程**（每轮 spawn 即退，无常驻 TUI，符合 headless CLI_SUBPROCESS 设计）
- harness `_runner --harness grok-native` 进程常驻 = 产品 idle 语义（与 28A/28B codex harness 同），非泄漏

### 4.3 代理环境（负向实测）

- 本卡未设 `OMNIGENT_GROK_PROXY`；模拟父环境带 HTTP/HTTPS/ALL_PROXY + NO_PROXY=x
- `GrokNativeExecutor._build_spawn_env()` 实测输出：
  - `HTTP_PROXY` 不在 / `https_proxy` 不在 / `ALL_PROXY` 不在 / `OMNIGENT_GROK_PROXY` 不在
  - `NO_PROXY = 127.0.0.1,localhost`（严格相等，非继承的 "x"）
- 阻塞 2 修复的真机/构造证据成立（正向注入已由 47/47 定向测试覆盖，本卡未做正向外网访问）

## 5. final check + leak-scan

- grok CLI 子进程：**已退出**（无 `--single/--resume` 进程）
- harness 进程：常驻（产品 idle 语义）
- 端口：6767 正常监听；**10100 未监听**（OpenCodex 未触碰）
- 会话状态：idle
- leak-scan：无 grok CLI 泄漏（`ps grep` 计数的 3 = harness + grep/tee 自身，精确 `--single/--resume` 匹配为 0）
- 凭据：全报告 `[REDACTED]`；`/proc/<pid>/environ` 只读检查仅记录键名不记录值

## 6. 唯一分类

### `HEADLESS_PRECHECK_PASS`

7 项成功判据全部满足；核心负向证据（无 terminal_tui_main / tmux / control / REPL）来自**修复后全新 session 的真实资源快照**，非代码推断。

## 7. 边界声明

- **本卡不等于 Gate 2 PASS，不代表全仓 GREEN，也不代表可 merge。**
- 本卡为 Gate 2 前置观察：验证 headless 资源负向 + 代理负向；Gate 2 六轮验收仍需 Codex 另开独立卡。
- 已知保留项（Codex 记录）：`test_catalog_rows_carry_setup_steps` 1 项 pre-existing 失败（用户 `acp:grok-code` 动态行），与本次无关。
- 未修改源码/测试/配置/TUN/Clash/OpenCodex/10100/240s watchdog；未 commit/push/merge/tag。

## 8. 证据位置

- `C:\Users\Administrator\omnigent-diagnostics\grok-native-headless-precheck-20260804T0015Z-r1\`（9 文件，未删）
- runner 日志：`/home/administrator/.omnigent-zh-cn/logs/runner/runner-13697c005389496bbc02738824a8ffcf-*.log`
- grok session home：`/home/administrator/.grok-omnigent/sessions/`（历史隔离目录，未删）
