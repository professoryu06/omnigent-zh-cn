# QWEN TASK r04 — fix PR #2 pre-merge gate runbook

Working directory: this repo
Branch: docs/fix-plans-core-secondary
HEAD start: dc83140c73ceb12fa165753c1880c19f68da86f4
Run id: fixrun-20260724-target-v0.6.0-zhcn.2-r04
Target version: target-v0.6.0-zhcn.2

## ONLY CORE
Fix PRE_MERGE_GATES.md Gate1 exit-code capture and absolute evidence directory.
Do not merge/tag/push. Do not edit PR #3/#4/#5 feature code. Do not implement #2853 Phase2.

## EDIT THESE FILES
1. docs/fixes/PRE_MERGE_GATES.md  (required)
2. docs/fixes/STATUS.md  (required)
3. docs/fixes/POST_FIX_HANDOFF_PROMPT.md  (required)
4. docs/fixes/handoffs/HANDOFF_20260724_r04.md  (create)

## PRE_MERGE_GATES.md REQUIRED CHANGES
A) Every Gate 1 pytest|tee block currently like:
```
uv run pytest -q ... 2>&1 | tee artifacts/pre-merge/$RUN_ID/baseline-pytest.txt
echo EXIT:$? | tee -a ...
```
MUST become:
```
set -o pipefail
uv run pytest -q ... 2>&1 | tee "$EVIDENCE_ROOT/baseline-pytest.txt"
pytest_status=${PIPESTATUS[0]}
echo "EXIT:$pytest_status" | tee -a "$EVIDENCE_ROOT/baseline-pytest.txt"
# EXIT must be pytest status, never tee
```
Apply same pattern to integrate-pytest and any similar pytest|tee blocks.

B) Introduce absolute EVIDENCE_ROOT shared by both worktrees:
```
export RUN_ID=YYYYMMDD-HHMM-<shortsha>
export EVIDENCE_ROOT=/tmp/omnigent-premerge-evidence/$RUN_ID
mkdir -p "$EVIDENCE_ROOT/agentcenter"
```
All baseline/integrate/targeted/ruff/agentcenter outputs write under $EVIDENCE_ROOT.
Update Gate 0.4 tree listing accordingly.
Do not rely on relative artifacts/ after cd into another worktree.

C) Keep Gate1/Gate2 status honest: still 未执行 until actually run.

## STATUS.md / POST_FIX_HANDOFF_PROMPT.md
- Record run id fixrun-20260724-target-v0.6.0-zhcn.2-r04
- Note: gate script P1 fixed; Gate1/Gate2 still not executed
- Do NOT claim merge/tag/pass

## HANDOFF_20260724_r04.md must include
- 本轮核心
- 改动文件
- 关键 diff 摘要
- 验证方式
- Git 上传时机：Codex 审查通过后 push PR#2；禁止 merge/tag
- 下一步 r05：真实跑 Gate1/Gate2
- 整体 TodoList 进度

## DONE WHEN
1. No bare `echo EXIT:$?` after pytest|tee
2. EVIDENCE_ROOT absolute path used consistently
3. handoff exists
4. print git status and git diff --stat
5. DO NOT commit or push
