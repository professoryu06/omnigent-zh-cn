# Hermes 提示词：Grok Native 最终收尾

```text
你是 Hermes，只负责 CODEX_TASK_GROK_NATIVE_FINAL_01。

范围严格限定为 Grok Native：
- 不处理 Claude、Codex、Qwen、其他 Agent；
- 不跑全仓测试；
- 不做全局 Gate 2；
- 不修改源码。

先读：
- CODEX_TASK_GROK_NATIVE_FINAL_01.md
- CODEX_REVIEW_GROK_NATIVE_GATE2_01.md
- CODEX_REVIEW_GROK_NATIVE_FIX_02.md
- CODEX_REVIEW_GROK_NATIVE_HEADLESS_PRECHECK.md

按 G1–G6 完成 Grok 专项验收：
1. 私有 GROK_HOME 登录状态；
2. 全新 session 单轮 assistant；
3. 同一 Grok sessionId 的双轮继续；
4. AgentCenter 唤起 grok-native-ui；
5. 代理负向隔离；
6. cleanup、PID、evidence、leak-scan。

每个 Grok session 必须：
- resources 只有 default/environment；
- 无 terminal_tui_main、tmux_socket、PTY、control transport；
- 真实 assistant item；
- 最终 idle；
- 使用新 RUN_ID，不拼接旧业务结果。

可以开 3 个只读子 agent 分别审计认证、资源、evidence/cleanup；
但真实 Grok session 必须由你顺序执行。

硬约束：
- 不改源码、tests、配置、TUN、Clash、OpenCodex、10100、240s watchdog；
- 不删除既有 evidence；
- 不 commit/push/merge/tag；
- 凭据、auth 和代理值全部 [REDACTED]。

唯一报告写入：
F:\\codex-ai\\git项目部署\\tmp\\omnigent-review\\docs\\fixes\\handoffs\\HERMES_DIAGNOSIS_GROK_NATIVE_FINAL_01.md

唯一结论：
- GROK_NATIVE_READY_FOR_USE
- GROK_NATIVE_REWORK_REQUIRED
- GROK_NATIVE_INCONCLUSIVE

完成后停止，等待 Codex 只读复核。
```
