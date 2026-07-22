# 修复与复现状态跟踪

**权威状态来源：** 本表 + `gh pr view <n> --json headRefOid,state`。  
**不要**把历史快照 SHA 当成永久 head。重新执行前请用 gh 刷新。

## 文档 PR #2

| 字段 | 值 |
|------|-----|
| URL | https://github.com/professoryu06/omnigent-zh-cn/pull/2 |
| 分支 | `docs/fix-plans-core-secondary` |
| 生成时 head | 以 `gh pr view 2 --json headRefOid` 为准 |

## 合并前门槛（#3/#4/#5 合入 main 前）

规格全文：[PRE_MERGE_GATES.md](./PRE_MERGE_GATES.md)

| 门槛 | 状态（时间快照） | 判定说明 |
|------|------------------|----------|
| Gate 1 Linux 全仓 pytest | **未执行 / 未达标** | 需 Ubuntu+py3.12+`uv sync --locked --extra dev`；优先绝对全绿，否则与 clean main 对比无**新增**失败。Windows 定向 67 **≠** 本门槛 |
| Gate 2 AgentCenter C/E/R smoke | **未执行 / 未达标** | 需三角色配置与日志证据（隔离/harness/model/warn/strict）。**未伪造** |
| 定向 67 + 目标 Ruff | **曾通过**（临时集成） | 3+7+57 passed；Ruff clean — **必要不充分** |

**当前是否达到合并门槛：否。**

证据目录约定：`artifacts/pre-merge/<run-id>/`（gitignore，不入库）。

---

## Issue 跟踪

| Issue | 优先级 | 证据标签 | 分支 | PR | 可复跑命令 / 结果 | 状态 |
|-------|--------|----------|------|-----|-------------------|------|
| #3016 | P0 候选 | **根因已证实** + 修复 PR **open 未 merge** | `fix/core-workspace-3016` | [#3](https://github.com/professoryu06/omnigent-zh-cn/pull/3) | `pytest tests/runner/test_session_workspace_cache.py` | fix-pr-open |
| #2853 | P0 候选 | **根因已证实**；**mitigated/fail-loud Phase1**；**prompt apply / 真实送达未实现**；AgentCenter E2E **未验证** | `fix/core-2853-native-prompt` | [#5](https://github.com/professoryu06/omnigent-zh-cn/pull/5) | `pytest tests/inner/test_native_system_prompt_delivery.py` | **mitigated/fail-loud phase 1**（非完整 fixed） |
| #2747 | P1 | **根因已证实** + 修复 PR **open 未 merge** | `fix/core-spec-parse-2746-2747` | [#4](https://github.com/professoryu06/omnigent-zh-cn/pull/4) | `pytest tests/inner/test_loader_executor_nested.py` | fix-pr-open |
| #2746 | P1 | **根因已证实** + 修复 PR **open 未 merge** | 同上 | #4 | `pytest tests/runner/test_codex_native_model_from_spec.py` | fix-pr-open |
| #2854 | P1 | 仅上游报告 | — | — | — | planned |
| #2539 | P1 | 仅上游报告 | — | — | — | planned |
| #2967 | P1 长任务 | 仅上游报告 | — | — | — | planned |
| #3012 | 条件性 | 上游 draft PR #3013（状态须重查） | 不重复实现 | — | L0=诊断+人工 login | track-upstream |
| #2575 | 条件 | 上游 #2833 open/未 merge/不默认落地（须重查） | 不 backport | — | — | track-upstream |
| Scale | Scale | 仅上游报告 | — | — | — | deferred |

### #2853 状态措辞（强制）

- **mitigated / fail-loud phase 1**
- Phase1 **单元级** fail-loud 实现完成（warn / `OMNIGENT_STRICT_PROMPT`）
- **真实 prompt 送达未实现**；**不得**写 prompt 已送达
- AgentCenter / 真实 native E2E：**未验证**（除非 Gate 2 PASS 并附证据）
- 不得标成完整 fixed / 不得关上游 issue

### 可审计证据

- 优先：各功能 PR 的 **test-first commit** + 上表 pytest
- 门槛证据：`artifacts/pre-merge/<run-id>/` + 本表门槛行
- 本地 `artifacts/*` 默认不入库

## 未声称已合并

所有功能 PR **open、未 merge**；**本轮未创建新 Tag、未发版**（仓库已有 `v0.6.0-zhcn.1`）。

> **Tag 事实：** `v0.6.0-zhcn.1` 已存在于 origin（2026-07-19，早于本轮）。本轮仅未创建**新** Tag。
