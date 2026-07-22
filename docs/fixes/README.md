# Omnigent 问题修复方案总览（修订版）

**仓库：** [professoryu06/omnigent-zh-cn](https://github.com/professoryu06/omnigent-zh-cn)  
**上游：** [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent)  
**权威状态：** PR head + [STATUS.md](./STATUS.md)（勿在正文写死「当前 commit」当权威）  
**交接审查包：** [../AGENT_HANDOFF_omnigent_issues_and_fix_plans.md](../AGENT_HANDOFF_omnigent_issues_and_fix_plans.md)

---

## 1. 证据纪律（强制）

每个 issue 的结论必须标注其一：

| 标签 | 含义 |
|------|------|
| **已证实** | 本仓库当前代码上有稳定失败测试/复现产物 |
| **未复现** | 尝试后不能稳定失败；不得套补丁 |
| **仅上游报告** | 仅 issue/讨论描述；本地未验证 |
| **已被上游修复** | upstream main 或已合并 PR 已消除行为 |

禁止把 issue 描述、方案文档或上游标签当成「本地已经确认中招」。

---

## 2. 首批待复现的核心候选（非「唯一正确性 backlog」）

下列 issue 是**首批待复现的核心候选**。它们混合了：

- **正确性**（身份、路由）
- **隔离性**（workspace）
- **可组合性**（子会话）
- **长任务可用性**（compact / 认证生命周期）

### 建议优先级

| 优先级 | Issue | 类别 |
|--------|-------|------|
| **P0 / Release Blocker 候选** | #2853、#3016 | 静默身份丢失；工作区隔离毒化 |
| **P1** | #2747 / #2746、#2854、#2539 | 路由/覆盖/子会话 |
| **P1 长任务能力** | #2967 | 上下文满后可用性 |
| **条件性 P0/P1** | #3012 | 双机、重连、无人值守时升级；默认跟踪上游 |
| **Scale（本轮不先大改热路径）** | #3004、#3003、#2702、#3001 | 吞吐/UI |

### 修复分层

| 层 | 含义 |
|----|------|
| **L0 运维** | runbook / 诊断 / 人工步骤；**不声称**解决生命周期根因 |
| **L1 zh-cn 补丁** | 有复现证据后在 fork 修 + 测试 |
| **L2 上游** | 干净 PR 回 omnigent-ai；优先跟踪已有 upstream PR |

---

## 3. 方案入口

| 文档 | 内容 |
|------|------|
| [CORE_FIX_PLANS.md](./CORE_FIX_PLANS.md) | 核心候选：按 harness/契约的修复方案 |
| [SECONDARY_FIX_PLANS.md](./SECONDARY_FIX_PLANS.md) | #3012 与 Scale |
| [STATUS.md](./STATUS.md) | 分支 / PR / 复现状态 |
| [../omnigent-issues-analysis-report.md](../omnigent-issues-analysis-report.md) | 原始筛选报告（历史输入，非证据） |
| [../../ops/versioning/BRANCHING.md](../../ops/versioning/BRANCHING.md) | 分支与发布序列 |
| [../../scripts/repro/README.md](../../scripts/repro/README.md) | 可运行矩阵 vs checklist |

---

## 4. 版本 / Tag 语义（本轮不打 Tag）

优先**单调发布序列**：

```text
v0.6.0-zhcn.1
v0.6.0-zhcn.2
```

`core` / `scale` 写入 changelog、release note、GitHub label 或补丁清单，**不**再形成两条独立版本线。

若使用 `fix-core.N` / `fix-scale.N` 命名，必须：每个 Tag 建立在上一发布 Tag 上，并列出完整包含关系、上游基线 SHA、补丁集合。

**本轮执行：不创建 Tag、不发布包、不合并 PR。**

---

## 5. 推荐实施顺序（以复现结果为准）

```text
1. 文档修订（PR #2）
2. 可运行复现：C-3016、C-2853、C-2747/C-2746（先失败证据）
3. 功能 PR：#3016 → #2853 → #2747/#2746（各自独立分支）
4. 其余：#2854、#2539、#2967 补复现；#3012 跟踪 upstream #3013
5. Scale：仅基线与计划，核心正确性前不大改热路径
```

---

## 6. 状态权威来源

- **生成时快照：** 见 STATUS.md「文档生成快照」行（会过期）
- **权威：** `gh pr view <n> --json headRefOid` 与 STATUS.md 表中实测结果列
- **「已修复」：** 仅当预修复失败 + 修复后通过 + 代码提交齐全
