# 修复与复现状态跟踪

**权威状态来源：** 本表 + `gh pr view <n> --json headRefOid,state`。  
**不要**把历史快照 SHA 当成永久 head。

## 文档 PR #2

| 字段 | 值 |
|------|-----|
| URL | https://github.com/professoryu06/omnigent-zh-cn/pull/2 |
| 分支 | `docs/fix-plans-core-secondary` |
| 生成时 head（会过期） | 以 `gh pr view 2 --json headRefOid` 为准 |

## Issue 跟踪

| Issue | 优先级 | 证据标签 | 分支 | PR | 预修复 | 修复后 | 状态 |
|-------|--------|----------|------|-----|--------|--------|------|
| #3016 | P0 候选 | **已证实** | `fix/core-workspace-3016` | https://github.com/professoryu06/omnigent-zh-cn/pull/3 | 2 failed | 2 passed (+ snapshot regression) | fix-pr-open |
| #2853 | P0 候选 | **已证实**（静默 del；fail-loud 已 PR） | `fix/core-2853-native-prompt` | https://github.com/professoryu06/omnigent-zh-cn/pull/5 | 源码 `del system_prompt` 无日志；契约测试后通过 | 6 + 30 native 回归 passed | fix-pr-open |
| #2747 | P1 | **已证实** | `fix/core-spec-parse-2746-2747` | https://github.com/professoryu06/omnigent-zh-cn/pull/4 | nested → openai-agents | 7 passed | fix-pr-open |
| #2746 | P1 | **已证实** | 同上（独立 commit） | #4 | model→None | 同上 | fix-pr-open |
| #2854 | P1 | 仅上游报告 | — | — | — | — | planned |
| #2539 | P1 | 仅上游报告 | — | — | — | — | planned |
| #2967 | P1 长任务 | 仅上游报告 | — | — | — | — | planned |
| #3012 | 条件性 | 上游 draft PR #3013 | 不重复实现 | — | — | — | track-upstream |
| #2575 | 条件 | 上游 PR #2833 open | 不 backport | — | — | — | track-upstream |
| Scale #300x/#2702 | Scale | 仅上游报告 | — | — | — | — | deferred |

## 本地复现产物（不入库）

```
artifacts/repro/c-3016/pre-fix.txt
artifacts/repro/c-3016/post-fix.txt
artifacts/repro/c-2747-2746/pre-fix.txt
artifacts/repro/c-2747-2746/post-fix.txt
artifacts/repro/c-2853/post-fix.txt
```

## 未声称已合并

所有功能 PR **open、未 merge**；**未打 Tag**；**未发版**。
