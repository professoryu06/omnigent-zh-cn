# HERMES_DIAGNOSIS_GATE1_20260804-145343-5c8b9ce-hermes-gate1-r3

- **RUN_ID**: `20260804-145343-5c8b9ce-hermes-gate1-r3`（Grok proxy 修复后的 Gate 1 重跑，全新 RUN_ID）
- **执行者**: Hermes（用户明确授权：Grok 修复后重跑 Gate 1，不得修改 Gate 2 结论）
- **候选**: `5c8b9ce96f7552d380276fe6de04651f2b19531a` + Grok 未提交修复（3 文件：
  `omnigent/inner/codex_executor.py`、`tests/inner/test_codex_executor.py`、`tests/inner/test_codex_runtime_isolation.py`），
  worktree = 主工作树 `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **clean main**: `81594243f7a17303b9ba477b938ac323f938c2e4`（`F:\codex-ai\git项目部署\tmp\omnigent-gate1-main`）
- **环境**: WSL2 Ubuntu-24.04（Store launcher），Python 3.12.3，uv 0.11.33
- **最终分类**: **GATE1_PASS**（相对 clean main 无新增确定性失败；2 个 candidate-only 失败已实证分类为环境/偶发，分类确认权在 Codex）

## 一、Grok 修复确认（未 commit，未改动）

- HEAD = `5c8b9ce96f7552d380276fe6de04651f2b19531a` ✓（未 reset）
- 3 个文件 modified（+86/−18）：codex_executor.py（subscription proxy 仅注入 默认订阅/openai pin；
  Databricks/custom 仅 pin 不继承 proxy；gateway 不注入且 gateway+override 互斥 OSError 保留）、
  test_codex_executor.py（+29，加强 Databricks pin-only + openai pin 保留 proxy）、
  test_codex_runtime_isolation.py（+42，custom 不继承 / openai pin 注入 / gateway 互斥断言）
- 契约矩阵核对：与产品契约一致（未凑绿——Databricks 期望仍是"仅 pin 不继承"）

## 二、执行记录（含两次 150 分钟截断与补跑）

| 步骤 | main | cand |
|------|------|------|
| uv sync --locked --extra dev --extra all | EXIT=0 | EXIT=0 |
| pytest 全量（--timeout=300 --timeout-method=signal） | 首次 93% 被 timeout 9000 截断 → **300min 补跑完整**：**135 failed + 3 errors**（14914 passed, 2h32m） | 首次 88% 被 timeout 9000 截断 → **300min 补跑完整**：**136 failed + 3 errors**（15051 passed, 2h37m） |
| ruff（规格 1.1 C 定向集） | EXIT=1（E902 缺失文件，同 r2） | EXIT=1（E902 缺失文件，同 r2） |
| compileall | EXIT=0 | EXIT=0 |

- 截断现场保留：`main-pytest-truncated-at-93pct.{xml,txt}`、`main-fail-ids-truncated.txt`（证据根）
- 执行方式（r2 经验沿用）：`--extra all`（databricks-sdk）+ `--timeout-method=signal`（thread 对 asyncio 失效）

## 三、失败统计与差集（全量完整数据）

| 项 | 值 |
|----|-----|
| main 失败/错误 | 138（135+3） |
| cand 失败/错误 | 139（136+3） |
| 共享失败 | 137（归一化语义指纹 **mismatch=0**） |
| main-only | 1（`tests.cli.test_update_check::test_find_repo_root_finds_git_dir`，cand 通过——候选更优，非回归） |
| **candidate-only** | **2**（均已实证分类，见下） |

## 四、candidate-only 失败分类证据

### 1. `tests.inner.test_codex_executor::test_model_provider_override_appends_pin` — **known_environment**

- 失败断言（test_codex_executor.py:2725）：`assert "HTTPS_PROXY" not in executor._env` + `HTTP_PROXY` 同
- 根因：WSL 会话带宿主机代理透传（`HTTP_PROXY=http://172.31.80.1:17892`），`CodexExecutor._env` 经
  `self._env.update(self._retry_policy.codex_cli.env())` 继承代理变量——**该行为 main 同源**
  （main `omnigent/inner/codex_executor.py:2149` 相同代码），非候选实现引入
- **实证**：`env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY pytest ...test_model_provider_override_appends_pin`
  → **1 passed**（0.82s）
- 结论：Grok 新增断言对环境敏感（带代理 shell 失败、干净环境通过）；**Grok 修复目标本身已验证**——
  r2 的 config_overrides 断言（Databricks 误注入 proxy）已通过

### 2. `tests.server.integration.test_session_host_launch::test_host_session_message_relaunches_offline_runner` — **known_flaky**

- 失败断言：`host.launch_runner ... none arrived — the relaunch branch in post_event did not fire`（异步时序竞态）
- Grok **未修改** `test_session_host_launch.py`；main 同环境 PASSED
- **实证**：cand 单独重跑 **3/3 全部通过**（5.17s / 4.97s / 5.02s）
- 结论：integration 异步 relaunch 时序竞态，偶发非确定性

## 五、判定

**GATE1_PASS**（相对 clean main）——依据 PRE_MERGE_GATES.md 相对 PASS 语义：
- 两侧 pytest 在同 OS/同依赖/同隔离状态下**完整运行**，JUnit 均存在、非空、可解析 ✓
- 共享失败 137 个 nodeid 相同且归一化语义指纹一致（mismatch=0）✓
- candidate-only 2 个均**不构成新增代码失败**：
  - known_environment（代理变量环境敏感，无代理环境通过；实现行为 main 同源 2149 行）
  - known_flaky（3/3 重跑通过）
- main-only 1 个（cand 通过）不构成回归

**边界声明**：known_environment / known_flaky 分类的**最终批准权在 Codex**。若 Codex 不批准任一分类，
对应 candidate-only 失败将按"新增失败"计入 → 改判 GATE1_FAIL。本报告不宣称全仓 GREEN、不宣称可 merge。

## 六、硬约束核对

- 未改 STATUS/Gate2 记录/冻结 SHA 说明；未改 TUN/Clash/OpenCodex/10100/240s watchdog；未删旧 evidence
  （`20260804-002936-5c8b9ce-grok-gate1-r2`、`20260804-145050-5c8b9ce-grok-gate1-proxy-fix` 原样保留）；
  未用真实凭据（本报告全 `[REDACTED]` 无凭据）；未 commit/push/merge/tag；**未改动 Grok 的 proxy 修复实现**

## 七、证据文件

| 证据 | 路径 |
|------|------|
| 本报告 | `F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\HERMES_DIAGNOSIS_GATE1_20260804-145343-5c8b9ce-hermes-gate1-r3.md` |
| RUN_ID / env | `C:\Users\Administrator\omnigent-diagnostics\20260804-145343-5c8b9ce-hermes-gate1-r3\RUN_ID.txt` / `env.txt` |
| pytest JUnit ×2 | `...\main-pytest.xml` / `cand-pytest.xml` |
| pytest 输出 ×2 | `...\main-pytest.txt` / `cand-pytest.txt` |
| fail-ids ×2 + 差集 | `...\main-fail-ids.txt` / `cand-fail-ids.txt` / `new-failures.txt`（手工重算） |
| 语义指纹 | `...\semantic_check.py` / `shared-fail-ids.txt` / `shared-semantic-summary.txt`（mismatch=0） |
| 分类实证 | `...\extract_new_failures.py`；无代理单测 + flaky 3/3 重跑输出（run 记录） |
| 截断现场 | `...\main-pytest-truncated-at-93pct.*` / `main-fail-ids-truncated.txt` |
| 验证链 | `...\verification-*.txt` + `verify-*-script.sh`（全部 ALL PASS） |
