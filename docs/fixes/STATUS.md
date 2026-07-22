# 修复与复现状态跟踪

**权威状态来源：** 本表 + `gh pr view <n> --json headRefOid,state`。
**不要**把历史快照 SHA 当成永久 head。重新执行前请用 gh 刷新。

## 文档 PR #2

| 字段 | 值 |
|------|-----|
| URL | https://github.com/professoryu06/omnigent-zh-cn/pull/2 |
| 分支 | `docs/fix-plans-core-secondary` |
| 生成时 head | 以 `gh pr view 2 --json headRefOid` 为准 |

## Issue 跟踪

| Issue | 优先级 | 证据标签 | 分支 | PR | 可复跑命令 / 结果 | 状态 |
|-------|--------|----------|------|-----|-------------------|------|
| #3016 | P0 候选 | **根因已证实** + 修复 PR | `fix/core-workspace-3016` | [#3](https://github.com/professoryu06/omnigent-zh-cn/pull/3) | `pytest tests/runner/test_session_workspace_cache.py` — pre fail / post pass（test-first commits） | fix-pr-open |
| #2853 | P0 候选 | **根因已证实**；**fail-loud 缓解已实现**；**prompt apply 未实现** | `fix/core-2853-native-prompt` | [#5](https://github.com/professoryu06/omnigent-zh-cn/pull/5) | `pytest tests/inner/test_native_system_prompt_delivery.py` — multi-native warn/strict + no log leak | **mitigated/fail-loud phase 1**（非完整 fixed） |
| #2747 | P1 | **根因已证实** + 修复 PR | `fix/core-spec-parse-2746-2747` | [#4](https://github.com/professoryu06/omnigent-zh-cn/pull/4) | `pytest tests/inner/test_loader_executor_nested.py` — hard `harness_kind` | fix-pr-open |
| #2746 | P1 | **根因已证实** + 修复 PR | 同上（独立 commit） | #4 | `pytest tests/runner/test_codex_native_model_from_spec.py` | fix-pr-open |
| #2854 | P1 | 仅上游报告 | — | — | — | planned |
| #2539 | P1 | 仅上游报告 | — | — | — | planned |
| #2967 | P1 长任务 | 仅上游报告 | — | — | — | planned |
| #3012 | 条件性 | 上游 draft PR #3013 | 不重复实现 | — | L0=诊断+人工 login，非脚本自动恢复 | track-upstream |
| #2575 | 条件 | 上游 PR #2833 open | 不 backport | — | — | track-upstream |
| Scale | Scale | 仅上游报告 | — | — | — | deferred |

### #2853 状态措辞（强制）

- **mitigated / fail-loud phase 1**
- warn/error 已实现；apply **未**实现
- native 角色 prompt **仍可能未送达**
- 不得标成完整 fixed / 不得关上游 issue

### 可审计证据

- 优先：各功能 PR 上的 **test-first commit** + 上表 pytest 命令
- 本地 `artifacts/repro/*` 仅辅助，**不是**唯一证明，且通常不入库

## 未声称已合并

所有功能 PR **open、未 merge**；**未打 Tag**；**未发版**。
