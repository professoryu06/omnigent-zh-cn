# CODEX_TASK_29 — Grok 独立审查卡

## 1. 角色与启动条件

你是 Grok，负责 Task 29 的独立高风险审查。默认权限是只读审查，不是修复。

只有以下交付全部齐全后才能启动：

### Claude-DS

- 完整候选 SHA；
- `semantic-diff.patch`；
- `implementation-report.md`；
- TARGETED_IMPLEMENTATION evidence 根。

### Qwen3.8

- `validation-report.md`；
- `cli-matrix.tsv`；
- 定向 pytest、Ruff、compileall evidence；
- ports、timeline、cleanup、credential leak-scan；
- TARGETED_VALIDATION evidence 根。

缺少关键输入时输出 `INCONCLUSIVE`，列出缺失的绝对 WSL 路径并停止。不得替 Claude 或 Qwen 补造证据。

## 2. 固定路径

- 基线：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged`
- 基线 SHA：`8ef79ac348711d523053019cdb2f36e8cbbfef7e`
- 历史只读树：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-review`
- Claude worktree，只读：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds`
- Qwen worktree，只读：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-qwen-verify`
- 独立 Grok 审查 worktree：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review`
- Evidence 根：`/mnt/c/Users/Administrator/omnigent-diagnostics`

所有命令必须使用 WSL `/mnt/...` 路径。不得直接修改 Claude、Qwen、基线或历史 worktree。

## 3. 启动前必读

完整读取：

1. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/AGENTS.md`
2. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/CONTRIBUTING.md`
3. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/CODEX_TASK_29_ORCHESTRATION.md`
4. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/MODEL_ROLE_MATRIX_20260806.md`
5. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/HERMES_DIAGNOSIS_GATE1_20260805-164315-5c8b9ce-hermes-gate1-r6.md`
6. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/GROK_FIX_RELAUNCH_RACE_20260806-103154-5c8b9ce-grok-relaunch-race-fix.md`
7. Claude 的完整交付；
8. Qwen 的完整交付和 evidence manifest。

## 4. 创建独立只读审查 worktree

从 Claude 报告取得 `CLAUDE_CANDIDATE_SHA`：

```bash
BASE_TREE="/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged"
WORKTREE="/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review"
BASE_SHA="8ef79ac348711d523053019cdb2f36e8cbbfef7e"
CLAUDE_SHA="${CLAUDE_CANDIDATE_SHA:?set from Claude implementation-report.md}"

test "$(git -C "$BASE_TREE" rev-parse HEAD)" = "$BASE_SHA"
test ! -e "$WORKTREE"
git -C "$BASE_TREE" cat-file -e "${CLAUDE_SHA}^{commit}"
git -C "$BASE_TREE" worktree add --detach "$WORKTREE" "$CLAUDE_SHA"
test "$(git -C "$WORKTREE" rev-parse HEAD)" = "$CLAUDE_SHA"
```

任一步失败都必须停止并输出 INCONCLUSIVE。不得修改 `.git` 指针或复用 Claude/Qwen worktree。

## 5. 新 RUN_ID 与审查 evidence

```bash
CANDIDATE_SHORT="$(git -C "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review" rev-parse --short=7 HEAD)"
RUN_ID="$(date -u +%Y%m%d-%H%M%S)-${CANDIDATE_SHORT}-grok-independent-review-r1"
EVIDENCE_ROOT="/mnt/c/Users/Administrator/omnigent-diagnostics/${RUN_ID}"
test ! -e "$EVIDENCE_ROOT"
mkdir -p "$EVIDENCE_ROOT"
```

若目录已存在，生成新的时间戳。不得覆盖、拼接或复用 Claude、Qwen、历史 Gate 或旧 Grok RUN_ID。

至少保存：

- `input-manifest.txt`
- `reviewed-shas.txt`
- `diff-scope.txt`
- `candidate-diff.patch`
- `race-review.md`
- `proxy-isolation-review.md`
- `codex-opencodex-review.md`
- `windows-wsl-boundary-review.md`
- `qwen-evidence-audit.md`
- `findings.md`
- `final-verdict.txt`
- `review-report.md`

## 6. 审查项目

### 6.1 Diff 边界

- 比较 `8ef79ac348711d523053019cdb2f36e8cbbfef7e..CLAUDE_SHA`。
- 变更只能包含：
  - `omnigent/inner/codex_executor.py`
  - `tests/inner/test_codex_executor.py`
  - `tests/inner/test_codex_runtime_isolation.py`
  - `tests/server/integration/test_session_host_launch.py`
- 检查 CRLF/LF 整文件重写、无关历史 hunk、PR #2/#5 意外带入和测试文件整体复制。
- 确认 `tests/inner/test_codex_runtime_isolation.py` 若为新增文件，内容是当前 main API 所需的最小隔离测试。

建议只读命令：

```bash
git -C "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review" \
  diff --stat "8ef79ac348711d523053019cdb2f36e8cbbfef7e..HEAD"
git -C "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review" \
  diff --check "8ef79ac348711d523053019cdb2f36e8cbbfef7e..HEAD"
git -C "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-review" \
  diff --ignore-space-at-eol "8ef79ac348711d523053019cdb2f36e8cbbfef7e..HEAD"
```

### 6.2 代理隔离

逐路径验证：

- 默认 OpenAI subscription；
- explicit `openai` provider pin；
- custom model provider；
- gateway。

检查大小写两套 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`、`NO_PROXY` 是否被正确清理或重建；检查 WSL host IP、宿主代理和 OpenCodex 路由是否可能串入 Codex 子进程。

检查日志是否泄漏代理凭据、token、cookie、密钥、私密 URL 或 `auth.json` 内容。

### 6.3 Codex/OpenCodex 与 10100

- Codex subscription 必须使用私有 `CODEX_HOME`。
- 不得读取或改写 OpenCodex `config.toml`。
- 审查中不得连接、占用、释放 10100 或杀 OpenCodex。
- 不得修改 TUN、Clash、认证、全局代理或 240s watchdog。
- Qwen 的 10100 evidence 必须是只观察；若出现 `curl`、`nc`、`telnet` 或连接行为，记录为 REWORK。

### 6.4 Relaunch 竞态

检查：

- trigger event 是否包住真实生产调用；
- host receiver 是否在 POST 前进入可调度状态；
- frame ACK、launch completion 和 `runner_id` 旋转是否有明确顺序；
- per-poll 与 overall timeout 是否均有上限；
- frame/post task 异常是否总被消费；
- communicator 和 client 是否可靠关闭；
- monkeypatch 是否绕过了需要验证的生产 relaunch 路径；
- 测试是否依赖盲目 sleep、无限等待或失败重试；
- Windows/WSL 调度和 asgiref quiet slice 是否会造成假 PASS 或假 FAIL。

### 6.5 Qwen evidence

- 验证 RUN_ID 是新目录，输入 SHA 与 Claude 候选一致。
- 核对命令、stdout/stderr、exit、UTC 时间线和文件哈希。
- 核对 pytest、Ruff、compileall、ports-before/after、cleanup 和 leak-scan 是否互相一致。
- 核对五类 CLI 的状态是否有直接证据；无证据时必须是 UNKNOWN 或 LOGIN_REQUIRED。
- 确认测试后源码/测试未被 Qwen 修改。
- 定向结果不得被写成 Gate 1/Gate 2 PASS。

## 7. 可复现缺陷标准

一个 finding 只有同时满足以下条件，才可标为明确缺陷：

1. 有确定的文件和代码路径；
2. 有最小、可重复的只读检查或定向复现命令；
3. 实际结果与预期行为明确冲突；
4. 可归因于 Claude 候选，而不是基线、WSL 工具缺失或历史环境；
5. 不依赖泄漏凭据、连接 10100 或修改全局系统状态。

仅有推测、风格偏好、旧 Gate 失败或无法复现的竞态，不能授权修复。

## 8. 修复分支约束

本审查卡本身不授权修改源码。只有发现可复现且明确归因于 Claude 候选的缺陷，才允许创建新的修复 worktree。若发现满足第 7 节的缺陷：

1. 先在 `findings.md` 记录 REWORK、复现证据和最小修复范围；
2. 输出一张新的独立修复卡；
3. 修复 worktree 必须使用新的 `/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-grok-fix-<finding-id>` 路径；
4. 修复 evidence 必须使用新的 RUN_ID；
5. 不得在 Claude、Qwen 或本审查 worktree直接修复；
6. 修复范围仍不得越过获批的 4 个文件，除非 Codex 另行明确授权。

## 9. 结论

`final-verdict.txt` 只能使用一个结论：

- `ACCEPT`：diff 和 evidence 未发现明确缺陷，可交 Codex 最终验收；
- `REWORK`：存在可复现且可归因的候选缺陷；
- `INCONCLUSIVE`：输入或证据不足，无法可靠判断。

不得使用 Gate 1 PASS、Gate 2 PASS、全仓 GREEN 或 mergeable。ACCEPT 也只表示通过本次独立审查，不代表 Gate 或合并授权。

## 10. 完成报告

`review-report.md` 按以下顺序包含：

1. Completed tasks：审查范围、findings 和最终结论。
2. Handoff documents：Claude、Qwen 和 Grok evidence 的绝对 WSL 路径。
3. Next-agent prompt：交给 Codex / Luna 做最终只读验收。
4. Watch-outs：未验证事项、环境限制、剩余竞态风险和 Gate 边界。

## 11. 成功标准

- 在独立 Grok worktree完成只读审查。
- Claude diff 与 Qwen evidence 均被逐项核对。
- 所有 findings 有证据、归因和复现步骤。
- 输出严格为 ACCEPT、REWORK 或 INCONCLUSIVE。
- 未修改任何源码、测试、其他角色 worktree或旧 evidence。
- 未连接或干预 10100，未修改 TUN、Clash、OpenCodex、认证或 240s watchdog。
- 未运行完整 Gate 1/Gate 2，未 push、未 merge，也未改变 Gate 状态。
