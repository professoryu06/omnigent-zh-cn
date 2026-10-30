# CODEX_REVIEW_GROK_NATIVE_GATE2_01

日期：2026-08-04  
角色：Codex 只读 Gate 2 验收官  
RUN_ID：`grok-native-gate2-01-20260804T0100Z`

## 唯一裁决

**GATE2_NOT_SIGNED / REWORK_REQUIRED**。

六轮业务响应本身均有真实 assistant sentinel、idle 状态和 headless 资源快照，但本 RUN 不满足现行 Gate 2 协议的完整审计条件，不能签 Gate 2 PASS，也不能 merge。

## 已确认通过的部分

Evidence 根仍存在：

`C:\Users\Administrator\omnigent-diagnostics\grok-native-gate2-01-20260804T0100Z\`

六个新 session 均有 assistant item、idle 和仅 `default/environment` resource：

- C：`CONTROLLER_OK`
- E-pos：`EXECUTOR_OK`
- E-pos-strict：`EXECUTOR_OK`
- E-neg：`EXECUTOR_NEG_OK`
- E-neg-strict：`EXECUTOR_NEG_OK`
- R：`REVIEWER_OK`

E-pos 与 E-neg 使用不同 session；六轮没有 `terminal_tui_main`、tmux socket、PTY/control resource。代理负向记录显示未设置 `OMNIGENT_GROK_PROXY` 时只保留强制 `NO_PROXY=127.0.0.1,localhost`。首次认证失败后重新登录、使用新 RUN 重跑并在报告中说明，这部分审计透明性可以接受。

## 阻塞缺口

### 1. workspace 隔离不符合 Gate 2 现行矩阵

报告明确写明六轮共用：

`/home/administrator/omnigent-workspaces`

而 `CODEX_TASK_28_PLAN.md` / `GROK_GATE2_POLICY_REVIEW.md` 的 Gate 2 矩阵要求 C、E-positive、E-negative、R 使用不同 workspace 根，并用 workspace sentinel 证明隔离。当前没有每轮独立 workspace 的证据，也没有批准的例外记录。

这不是单纯的展示问题：共享 workspace 会让 C/E/R 的文件、缓存和运行产物互相污染，无法证明 Gate 2 的 workspace isolation 条件。

**处理：**新 RUN 必须为 C、E-pos、E-neg、R 分配不同绝对 workspace；E-pos-strict 与 E-pos 可沿用同一 E-positive workspace 仅在协议明确允许时，E-neg 两轮必须与 E-positive 分开。

### 2. “strict”轮次没有 strict 证据

`sessions.txt` 六行均为 `strict=0`，包括：

- `role=E-pos-strict`
- `role=E-neg-strict`

因此当前证据只能证明两次普通 Grok headless turn，不能证明名为 strict 的轮次真的启用了 strict 条件。若 Grok 没有 `native_prompt_delivery` 的 strict 通道，应将这两轮改名为明确的隔离负向/正向控制，不得继续使用 `*-strict` 名称冒充 strict Gate 2 轮次；若 Gate 2 协议要求 strict，则必须提供真实 strict 环境注入和对应失败/继续判据。

### 3. evidence 文件数量自相矛盾

实际目录列出 **32 个文件**：30 个轮次文件（6 轮 × 5）+ `manifest.txt` + `sessions.txt`。但：

- Hermes 报告第 1、7 节写 **36 文件**，并写“6 轮 × 6”；
- `grok-gate2-final-verification.txt` 同时写“36 文件”和“目录总数 32”；
- r2/r3 验证又按 32 文件通过。

这必须在新的 Gate 2 报告和验证脚本中统一为实际清单，不得继续保留矛盾数字。此项单独可文档修正，但与前两项一起构成当前 Gate2 不可签字的审计缺口。

## 清理边界

manifest 的 leak-scan 分为三类是正确方向：vendor Grok CLI 为 0、观察工具单独列出、harness 单独列出。但当前仍有 9 个常驻 harness，其中包含 precheck 和旧认证失败会话的残留。即使产品 idle 语义允许常驻 harness，也必须在 Gate2 结论中明确：

- 哪些属于本 RUN 必须保留的 harness；
- 哪些是旧失败 RUN 的残留；
- 旧残留何时回收、PID 是否最终 dead。

在旧失败 harness 未回收或没有明确授权保留前，不应写“cleanup 完整”或进入 merge。

## E-neg 语义适配结论

Grok CLI_SUBPROCESS 没有 `native_prompt_delivery` 模块，因此把 E-neg 的业务断言改为“代理负向 + headless 负向”在 Grok 专项验收中可以作为产品隔离证据；但它不能自动替代全局 Gate 2 的 prompt-delivery warn/strict 契约。报告必须明确这是 **Grok 专项适配矩阵**，而不是证明全仓 native prompt-delivery Gate 已通过。

## 下一步唯一建议

开一张新的 Gate 2 修正卡，使用全新 RUN_ID，先修正并重新取证：

1. C/E/R 分离 workspace；
2. 明确 strict 轮的真实语义和证据，不能 `strict=0` 仍命名 strict；
3. 统一 evidence 实际文件清单为 32 或按新增文件重新生成一致清单；
4. 回收旧认证失败会话的残留 harness，记录 PID dead；
5. 保留六轮 headless 资源和代理负向断言。

修正后再由 Codex 只读复核。当前结论：**Gate 2 未签字、不可 merge、非全仓 GREEN**。

本审查未修改源码、测试、TUN、Clash、OpenCodex、10100 或 evidence，未 commit/push/merge/tag。
