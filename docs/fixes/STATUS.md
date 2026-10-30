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
| Gate 2 AgentCenter C/E/R smoke | **PASS**（2026-08-03，RUN `20260803-232354-gate2-sixrounds-r5`） | 六轮 C/E-pos/E-pos-strict/E-neg-warn/E-neg-strict/R 全部执行，AC-1~AC-6 全部满足；证据：`docs/fixes/handoffs/GATE2_REVIEW_20260803-232354-gate2-sixrounds-r5.md` + `C:\Users\Administrator\omnigent-diagnostics\20260803-232354-gate2-sixrounds-r5\`。**边界：仅 codex-native Phase 2 apply 实证送达；claude-native 保持 warn；不等同全仓 GREEN 或可 merge；merge 决定权 Codex** |
| 定向 67 + 目标 Ruff | **曾通过**（临时集成） | 3+7+57 passed；Ruff clean — **必要不充分** |

**当前是否达到合并门槛：否。**

## Gate 2 基线冻结（2026-08-03）

- **冻结 HEAD**：`c3c4ebad074ddce6b458c77dfe06e1ab76498e84`（分支 `docs/fix-plans-core-secondary`）
- **冻结 manifest**：[BASELINE_FREEZE_20260803.md](./BASELINE_FREEZE_20260803.md)
- Commit 1（A 类修复 44 文件）：`e691d08cbfca5e1a36656ced8a0f317b495ffbbe`
- Commit 2（C 类文档 124 文件）：`c3c4ebad074ddce6b458c77dfe06e1ab76498e84`
- 排除：`nul`（D 类清理卡）、`evidence/`（B 类 grok 卡）
- **Gate 2 基线已冻结，等待 Codex 验收；基线冻结不改变"未达合并门槛"判定**

### Gate 2 验收记录（2026-08-03）

- **RUN_ID**：`20260803-232354-gate2-sixrounds-r5`（最终验收轮；前置作废轮 r1/r2/r3/r4 见各自证据目录）
- **结论**：**GATE2_PASS**（六轮 C/E-pos/E-pos-strict/E-neg-warn/E-neg-strict/R，AC-1~AC-6 全部满足）
- **证据路径**：`C:\Users\Administrator\omnigent-diagnostics\20260803-232354-gate2-sixrounds-r5\`（runner 日志 ×6、receipt ×2、agent YAML ×6、验证链 ALL PASS）
- **验收报告**：`docs/fixes/handoffs/GATE2_REVIEW_20260803-232354-gate2-sixrounds-r5.md`
- **执行载体**：独立基线 stack（server 6868 + host×2 + runner，全部 `omnigent-review-gate2` @ `5c8b9ce` venv）；现网 6767/omnigent-zh-next 未触碰
- **GATE2_PASS 边界**：仅 codex-native Phase 2 apply 实证送达（receipt 机制）；claude-native 为 warn-only 未声称送达；Gate 2 PASS 不等同全仓 GREEN 或可 merge；merge 决定权专属 Codex

证据目录约定：`$EVIDENCE_ROOT`（即 `/tmp/omnigent-premerge-evidence/<run-id>/`，绝对路径，gitignore，不入库）。

**最近文档修复轮次：** `fixrun-20260724-target-v0.6.0-zhcn.2-r05`
- r04：修复 Gate 脚本 P1 缺陷（`echo EXIT:$?` → `PIPESTATUS[0]`；相对 `artifacts/` → 绝对 `$EVIDENCE_ROOT`）
- r05：补全证据真实性 — pipeline `set +e` + `PIPESTATUS` 数组捕获 + `PYTEST_EXIT`/`TEE_EXIT` 双写 + INVALID 语义 + 统一 `*-fail-ids.txt` 命名 + `commits.txt` / `new-failures.txt` 生成步骤
- Gate 1 / Gate 2 **仍未实际执行**（需 Linux 环境实跑）
- 未 push；未 merge；未创建新 Tag；未声称 Gate PASS


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
- 门槛证据：`$EVIDENCE_ROOT` + 本表门槛行
- 本地 `artifacts/*` 默认不入库

## 未声称已合并

所有功能 PR **open、未 merge**；**本轮未创建新 Tag、未发版**（仓库已有 `v0.6.0-zhcn.1`）。

> **Tag 事实：** `v0.6.0-zhcn.1` 已存在于 origin（2026-07-19，早于本轮）。本轮仅未创建**新** Tag。
