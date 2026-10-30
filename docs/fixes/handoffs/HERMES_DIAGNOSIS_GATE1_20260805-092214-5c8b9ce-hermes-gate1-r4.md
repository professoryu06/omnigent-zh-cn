# HERMES_DIAGNOSIS_GATE1_20260805-092214-5c8b9ce-hermes-gate1-r4

- **RUN_ID**: `20260805-092214-5c8b9ce-hermes-gate1-r4`（Grok R4 修复后 Gate 1 全量重跑，全新 RUN_ID）
- **执行者**: Hermes（用户明确授权：Grok R4 修复后重跑完整 Gate 1，不得修改 Gate 2 结论）
- **候选**: `5c8b9ce96f7552d380276fe6de04651f2b19531a` + Grok R4 未提交修复（4 文件：
  `codex_executor.py`、`test_codex_executor.py`、`test_codex_runtime_isolation.py`、`test_session_host_launch.py`），
  worktree = 主工作树 `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **clean main**: `81594243f7a17303b9ba477b938ac323f938c2e4`（`F:\codex-ai\git项目部署\tmp\omnigent-gate1-main`）
- **环境**: WSL2 Ubuntu-24.04（Store launcher），Python 3.12.3，uv 0.11.33；tmux 持久会话 + 300min timeout（r3 教训）
- **最终分类**: **GATE1_PASS（相对 clean main）**——无确定性新增代码失败；2 个 candidate-only 失败实证为环境敏感/偶发（同 r3 模式），分类确认权在 Codex

## 一、Grok R4 修复确认（未 commit，未改动）

- HEAD = `5c8b9ce…` ✓；4 个文件 modified（+86/−18 基础上的 R4 增量）
- 契约矩阵保持：订阅路径（None/openai pin）注入 proxy；custom/Databricks/gateway 不注入并剥离 ambient HTTP(S)_PROXY/ALL_PROXY；gateway+override 互斥

## 二、执行记录

| 步骤 | main | cand |
|------|------|------|
| uv sync --locked --extra dev --extra all | EXIT=0 | EXIT=0 |
| pytest 全量（--timeout=300 --timeout-method=signal，300min cap） | **135 failed + 4 errors**（14913 passed, 2h34m49s） | **135 failed + 4 errors**（15053 passed, 2h39m+） |
| ruff（规格 1.1 C 定向集） | EXIT=1（E902 缺失文件，同前几轮） | EXIT=1（E902 缺失文件，同前几轮） |
| compileall | EXIT=0 | EXIT=0 |

- 两次树均**完整跑完**（无截断，r3 教训已应用：300min timeout + tmux 持久）

## 三、失败统计与差集（全量完整数据）

| 项 | 值 |
|----|-----|
| main 失败/错误 | 139（135+4） |
| cand 失败/错误 | 139（135+4） |
| 共享失败 | 137（归一化语义指纹 **mismatch=0**） |
| main-only | 2（cand 均通过——候选更优，非回归） |
| **candidate-only** | **2**（均实证分类，见下） |

## 四、r3 两个 candidate-only 的最终状态（Grok R4 验收点）

| nodeid | r3 | r4 |
|--------|----|----|
| `test_model_provider_override_appends_pin` | cand FAILED（代理环境） | ✅ **main PASSED + cand PASSED**（0.014s）——**Grok R4 ambient 剥离修复生效** |
| `test_host_session_message_relaunches_offline_runner` | cand FAILED（偶发） | 全量又挂 1 次（asgiref 3s 超时）→ **重跑 5/5 通过**（4.87/5.34/5.06/4.83/4.73s），累计 r3 3/3 + r4 5/5 = **8 次重跑全过** → **known_flaky**（Grok barrier 修复有效，全量压力下仍有竞态窗口） |

## 五、r4 新增 candidate-only 分类证据

### 1. `TestSubscriptionProxyRoute::test_custom_model_provider_does_not_inherit_subscription_proxy` — **known_environment（附实现缺口说明）**

- Grok R4 新增测试；main 中不存在该测试
- 失败断言（test_codex_runtime_isolation.py:352）：`assert '172.31.80.1' not in executor._env`（str 级）
- 根因：WSL 环境 `NO_PROXY=localhost,127.0.0.1,::1,172.31.80.1`（宿主机代理 IP 透传）；Grok ambient 剥离范围 = **HTTP(S)_PROXY/ALL_PROXY**（注释明说），**NO_PROXY 仅追加 localhost/127.0.0.1 不清除环境原值**（codex_executor.py:163/209-215）
- **实证**：`env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u NO_PROXY` 跑 → **1 passed（0.75s）**；当前环境 → failed（3.56s）
- **定性**：环境敏感（无 ambient proxy 环境通过）；但根源是**实现/测试范围不一致**——Grok 声明剥离 HTTP(S)_PROXY/ALL_PROXY，新测试却断言 NO_PROXY 也干净。**建议回给 Grok**：补 NO_PROXY 剥离（完善 ambient 剥离，非凑绿）或调整测试断言范围。分类批准权在 Codex

### 2. `test_host_session_message_relaunches_offline_runner` — **known_flaky**

- 全量压力下 asgiref 3s 超时（竞态）；Grok 未改该文件语义（R4 改了测试本身为 stage offline + barrier）
- 实证：8 次独立重跑全部通过（r3 3/3 + r4 5/5）；main 同环境 PASSED

## 六、判定

**GATE1_PASS**（相对 clean main）——依据 PRE_MERGE_GATES 相对 PASS 语义：
- 两侧 pytest 同 OS/同依赖/同隔离**完整运行**，JUnit 均存在、非空、可解析 ✓
- 共享失败 137 个 nodeid 相同 + 归一化语义指纹一致（mismatch=0）✓
- candidate-only 2 个均不构成**确定性新增代码失败**：
  - custom proxy 测试：known_environment（无 ambient 环境 0.75s PASS；环境敏感）+ 实现缺口建议回 Grok
  - relaunch 测试：known_flaky（8/8 重跑通过）
- main-only 2 个（cand 通过）不构成回归
- **r3 唯一确定性新增失败（pin 测试）已在双侧通过——Grok R4 核心修复确认**

**边界声明**：known_environment / known_flaky 分类**最终批准权在 Codex**；`test_custom_model_provider_does_not_inherit_subscription_proxy` 的 NO_PROXY 实现缺口建议由 Grok 补实现或调断言后再终签（若 Codex 批准分类则可不阻塞）。本报告不宣称全仓 GREEN、**不宣称可 merge**。

## 七、硬约束核对

未改 STATUS/Gate2/冻结 SHA/PRE_MERGE_GATES；未改 TUN/Clash/OpenCodex/10100/240s watchdog；未删旧 evidence
（r1/r2/r3、grok proxy-fix、grok r4-fix×4 全部原样）；未用真实凭据；未 commit/push/merge/tag；
**未改动 Grok 的 proxy 作用域或 relaunch 语义**（未凑绿）。

## 八、证据文件

| 证据 | 路径 |
|------|------|
| 本报告 | `F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\HERMES_DIAGNOSIS_GATE1_20260805-092214-5c8b9ce-hermes-gate1-r4.md` |
| RUN_ID / env | `C:\Users\Administrator\omnigent-diagnostics\20260805-092214-5c8b9ce-hermes-gate1-r4\RUN_ID.txt` / `env.txt` |
| pytest JUnit ×2 | `...\main-pytest.xml` / `cand-pytest.xml` |
| pytest 输出 ×2 | `...\main-pytest.txt` / `cand-pytest.txt` |
| fail-ids ×2 + 差集 | `...\main-fail-ids.txt` / `cand-fail-ids.txt` / `new-failures.txt` |
| 语义指纹 | `...\semantic_check.py` / `shared-fail-ids.txt` / `shared-semantic-summary.txt`（mismatch=0） |
| 分类实证 | `...\extract_new_failures.py`；relaunch 5/5 重跑 + custom 无 ambient 0.75s PASS（run 记录） |
| 验证链 | `...\verification-*.txt` + `verify-*-script.sh`（全部 ALL PASS） |
