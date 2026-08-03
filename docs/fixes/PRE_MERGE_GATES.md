# 功能 PR（#3 / #4 / #5）合并前门槛

**目的：** 在维护者 merge `#3 → #4 → #5` 之前，用**可复跑命令**证明集成不破坏正确性，并用最小实机场景证明 AgentCenter 关键路径可用。  
**本文件是门槛规格；结果写入** `$EVIDENCE_ROOT`（即 `/tmp/omnigent-premerge-evidence/<run-id>/`，绝对路径，默认 gitignore，不入库）**及 `docs/fixes/STATUS.md`。**

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

### 0.4 证据目录（每次 run 固定，绝对路径）

```bash
export RUN_ID=YYYYMMDD-HHMM-<shortsha>
export EVIDENCE_ROOT=/tmp/omnigent-premerge-evidence/$RUN_ID
mkdir -p "$EVIDENCE_ROOT/agentcenter"
```

```text
$EVIDENCE_ROOT/
  env.txt                 # uname -a, python -V, uv -V, apt 包版本摘要
  commits.txt             # MAIN_SHA, PR3/4/5 SHA, integrate tip SHA
  baseline-pytest.xml     # clean main JUnit
  baseline-pytest.txt     # human summary + PYTEST_EXIT/TEE_EXIT
  baseline-fail-ids.txt   # clean main 失败 nodeid 列表
  integrate-pytest.xml
  integrate-pytest.txt    # human summary + PYTEST_EXIT/TEE_EXIT
  integrate-fail-ids.txt  # integrate 失败 nodeid 列表
  new-failures.txt        # comm 比较结果（新增失败 nodeid）
  targeted-67.txt         # 定向 67 复跑
  ruff.txt
  agentcenter/            # smoke 日志与配置快照（若执行）
    config.snapshot.yaml  # 脱敏后
    smoke.log
    assertions.md         # pass/fail 表
```

`RUN_ID` 格式：`YYYYMMDD-HHMM-<short-integrate-sha>`。
**EVIDENCE_ROOT 为绝对路径**，两棵 worktree 共享同一证据根，不依赖 `cd` 后的相对 `artifacts/`。
**默认 gitignore**；PR 描述或 STATUS 只写路径 + SHA + 结论摘要。

---

## Gate 1 — Linux 全仓 / 平台回归

### 1.1 命令

**A. clean main**

```bash
cd /tmp/omnigent-premerge-main
uv sync --locked --extra dev
export RUN_ID=...
export EVIDENCE_ROOT=/tmp/omnigent-premerge-evidence/$RUN_ID
mkdir -p "$EVIDENCE_ROOT/agentcenter"
{
  echo "MAIN=$(git rev-parse HEAD)"
  uname -a
  uv run python -V
  uv -V
} | tee "$EVIDENCE_ROOT/env.txt"

set +e
set -o pipefail
uv run pytest -q \
  --junitxml="$EVIDENCE_ROOT/baseline-pytest.xml" \
  2>&1 | tee "$EVIDENCE_ROOT/baseline-pytest.txt"
pipeline_status=("${PIPESTATUS[@]}")
pytest_status=${pipeline_status[0]}
tee_status=${pipeline_status[1]}
set +o pipefail
# 恢复 errexit（若之前启用）
set -e
{
  echo "PYTEST_EXIT:$pytest_status"
  echo "TEE_EXIT:$tee_status"
} | tee -a "$EVIDENCE_ROOT/baseline-pytest.txt"

# INVALID 判定：tee 非零 / JUnit 缺失 / 证据目录不可写 → 证据无效
if [ "$tee_status" -ne 0 ] || [ ! -f "$EVIDENCE_ROOT/baseline-pytest.xml" ] || [ ! -w "$EVIDENCE_ROOT" ]; then
  echo "INVALID: baseline evidence capture failed (tee=$tee_status, junit=$([ -f "$EVIDENCE_ROOT/baseline-pytest.xml" ] && echo present || echo missing), writable=$([ -w "$EVIDENCE_ROOT" ] && echo yes || echo no))" | tee -a "$EVIDENCE_ROOT/baseline-pytest.txt"
  # INVALID 不得 PASS
fi
# pytest 非零可继续（baseline/integrate 比较模式）
```

**B. main+#3+#4+#5**

```bash
cd /tmp/omnigent-premerge-345
uv sync --locked --extra dev
export EVIDENCE_ROOT=/tmp/omnigent-premerge-evidence/$RUN_ID
set +e
set -o pipefail
uv run pytest -q \
  --junitxml="$EVIDENCE_ROOT/integrate-pytest.xml" \
  2>&1 | tee "$EVIDENCE_ROOT/integrate-pytest.txt"
pipeline_status=("${PIPESTATUS[@]}")
pytest_status=${pipeline_status[0]}
tee_status=${pipeline_status[1]}
set +o pipefail
set -e
{
  echo "PYTEST_EXIT:$pytest_status"
  echo "TEE_EXIT:$tee_status"
} | tee -a "$EVIDENCE_ROOT/integrate-pytest.txt"

if [ "$tee_status" -ne 0 ] || [ ! -f "$EVIDENCE_ROOT/integrate-pytest.xml" ] || [ ! -w "$EVIDENCE_ROOT" ]; then
  echo "INVALID: integrate evidence capture failed (tee=$tee_status, junit=$([ -f "$EVIDENCE_ROOT/integrate-pytest.xml" ] && echo present || echo missing), writable=$([ -w "$EVIDENCE_ROOT" ] && echo yes || echo no))" | tee -a "$EVIDENCE_ROOT/integrate-pytest.txt"
fi
```

**C. 定向 67 + Ruff（两棵树都建议跑集成树）**

```bash
export EVIDENCE_ROOT=/tmp/omnigent-premerge-evidence/$RUN_ID

uv run pytest -q \
  tests/runner/test_session_workspace_cache.py \
  tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries \
  tests/inner/test_loader_executor_nested.py \
  tests/runner/test_codex_native_model_from_spec.py \
  tests/inner/test_native_system_prompt_delivery.py \
  tests/inner/test_claude_native_executor.py \
  tests/inner/test_codex_native_executor.py \
  2>&1 | tee "$EVIDENCE_ROOT/targeted-67.txt"

uv run ruff check \
  omnigent/runner/app.py omnigent/inner/loader.py \
  omnigent/inner/*native*.py omnigent/inner/native_prompt_delivery.py \
  omnigent/native_server_harness.py \
  tests/runner/test_session_workspace_cache.py \
  tests/inner/test_loader_executor_nested.py \
  tests/runner/test_codex_native_model_from_spec.py \
  tests/inner/test_native_system_prompt_delivery.py \
  2>&1 | tee "$EVIDENCE_ROOT/ruff.txt"
```

### 1.2 Pass / Fail 规则

| 结果 | 判定 |
|------|------|
| 集成树 `pytest -q` **绝对全绿**（0 failed, 0 errors） | **Gate 1 PASS（绝对全绿）** |
| clean main **已有**失败，且候选树失败 nodeid **⊆** main 失败集（同环境、同依赖、同隔离状态） | **Gate 1 PASS（相对 main 无新增失败）** — 必须同时满足下列"相对 PASS 安全条件"；任一缺失均不得 PASS |
| 集成树出现 main **没有**的失败或 error | **Gate 1 FAIL** — 阻塞 merge |
| 仅 Windows 定向 67 绿 | **不足** — Gate 1 未满足 |

#### 相对 PASS 安全条件

相对 main PASS 必须同时满足：

1. baseline 与 candidate 在同 OS、同依赖、同隔离状态下完整运行，且两侧 JUnit 均存在、非空、可解析，pytest/tee 退出码均被独立冻结。
2. candidate 失败 nodeid 集合是 baseline 的子集，`new-failures.txt` 为空；任何 candidate-only failure/error 均为 Gate 1 FAIL。
3. 每个共享失败必须有具体分类与证据，且只能分别记录为：
   - `known_environment`：可归因 Gate 执行环境缺失，例如缺包、缺服务、缺凭据、网络限制或资源布局异常；
   - `known_flaky`：有独立复现证据证明同一代码与环境下交替 pass/fail；
   - `documented_main_code_failure`：clean main 上可复现的确定性代码失败，已记录具体根因，且不属于本候选引入的回归。
4. 每个共享失败的归一化语义指纹必须在 baseline 与 candidate 之间相同。归一化可以去除树绝对路径、pytest 临时运行编号、随机 UUID/会话 ID/PID/内存地址和耗时，但必须保留异常类型、实际/期望值、HTTP 状态码、模块名、策略动作与其他影响失败语义的字段。
5. 任一共享 nodeid 的异常类型、实际/期望值、关键错误码或其他稳定语义发生变化时，视为可能恶化；必须逐项独立审查，不能仅凭 nodeid 相同计入相对 PASS。
6. 候选新增测试必须全部通过；当前候选的定向套件、Ruff、diff-check和保护 blob证据必须有效且无回归。
7. 三类baseline失败必须分别统计，不得把`documented_main_code_failure`称为环境或flaky，也不得只写"main也失败"。
8. 使用`documented_main_code_failure`形成相对PASS必须有一次明确、可审计的Codex/用户批准；报告或执行者不得自行扩大门槛。
9. 相对PASS不等于全仓GREEN，不等于Gate 2 PASS，不等于可merge。

> **政策修订记录（2026-07-29，Codex显式批准）：** 原版只允许`known_environment`/`known_flaky`作为已知baseline。r6同环境双侧证据显示，clean main另有85项确定性代码失败；candidate无新增失败，126个共享失败的归一化语义指纹全部相同。为避免有限范围修复被无关main失败无限期误阻，增加`documented_main_code_failure`第三类，同时强制逐项分类、语义指纹比较、候选新增测试/定向质量证据和显式批准。该修订不追认全仓GREEN、Gate 2或merge许可。

比较失败列表示例：

```bash
# 生成 commits.txt
{
  echo "MAIN=$MAIN_SHA"
  echo "PR3=$PR3_SHA"
  echo "PR4=$PR4_SHA"
  echo "PR5=$PR5_SHA"
  echo "INTEGRATE_TIP=$(git -C /tmp/omnigent-premerge-345 rev-parse HEAD)"
} > "$EVIDENCE_ROOT/commits.txt"

# 从 JUnit XML 或 pytest --lf 缓存提取失败 nodeid 后：
# （baseline-fail-ids.txt 与 integrate-fail-ids.txt 各含一行一个 nodeid）
comm -13 <(sort "$EVIDENCE_ROOT/baseline-fail-ids.txt") \
         <(sort "$EVIDENCE_ROOT/integrate-fail-ids.txt") \
  > "$EVIDENCE_ROOT/new-failures.txt"
# new-failures.txt 非空 → 新增失败 → FAIL
```

---

## Gate 2 — AgentCenter 最小 C/E/R smoke（Phase 2 正向 + Phase 1 负向分轨）

### 2.1 固定最小配置（示例；路径按部署改）

Gate 2 拆成五个逻辑轮次，正向 codex-native Phase 2 apply 与负向 warn-only native Phase 1 控制**不得共用 session**：

| 轮次 | harness | session 要求 | 目的 |
|---|---|---|---|
| C | 可用非 native | 独立 workspace/session | Controller 短回复 |
| E-pos | `codex-native` | fresh、非 fork、STRICT 未设置 | Phase 2 apply 正向证据 |
| E-pos-strict | `codex-native` | **新的** fresh、非 fork session/runner；**进程启动前** STRICT=1 | receipt 匹配时 strict 仍继续 |
| E-neg-warn / E-neg-strict | 能力矩阵为 `warn` 的**非 codex** native harness | 两个新 session；分别从启动前 STRICT 未设置/STRICT=1 | Phase 1 warning 与注入前失败 |
| R | 可用非 native | 独立 workspace/session | Reviewer 短回复 |

**禁止**把 receipt-mismatch、resume 或 fork codex-native 充当 E-negative 负向控制。receipt 缺失不能可靠证明 private config 中没有历史 `developer_instructions`；这种控制不等价于"无 apply 通道"。

配置示例：

```yaml
# agents/e-pos.yaml — codex-native Phase 2 正向
name: e-pos-gate
prompt: "You are E-pos. Reply with the single token E_POS_OK and stop."
executor:
  type: omnigent
  config:
    harness: codex-native
  model: <PINNED_NON_DEFAULT_MODEL>

# agents/e-pos-strict.yaml — codex-native Phase 2 strict（新 session/runner）
name: e-pos-strict-gate
prompt: "You are E-pos-strict. Reply with the single token E_POS_STRICT_OK and stop."
executor:
  type: omnigent
  config:
    harness: codex-native
  model: <PINNED_NON_DEFAULT_MODEL>

# agents/e-neg.yaml — warn-only 非 codex native（以 preflight 实际可用者为准）
name: e-neg-gate
prompt: "You are E-neg. Reply with the single token E_NEG_OK and stop."
executor:
  type: omnigent
  config:
    harness: claude-native   # 首选示例；以 preflight 实际可用的 warn-only native 为准
  model: <PINNED_MODEL>

# agents/controller.yaml — 可用非 native
name: controller-gate
prompt: "You are Controller. Reply with CONTROLLER_OK and stop."
executor:
  harness: claude-sdk
  model: <PINNED_MODEL>

# agents/reviewer.yaml — 可用非 native
name: reviewer-gate
prompt: "You are Reviewer. Reply with REVIEWER_OK and stop."
executor:
  harness: claude-sdk
  model: <PINNED_MODEL>
```

E-negative 使用 `native_prompt_delivery.py` 能力矩阵中值为 `warn` 的**非 codex** native harness；不得预先写死本机不存在的 CLI。文档列 `claude-native` 为首选示例，但**以 preflight 实际可用者为准**。若本机没有第二个可启动的、能力矩阵为 `warn` 的 native CLI，Gate 2=`NOT_EXECUTED/未完成`，阻塞 merge；不得降级为 codex receipt-mismatch。

所有 role prompt 非空且使用短 token 回复；证据中不得保存 prompt 正文。E-pos、E-pos-strict、E-neg-warn、E-neg-strict 禁止共用 session id。

### 2.2 启动步骤（模板）

```bash
# 1) 新建独立 Gate 2 evidence root，不复用 Gate 1 evidence
export GATE2_EVIDENCE_ROOT=/tmp/omnigent-gate2-evidence/$RUN_ID
mkdir -p "$GATE2_EVIDENCE_ROOT"

# 2) preflight（不打印 secret/token）
omnigent-zh --version | tee "$GATE2_EVIDENCE_ROOT/version.txt"
# codex CLI 存在性、第二个 warn-only native CLI 存在性、
# credential 存在性布尔值、真实可用模型、端口、现有进程

# 3) 建立 C、E-pos、E-pos-strict、E-neg-warn、E-neg-strict、R
#    各自独立 workspace/session；每个 workspace 放唯一 sentinel 证明文件不串

# 4) C/R 执行 one-shot 短回复

# 5) E-pos：STRICT 未设置，fresh 非 fork codex-native 启动
#    证明 receipt/config 摘要、harness/model、真实回复、无 fail-loud warning

# 6) E-pos-strict：新建 fresh 非 fork session/runner
#    在启动命令之前设置 OMNIGENT_STRICT_PROMPT=1
#    证明 receipt 匹配并继续成功
#    注意：环境变量只在子进程启动时继承；
#    禁止对已启动 runner 事后设置 STRICT 后复用

# 7) E-neg-warn：新建 warn-only native session，启动前确保 STRICT 未设置
#    证明 warning 含 chars=N、不含 prompt 正文，用户消息未拼接 role prompt

# 8) E-neg-strict：再新建 warn-only native session/runner，启动前设置 STRICT=1
#    证明在任何用户消息 RPC/注入前失败

# 9) 记录 session id、绝对 workspace、harness、YAML model、
#    实际 launch model、strict、退出码、日志文件

# 10) 只清理由本 RUN_ID 启动并可精确绑定的进程；
#     禁止 blanket pkill、tmux kill-server、无差别 TERM/KILL
```

模板约束：

- `run --harness codex-native -p ...` 会走 native TUI 且拒绝 REPL 参数，不能作为 E-positive；E-positive 必须使用 `run <executor-yaml> -p ...` 的 session/runner/app-server 路径。
- 环境变量只在子进程启动时继承；禁止对已启动 runner 事后设置 STRICT 后复用。
- receipt 证据只保存 `harness_id/channel/chars/sha256`；private config 只保存键存在性、model、chars 与 digest 摘要，不复制 `developer_instructions` 正文。
- 任何 log、异常、argv、env、receipt、报告中不得出现 prompt 正文或 credential 值。

### 2.3 断言表（全部 PASS 才算 smoke 完成）

| ID | 必须断言 | 最低证据 |
|---|---|---|
| AC-1 | C、E-pos、E-pos-strict、E-neg-warn、E-neg-strict、R workspace 路径均不同，sentinel 不串 | `sessions.txt` + workspace 清单 |
| AC-2 | E-pos/E-pos-strict YAML 声明与实际 `harness_kind` 均为 `codex-native`，未被 model prefix 替换 | launch 日志/会话快照 |
| AC-3 | E-pos/E-pos-strict 实际 model 与各自 YAML pin 字符串相等 | launch 日志 + private config model 摘要 |
| AC-4-pos | E-pos 非空 prompt receipt 四项匹配，private config 有 `developer_instructions` 键，真实回复成功，且无 `not applying` warning | receipt/config 摘要 + launch/smoke log |
| AC-4-neg | E-neg-warn 必须出现含 `chars=N` 的 fail-loud warning，且任何证据无 prompt 正文 | `e-neg-warn.log` + 泄漏扫描 |
| AC-5-pos | E-pos-strict 从进程启动前 STRICT=1；receipt 匹配，仍能完成真实 turn | env-presence（无值）+ 时间序日志 |
| AC-5-neg | E-neg-strict 从进程启动前 STRICT=1；在任何用户消息 RPC/注入前失败，无成功模型回复 | 时间序日志/错误事件 |
| AC-6 | 只有 AC-2、AC-3、AC-4-pos、AC-5-pos 全部具备实机证据时，才可写"codex-native Phase 2 已送达"；其余 native 永远不得声称送达；单元测试或无 warning 不能替代证据链 | 审查文案 + E-positive evidence |

判定规则：

- 所有必跑轮次及 AC-1～AC-6 全部满足，且 evidence 可解析 → Gate 2 PASS。
- CLI、credential、真实模型或第二个 warn-only native 缺失 → Gate 2 `NOT_EXECUTED/未完成`，阻塞 merge。
- 环境具备且实际断言失败 → Gate 2 FAIL。
- 日志/退出码/session 映射缺失、证据串轮或无法判断注入时序 → Gate 2 INVALID，必须重跑；不得拼接不同 run。

---

## 本环境执行记录（时间快照）

| 项 | 结果 |
|----|------|
| 执行机 | WSL2 Ubuntu 24.04.4 x86_64 / Python 3.12.3 / uv 0.11.33 |
| Gate 1 Linux 全仓 | **PASS（相对 main）** — baseline/candidate 均非全绿；r6：baseline 123 failed + 3 errors，candidate 123 failed + 3 errors；双方 126 个失败/错误 nodeid 相同，归一化语义指纹 126/126 相同，candidate-only=0。证据根：`C:\Users\Administrator\gate1-evidence\20260729-1715-dc83140-grok-r6\`。不等于全仓 GREEN。 |
| Gate 2 AgentCenter | **未执行、未判定** — 阻塞：需要 codex CLI + 第二个 warn-only native CLI + credential + 真实模型 |
| 结论 | **合并门槛仍未达到；不可 merge** |

更新 STATUS 时必须写：`Gate1=未执行/FAIL/PASS(绝对|相对)`，`Gate2=未执行/FAIL/PASS`。

---

## 与「定向 67」的关系

- 定向 67 + Ruff：**必要但不充分**。  
- 通过定向 67 **不能**标记 Gate 1/2 完成，**不能**替代 merge 前门槛。
