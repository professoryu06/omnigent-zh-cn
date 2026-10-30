# CODEX_TASK_GROK_NATIVE_GATE2_01

## 目的

在 `HEADLESS_PRECHECK_PASS` 已通过后，执行一次**独立的 Gate 2 六轮验收**。本卡不是实现卡，不能修改源码或测试。

## 前置

- 前置验收：`CODEX_REVIEW_GROK_NATIVE_HEADLESS_PRECHECK.md`
- 前置 RUN：`grok-native-headless-precheck-20260804T0015Z-r1`
- 候选工作树：`F:\codex-ai\omnigent-zh-next`
- 分支：`integration/omnigent-zh-20260731`
- 当前 HEAD：`c2982266f1d702d83d47f9352bbe5e0aa8c987f9`
- 规范参考：`CODEX_TASK_28_PLAN.md`、`GROK_GATE2_POLICY_REVIEW.md`

## 硬约束

- 使用全新 Gate 2 RUN_ID、全新 evidence 根和全新角色 session；不得拼接旧 RUN。
- 按现行 Gate 2 六轮协议完整执行，不得只做单次 full-run 或缩减为 Grok 双轮。
- Grok 角色使用 `grok-native-ui`；每轮记录真实 assistant item、session 状态、harness/model、workspace 和时间线。
- 每个 Grok session 都必须保持 headless：不得出现 `terminal_tui_main`、tmux socket、PTY 或 `terminal_transport=control`。
- 代理隔离继续核对：未设置 `OMNIGENT_GROK_PROXY` 时无 HTTP/HTTPS/ALL_PROXY（大小写均无），`NO_PROXY=127.0.0.1,localhost`；如做显式代理轮，只记录脱敏值。
- 不改 TUN/Clash/OpenCodex/10100/认证/240s watchdog。
- 不修改 `omnigent/`、`tests/`、政策、STATUS 或用户配置。
- 不删除 evidence；不 commit、push、merge、tag。
- 凭据统一 `[REDACTED]`。

## Gate 2 执行要求

1. 先做 identity/preflight：记录 branch、HEAD、CLI/native 路径与 SHA、server/host、模型、workspace、TUN start/end。
2. 按 `CODEX_TASK_28_PLAN.md` 的现行 C/E/R 六轮矩阵执行。E-positive 与 E-negative 必须使用不同 session；不得用一次成功的 Grok precheck 冒充六轮。
3. 每轮 evidence 实时落盘；在最终 manifest 中列出实际文件数量，不得写“9 文件”而目录只有 7 文件。
4. cleanup/leak-scan 最后执行，分离记录：vendor CLI 子进程、预期 harness、观察工具；不得把观察工具计数写成 Grok 泄漏。
5. 所有轮次完成后才由 Codex 只读验收 Gate 2；任何一轮缺失、资源证据不完整或 pre-existing 失败边界不清，Gate 2 为未完成/不通过。

## Gate 边界

`HEADLESS_PRECHECK_PASS` 只证明 Grok 新 session 的 headless 资源和代理负向条件成立；本卡完成前不得声称 Gate 2 PASS、全仓 GREEN 或 mergeable。

## 交付

唯一交付为新的 Gate 2 evidence、执行报告和清单；报告必须包含唯一 Gate 2 裁决、六轮逐项结果、所有 evidence 路径、cleanup/leak-scan、pre-existing 测试边界，并等待 Codex 复核。
