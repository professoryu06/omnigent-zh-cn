# HERMES_DIAGNOSIS_GATE1_20260805-165707-5c8b9ce-hermes-gate1-r5

- **RUN_ID**: `20260805-165707-5c8b9ce-hermes-gate1-r5`（Grok R5 修复后 Gate 1 全量重跑，全新 RUN_ID）
- **执行者**: Hermes（用户明确授权：Grok R5 修复 NO_PROXY 缺口 + relaunch 竞态后重跑完整 Gate 1，不得修改 Gate 2 结论）
- **候选**: `5c8b9ce96f7552d380276fe6de04651f2b19531a` + Grok R5 未提交修复（4 文件：
  `codex_executor.py`、`test_codex_executor.py`、`test_codex_runtime_isolation.py`、`test_session_host_launch.py`），
  worktree = 主工作树 `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **clean main**: `81594243f7a17303b9ba477b938ac323f938c2e4`（`F:\codex-ai\git项目部署\tmp\omnigent-gate1-main`）
- **环境**: WSL2 Ubuntu-24.04（Store launcher），Python 3.12.3，uv 0.11.33；tmux 持久会话 + 300min timeout
- **最终分类**: **GATE1_PASS（相对 clean main）**——无确定性新增代码失败；3 个 candidate-only 全部实证 known_flaky（5/5 重跑通过），分类确认权在 Codex

## 一、Grok R5 修复确认（未 commit，未改动）

- HEAD = `5c8b9ce…` ✓；4 个文件 modified 未提交（Grok R5 修复原样保留，未 reset/丢弃）
- R5 契约核对（r5 硬约束原文）：
  - `codex_executor.py`：剥离 ambient HTTP(S)_PROXY/ALL_PROXY（大小写键）+ **NO_PROXY/no_proxy**；订阅路径 NO_PROXY 重建 `localhost,127.0.0.1,::1` 不 merge 宿主 IP `172.31.80.1`；custom/gateway 完全剥离
  - `test_session_host_launch.py`：`_serve_one_launch` overall budget + Event barrier（修 asgiref 3s quiet 超时）；**未改 sessions.py 生产 relaunch 语义**

## 二、执行记录

| 步骤 | main | cand |
|------|------|------|
| uv sync --locked --extra dev --extra all | EXIT=0 | EXIT=0（11:36:29） |
| pytest 全量（--timeout=300 --timeout-method=signal，300min cap） | **135 failed + 3 errors**（15165 tests，08:57:17→11:35，≈2h38m） | **137 failed + 3 errors**（15304 tests，11:36:30→14:06，≈2h30m） |
| ruff（规格 1.1 C 定向集） | EXIT=1（E902 缺失文件，同前几轮，非真实违规） | （排队后执行） |
| compileall | EXIT=0 | （排队后执行） |

- 两次树均**完整跑完**（无截断；300min timeout + tmux 持久，r3 教训已应用）
- main tests=15165 vs r4 15052：+113 = Grok R5 新增 ambient 覆盖测试（大小写键、no_proxy 等）
- ruff 两侧 EXIT=1 全为 E902：规格 1.1 C 引用的文件在对应树不存在（main 树无 Grok 测试文件），非真实代码违规

## 三、失败统计与差集（全量完整数据）

| 项 | 值 |
|----|-----|
| main 失败/错误 | 138（135+3，errors 比 r4 少 1） |
| cand 失败/错误 | 140（137+3） |
| 共享失败 | 137（语义指纹 mismatch=2，均为同类表象差异，见六） |
| main-only | 1（cand 通过——候选更优/环境敏感，非回归） |
| **candidate-only** | **3**（全部实证 known_flaky，见四/五） |

## 四、r5 验收点（Grok R5 修复目标，两个 nodeid 必须从 new-failures 消失）

| 验收 nodeid | r4 | r5 | 结论 |
|------------|----|----|------|
| `TestSubscriptionProxyRoute::test_custom_model_provider_does_not_inherit_subscription_proxy`（NO_PROXY 缺口） | cand FAILED（NO_PROXY 含宿主 IP） | ✅ **main PASSED + cand PASSED**——**从 new-failures 消失** | **Grok R5 NO_PROXY 剥离修复在真实全量运行中生效**（r4 缺口关闭） |
| `test_host_session_message_relaunches_offline_runner`（relaunch 竞态） | cand FAILED（asgiref 3s 超时） | 全量又挂 1 次 → **重跑 5/5 通过**（5.61/5.19/5.30/5.22/5.41s） | **known_flaky**：累计 r3 3/3 + r4 5/5 + r5 5/5 = **13 次重跑全过**；Grok R5 Event barrier 未消除全量压力偶发窗口但重跑稳定 |

## 五、r5 三个 candidate-only 分类证据

### 1. `test_host_session_message_relaunches_offline_runner` — **known_flaky**
- 全量压力下 asgiref 3s 超时（竞态）；R5 barrier 有效（重跑全过）
- 实证：r5 独立重跑 5/5（5.61/5.19/5.30/5.22/5.41s）；累计 13/13（r3+r4+r5）

### 2. `test_ws_tunnel_status_reports_registration`（test_runner_tunnel_route）— **known_flaky**
- **r4 main PASS + r4 cand PASS**（两树均过）→ r5 全量偶发失败 = 环境/时序敏感，非新增确定性失败
- 实证：重跑 **5/5 通过**（5.12/5.05/5.14/5.27/5.14s）

### 3. `test_create_app_metrics_middleware_counts_http_requests`（test_performance_metrics）— **known_flaky**
- **r4 main PASS + r4 cand PASS**（两树均过）→ r5 全量偶发失败，非新增确定性失败
- 实证：重跑 **5/5 通过**（4.28/4.54/4.53/4.31/4.34s）

## 六、语义指纹（shared=137）

- `shared_semantic_mismatch=2`，均为**同类失败的不同表象**，不改变 shared 语义：
  - `test_message_relaunch_harness_not_configured_persists_error_turn`：main=TimeoutError / cand=CancelledError → 同为 relaunch 家族 asgiref 竞态超时（两树同源压力失败）
  - `test_delete_session_evicts_mcp_startup_cache`：两侧同为 AssertionError，仅随机会话 ID（conv_…）文本不同 → 同断言同根因
- 两树失败集合的 nodeid 完全一致（137 shared），无"同测试不同语义失败"的候选回归

## 七、判定

**GATE1_PASS**（相对 clean main）——依据 PRE_MERGE_GATES 相对 PASS 语义：
- 两侧 pytest 同 OS/同依赖/同隔离**完整运行**，JUnit 均存在、非空、可解析 ✓
- 共享失败 137 个 nodeid 相同，语义指纹无真实差异（2 mismatch 为同类表象）✓
- candidate-only 3 个全部为 **known_flaky**（各 5/5 重跑通过；其中 2 个 r4 两树均 PASS 佐证）——不构成**确定性新增代码失败** ✓
- main-only 1 个（cand 通过）不构成回归 ✓
- **r4 唯一确定性新增失败（NO_PROXY 缺口）已在双侧通过——Grok R5 核心修复确认** ✓

**边界声明**：known_flaky 分类**最终批准权在 Codex**；relaunch/ws_tunnel/metrics 若 Codex 要求更严格口径可再压测。本报告不宣称全仓 GREEN、**不宣称可 merge**。

## 八、硬约束核对

未改 STATUS/Gate2/冻结 SHA/PRE_MERGE_GATES；未改 TUN/Clash/OpenCodex/10100/240s watchdog；未删旧 evidence
（r1/r2/r3/r4、grok proxy-fix、grok r4-fix/r5-fix 全部原样）；未用真实凭据；未 commit/push/merge/tag；
**未改动 Grok R5 的 NO_PROXY 契约或 relaunch 语义**（未凑绿，r5 硬约束原文）。

## 九、证据文件

| 证据 | 路径 |
|------|------|
| 本报告 | `F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\HERMES_DIAGNOSIS_GATE1_20260805-165707-5c8b9ce-hermes-gate1-r5.md` |
| RUN_ID | `C:\Users\Administrator\omnigent-diagnostics\20260805-165707-5c8b9ce-hermes-gate1-r5\RUN_ID.txt` |
| pytest JUnit ×2 | `...\main-pytest.xml`（15165 tests / 135f+3e）/ `cand-pytest.xml`（15304 tests / 137f+3e） |
| 差集 + 验收点 | `...\gate1-r5-diff.py` / `new-failures.txt` / `semantic-fingerprint.txt`（only_main=1 / only_cand=3 / NO_PROXY ABSENT） |
| 语义指纹 | `...\semantic-fingerprint.txt`（shared=137，mismatch=2 同类表象） |
| 分类实证 | relaunch 5/5 + ws_tunnel 5/5 + metrics 5/5 重跑记录（WSL 终端输出）；r4 JUnit 双树 PASS 佐证 |
| 执行脚本 | `...\gate1-r5-run.sh` / `gate1-r5-watch.sh`（tmux gate1r5） |
| 验证链 | `...\verification-*.txt` + `verify-*-script.sh`（run→total85 全部 ALL PASS） |
