# Hermes 提示词：Gate 2 证据修正重跑

```text
你是 Hermes，执行 CODEX_TASK_GROK_NATIVE_GATE2_REWORK_02。

先读：
- CODEX_REVIEW_GROK_NATIVE_GATE2_01.md
- CODEX_TASK_GROK_NATIVE_GATE2_REWORK_02.md
- CODEX_TASK_28_PLAN.md
- GROK_GATE2_POLICY_REVIEW.md

目标：只验证 Grok Native 是否稳定可用；不涉及 Claude、Codex、Qwen、其他 Agent、全仓 Gate 2 或整体发布。不改源码，修正 Grok 专项证据缺口并重新取得可审计的六轮结果。

必须完成：
1. 使用全新 RUN_ID/evidence，不拼接旧 gate2-01 业务结果；
2. C、E-positive、E-negative、R 使用不同绝对 workspace，并写唯一 sentinel；
3. Grok 没有 prompt-delivery strict 通道，把两轮改名为 E-pos-control/E-neg-control，不能再写 strict；本卡不切换其他 Agent；
4. evidence、manifest、报告、验证脚本的文件数量完全一致；
5. 清点并回收旧认证失败 session 的残留 harness，记录每个 PID dead；
6. leak-scan 分开记录 vendor CLI、产品 harness、观察工具，vendor CLI 必须为 0；
7. 每轮 resources 仍只能有 default/environment，无 terminal_tui_main、tmux_socket、PTY 或 control transport；
8. 代理负向仍满足：无 OMNIGENT_GROK_PROXY 时无 HTTP/HTTPS/ALL_PROXY，NO_PROXY=127.0.0.1,localhost。

子 agent 允许并行做只读审计：
- workspace-audit
- strict-semantics-audit
- evidence-cleanup-audit

子 agent 不得创建真实 session、不改源码、不改配置、不改共享 server/host 状态。真实六轮只能由你顺序执行。

硬约束：
- 不改 TUN/Clash/OpenCodex/10100/认证/240s watchdog；
- 不改 omnigent/、tests/、策略、STATUS；
- 不删除旧 evidence；
- 不 commit/push/merge/tag；
- 凭据与代理值全部 [REDACTED]。

交付：
F:\\codex-ai\\git项目部署\\tmp\\omnigent-review\\docs\\fixes\\handoffs\\HERMES_DIAGNOSIS_GROK_NATIVE_GATE2_REWORK_02.md

唯一分类只能是：
- GATE2_READY_FOR_CODEX_SIGNOFF
- GATE2_REWORK_INCONCLUSIVE

完成后停止，等待 Codex 只读验收。
```
