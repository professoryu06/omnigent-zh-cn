# Agent 交接审查包：Omnigent 问题分析 + 修复方案 + 当前状态（审查修订版）

**文档用途：** 给独立 agent / 审查者。  
**权威状态：** `gh pr view 2 --json headRefOid` + [fixes/STATUS.md](./fixes/STATUS.md) — **不要**把文中快照 SHA 当永久 head。  
**生成时说明：** 正文可含历史快照；以 PR head 为准。

---

## 0. 现在是什么情况

| 项 | 现状 |
|----|------|
| 分发仓 | [professoryu06/omnigent-zh-cn](https://github.com/professoryu06/omnigent-zh-cn) |
| 上游 | [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent) |
| 文档 PR | https://github.com/professoryu06/omnigent-zh-cn/pull/2 （**勿擅自 merge**） |
| 功能代码 | 以后续独立 `fix/*` PR 为准；文档 PR 不应混入未复现的大补丁 |
| 证据纪律 | 已证实 / 未复现 / 仅上游报告 / 已被上游修复 |
| 禁止 | 擅自 merge、打发布 Tag、发版、关上游 issue |

### 审查修订要点（相对初稿）

1. **不再**称 7 项为「近期唯一正确性 backlog」→ **首批待复现的核心候选**（混合正确性/隔离/组合/长任务）。  
2. 优先级：P0 候选 #2853+#3016；P1 #2747/#2746+#2854+#2539；P1 长任务 #2967；条件性 #3012；Scale 延后。  
3. **#3012：** 禁止「定时 login 无人值守」表述；默认跟踪 [upstream #3013](https://github.com/omnigent-ai/omnigent/pull/3013)；L0 仅 runbook；注意 replica grant 与并发刷新锁。  
4. **#2853：** 逐 harness 矩阵；apply|warn|error；第一阶段最低 = 禁止静默；方案 C ≠ 单纯 warn-only。  
5. **#2747/#2746：** 可同 PR，**独立 commit + 独立测试**；优先级从规范/代码确认。  
6. **矩阵：** Markdown checklist ≠ 可运行；pytest 优先。  
7. **Tag：** 单调 `v0.6.0-zhcn.N`；本轮不打 Tag。

---

## 1. 用户场景

- AgentCenter / agentpeihe 多角色编排；多 harness（sdk + native + pi 等）。  
- 本机可能有 `omnigent` CLI；**环境存在 ≠ issue 已复现**。

---

## 2. 原始分析报告

全文：[omnigent-issues-analysis-report.md](./omnigent-issues-analysis-report.md)  

该报告是**筛选输入**，证据标签默认为 **仅上游报告**，直到本地可运行测试落定。

---

## 3. 首批待复现的核心候选

### 3.1 约束类型（混合）

| 类型 | Issue 例 |
|------|----------|
| 正确性（身份/路由） | #2853, #2747, #2746, #2854 |
| 隔离性 | #3016 |
| 可组合性 | #2539 |
| 长任务可用性 | #2967, 条件 #3012 |

### 3.2 优先级表

| 优先级 | Issue |
|--------|-------|
| P0 / Release Blocker **候选** | #2853, #3016 |
| P1 | #2747, #2746, #2854, #2539 |
| P1 长任务 | #2967 |
| 条件性 P0/P1 | #3012（双机/重连/无人值守时升级） |
| Scale | #3004, #3003, #2702, #3001 |

### 3.3 大白话效果（非证据）

| 现象 | 候选 | 档 |
|------|------|----|
| 角色 prompt 静默没了 | #2853 | P0 候选 |
| 多 agent 目录串了 | #3016 | P0 候选 |
| YAML harness/model 不对 | #2747/#2746 | P1 |
| 长跑 403 | #3012 | 条件性；看 #3013 |

---

## 4. 修复方案摘要

详册：

- [fixes/README.md](./fixes/README.md)  
- [fixes/CORE_FIX_PLANS.md](./fixes/CORE_FIX_PLANS.md)  
- [fixes/SECONDARY_FIX_PLANS.md](./fixes/SECONDARY_FIX_PLANS.md)  

### #2853

- 矩阵 + capture double；apply / warn / error。  
- 最低：禁止静默。敏感内容慎用 argv。

### #3016

- 失败 snapshot 不写 workspace 投影缓存；reset 驱逐；注意错误 cwd 已启动进程。

### #2747 / #2746

- 从 loader / `_codex_native_model_from_spec` 源码确认契约；独立测试。

### #3012

- **跟踪** draft PR https://github.com/omnigent-ai/omnigent/pull/3013  
- L0：人工 re-login、提高 TTL、诊断文案 — **不**解决生命周期根因  
- 风险：每 replica 独立 grant；并发 refresh 要锁  
- **禁止** zh-cn 另造 refresh 协议

---

## 5. Git / 版本

见 [ops/versioning/BRANCHING.md](../ops/versioning/BRANCHING.md)：

- 文档 → PR #2 分支  
- 功能 → 独立 `fix/*` PR  
- 发布 tag 单调 `v0.6.0-zhcn.N`；**本轮不创建**

---

## 6. 可运行复现

见 [scripts/repro/README.md](../scripts/repro/README.md) 与 pytest 目标路径。

---

## 7. 审查清单（修订后）

1. 优先级分层是否同意？  
2. #3012 跟踪上游是否足够？  
3. #2853 第一阶段 fail-loud 是否可接受？  
4. Tag 单调序列是否同意？  
5. 是否要求先可运行失败测试再合功能 PR？  

---

## 8. 停线条件（执行方）

源码与 issue 不符 / 无法稳定复现 / 上游已修 / 需破坏性 API 无迁移 / prompt 只能走不安全 argv / 断言只能靠模型随机性 / 工作区有冲突用户改动 → **停该 issue 实现**，报告证据，继续其他项。

---

*「已修复」必须以预修复失败 + 修复后通过 + 提交为准。*
