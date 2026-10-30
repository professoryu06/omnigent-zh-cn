# Grok Native Headless 前置观察卡

> 执行者：Hermes  
> 复核者：Codex  
> 目的：在进入独立 Gate 2 六轮前，验证修复后的 Grok 新会话不会再创建 Omnigent REPL/tmux/PTY 资源。  
> 本卡不是 Gate 2 验收，也不允许提交或合并。

## 工作身份

- 候选工作树：`F:\codex-ai\omnigent-zh-next`
- 分支：`integration/omnigent-zh-20260731`
- 预期 HEAD：`c2982266f1d702d83d47f9352bbe5e0aa8c987f9`
- 修复说明：`F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\GROK_NATIVE_FIX_02.md`
- 前次复核：`F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\CODEX_REVIEW_GROK_NATIVE_FIX_02.md`

## 只读 / 禁止事项

- 不修改 `omnigent/`、`tests/`、策略、配置或文档（最终诊断报告除外）。
- 不运行完整 Gate 2 六轮，不重跑旧的 Grok 双轮业务验收，不运行 D0/D1 或其他 Agent 验收。
- 不改 TUN/Clash/OpenCodex/10100/认证，不修改 240s watchdog。
- 不删除既有 evidence；本卡使用全新 RUN_ID 和新 evidence 目录。
- 不 commit、push、merge、tag。
- 所有凭据、代理值、auth 内容写成 `[REDACTED]`，只记录变量是否存在和键名。

## 执行步骤

### 1. 固定身份与环境

- 记录 RUN_ID：`grok-native-headless-precheck-<UTC timestamp>-r1`。
- 记录工作树、branch、HEAD、server URL、host id、CLI 路径和版本。
- 确认使用的是修复后的工作树，不拼接旧 RUN 的业务结论。
- 只观察现有 TUN 状态 start/end，不开关 TUN。

### 2. 新建一次 Grok session

- 使用内置 agent `grok-native-ui`，创建全新 session；不要复用 `539829a7...`、`f4118739...`、`9723a19b...` 或任何修复前 session。
- 只发送一次 sentinel：`Reply with GROK_NATIVE_HEADLESS_OK and stop.`
- 等待真实 assistant item 和最终 idle；不追加第二轮。
- 记录 session JSON、items、runner/host 状态和时间线。

### 3. 资源与进程观察

必须实时落盘以下证据：

- session final JSON / item 事件；
- session resources 列表；
- runner/host 日志相关窗口；
- Grok 子进程 PID、命令名、退出状态；
- 资源与进程观察开始/结束时间。

检查结果必须明确写出：

- 不存在 `terminal_tui_main`；
- 不存在 `tmux_socket`；
- 不存在 `terminal_transport=control`；
- 不存在由 `_auto_create_repl_terminal` 创建的 `tui/main` REPL 资源；
- Grok CLI 是 `grok-native` 的 CLI subprocess，而不是 vendor native/TUI；
- 没有 Windows `tmux/PTY not supported` 崩溃。

### 4. 代理环境观察

- 本卡默认不设置 `OMNIGENT_GROK_PROXY`，只记录 Grok 子进程环境中的键名，不记录值。
- 负向判据：`HTTP_PROXY`、`http_proxy`、`HTTPS_PROXY`、`https_proxy`、`ALL_PROXY`、`all_proxy` 不得出现；`NO_PROXY` 必须为 `127.0.0.1,localhost`。
- 正向注入已由 47/47 定向测试覆盖，本卡不需要为正向代理再次访问外网；如做正向检查，只记录脱敏后的变量键和值形态，不泄露代理或凭据。

### 5. 清理与 evidence

- 结束 session/runner，确认 PID dead、临时 runtime 清理、端口状态正常。
- evidence 目录持久保留：`C:\Users\Administrator\omnigent-diagnostics\<RUN_ID>\`。
- 最后写 `final-check` 和清单；报告写入仓库后不得修改业务 evidence。

## 成功判据

本卡只有在以下条件同时满足时才算 `HEADLESS_PRECHECK_PASS`：

1. 真实 assistant item 含 `GROK_NATIVE_HEADLESS_OK`；
2. session 最终 idle，业务没有 runner error；
3. session resources 无 `terminal_tui_main`、tmux socket、PTY/control transport 或 REPL `tui/main`；
4. runner/host 没有 native terminal launch 或 Windows tmux/PTY 错误；
5. Grok 子进程的代理负向规则满足；
6. evidence 实时落盘、RUN_ID 全新、无旧 RUN 拼接；
7. cleanup 和 leak-scan 可审计，凭据均为 `[REDACTED]`。

任一资源、时间线、进程或环境项无法审计，分类为 `HEADLESS_PRECHECK_INCONCLUSIVE`，不得进入 Gate 2 六轮。

## 交付

唯一仓库交付：

`F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\HERMES_DIAGNOSIS_GROK_NATIVE_HEADLESS_PRECHECK.md`

报告必须包含：RUN_ID/evidence 路径、HEAD/host/server、assistant item、资源列表、tmux/PTY 负向证据、代理键名观察、cleanup/leak-scan、唯一分类以及“本卡不等于 Gate 2 PASS”的声明。

完成后停止，等待 Codex 只读复核。
