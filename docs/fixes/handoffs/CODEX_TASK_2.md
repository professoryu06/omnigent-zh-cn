# CODEX TASK 2 — Grok 独立审查 #3016 workspace 投影缓存修复

**执行者：** Grok（独立代码审查者）

**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**阶段边界：** 仅阶段 2；审查阶段 1 的 #3016 候选，不修改任何源码或测试

**阶段 1 验收状态：** Codex 已核对 Hermes 报告、当前 diff 与定向 GREEN；此结论仅允许进入独立审查，不代表准许合并，也不代表 Gate 1/2 通过

## 1. 必读材料

按顺序完整阅读：

1. `docs/fixes/handoffs/CODEX_TASK_1.md`
2. `docs/fixes/handoffs/HERMES_COMPLETION_1.md`
3. `docs/fixes/STATUS.md`
4. `docs/fixes/PRE_MERGE_GATES.md`
5. 当前 `omnigent/runner/app.py` diff
6. `tests/runner/test_session_workspace_cache.py`

语义参照：

- PR #3 分支：`fix/core-workspace-3016`
- PR #3 审查基准 HEAD：`744e3a04a9b041b7bf3c2ae25cd22f96f5945038`
- PR #3 test-first 提交：`6fd9ef440ac9aadbb965904d6378f7072243d230`
- 当前工作树基线 HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`

## 2. 审查目标

独立判断阶段 1 候选是否满足以下契约：

1. 瞬时失败 snapshot 的 `workspace=None` 不得进入 `_session_workspace_cache`，后续访问仍会重新获取。
2. `_session_start_cache` 已建立但 workspace 尚未成功解析时，`_ensure_session_registered()` 不得永久短路 workspace 补取。
3. 成功 snapshot 的 `workspace=None` 仍可缓存，保持“成功但无显式 workspace”的原语义。
4. agent-cache reset 同时清理 `_session_workspace_cache` 和 `_session_fs_registries`，使新的 session worktree 生效。
5. 改动保持最小，只触及指定三个函数和两个精确回归测试，不引入跨阶段逻辑或新依赖。

## 3. 必做只读核对

### 3.1 范围、HEAD 与禁止操作证据

```powershell
git status --short --branch
git rev-parse HEAD
git rev-parse origin/docs/fix-plans-core-secondary
git diff --name-status
git ls-files --others --exclude-standard
git reflog -10 --date=iso
```

期望：

- HEAD 与远端跟踪分支仍为 `dc83140c73ceb12fa165753c1880c19f68da86f4`。
- 阶段 1 新增源码范围只有 `omnigent/runner/app.py` 和 `tests/runner/test_session_workspace_cache.py`。
- r05 的三个既有文档 diff 仍在，不能把它们归为阶段 1 改动。
- 没有阶段 1 产生的 checkout、commit、merge 或 tag 记录。

可只读刷新远端状态：

```powershell
gh pr view 2 --repo professoryu06/omnigent-zh-cn --json number,state,headRefName,headRefOid,mergedAt
gh pr view 3 --repo professoryu06/omnigent-zh-cn --json number,state,headRefName,headRefOid,mergedAt
git ls-remote --tags origin
```

远端核对仅用于确认未 push/merge/tag；不得编辑 PR/Issue。

### 3.2 RED 证据真实性

不要通过回退、覆盖或临时修改当前源码来重演 RED。审计既有 test-first 链条：

```powershell
git rev-parse 6fd9ef440ac9aadbb965904d6378f7072243d230:tests/runner/test_session_workspace_cache.py
git hash-object tests/runner/test_session_workspace_cache.py
git show 6fd9ef440ac9aadbb965904d6378f7072243d230^:omnigent/runner/app.py | Select-String -Pattern 'async def _session_workspace_value|async def _ensure_session_registered|def _clear_session_agent_caches' -Context 0,35
```

必须确认：

- 两个测试文件 blob 完全相同；预期 blob 为 `02cce3ca6e28233d5d0cac350a7be6316ff582d2`。
- test-first 父基线确有三处根因：失败 workspace 被缓存、start cache 直接短路、reset 未清 workspace/fs registry。
- `HERMES_COMPLETION_1.md` 同时记录两个单测的命令、失败结果和以下根因断言：
  - `Missing agent_change.py means workspace cache stayed poisoned`
  - `Missing only_b.py means workspace and/or per-session fs registry projection survived reset`
- 如果认为 RED 证据不足，必须给出具体缺口；不得自行修改源码补证据。

### 3.3 实现 diff 审查

```powershell
git diff --stat -- omnigent/runner/app.py
git diff --no-ext-diff --unified=30 -- omnigent/runner/app.py
git diff --no-ext-diff --unified=20 origin/fix/core-workspace-3016 -- omnigent/runner/app.py
```

逐项检查：

- `_session_workspace_value()` 只在 `snapshot.ok` 时缓存；失败返回 `None` 但保持未来重试。
- `_ensure_session_registered()` 只有 start 和 workspace 投影都存在时才短路；created_at 不被后续 retry 覆盖。
- `_clear_session_agent_caches()` 同时 pop workspace cache 与 per-session filesystem registry。
- 当前 +11/−4 的写法与 PR #3 行为等价；与 PR #3 的差异只能是更少注释或等价控制流，不能改变缓存契约。
- 无 sleep、retry loop、异常吞噬、断言弱化、强制 worktree、公开接口变化或跨阶段改动。

### 3.4 独立 GREEN、Ruff 与空白检查

在 PowerShell 中使用进程内环境变量，避免 hermes-agent 的 `PYTHONPATH` 污染：

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/runner/test_session_workspace_cache.py
uv run pytest -q tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries
uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries
uv run ruff check omnigent/runner/app.py tests/runner/test_session_workspace_cache.py
git diff --check
```

审查报告必须逐条记录实际结果与退出状态。这里的 GREEN 只是 Windows 定向证据，绝不能写成 Linux Gate 1 或 AgentCenter Gate 2。

### 3.5 r05 文档保护核对

```powershell
Get-Item docs/fixes/STATUS.md,docs/fixes/PRE_MERGE_GATES.md,docs/fixes/POST_FIX_HANDOFF_PROMPT.md | Select-Object FullName,LastWriteTime
git diff --check -- docs/fixes/STATUS.md docs/fixes/PRE_MERGE_GATES.md docs/fixes/POST_FIX_HANDOFF_PROMPT.md
rg -n "fixrun-20260724-target-v0\.6\.0-zhcn\.2-r05|pipeline_status|PYTEST_EXIT|TEE_EXIT|INVALID|baseline-fail-ids\.txt|integrate-fail-ids\.txt|new-failures\.txt|未执行" docs/fixes/STATUS.md docs/fixes/PRE_MERGE_GATES.md docs/fixes/POST_FIX_HANDOFF_PROMPT.md
```

期望三个文件的 LastWriteTime 仍为 2026-07-24，且 r05 真实性标记与 Gate 1/2“未执行”措辞仍存在。不得整理或修改这些文档。

## 4. 审查结论规则

结论只能是：

- `approve`：阶段 1 的实现与证据可接受，可以进入阶段 3 策划；但 Gate 1/2 仍未执行，不批准 merge。
- `request-changes`：存在 P0/P1，或 RED/GREEN 证据无法支撑根因。列出退回 Hermes 的精确文件、函数、测试或报告缺口；Grok 不得自行修复。

问题按以下级别记录：

- P0：安全/数据隔离错误、明显使用错误 workspace、证据伪造或范围失控。
- P1：缓存契约仍不正确、回归测试不覆盖根因、定向验证失败、跨阶段改动。
- P2：不阻塞本阶段的可维护性或报告精度问题；必须说明是否建议后续处理。

没有发现某级问题时明确写“无”。不得用 `approve` 表示“可合并”。

## 5. 唯一允许写入的文件

只允许创建：

`docs/fixes/handoffs/GROK_REVIEW_2.md`

必须包含：

1. 结论：`approve` 或 `request-changes`
2. 审查基线：HEAD、PR #3 参照 HEAD、实际文件范围
3. RED 证据审计结果
4. 实现语义检查结果
5. 独立 GREEN/Ruff/`git diff --check` 命令、退出状态与结果
6. P0/P1/P2 分级发现
7. 必须修改项（无则写“无”）
8. 剩余风险
9. Gate 1/2 明确为“未由本阶段执行或判定”
10. 最终 `git status --short --branch`

## 6. 禁止项

- 不得修改 `omnigent/`、`tests/`、r05 文档、Hermes 报告或既有任务卡。
- 不得 checkout/switch/rebase/cherry-pick、stash、reset、clean、暂存文件或回退源码重演 RED。
- 不得 commit、push、merge、创建/移动 Tag、发版或编辑 PR/Issue。
- 不得修复审查中发现的问题；只记录结论并退回 Hermes。
- 不得开始阶段 3 的上游 #3175/#3178/#3060 回移。
- 不得声称 PR #3 可合并、Issue #3016 已关闭、Gate 1/2 已执行或通过。

## 7. 完成标准

阶段 2 仅在以下全部满足时完成：

1. 所有必做只读核对与定向命令均有实际结果。
2. 审查覆盖 RED 链条、三个函数、两个测试、文件范围、r05 保护和禁止操作证据。
3. `GROK_REVIEW_2.md` 给出明确结论、P0/P1/P2、必须修改项和剩余风险。
4. 除 `GROK_REVIEW_2.md` 外没有新增或修改任何文件。
5. 报告没有把定向 GREEN 写成 Gate 1/2，也没有批准 merge/push/tag。

Grok 交付后，Codex 只记录其审查结论：`approve` 才进入阶段 3 任务卡；`request-changes` 则只生成返工要求交给 Hermes。
