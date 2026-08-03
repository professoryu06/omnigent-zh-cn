# CODEX TASK 1 — 完成 #3016 workspace 投影缓存修复

**执行者：** Hermes（Qwen3.8，唯一开发者）

**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**阶段边界：** 仅阶段 1（#3016）；不得开始阶段 2 审查或阶段 3 上游回移

**语义基准：** PR #3 `fix/core-workspace-3016`，策划时实时 HEAD 为 `744e3a04a9b041b7bf3c2ae25cd22f96f5945038`；test-first 提交为 `6fd9ef440ac9aadbb965904d6378f7072243d230`

## 1. 当前事实与问题

- 当前工作树位于 `docs/fix-plans-core-secondary`，源码仍是未包含 PR #3 的基线；工作树已有 r05 文档改动和 `docs/fixes/handoffs/` 未跟踪文件。它们属于前置状态，必须原样保留。
- 上游 Issue #3016 仍为 OPEN；本阶段不得假定上游已经修复。
- `_session_snapshot()` 不缓存失败或不完整的 snapshot，但它的 workspace 投影层破坏了这一重试语义：
  - `_session_workspace_value()` 会把失败 snapshot 的 `workspace=None` 写入 `_session_workspace_cache`；
  - `_ensure_session_registered()` 也会无条件写入该投影，并因 `_session_start_cache` 已存在而阻止后续补取 workspace；
  - `_clear_session_agent_caches()` 不清理 workspace 投影和按 session 创建的 filesystem registry。
- 后果：一次瞬时非 200 响应可把 session 永久钉到 runner 全局 workspace；agent-cache reset 也无法让新的 worktree 路径生效。

目标是保留 PR #3 的既有语义，不扩大或重新设计缓存体系。

## 2. 精确文件范围

仅允许改动/创建以下文件：

1. 修改 `omnigent/runner/app.py`
   - `_session_workspace_value()`（当前约第 8605 行）
   - `_ensure_session_registered()`（当前约第 17328 行）
   - `_clear_session_agent_caches()`（当前约第 17935 行）
2. 创建 `tests/runner/test_session_workspace_cache.py`
3. 完成后创建 `docs/fixes/handoffs/HERMES_COMPLETION_1.md`

不得改动 `docs/fixes/STATUS.md`、`docs/fixes/PRE_MERGE_GATES.md`、`docs/fixes/POST_FIX_HANDOFF_PROMPT.md` 或其他既有 handoff；这些文件当前已有未提交内容。

## 3. RED：先写并确认失败测试

测试语义必须与 PR #3 的 test-first 提交 `6fd9ef4` 一致；可用以下只读命令核对其完整测试文件：

```powershell
git show 6fd9ef440ac9aadbb965904d6378f7072243d230:tests/runner/test_session_workspace_cache.py
```

在修改 `omnigent/runner/app.py` 之前创建测试文件，并包含这两个精确测试：

### 3.1 `test_failed_snapshot_does_not_poison_workspace_cache`

- 创建 runner 全局 repo 和独立 session worktree；只有 session worktree 含 `agent_change.py`。
- mock `GET /v1/sessions/{id}`：第一次返回 503，之后返回 200 和 session worktree 路径。
- 连续两次读取 session filesystem `/changes`。
- 第二次必须能看到 `agent_change.py`，证明失败 snapshot 没有把 `None` 永久缓存。

基线预期：**FAIL**，断言信息包含 `Missing agent_change.py means workspace cache stayed poisoned`；失败输出应表明仍使用全局 workspace。若该测试在未改源码时通过，停止实施并在报告中说明基线已变化，不得为了制造 RED 而削弱断言。

### 3.2 `test_reset_agent_cache_evicts_workspace_projection`

- 初次由 server 返回 workspace A，并确认 `/changes` 能看到 `only_a.py`。
- 将 server 返回值切到 workspace B，调用 `POST /v1/sessions/{id}/agent-cache/reset`，再读 `/changes`。
- reset 后必须看到 `only_b.py`，证明 workspace 投影和 per-session filesystem registry 都已清除并重建。

基线预期：**FAIL**，断言信息包含 `Missing only_b.py means workspace and/or per-session fs registry projection survived reset`。若未改源码时通过，同样停止并报告。

逐个执行并保存 RED 的命令、退出码和关键断言：

```powershell
uv run pytest -q tests/runner/test_session_workspace_cache.py::test_failed_snapshot_does_not_poison_workspace_cache
uv run pytest -q tests/runner/test_session_workspace_cache.py::test_reset_agent_cache_evicts_workspace_projection
```

只有两个测试均真实覆盖各自根因并在旧实现上失败后，才能修改实现。

## 4. 最小改法

严格保持 PR #3 `744e3a0` 的行为边界：

1. `_session_workspace_value()`
   - 调用 `_session_snapshot()` 后，仅当 `snapshot.ok` 为真时写 `_session_workspace_cache`。
   - snapshot 失败时直接返回 `None`，但不得把该 `None` 缓存；后续调用必须仍可重新获取。
   - 成功 snapshot 的 `workspace=None` 仍可作为“成功解析但没有显式 workspace”缓存，保持原有成功响应语义。
2. `_ensure_session_registered()`
   - 首次调用仍可记录 `snapshot.created_at`，但只有 `snapshot.ok` 时才投影 workspace。
   - 若 `_session_start_cache` 已有值而 `_session_workspace_cache` 没有值，不得直接永久短路；重新取 snapshot，并仅在成功时填入 workspace。
   - 不改变 agent/spec 解析、start time fallback 或其他 session 注册行为。
3. `_clear_session_agent_caches()`
   - 除既有 spec/tool/snapshot 缓存外，同时移除该 session 的 `_session_workspace_cache` 与 `_session_fs_registries` 条目。
   - 不扩展到其他缓存或生命周期重构。

禁止通过 sleep、额外 retry loop、吞异常、放宽测试断言或强制使用 session worktree 来让测试变绿。

## 5. GREEN 与定向回归命令

实现后按顺序执行：

```powershell
uv run pytest -q tests/runner/test_session_workspace_cache.py
uv run pytest -q tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries
uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries
uv run ruff check omnigent/runner/app.py tests/runner/test_session_workspace_cache.py
git diff --check
```

最后只读报告范围：

```powershell
git status --short --branch
git diff --stat -- omnigent/runner/app.py tests/runner/test_session_workspace_cache.py docs/fixes/handoffs/HERMES_COMPLETION_1.md
git diff -- omnigent/runner/app.py tests/runner/test_session_workspace_cache.py
```

这些是阶段 1 的定向证据，不是 Linux Gate 1 或 AgentCenter Gate 2。

## 6. 禁止项

- 不得 checkout/switch/rebase/cherry-pick；不得清理、覆盖或暂存当前 r05 文档改动。
- 不得修改上述三个允许文件以外的任何文件；依赖锁、配置、CI、文档状态表均不动。
- 不得顺手修复 #2746/#2747、回移 #3175/#3178/#3060、实施 #2853 或处理 #2539/#2854/#2967。
- 不得重构 `create_runner_app()`、重命名缓存、改变公开接口或引入新依赖。
- 不得修改密钥、账号、模型凭据或真实 AgentCenter 配置。
- 不得 commit、push、merge、创建/移动 Tag、发版或编辑 PR/Issue。
- 不得声称 PR #3 可合并、Issue 已关闭、Gate 1/2 已执行或已通过。

## 7. 完成标准

仅当以下全部满足，Hermes 才可报告阶段 1 完成：

1. 报告两个新增测试在实现前的真实 RED：命令、非零退出码、关键失败断言齐全。
2. 源码只改动 `omnigent/runner/app.py` 的三个指定函数；测试只新增 `tests/runner/test_session_workspace_cache.py`，语义与 PR #3 一致。
3. 两个新增测试 GREEN，既有 `test_failed_session_snapshot_is_not_cached_and_retries` GREEN，组合定向命令 GREEN。
4. 目标 Ruff 通过，`git diff --check` 通过。
5. 当前 r05 文档改动保持原样；没有额外源码、配置或依赖文件变化。
6. `docs/fixes/handoffs/HERMES_COMPLETION_1.md` 明确记录：根因、精确文件、RED/GREEN 命令与结果、关键 diff、风险、未完成项、最终 `git status`。
7. 报告明确写明：Gate 1 / Gate 2 **未由本阶段执行或判定**；无 commit/push/merge/tag。

Hermes 交付后，Codex 只验收 `HERMES_COMPLETION_1.md` 及其报告证据；通过后才交给 Grok 做阶段 2 独立审查。
