# QWEN TASK r05 — PRE_MERGE evidence authenticity

Working directory: this repo only
Branch: docs/fix-plans-core-secondary
Run id: fixrun-20260724-target-v0.6.0-zhcn.2-r05

## Constraints
- Only modify PR #2 documentation worktree files under docs/fixes/
- DO NOT commit
- DO NOT push
- DO NOT merge
- DO NOT create Tag
- DO NOT edit PR #3/#4/#5 feature code
- DO NOT claim Gate1/Gate2 executed/PASS
- DO NOT claim #2853 prompt delivered

## Goal
Fix remaining evidence-authenticity issues in PRE_MERGE_GATES.md.

### 1) baseline/integrate pytest pipeline
For each baseline/integrate pytest pipeline block:
- Explicitly `set +e`
- Then `set -o pipefail`
- After pipeline, immediately save full array:
  ```bash
  pipeline_status=("${PIPESTATUS[@]}")
  pytest_status=${pipeline_status[0]}
  tee_status=${pipeline_status[1]}
  ```
- Write both PYTEST_EXIT and TEE_EXIT into evidence files
- pytest non-zero may continue for baseline/integrate comparison
- tee non-zero, missing JUnit, or unwritable evidence dir MUST mark `INVALID` and must NOT PASS
- After capture, restore previous errexit state, or explicitly restore `set -e`

### 2) Unify and actually generate evidence files
Always create/use:
- commits.txt (main, PR3, PR4, PR5, integrate tip)
- baseline-fail-ids.txt
- integrate-fail-ids.txt
- new-failure comparison result

Do NOT mix `*-failures.txt` with `*-fail-ids.txt`.

### 3) Update docs
Update:
- docs/fixes/STATUS.md
- docs/fixes/POST_FIX_HANDOFF_PROMPT.md
- create docs/fixes/handoffs/HANDOFF_20260724_r05.md

Wording rules:
- r04 only claims fixing the original two defects
- r05 completes evidence-write / INVALID semantics
- Gate1/Gate2 remain 未执行
- #2853 remains Phase1 fail-loud only; forbid “prompt 已送达”

## Done when
1. PRE_MERGE_GATES has pipeline_status array capture + PYTEST_EXIT/TEE_EXIT + INVALID rules
2. commits.txt / baseline-fail-ids.txt / integrate-fail-ids.txt naming is consistent
3. STATUS / POST_FIX / HANDOFF_r05 updated with correct r04/r05 semantics
4. print:
   - git status
   - git diff --check
   - key diff summary
   - unfinished gates
5. no commit / push
