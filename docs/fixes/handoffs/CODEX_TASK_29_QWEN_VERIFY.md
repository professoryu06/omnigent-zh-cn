# CODEX_TASK_29 — Qwen3.8 定向验证卡

## 1. 角色与启动条件

你是 Qwen3.8，负责低成本、独立、只验证的 WSL 检查。只有 Claude-DS 已经交付以下三项后才能启动：

1. 完整候选 SHA；
2. `semantic-diff.patch`；
3. `implementation-report.md`，标题为 `TARGETED_IMPLEMENTATION`。

缺少任何一项都必须输出 `INCONCLUSIVE_INPUT_MISSING` 并停止。不得进入 Claude 的可写 worktree替其补交付。

本卡只授权 TARGETED_VALIDATION，不授权修改源码/测试、完整 Gate 1、Gate 2、push 或 merge。

## 2. 固定输入

- 基线目录：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged`
- 基线 SHA：`8ef79ac348711d523053019cdb2f36e8cbbfef7e`
- 历史只读树：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-review`
- Claude worktree，只读：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-claude-ds`
- 独立验证 worktree：`/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-qwen-verify`
- Evidence 根：`/mnt/c/Users/Administrator/omnigent-diagnostics`

所有 WSL 命令必须使用 `/mnt/...` 路径。

## 3. 启动前必读

完整读取：

1. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/AGENTS.md`
2. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/CONTRIBUTING.md`
3. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/CODEX_TASK_29_ORCHESTRATION.md`
4. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/MODEL_ROLE_MATRIX_20260806.md`
5. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/HERMES_DIAGNOSIS_GATE1_20260805-164315-5c8b9ce-hermes-gate1-r6.md`
6. `/mnt/f/codex-ai/git项目部署/tmp/omnigent-review/docs/fixes/handoffs/GROK_FIX_RELAUNCH_RACE_20260806-103154-5c8b9ce-grok-relaunch-race-fix.md`
7. Claude evidence 中的 `semantic-diff.patch` 和 `implementation-report.md`。

记录 Claude evidence 的绝对 WSL 路径和 SHA，不得引用模糊的“最新目录”。

## 4. 创建独立验证 worktree并应用候选

从 Claude 报告取得 `CLAUDE_CANDIDATE_SHA` 后：

```bash
BASE_TREE="/mnt/f/codex-ai/git项目部署/tmp/omnigent-main-merged"
WORKTREE="/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-qwen-verify"
BASE_SHA="8ef79ac348711d523053019cdb2f36e8cbbfef7e"
CLAUDE_SHA="${CLAUDE_CANDIDATE_SHA:?set from Claude implementation-report.md}"

test "$(git -C "$BASE_TREE" rev-parse HEAD)" = "$BASE_SHA"
test ! -e "$WORKTREE"
git -C "$BASE_TREE" cat-file -e "${CLAUDE_SHA}^{commit}"
git -C "$BASE_TREE" worktree add --detach "$WORKTREE" "$BASE_SHA"
git -C "$WORKTREE" cherry-pick --no-commit "$CLAUDE_SHA"
```

验证应用后的 diff 与 Claude `semantic-diff.patch` 等价，只能涉及：

- `omnigent/inner/codex_executor.py`
- `tests/inner/test_codex_executor.py`
- `tests/inner/test_codex_runtime_isolation.py`
- `tests/server/integration/test_session_host_launch.py`

应用候选是本卡唯一允许产生的源码/测试差异。应用后不得编辑、格式化、自动修复、提交或还原任何源码/测试。若候选无法干净应用，保存冲突信息并输出 `REWORK_APPLY_FAILED`，不得手工解决冲突。

## 5. 新 RUN_ID 与 evidence

```bash
CANDIDATE_SHORT="$(git -C "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-qwen-verify" rev-parse --short=7 "$CLAUDE_SHA")"
RUN_ID="$(date -u +%Y%m%d-%H%M%S)-${CANDIDATE_SHORT}-qwen-targeted-wsl-r1"
EVIDENCE_ROOT="/mnt/c/Users/Administrator/omnigent-diagnostics/${RUN_ID}"
test ! -e "$EVIDENCE_ROOT"
mkdir -p "$EVIDENCE_ROOT"
```

若目录已存在，生成新的时间戳。禁止覆盖、拼接或复用 Claude、历史 Gate 或其他旧 RUN_ID。

至少保存：

- `env.txt`
- `versions.txt`
- `worktree-sha.txt`
- `claude-input-manifest.txt`
- `candidate-diff.patch`
- `candidate-diff-sha256.txt`
- `cli-matrix.tsv`
- `cli-paths.txt`
- `auth-status-redacted.txt`
- `ports-before.txt` 和 `ports-after.txt`
- `targeted-pytest.txt` 和 `targeted-pytest-exit.txt`
- `relaunch-stability.txt`
- `ruff.txt` 和 `ruff-exit.txt`
- `compileall.txt` 和 `compileall-exit.txt`
- `timeline.txt`
- `cleanup-leak-scan.txt`
- `credential-leak-scan.txt`
- `validation-report.md`

每项记录 UTC 起止时间、命令、stdout、stderr 和真实退出码。不得记录 token、cookie、密钥或 `auth.json` 内容。

## 6. WSL 工具检查

只读检查以下项目的路径、版本和退出码：

- WSL distro 与 kernel；
- Python；
- uv；
- Node 和 npm；
- tmux；
- bwrap；
- git。

建议命令：

```bash
uname -a
cat /etc/os-release
command -v python3
python3 --version
command -v uv
uv --version
command -v node
node --version
command -v npm
npm --version
command -v tmux
tmux -V
command -v bwrap
bwrap --version
command -v git
git --version
```

工具缺失只记录 `NOT_INSTALLED`，不得安装、升级或修改系统配置。

## 7. 五类模型 CLI 检查

逐一检查：

1. Claude-DS / DeepSeek；
2. Qwen；
3. Grok；
4. Codex；
5. Pi。

每项依次执行无副作用检查：

- `command -v <cli>`；
- `<cli> --version`；
- `<cli> --help`；
- 仅当 CLI 官方提供非交互、只读的 auth-status 命令时才运行该命令。

不得启动交互式登录，不得执行会消耗模型额度的真实任务，不得读取认证文件。状态只能使用：

- `INSTALLED_AND_AUTHENTICATED`：有非交互 auth-status 的直接证据；
- `LOGIN_REQUIRED`：CLI 明确返回需要登录；
- `UNKNOWN`：已安装但没有安全、非交互的登录状态证据；
- `NOT_INSTALLED`：找不到可执行文件；
- `BLOCKED_BY_ENVIRONMENT`：命令被明确的环境问题阻塞。

不得根据配置目录存在、进程存在或个人经验猜测已登录。

## 8. 端口与 10100 观察

测试前后分别保存监听端口和相关进程快照。对 10100 只能观察：

```bash
ss -ltnp
ss -ltnp | awk '$4 ~ /:10100$/ {print}'
ps -ef
```

禁止使用 `curl`、`nc`、`telnet` 或任何客户端连接 10100；禁止占用、释放端口或杀进程。不得修改 OpenCodex、TUN、Clash、认证、全局代理或 240s watchdog。

## 9. 定向验证

在独立 Qwen worktree运行：

```bash
cd "/mnt/f/codex-ai/git项目部署/tmp/omnigent-task29-qwen-verify"

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

对 relaunch nodeid 做有限的逐轮稳定性验证，每轮独立记录退出码。失败只记录和分类，不修改测试或实现。

禁止全仓 pytest、完整 Gate 1、Gate 2、真实 AgentCenter 验收或将一次冒烟扩写为 Gate 结果。

## 10. 不变性与清理检查

- 验证测试后源码/测试 diff 与应用候选后完全一致。
- 记录新产生的缓存、临时进程、tmux socket、server、runner 和 child process。
- 只清理本 RUN_ID 明确创建且可安全归因的临时资源；不得删除旧 evidence、`nul` 或历史临时目录。
- 扫描 evidence 中的 token、cookie、`auth.json` 内容、私密 URL 和未脱敏代理凭据；发现时将值替换为 `[REDACTED]` 并记录泄漏来源，不把秘密复制进报告。

## 11. 完成报告

`validation-report.md` 标题必须是：

`# TARGETED_VALIDATION`

按以下顺序包含：

1. Completed tasks：实际定向结果、WSL 工具矩阵、五类 CLI 状态、端口与 cleanup。
2. Handoff documents：Claude 输入、Qwen evidence 和所有绝对 WSL 路径。
3. Next-agent prompt：交给 Grok，只读审查 Claude diff 和本 RUN_ID evidence。
4. Watch-outs：失败、UNKNOWN/LOGIN_REQUIRED、环境缺失、残留资源和证据缺口。

不得写 Gate 1 PASS、Gate 2 PASS、全仓 GREEN 或 mergeable。

## 12. 成功标准

- Claude 三项输入完整且候选被原样应用到独立 Qwen worktree。
- 应用后未修改任何源码或测试。
- 定向 pytest、目标 Ruff、目标 compileall 均有真实 stdout/stderr/exit evidence。
- WSL 七项工具和五类 CLI 都有证据支持的状态。
- 10100 仅被观察，没有连接、占用、释放或杀进程。
- 测试前后 diff、端口、cleanup 和 credential leak-scan 完整。
- 报告使用 TARGETED_VALIDATION，未改变任何 Gate 状态。
