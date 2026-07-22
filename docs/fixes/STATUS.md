# 修复与复现状态跟踪

**权威状态来源：** 本表 + `gh pr view <n> --json headRefOid,state`。  
**文档生成快照（会过期）：** 见下方「快照」行；以 PR head 为准。

| 字段 | 生成时快照 |
|------|------------|
| 文档 PR #2 分支 | `docs/fix-plans-core-secondary` |
| 快照时间 | 修订执行时写入 commit message / 本表更新行 |
| 快照 head | 以 push 后 `gh pr view 2 --json headRefOid` 为准 |

## Issue 跟踪

| Issue | 优先级 | 证据标签 | 分支 | PR | 预修复测试 | 修复后测试 | 状态 |
|-------|--------|----------|------|-----|------------|------------|------|
| #3016 | P0 候选 | 待复现 | `fix/core-workspace-3016` | — | — | — | planned |
| #2853 | P0 候选 | 待复现 | `fix/core-2853-native-prompt` | — | — | — | planned |
| #2747 | P1 | 待复现 | `fix/core-spec-parse-2746-2747` | — | — | — | planned |
| #2746 | P1 | 待复现 | 同上（独立 commit） | — | — | — | planned |
| #2854 | P1 | 仅上游报告 | — | — | — | — | planned |
| #2539 | P1 | 仅上游报告 | — | — | — | — | planned |
| #2967 | P1 长任务 | 仅上游报告 | — | — | — | — | planned |
| #3012 | 条件性 | 上游 draft PR #3013 | 不重复实现 | — | — | — | track-upstream |
| #2575 | 条件 | 上游 PR #2833 open | 不 backport 除非缺口 | — | — | — | track-upstream |
| #3004/#3003/#2702/#3001 | Scale | 仅上游报告 | — | — | — | — | deferred |

状态枚举：`planned` → `repro-failed-as-expected` → `fix-pr-open` → `fix-pr-merged` → `upstream-merged` / `wontfix` / `not-reproduced` / `track-upstream` / `deferred`

## 文档波次

| 波次 | 内容 | 分支 | 状态 |
|------|------|------|------|
| 0 | 初稿方案 | `docs/fix-plans-core-secondary` | superseded |
| 1 | 审查修订（优先级/#3012/#2853 契约/矩阵/Tag） | 同上 | in-progress |
