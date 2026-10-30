# CODEX_TASK_GROK_NATIVE_GATE2_REWORK_02

## 目标

只验证 **Grok Native 是否可稳定使用**。修正 `grok-native-gate2-01` 的 Grok 专项审计缺口，重新取得可签字的 Grok 六轮证据。**不涉及 Claude、Codex、Qwen、其他 Agent、全仓 Gate 2 或项目整体发布验收；不修改源码**。

## 前置审查

- `CODEX_REVIEW_GROK_NATIVE_GATE2_01.md`
- `CODEX_TASK_GROK_NATIVE_GATE2_01.md`
- `CODEX_TASK_28_PLAN.md`
- `GROK_GATE2_POLICY_REVIEW.md`

## 必须修正的四项

### 1. Workspace 隔离

使用全新 RUN_ID 和全新 evidence 根，至少建立以下不同绝对 workspace：

- C：`.../workspaces/controller`
- E-positive：`.../workspaces/executor-positive`
- E-negative：`.../workspaces/executor-negative`
- R：`.../workspaces/reviewer`

每个 workspace 写入唯一 sentinel 文件，session 创建、manifest、runner 日志和最终报告必须能对应到正确 workspace。E-positive 与 E-negative 不得共用 workspace。

### 2. Strict 语义重新定名或补齐

在 Grok 没有 `native_prompt_delivery` strict 通道的前提下，不能继续把普通隔离轮命名为 `E-pos-strict` / `E-neg-strict`。

本卡采用 **Grok 专项路径**：改名为 `E-pos-control` / `E-neg-control`，报告明确它们只验证 Grok 的代理隔离、headless 资源和多轮可用性，不声称 prompt-delivery strict。不得出现角色名含 `strict` 但 `sessions.txt` 仍为 `strict=0` 的情况。

### 3. Evidence 清单统一

实际目录有多少文件就记录多少。当前结构为每轮 5 个文件 × 6 轮 + `manifest.txt` + `sessions.txt` = 32 个文件；如果增加代理复核文件，必须真实写入并重新计数。报告、manifest、验证脚本三处数字必须一致。

### 4. 清理旧 harness

重跑前清点并回收旧认证失败 session 的残留 harness；每个旧 PID 必须记录 dead。最终 leak-scan 分三类记录：

- vendor Grok CLI：必须为 0；
- 本 RUN 仍在工作的产品 harness：逐项列出，不称为泄漏；
- 观察脚本/tee：单独列出。

如果旧残留不能安全回收，必须分类为 `REWORK_INCONCLUSIVE`，不得写 cleanup 完整。

## 执行硬约束

- 全新 RUN_ID；不得拼接 `grok-native-gate2-01` 旧业务结果。
- TUN/Clash/OpenCodex/10100/认证/240s watchdog 不改。
- 不修改 `omnigent/`、`tests/`、策略、STATUS 或用户配置。
- 不删除旧 evidence；不 commit/push/merge/tag。
- 凭据和代理值全部 `[REDACTED]`。

## 子 agent 并行安排

Hermes 主 agent 可以并行派 3 个只读子 agent，禁止子 agent 启动真实六轮或修改共享运行状态：

1. `workspace-audit`：核对 Gate 2 workspace 隔离要求，给出 manifest 字段清单；
2. `strict-semantics-audit`：核对 Grok CLI 是否存在 strict/prompt-delivery 通道，明确采用 control 命名还是切换 warn/strict native；
3. `evidence-cleanup-audit`：核对旧 harness PID、证据文件数量和三类 leak-scan 口径。

Hermes 主 agent 负责唯一一次真实六轮执行、合并子 agent 报告和最终 evidence，避免多个 agent 并发创建 session。

## 交付

唯一仓库报告：

`F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\HERMES_DIAGNOSIS_GROK_NATIVE_GATE2_REWORK_02.md`

报告必须给出唯一 Grok 专项分类：

- `GATE2_READY_FOR_CODEX_SIGNOFF`：所有缺口关闭；或
- `GATE2_REWORK_INCONCLUSIVE`：任一 workspace/strict/计数/cleanup 不可审计。

完成后停止，等待 Codex 只读验收。
