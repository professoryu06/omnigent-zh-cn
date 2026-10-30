# Hermes 执行提示词：Grok Native Gate 2 六轮

```text
你是 Hermes，负责执行 CODEX_TASK_GROK_NATIVE_GATE2_01。

工作树：
F:\\codex-ai\\omnigent-zh-next
分支：integration/omnigent-zh-20260731
HEAD：c2982266f1d702d83d47f9352bbe5e0aa8c987f9

先读：
1. docs/fixes/handoffs/CODEX_TASK_GROK_NATIVE_GATE2_01.md
2. docs/fixes/handoffs/CODEX_TASK_28_PLAN.md
3. docs/fixes/handoffs/GROK_GATE2_POLICY_REVIEW.md
4. docs/fixes/handoffs/CODEX_REVIEW_GROK_NATIVE_HEADLESS_PRECHECK.md
5. docs/fixes/handoffs/HERMES_DIAGNOSIS_GROK_NATIVE_HEADLESS_PRECHECK.md

任务：按仓库现行 Gate 2 六轮协议完整执行，不实施代码修复。

硬约束：
- 使用全新 Gate 2 RUN_ID、全新 evidence 根和全新 session；不得拼接旧 RUN。
- 不修改源码、tests、政策、STATUS、配置、TUN、Clash、OpenCodex、10100、认证或 240s watchdog。
- 不删 evidence，不 commit/push/merge/tag。
- 不把 HEADLESS_PRECHECK_PASS 写成 Gate 2 PASS。
- 凭据和代理值一律 [REDACTED]。

Grok 相关要求：
- 使用 grok-native-ui。
- 每个 session 都必须是真实 assistant item，记录 harness/model/workspace/status。
- 每个 Grok session 必须无 terminal_tui_main、tmux_socket、PTY、terminal_transport=control 或 REPL tui/main。
- 未设置 OMNIGENT_GROK_PROXY 时，HTTP_PROXY/http_proxy、HTTPS_PROXY/https_proxy、ALL_PROXY/all_proxy 均不得进入子进程；NO_PROXY 必须是 127.0.0.1,localhost。
- 每轮都记录资源快照和 runner/host 时间线。

Gate 2 执行：
- 完整执行 CODEX_TASK_28_PLAN / GROK_GATE2_POLICY_REVIEW 规定的 C/E/R 六轮矩阵。
- E-positive 与 E-negative 必须使用不同 session。
- 不得用此前 Grok 双轮或 headless precheck 代替任何一轮。
- 不得用单元测试代替真实 Gate 2 smoke。

证据要求：
- 所有事件实时落盘到新的 evidence 根。
- manifest 列出实际文件数量和绝对路径；不要写“9 文件”而目录实际只有 7 文件。
- cleanup/leak-scan 最后执行，并分开记录：vendor Grok CLI、预期常驻 harness、观察工具 PID。
- 任何一轮缺失、资源不可审计、代理边界不清或 cleanup 不完整，都不能判 Gate 2 PASS。

交付：
- 新的 Gate 2 evidence 根；
- 唯一执行报告写入：
  F:\\codex-ai\\git项目部署\\tmp\\omnigent-review\\docs\\fixes\\handoffs\\HERMES_DIAGNOSIS_GROK_NATIVE_GATE2_01.md
- 报告列出六轮逐项结果、RUN_ID、evidence、资源负向、代理隔离、cleanup/leak-scan、pre-existing 测试边界。
- 完成后停止，等待 Codex 只读验收。
```
