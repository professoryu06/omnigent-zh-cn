# 修完后交给审查 agent 的标准提示词（模板 + 当前填充）

**用法：** 每轮功能/文档修复结束后，更新下方「当前快照」区块，把「完整提示词」整段复制给 Codex/其他审查 agent。  
**约束默认：** 不 merge、不打新 Tag、不关上游 issue、不实现未复现问题（除非提示词明确授权）。

---

## 当前快照（2026-07-23，以 `gh pr view` 为准）

| PR | 主题 | head（快照） | 状态 |
|----|------|--------------|------|
| [#2](https://github.com/professoryu06/omnigent-zh-cn/pull/2) | 方案/Tag/矩阵/交接文档 | `ba70d41` | OPEN |
| [#3](https://github.com/professoryu06/omnigent-zh-cn/pull/3) | #3016 workspace 缓存 | `744e3a0` | OPEN，审查倾向 approve |
| [#4](https://github.com/professoryu06/omnigent-zh-cn/pull/4) | #2747 harness + #2746 model | `30c04c3` | OPEN，审查倾向 approve |
| [#5](https://github.com/professoryu06/omnigent-zh-cn/pull/5) | #2853 fail-loud Phase1 | `1f42a89` | OPEN，审查倾向 approve |

- **Tag：** 远端已有 `v0.6.0-zhcn.1`（2026-07-19）；本轮**未创建新 Tag**。  
- **集成：** main+PR3+4+5 本地临时合入无冲突；定向 3+7+57 tests 全绿；全仓 pytest 因 Windows/依赖受限。  
- **AgentCenter 实机 smoke：** 未执行。

### 交接文档入口

| 文档 | 路径 / 链接 |
|------|-------------|
| 本提示词模板 | `docs/fixes/POST_FIX_HANDOFF_PROMPT.md` |
| 修复交接总包 | `docs/fixes/REVIEW_HANDOFF_2026-07-22.md` |
| 状态表 | `docs/fixes/STATUS.md` |
| 核心方案 | `docs/fixes/CORE_FIX_PLANS.md` |
| 次要方案 | `docs/fixes/SECONDARY_FIX_PLANS.md` |
| 可运行矩阵规格 | `scripts/repro/matrix-core.md` |
| 版本约定 | `ops/versioning/BRANCHING.md` |
| PR #2 浏览 | https://github.com/professoryu06/omnigent-zh-cn/blob/docs/fix-plans-core-secondary/docs/fixes/ |

### 接下来打算做什么（建议顺序）

1. **维护者 merge：** #3 → #4 → #5（注明 fail-loud）→ #2  
2. **#2853 Phase2：** 逐 harness 安全 apply（禁止盲目 argv）  
3. **未复现核心：** #2539 → #2854 → #2967（先红后绿）  
4. **#3012：** 跟踪上游 #3013，不重复实现  
5. **Scale：** #3004/#3003/#2702/#3001（核心合入后再做）  
6. **AgentCenter smoke：** 多角色隔离 + harness/model + native warn/strict  

---

## 整体修复计划 TodoList

### A. 工程闭环（非代码）

- [ ] Merge PR #3（#3016）
- [ ] Merge PR #4（#2747/#2746）
- [ ] Merge PR #5（#2853 Phase1，release note 写清非完整送达）
- [ ] Merge PR #2（文档）
- [ ] （可选）发版：下一单调 Tag `v0.6.0-zhcn.2` + changelog 列出补丁集合
- [ ] Linux/完整 dev 环境全仓 pytest 基线对比

### B. 核心正确性（代码）

| ID | Issue | 状态 | 下一步 |
|----|-------|------|--------|
| B1 | #3016 workspace 毒化 | **PR #3 待合** | merge |
| B2 | #2747 nested harness | **PR #4 待合** | merge |
| B3 | #2746 codex model | **PR #4 待合** | merge |
| B4 | #2853 fail-loud | **PR #5 待合** | merge；**不算完整修完** |
| B5 | #2853 prompt apply | **未做** | Phase2：能力矩阵 + 安全通道 + capture double |
| B6 | #2539 named 子会话 | **未复现** | 先写可失败测试再修 |
| B7 | #2854 harness_override kickoff | **未复现** | 同上 |
| B8 | #2967 auto-compact | **未复现** | 同上 |

### C. 条件性 / 上游

| ID | Issue | 状态 | 下一步 |
|----|-------|------|--------|
| C1 | #3012 JWT 续期 | 跟踪 **#3013** draft | 验证/backport 仅紧急时 |
| C2 | #2575 pi-native | 跟踪 **#2833** | 无缺口不 backport |

### D. Scale（后置）

| ID | Issue | 状态 |
|----|-------|------|
| D1 | #3004 stream ACL 查询 | 仅计划 |
| D2 | #3003 policy rebuild | 仅计划 |
| D3 | #2702 idle tmux | 仅计划 |
| D4 | #3001 sessions list | 仅计划 |

### E. 产品验收

- [ ] AgentCenter：workspace 隔离（#3016）
- [ ] nested codex-native 不被 model-prefix 替换（#2747）
- [ ] codex 使用 executor.model（#2746）
- [ ] native 非 strict 有告警、strict 注入前失败（#2853 P1）
- [ ] **不**声称 prompt 已送达，除非 Phase2 证据齐全

---

## 完整提示词（复制给 Codex）

```text
你是独立审查 agent。请审查 Omnigent-zh-cn「当前进度 + 本轮修复成果 + 后续计划」，判断 PR 是否可合、剩余工作是否合理，最多给 3 条下一步。

## 仓库
https://github.com/professoryu06/omnigent-zh-cn
上游：https://github.com/omnigent-ai/omnigent

## 开始前必须
gh pr view 2 --json headRefName,headRefOid,state,url,title
gh pr view 3 --json headRefName,headRefOid,state,url,title
gh pr view 4 --json headRefName,headRefOid,state,url,title
gh pr view 5 --json headRefName,headRefOid,state,url,title
git ls-remote --tags origin

交接文档（以 PR #2 分支为准）：
- docs/fixes/POST_FIX_HANDOFF_PROMPT.md（进度+todo+本提示词）
- docs/fixes/REVIEW_HANDOFF_2026-07-22.md
- docs/fixes/STATUS.md
- docs/fixes/CORE_FIX_PLANS.md

## 1. 之前做到哪了（进度）

### 已完成（有独立 PR，均 OPEN 未 merge）
| 项 | PR | 说明 |
|----|-----|------|
| #3016 workspace 缓存毒化 | #3 | 完整功能修复；test-first；审查倾向 approve |
| #2747 nested config.harness | #4 | 完整功能修复；只 alias harness；flat 优先 |
| #2746 codex executor.model | #4 | 完整功能修复；优先 executor.model |
| #2853 Phase1 fail-loud | #5 | **仅缓解**：warn/strict；**未 apply prompt** |
| 方案/Tag/矩阵/交接文档 | #2 | 单调 v0.6.0-zhcn.N；fix-core/scale 废弃；Tag 事实已澄清 |

### 半完成
- #2853：诊断 100%，真实送达 0%（Phase2 未做）

### 未开始 / 仅跟踪
- #2854、#2539、#2967（核心候选，未复现）
- #3012（上游 #3013）、#2575（上游 #2833）
- Scale #3003/#3004/#2702/#3001

### 工程事实
- 远端已有 Tag `v0.6.0-zhcn.1`（本轮前）；本轮未创建新 Tag、未发版
- 本轮未 merge 任何 PR
- 临时集成 main+#3+#4+#5：无冲突；定向 3+7+57 tests 绿；Ruff 绿
- 全仓 pytest：Windows 上 collection/环境失败多，不能当干净绿灯
- AgentCenter 多角色 smoke：未执行

## 2. 修复交接文档是什么
1. docs/fixes/REVIEW_HANDOFF_2026-07-22.md — 总交接包
2. docs/fixes/STATUS.md — 状态表与证据标签
3. docs/fixes/CORE_FIX_PLANS.md / SECONDARY_FIX_PLANS.md — 方案
4. scripts/repro/matrix-core.md — 验收矩阵规格
5. ops/versioning/BRANCHING.md — 分支/Tag
6. docs/fixes/POST_FIX_HANDOFF_PROMPT.md — 本进度+todo+提示词

## 3. 接下来打算做什么
1. 维护者 merge：#3 → #4 → #5（注明 fail-loud）→ #2
2. #2853 Phase2 安全 apply（禁止盲目 argv）
3. 复现并修：#2539 → #2854 → #2967
4. #3012 跟踪上游 #3013
5. Scale 后置
6. AgentCenter 实机 smoke

## 4. 整体 TodoList（审查时请核对是否合理）
A 闭环：merge #3/#4/#5/#2；可选 v0.6.0-zhcn.2
B 核心：B5 apply；B6 #2539；B7 #2854；B8 #2967
C 上游：#3013/#2833
D Scale：#3004/#3003/#2702/#3001
E 产品验收：隔离/harness/model/warn-strict；不误称 prompt 已送达

## 审查要求
- 区分：已证实 / mitigated(fail-loud) / 未复现 / PR open 未 merge
- 核对 #2 是否仍有 0x0B 控制字符、「未打 Tag/无 Tag」、fix-core 双轨例外
- 核对 #5 是否仍可能被误读为「prompt 已送达」
- 核对 #4 body 是否只声称 alias config.harness
- 不要 merge、不要打 Tag、不要实现 Phase2（除非用户另授）

## 输出格式
## 审查结论
- 总体：
- PR #2/#3/#4/#5：

## 进度是否准确
- 同意 / 需更正：…

## TodoList 是否合理
- 同意 / 调整建议：…

## 发现问题
- [P0/P1/P2] …

## 下一步（最多 3 条）
1. …
2. …
3. …
```

---

## 维护说明（给人/执行 agent）

每轮修完后更新本文件顶部「当前快照」三块：

1. PR head 表  
2. 做到哪 / 半完成 / 未做  
3. 接下来 3～6 条  

然后把「完整提示词」整段发出去。勿在提示词里写死会过期的 SHA 却不写「以 gh 为准」。
