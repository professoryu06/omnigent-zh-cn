# Codex 只读验收 — Grok Native Final 01

## 裁决

**GROK_NATIVE_READY_FOR_USE（ACCEPT_WITH_NOTES）**。

本裁决仅适用于 Grok Native 专项，不是全仓 GREEN、不是全局 Gate 2 PASS，也不构成 merge 授权。

## RUN 身份

- RUN_ID：`grok-native-final-01-20260804T0110Z`
- Evidence：`C:\Users\Administrator\omnigent-diagnostics\grok-native-final-01-20260804T0110Z\`
- Evidence 状态：仍存在；实际文件数 20，与 `manifest.txt` 及诊断报告的计数一致。
- 工作树：`F:\codex-ai\omnigent-zh-next`
- 分支：`integration/omnigent-zh-20260731`
- HEAD：`c2982266f1d702d83d47f9352bbe5e0aa8c987f9`
- 报告：`docs/fixes/handoffs/HERMES_DIAGNOSIS_GROK_NATIVE_FINAL_01.md`

## G1–G6 只读核对

| 项目 | 结论 | 依据 |
|---|---|---|
| G1 认证 | PASS | 私有 `GROK_HOME`、`grok models` 登录状态、`auth.json` 存在；凭据未进入本验收文档 |
| G2 单轮 | PASS | `G2-event.json`、`G2-poll.json`、`G2-assistant.txt`、`G2-resources.json`；真实 assistant、idle、仅 1 个 environment |
| G3 双轮同 session | PASS（带审计备注） | `G3-r1-*`/`G3-r2-*` 显示同一 Omnigent session 两轮均有 assistant 且最终 idle；报告指向唯一 Grok session home 与 `session_search.sqlite` 的 `session_docs` 记录，并有两轮时间覆盖 |
| G4 AgentCenter | PASS | `G4-target-create.json` 有 caller→target、`parent_session_id`、`kind=sub_agent`；`G4-final.json`/`G4-assistant.txt` 有真实 `GROK_AGENTCENTER_FINAL_OK`，资源仅 environment |
| G5 代理隔离 | PASS | 父环境代理变量被剥离；spawn env 仅 `NO_PROXY=127.0.0.1,localhost`，未设置 `OMNIGENT_GROK_PROXY` |
| G6 清理/泄漏边界 | PASS | 旧认证失败 harness PID 已 SIGTERM/SIGKILL 并确认 dead；vendor CLI 泄漏数为 0；常驻 harness 10 个被单独标为产品 idle 语义；观察工具单列；10100 未监听；leak-scan 最后执行 |

## 重点审查结论

### G3 会话复用

证据足以支持“第一轮创建、第二轮 resume 复用同一 Grok session”的专项功能结论：G3 两轮事件/轮询均落盘，G3 只有一个 Grok session home，且报告给出 `session_search.sqlite` 的 `session_docs`、session id 和两轮时间关系。该证据不要求把包含认证材料的原始 `GROK_HOME` 复制进 evidence。

审计改进建议：后续 RUN 在 evidence 中增加不含凭据的 session id、SQLite 行计数/时间范围和 SHA-256 摘要，以便离线复核，不要导出 `auth.json`。

### G4 AgentCenter

`caller=claude-native-ui` → `target=grok-native-ui`，并且 target 创建记录带 `parent_session_id`、`kind=sub_agent`，随后收到 Grok assistant sentinel。这满足 AgentCenter 调用语义；不是简单手工新建 Grok 会话。

### G6 清理与常驻进程

旧失败认证会话的 PID 已确认退出。leak-scan 中的 10 个 harness 是本产品 idle 会话，且与 vendor CLI 泄漏计数、观察工具分开记录；不能把它们误判为泄漏。该边界满足 Grok 专项验收。

## 唯一审计备注（不阻塞可用性）

`sessions.txt` 当前只列出 G2、G3 两项，没有列出 G4 target。G4 的 target/create/final 证据本身存在且自洽，因此这不是功能失败，也不需要重跑；但 session manifest 不完整。建议仅补写一条 G4 caller/target 记录并重新生成该文档摘要，保留原 evidence，不修改业务证据。

## 最终边界

- Grok Native：可进入日常使用。
- 本结论不扩大到 Claude、Codex、Qwen、Pi 或全局 Gate 2。
- 不代表全仓测试通过、全仓 GREEN 或可 merge。
- 若后续要签全局 Gate 2，必须另开独立卡并覆盖其余范围。

本次验收未修改源码、测试、配置或 evidence，未重跑业务。
