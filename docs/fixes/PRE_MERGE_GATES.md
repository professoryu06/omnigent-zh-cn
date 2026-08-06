# 功能 PR（#3 / #4 / #5）合并前门槛

**目的：** 在维护者 merge `#3 → #4 → #5` 之前，用**可复跑命令**证明集成不破坏正确性，并用最小实机场景证明 AgentCenter 关键路径可用。  
**本文件是门槛规格；结果写入** `artifacts/pre-merge/<run-id>/` **（默认 gitignore，不入库）及 `docs/fixes/STATUS.md`。**

**状态标签（强制区分）：**

| 标签 | 含义 |
|------|------|
| PR open 未 merge | 代码在分支上，main 未包含 |
| mitigated/fail-loud Phase1 | #2853 仅告警/strict，**非** prompt 送达 |
| prompt apply 未实现 | 不得声称角色 system_prompt 已进入 native CLI |
| 定向 67 绿 | 仅 #3+#4+#5 相关用例，**≠** 全仓通过 |
| 全仓绝对全绿 | `uv run pytest -q` 无 fail/error |
| 相对 main 无新增失败 | 集成树失败集 ⊆ clean main 失败集（同环境） |
| AgentCenter smoke 完成 | 下方断言全部有日志证据 |

---

## Gate 0 — 固定环境

### 0.1 权威平台（门槛 1 必须在此跑）

| 项 | 固定值 |
|----|--------|
| OS / 镜像 | **Linux `ubuntu-latest` 等价**：Ubuntu 22.04 或 24.04 x86_64（与 `.github/workflows/zh-cn-linux-smoke.yml` / 常见 CI 一致） |
| 架构 | x86_64 |
| Python | **3.12.x**（`requires-python = ">=3.12"`；CI 使用 3.12） |
| 包管理 | **uv**（与 `windows.yml` / `macos.yml`：`uv sync --locked --extra dev`） |
| 原生依赖 | `tmux`、`bubblewrap`（Linux smoke 安装项）；可选 git |
| 禁止 | 用 Windows 全仓 collection 失败替代 Linux 门槛结果 |

### 0.2 安装（Linux）

```bash
# 工作目录：仓库 clone
git fetch origin
# Python 3.12 + uv 已安装

sudo apt-get update
sudo apt-get install -y tmux bubblewrap git

uv sync --locked --extra dev
# 若 locked 失败：记录 uv 版本与错误，再评估 uv sync --extra dev（须写入证据）

uv run python -c "import sys; print(sys.version); assert sys.version_info[:2] >= (3, 12)"
```

### 0.3 集成树（不 push）

```bash
# 使用审查时实时 head（示例；执行前替换为 gh pr view 输出）
export MAIN_SHA=$(git rev-parse origin/main)
export PR3_SHA=744e3a04a9b041b7bf3c2ae25cd22f96f5945038   # 示例
export PR4_SHA=30c04c3a173543f2802f3d8277a1660a616b393a
export PR5_SHA=1f42a898fbd07e358f87de5cba391a93af1f43b9

git worktree add /tmp/omnigent-premerge-main origin/main
git worktree add -b tmp/premerge-345 /tmp/omnigent-premerge-345 origin/main
cd /tmp/omnigent-premerge-345
git merge --no-ff "$PR3_SHA" -m "tmp: PR3"
git merge --no-ff "$PR4_SHA" -m "tmp: PR4"
git merge --no-ff "$PR5_SHA" -m "tmp: PR5"
# 冲突 → 停止，报告冲突文件；不擅自改业务逻辑
```

### 0.4 证据目录（每次 run 固定）

```text
artifacts/pre-merge/<run-id>/
  env.txt                 # uname -a, python -V, uv -V, apt 包版本摘要
  commits.txt             # MAIN_SHA, PR3/4/5 SHA, integrate tip SHA
  baseline-pytest.xml     # clean main JUnit
  baseline-pytest.txt     # human summary + failed nodeids
  integrate-pytest.xml
  integrate-pytest.txt
  targeted-67.txt         # 定向 67 复跑
  ruff.txt
  agentcenter/            # smoke 日志与配置快照（若执行）
    config.snapshot.yaml  # 脱敏后
    smoke.log
    assertions.md         # pass/fail 表
```

`run-id` 建议：`YYYYMMDD-HHMM-<short-integrate-sha>`。  
**默认 gitignore**；PR 描述或 STATUS 只写路径 + SHA + 结论摘要。

---

## Gate 1 — Linux 全仓 / 平台回归

### 1.1 命令

**A. clean main**

```bash
cd /tmp/omnigent-premerge-main
uv sync --locked --extra dev
export RUN_ID=...
mkdir -p artifacts/pre-merge/$RUN_ID
{
  echo "MAIN=$(git rev-parse HEAD)"
  uname -a
  uv run python -V
  uv -V
} | tee artifacts/pre-merge/$RUN_ID/env.txt

uv run pytest -q \
  --junitxml=artifacts/pre-merge/$RUN_ID/baseline-pytest.xml \
  2>&1 | tee artifacts/pre-merge/$RUN_ID/baseline-pytest.txt
echo EXIT:$? | tee -a artifacts/pre-merge/$RUN_ID/baseline-pytest.txt
```

**B. main+#3+#4+#5**

```bash
cd /tmp/omnigent-premerge-345
uv sync --locked --extra dev
uv run pytest -q \
  --junitxml=artifacts/pre-merge/$RUN_ID/integrate-pytest.xml \
  2>&1 | tee artifacts/pre-merge/$RUN_ID/integrate-pytest.txt
echo EXIT:$? | tee -a artifacts/pre-merge/$RUN_ID/integrate-pytest.txt
```

**C. 定向 67 + Ruff（两棵树都建议跑集成树）**

```bash
uv run pytest -q \
  tests/runner/test_session_workspace_cache.py \
  tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries \
  tests/inner/test_loader_executor_nested.py \
  tests/runner/test_codex_native_model_from_spec.py \
  tests/inner/test_native_system_prompt_delivery.py \
  tests/inner/test_claude_native_executor.py \
  tests/inner/test_codex_native_executor.py \
  2>&1 | tee artifacts/pre-merge/$RUN_ID/targeted-67.txt

uv run ruff check \
  omnigent/runner/app.py omnigent/inner/loader.py \
  omnigent/inner/*native*.py omnigent/inner/native_prompt_delivery.py \
  omnigent/native_server_harness.py \
  tests/runner/test_session_workspace_cache.py \
  tests/inner/test_loader_executor_nested.py \
  tests/runner/test_codex_native_model_from_spec.py \
  tests/inner/test_native_system_prompt_delivery.py \
  2>&1 | tee artifacts/pre-merge/$RUN_ID/ruff.txt
```

### 1.2 Pass / Fail 规则

| 结果 | 判定 |
|------|------|
| 集成树 `pytest -q` **绝对全绿**（0 failed, 0 errors） | **Gate 1 PASS（绝对全绿）** |
| clean main **已有**失败，且集成树失败 nodeid **⊆** main 失败集（同环境、同依赖） | **Gate 1 PASS（相对 main 无新增失败）** — 必须在 `baseline-failures.txt` / `integrate-failures.txt` 列出两边失败，并标注每个基线失败「已知环境/已知 flaky」 |
| 集成树出现 main **没有**的失败或 error | **Gate 1 FAIL** — 阻塞 merge |
| 仅 Windows 定向 67 绿 | **不足** — Gate 1 未满足 |

比较失败列表示例：

```bash
# 从 summary 或 --lf 缓存提取 nodeid 后：
comm -13 <(sort baseline-fail-ids.txt) <(sort integrate-fail-ids.txt)
# 非空 → 新增失败 → FAIL
```

---

## Gate 2 — AgentCenter 最小 C/E/R smoke

### 2.1 固定最小配置（示例；路径按部署改）

三角色单文件或目录 agent（**Executor 用 flat 或已验证的 nested harness 声明**）：

```yaml
# agents/executor.yaml  — 关键：nested harness 不得被 model-prefix 顶替
name: executor-gate
prompt: "You are Executor. Reply with the single token EXECUTOR_OK and stop."
executor:
  type: omnigent
  config:
    harness: codex-native   # 或团队实际目标 native；须与 assert 一致
  model: <PINNED_NON_DEFAULT_MODEL>

# agents/controller.yaml — 可用 claude-sdk / 非 native 降低环境依赖
name: controller-gate
prompt: "You are Controller. Reply with CONTROLLER_OK and stop."
executor:
  harness: claude-sdk
  model: <PINNED_MODEL>

# agents/reviewer.yaml
name: reviewer-gate
prompt: "You are Reviewer. Reply with REVIEWER_OK and stop."
executor:
  harness: claude-sdk
  model: <PINNED_MODEL>
```

环境变量（Phase1）：

```bash
# 非 strict 跑一轮 native 后，再：
export OMNIGENT_STRICT_PROMPT=1   # 仅用于 strict 断言轮次
```

### 2.2 启动步骤（模板）

```bash
# 使用已安装的 zh-cn CLI（或 uv run）
omnigent-zh --version | tee artifacts/pre-merge/$RUN_ID/agentcenter/version.txt

# 1) 为三角色创建 session，各自 worktree/workspace 路径不同
# 2) 记录 session id 与 workspace 绝对路径到 agentcenter/sessions.txt
# 3) Executor：发一条短消息（非 strict）
# 4) 抓 runner/server 日志中 fail-loud warning（chars=N，无 prompt 正文）
# 5) 设 OMNIGENT_STRICT_PROMPT=1，再发消息，确认在注入前失败
# 6) 检查 codex-native 实际 model / harness（日志或 debug API）
```

具体 CLI 以当前 `omnigent-zh` / Web UI 为准；**缺 CLI 或角色文件则 Gate 2 = 未执行**，不得编造。

### 2.3 断言表（全部 PASS 才算 smoke 完成）

| ID | 断言 | 证据 |
|----|------|------|
| AC-1 | Controller / Executor / Reviewer **workspace 互不共享**（路径不同且文件不串） | `sessions.txt` + 各 workspace 列表 |
| AC-2 | Executor **nested `codex-native`（或声明 harness）未被 model-prefix 换成其它 harness** | launch 日志 / harness_kind |
| AC-3 | Executor **实际 model = YAML `executor.model`**（非 provider 默默替换） | launch 日志 |
| AC-4 | native **非 strict**：出现 fail-loud **warning**（含 `chars=`，**无** system_prompt 原文） | `smoke.log` |
| AC-5 | **strict**：`OMNIGENT_STRICT_PROMPT=1` 时，在用户消息注入 native 前失败 | `smoke.log` 时间序 |
| AC-6 | **不得**在报告中写「prompt 已送达 / 角色指令已生效于 native」——除非另有 Phase2 证据 | 审查文案 |

任一失败 → Gate 2 FAIL。  
未部署 AgentCenter / 无 native CLI → Gate 2 **未执行**（阻塞 merge，证据缺口写清）。

---

## 本环境执行记录（时间快照）

| 项 | 结果 |
|----|------|
| 执行机 | Windows（非 Gate 0 Linux） |
| Gate 1 Linux 全仓 | **未执行** — 阻塞：当前执行环境为 Windows，缺少 fcntl/pexpect 完整路径及约定 Ubuntu 完整依赖；**不得**用 Windows 全仓 collection error 充当 Gate 1 |
| Gate 1 历史参考 | 同机曾跑：定向 67 绿；全仓 collection 10 errors（fcntl/pexpect/databricks）；扩大子集有大量 host/cli 环境失败 — **仅作参考，非门槛通过** |
| Gate 2 AgentCenter | **未执行** — 阻塞：仅有 `.omnigent` ACP Grok Code，无 C/E/R 三角色 agent YAML 与多 session worktree 编排 |
| 结论 | **合并门槛未达到** |

更新 STATUS 时必须写：`Gate1=未执行/FAIL/PASS(绝对|相对)`，`Gate2=未执行/FAIL/PASS`。

---

## 与「定向 67」的关系

- 定向 67 + Ruff：**必要但不充分**。  
- 通过定向 67 **不能**标记 Gate 1/2 完成，**不能**替代 merge 前门槛。
