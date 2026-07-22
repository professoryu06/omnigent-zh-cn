# 修完后交给审查 agent 的标准提示词（模板 + 当前填充）

**用法：** 每轮功能/文档修复结束后，更新下方「当前快照」区块，把「完整提示词」整段复制给 Codex/其他审查 agent。  
**约束默认：** 不 merge、不打新 Tag、不关上游 issue、不实现未复现问题（除非提示词明确授权）。  
**时间快照：** 下文 PR head、上游 PR 状态均为**生成时快照**；审查前必须用 `gh` 重新查询。

---

## 当前快照（约 2026-07-23，以 `gh pr view` 为准）

| PR | 主题 | head（快照） | 状态 |
|----|------|--------------|------|
| [#2](https://github.com/professoryu06/omnigent-zh-cn/pull/2) | 方案/Tag/矩阵/交接文档 | 以 `gh pr view 2` 为准 | OPEN |
| [#3](https://github.com/professoryu06/omnigent-zh-cn/pull/3) | #3016 workspace 缓存 | `744e3a0`（审查时） | OPEN，审查倾向 approve |
| [#4](https://github.com/professoryu06/omnigent-zh-cn/pull/4) | #2747 harness + #2746 model | `30c04c3`（审查时） | OPEN，审查倾向 approve |
| [#5](https://github.com/professoryu06/omnigent-zh-cn/pull/5) | #2853 fail-loud Phase1 | `1f42a89`（审查时） | OPEN，审查倾向 approve |

### 验证状态（如实，勿夸大）

| 项 | 状态 |
|----|------|
| 定向回归（PR#3+#4+#5 相关，合计 67 tests） | **已通过**（临时集成 main+3+4+5 时：3+7+57） |
| 目标路径 Ruff | **已通过**（同上集成树） |
| 全仓 `pytest -q` | **未获得绿灯**。Windows collection：fcntl/pexpect/databricks 等 **环境/平台限制**；不得写成「全仓已通过」或「代码回归已排除完毕」 |
| AgentCenter 实机 smoke | **未执行** |
| Tag | 远端已有 `v0.6.0-zhcn.1`（2026-07-19，早于本轮）；**本轮未创建新 Tag、未发版** |
| 四 PR merge | **均未 merge** |

### 交接文档入口

| 文档 | 路径 |
|------|------|
| 本文件 | `docs/fixes/POST_FIX_HANDOFF_PROMPT.md` |
| 修复交接总包 | `docs/fixes/REVIEW_HANDOFF_2026-07-22.md` |
| 状态表 | `docs/fixes/STATUS.md` |
| 核心方案 | `docs/fixes/CORE_FIX_PLANS.md` |
| 次要方案 | `docs/fixes/SECONDARY_FIX_PLANS.md` |
| 可运行矩阵规格 | `scripts/repro/matrix-core.md` |
| 版本约定 | `ops/versioning/BRANCHING.md` |

### 合并前门槛（功能 PR merge 之前必须完成）

以下两项是 **#3 / #4 / #5 合并前门槛**，不是可选项：

1. **Linux / 完整 dev 依赖环境** 上的全仓（或仓库约定的 CI 等价）pytest 回归  
2. **AgentCenter 最小** Controller / Executor / Reviewer **实机 smoke**（隔离、harness/model、native warn/strict；**不得**因此声称 prompt 已送达）

### 建议总顺序（只写计划，本 agent 不执行 merge/发布）

1. 合并前全仓/平台回归（门槛 1）  
2. AgentCenter smoke（门槛 2）  
3. 维护者 merge **#3 → #4 → #5**（#5 release note：仅 fail-loud Phase1）  
4. 刷新 `STATUS.md` 后 merge **#2**  
5. 可选：发布决策与 changelog（下一单调 Tag 仅当维护者明确要求）  
6. #2853 Phase2 安全 apply  
7. #2539 → #2854 → #2967（先复现再修）  
8. Scale 后置（#3004/#3003/#2702/#3001）  

---

## 整体修复计划 TodoList

### A. 工程闭环

- [ ] **合并前：** Linux/完整 dev 全仓 pytest（或 CI 等价）— **门槛**  
- [ ] **合并前：** AgentCenter 最小 C/E/R smoke — **门槛**  
- [ ] Merge PR #3（#3016）  
- [ ] Merge PR #4（#2747/#2746）  
- [ ] Merge PR #5（#2853 Phase1；文案不得写 prompt 已送达）  
- [ ] 刷新 STATUS 后 Merge PR #2  
- [ ] （可选）维护者决策：`v0.6.0-zhcn.2` + changelog  
- [x] 临时集成 #3+#4+#5 无冲突 + 定向 67 tests + 目标 Ruff（已做；**不等于**全仓/实机通过）

### B. 核心正确性

| ID | Issue | 状态 | 下一步 |
|----|-------|------|--------|
| B1 | #3016 | PR #3 待合 | 过门槛后 merge |
| B2 | #2747 | PR #4 待合 | 过门槛后 merge |
| B3 | #2746 | PR #4 待合 | 过门槛后 merge |
| B4 | #2853 fail-loud | PR #5 待合 | 过门槛后 merge；**不算完整修完** |
| B5 | #2853 prompt apply | **未实现** | Phase2：能力矩阵 + 安全通道 + capture double |
| B6 | #2539 | **未复现** | 先红后绿 |
| B7 | #2854 | **未复现** | 先红后绿 |
| B8 | #2967 | **未复现** | 先红后绿 |

### C. 条件性 / 上游（状态为时间快照，须重查）

| ID | Issue | 快照说明 | 下一步 |
|----|-------|----------|--------|
| C1 | #3012 JWT | 上游 **#3013** 审查时为 **open draft** | 跟踪/验证；紧急才考虑 backport |
| C2 | #2575 pi-native | 上游 **#2833** 审查时 **open、未 merge，且审查时不可合并** | **仅跟踪，不默认直接落地**；无缺口不 backport |

### D. Scale（后置）

| ID | Issue | 状态 |
|----|-------|------|
| D1–D4 | #3004 / #3003 / #2702 / #3001 | 仅计划；核心合入后再动 |

### E. 产品验收（与门槛 2 重叠）

- [ ] workspace 隔离（#3016）  
- [ ] nested codex-native 不被 model-prefix 替换（#2747）  
- [ ] codex 使用 `executor.model`（#2746）  
- [ ] native 非 strict 有告警；strict 在用户消息注入前失败（#2853 Phase1）  
- [ ] **禁止**在未完成 Phase2 证据前声称 prompt 已送达  

---

## 完整提示词（复制给 Codex）

```text
你是独立审查 agent。请审查 Omnigent-zh-cn「当前进度 + 交接计划 + 合并前门槛」，判断文档是否准确、Todo 顺序是否合理，最多给 3 条下一步。

## 仓库
https://github.com/professoryu06/omnigent-zh-cn

## 开始前必须
gh pr view 2 --json headRefName,headRefOid,state,url,title
gh pr view 3 --json headRefName,headRefOid,state,url,title
gh pr view 4 --json headRefName,headRefOid,state,url,title
gh pr view 5 --json headRefName,headRefOid,state,url,title
git ls-remote --tags origin
gh pr view 3013 --repo omnigent-ai/omnigent --json state,isDraft,mergeable 2>/dev/null || true
gh pr view 2833 --repo omnigent-ai/omnigent --json state,mergeable 2>/dev/null || true

交接：docs/fixes/POST_FIX_HANDOFF_PROMPT.md（主）、STATUS.md、REVIEW_HANDOFF_2026-07-22.md

## 1. 做到哪了（准确措辞）

### 代码/文档 PR（均 OPEN 未 merge）
- #3016 → PR #3：功能修复 + 定向测试通过（待合）
- #2747/#2746 → PR #4：功能修复 + 定向测试通过（待合）
- #2853 Phase1 → PR #5：
  - **Phase1 单元级 fail-loud 实现完成**（warn / OMNIGENT_STRICT_PROMPT）
  - **真实 prompt 送达未实现**
  - **AgentCenter / 真实 native E2E 未验证**
  - 不得写「诊断 100%」或「prompt 已送达」
- 文档 → PR #2：方案、Tag 语义、交接包

### 验证
- 定向 67 tests（3+7+57）+ 目标 Ruff：集成时已通过
- 全仓 pytest：**未通过/未获得绿灯**（Windows：fcntl/pexpect/databricks 等环境限制；非已证明代码回归）
- AgentCenter smoke：**未执行**
- Tag：已有 v0.6.0-zhcn.1；本轮未创建新 Tag

### 合并前门槛（必须先完成再 merge #3/#4/#5）
1. Linux/完整 dev 全仓 pytest（或 CI 等价）
2. AgentCenter 最小 C/E/R smoke

### 建议顺序
门槛回归 → smoke → merge #3→#4→#5 → 刷新 STATUS merge #2 → 可选发版 → Phase2 apply → #2539→#2854→#2967 → Scale

### 上游快照（须重查）
- #3013：open draft
- #2833：open、未 merge、审查时不可合并；仅跟踪不默认落地

## 2. 审查要点
- 完成度措辞是否夸大
- Todo 是否把全仓/smoke 放在 merge 前
- C2 是否写明 #2833 仅跟踪
- 无「未打 Tag/无 Tag」；fix-core/scale 仅废弃语境
- 不 merge、不打 Tag、不实现 Phase2（除非另授）

## 输出
## 审查结论
## 进度措辞是否准确
## Todo/门槛是否合理
## 发现问题
## 下一步（最多 3 条）
```

---

## 维护说明

每轮更新：

1. PR head 表（或写「以 gh 为准」）  
2. 验证状态表（定向 / 全仓 / smoke 分开）  
3. 上游 #3013/#2833 快照日期  
4. 门槛勾选状态  

**禁止：** 用「全绿/已验证」笼统概括；把 fail-loud 写成 prompt 已送达；把 Windows collection error 写成已证明的代码回归。
