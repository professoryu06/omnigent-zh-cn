# CODEX_TASK_29 — Claude-DS 定向实施卡

## 1. 角色与目标

你是 Claude Code，CCSwitch 后端为 DeepSeek V4 Flash。你的任务是从固定干净基线逐 hunk 重建 Task 29 的四文件候选，运行定向检查并生成可审计交付。

本卡只授权定向实现，不授权完整 Gate 1、Gate 2、push 或 merge。最终报告必须标记为 `TARGETED_IMPLEMENTATION`，不得写 Gate PASS、全仓 GREEN 或 mergeable。

## 2. 固定输入

- 基线目录：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged`
- 基线 SHA：`8ef79ac348711d523053019cdb2f36e8cbbfef7e`
- 历史只读树：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-review`
- 独立实施 worktree：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds`
- Evidence 根：`/mnt/c/Users/Administrator/omnigent-diagnostics`

所有命令必须在 WSL 中使用上述 `/mnt/...` 路径。不得修改历史树。

## 3. 启动前必读

开始任何 Git 或实现操作前，完整读取：

1. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/AGENTS.md`
2. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/CONTRIBUTING.md`
3. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/CODEX_TASK_29_ORCHESTRATION.md`
4. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/MODEL_ROLE_MATRIX_20260806.md`
5. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/HERMES_DIAGNOSIS_GATE1_20260805-164315-5c8b9ce-hermes-gate1-r6.md`
6. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/GROK_FIX_RELAUNCH_RACE_20260806-103154-5c8b9ce-grok-relaunch-race-fix.md`

## 4. 创建独立 worktree

先定义并验证路径：

```bash
BASE_TREE="/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged"
HISTORY_TREE="/mnt/f/codex-ai/git项目部署/tmp/omnigent-review"
WORKTREE="/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds"
BASE_SHA="8ef79ac348711d523053019cdb2f36e8cbbfef7e"

test "$(git -C "$BASE_TREE" rev-parse HEAD)" = "$BASE_SHA"
test ! -e "$WORKTREE"
git -C "$BASE_TREE" worktree add -b task29/claude-ds "$WORKTREE" "$BASE_SHA"
test "$(git -C "$WORKTREE" rev-parse HEAD)" = "$BASE_SHA"
```

任一命令失败都必须停止并报告 `BLOCKED`。不得改写 `.git` 指针，不得改用非 WSL 路径，也不得复用已存在的未知 worktree。

## 5. 唯一允许修改的文件

1. `omnigent/inner/codex_executor.py`
2. `tests/inner/test_codex_executor.py`
3. `tests/inner/test_codex_runtime_isolation.py`
4. `tests/server/integration/test_session_host_launch.py`

禁止修改任何其他源码、测试、配置、Gate 文档或 evidence。若 `tests/inner/test_codex_runtime_isolation.py` 在基线不存在，只能按当前 main API 重建与本任务直接相关的最小隔离测试，禁止整体复制历史版本。

## 6. 实现边界

### 6.1 逐 hunk 重建

- 从基线文件出发，对历史树使用忽略行尾差异的只读比较。
- 人工审核每个语义 hunk，再在 Claude worktree 重建。
- 禁止 `cp`、整文件覆盖、整树复制或对历史脏树整体 `git add`。
- 最终 diff 不得包含 CRLF/LF 引起的整文件改写。
- 不得顺带迁移 PR #2/#5、旧 Gate 文档或其他历史功能。

### 6.2 Codex/OpenCodex 和代理隔离

- 清理 Codex 子进程环境中大小写两套 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`、`NO_PROXY`。
- Subscription 路径只能重建受控的子进程代理变量。
- Custom provider 和 gateway 路径不得继承 subscription 或宿主代理。
- WSL host IP 不得被合入子进程 `NO_PROXY`。
- Explicit `openai` provider pin 的行为必须与 subscription 路径一致。
- Codex subscription 必须使用私有 `CODEX_HOME`；不得读取或改写 OpenCodex `config.toml`。
- 不得修改 TUN、Clash、OpenCodex、10100、认证、全局代理或 240s watchdog。

### 6.3 Relaunch 测试同步

- 分别观察生产 relaunch 被触发、`host.launch_runner` frame 被接收并 ACK、`runner_id` 完成旋转。
- 使用短 poll 加有限 overall timeout。
- 禁止盲目 `sleep(N)`、无限 timeout 或失败后重试凑绿。
- 确保 post task、frame task、communicator 和 client 均被清理，task 异常被消费。
- 不得通过过度 monkeypatch 绕过被测 relaunch 主路径。
- 除批准的测试文件外，不得修改 `sessions.py` 或 `runner/app.py`。

## 7. 新 RUN_ID 与 evidence

在修改前创建全新目录：

```bash
RUN_ID="$(date -u +%Y%m%d-%H%M%S)-8ef79ac-claude-ds-targeted-r1"
EVIDENCE_ROOT="/mnt/c/Users/Administrator/omnigent-diagnostics/${RUN_ID}"
test ! -e "$EVIDENCE_ROOT"
mkdir -p "$EVIDENCE_ROOT"
```

若目录已存在，生成新的时间戳，禁止覆盖、拼接或复用旧 RUN_ID。

至少保存：

- `env.txt`
- `baseline-sha.txt`
- `status-before.txt`
- `semantic-diff.patch`
- `diff-stat.txt`
- `targeted-pytest.txt` 和 `targeted-pytest-exit.txt`
- `relaunch-stability.txt`
- `ruff.txt` 和 `ruff-exit.txt`
- `compileall.txt` 和 `compileall-exit.txt`
- `cleanup-leak-scan.txt`
- `implementation-report.md`

每条命令都记录命令文本、UTC 起止时间、stdout、stderr 和真实退出码。通过管道时必须分别保存被测命令与 `tee` 的退出码。

## 8. 定向验证

在 `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds` 中运行：

```bash
cd "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds"

uv run pytest tests/inner/test_codex_executor.py -k "model_provider or proxy" -q
uv run pytest tests/inner/test_codex_runtime_isolation.py -q
uv run pytest tests/server/integration/test_session_host_launch.py::test_host_session_message_relaunches_offline_runner -q

uv run ruff check \
  omnigent/inner/codex_executor.py \
  tests/inner/test_codex_executor.py \
  tests/inner/test_codex_runtime_isolation.py \
  tests/server/integration/test_session_host_launch.py

uv run python -m compileall -q \
  omnigent/inner/codex_executor.py \
  tests/inner/test_codex_executor.py \
  tests/inner/test_codex_runtime_isolation.py \
  tests/server/integration/test_session_host_launch.py
```

对 relaunch nodeid 做有限次数、逐轮记录的稳定性检查；固定轮数和每轮退出码必须写入 `relaunch-stability.txt`。这仍然只是定向测试，不是 Gate 1。

禁止运行全仓 pytest、完整 Gate 1、Gate 2 或真实 OpenCodex/10100 连通测试。

## 9. 范围检查与本地候选

验证变更范围只包含 4 个文件：

```bash
git -C "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds" status --short
git -C "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds" diff --check
git -C "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds" diff --stat
```

为向 Qwen 提供稳定输入，必须创建一个仅含这 4 个文件的本地 signed-off 候选提交。提交前按 `AGENTS.md` 对目标文件运行 pre-commit；如果 hook 改写了目标文件，重新运行本卡的定向验证并更新 evidence。禁止 push 或 merge。

```bash
cd "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds"

uv run pre-commit run --files \
  omnigent/inner/codex_executor.py \
  tests/inner/test_codex_executor.py \
  tests/inner/test_codex_runtime_isolation.py \
  tests/server/integration/test_session_host_launch.py

git add -- \
  omnigent/inner/codex_executor.py \
  tests/inner/test_codex_executor.py \
  tests/inner/test_codex_runtime_isolation.py \
  tests/server/integration/test_session_host_launch.py

git commit -s -m "fix(inner): isolate codex runtime proxy handling"
git rev-parse HEAD
```

生成交付：

```bash
git -C "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds" \
  diff "8ef79ac348711d523053019cdb2f36e8cbbfef7e..HEAD" -- \
  omnigent/inner/codex_executor.py \
  tests/inner/test_codex_executor.py \
  tests/inner/test_codex_runtime_isolation.py \
  tests/server/integration/test_session_host_launch.py
```

把上述 semantic diff 保存为 `semantic-diff.patch`，并记录完整候选 SHA。

## 10. 完成报告

`implementation-report.md` 标题必须是：

`# TARGETED_IMPLEMENTATION`

按以下顺序包含：

1. Completed tasks：逐文件说明重建内容和实际定向结果。
2. Handoff documents：候选 SHA、`semantic-diff.patch`、evidence 绝对 WSL 路径。
3. Next-agent prompt：明确交给 Qwen3.8，只能在独立验证 worktree应用候选并验证。
4. Watch-outs：失败、环境差异、未验证事项和残留风险。

结论不得出现 Gate 1 PASS、Gate 2 PASS、全仓 GREEN 或 mergeable。

## 11. 成功标准

- worktree 的起点是固定 SHA，且与其他角色隔离。
- 只修改批准的 4 个文件。
- 所有变更均逐 hunk 重建，无整文件行尾噪声。
- 定向 pytest、目标 Ruff、目标 compileall 和 cleanup 都有真实 evidence。
- 候选 SHA、semantic patch 和实施报告齐全。
- 未触碰历史树、旧 evidence、`nul`、TUN、Clash、OpenCodex、10100、认证或 240s watchdog。
- 未运行完整 Gate 1/Gate 2，未 push、未 merge。
