# GROK_FIX_GATE1_R4_20260805-085331-5c8b9ce-grok-gate1-r4-fix

- **RUN_ID**: `20260805-085331-5c8b9ce-grok-gate1-r4-fix`
- **执行者**: Grok
- **候选 HEAD**: `5c8b9ce96f7552d380276fe6de04651f2b19531a`（未 commit / push / merge / tag）
- **工作树**: candidate review worktree（含 R3 前 Grok proxy scope 修复 + 本轮 R4 修复）
- **证据根**: `C:\Users\Administrator\omnigent-diagnostics\20260805-085331-5c8b9ce-grok-gate1-r4-fix\`
- **本报告不声称 Gate 1 PASS**；完整 Gate 1 由 Hermes 用新 RUN_ID 在 clean main × candidate 双 worktree 重跑。

## 一、R3 暴露的两个 candidate-only 问题

| # | 失败 | R3 分类 | 本轮处理 |
|---|------|---------|----------|
| 1 | `tests.inner.test_codex_executor::test_model_provider_override_appends_pin` | known_environment（WSL 宿主 `HTTP(S)_PROXY` 透传） | **实现 + 测试双修** |
| 2 | `tests.server.integration.test_session_host_launch::test_host_session_message_relaunches_offline_runner` | known_flaky（异步 relaunch 时序） | **测试同步硬化**（非生产语义变更） |

## 二、问题一：Codex proxy 环境敏感

### 根因
1. R2 修复将 subscription proxy 限定到 `None` / `openai` pin；Databricks/custom 只 pin。
2. R3 新增断言 `HTTPS_PROXY not in executor._env` 在**干净环境**通过，但在 WSL 宿主透传 `HTTP_PROXY=http://172.31.80.1:17892` 时失败。
3. `_clean_codex_env` 仍会把 ambient `HTTP_*` / `HTTPS_*` / `ALL_PROXY` 放进 child env；非订阅路径此前**不会**调用 `_configure_codex_subscription_proxy` 覆盖/剥离它们。

### 产品契约（保留并加强）
| 路径 | gateway | model_provider_override | subscription proxy | ambient host proxy |
|------|---------|-------------------------|--------------------|--------------------|
| 默认订阅 | F | None | YES（env + features.network_proxy + network_proxy.proxy_url） | 被受控 proxy 替换 |
| openai pin | F | openai | YES + pin | 被受控 proxy 替换 |
| Databricks/custom | F | 非 openai | NO（仅 pin） | **剥离** |
| gateway | T | None | NO | **剥离** |
| gateway + override | T | any | OSError 互斥 | — |

### 修改
**生产** `omnigent/inner/codex_executor.py`：
- 订阅路径：`_configure_codex_subscription_proxy`（不变）
- **else**（custom / gateway）：显式 `pop` 全部 `_CODEX_PROXY_ENV_KEYS`，避免 ambient 宿主代理伪装成路由

**测试**：
- `tests/inner/test_codex_executor.py`：`_isolate_codex_proxy_env` 固定/清理代理环境；pin-only / openai pin / gateway 互斥；新增 `test_custom_provider_strips_ambient_host_proxy`（模拟 172.31.80.1:17892）
- `tests/inner/test_codex_runtime_isolation.py`：gateway / custom 在 ambient 存在时也必须无 proxy env 与无 network_proxy overrides

未通过“放宽断言 / 删除断言 / 删除覆盖测试”凑绿。

## 三、问题二：session host relaunch 异步竞态

### 诊断
- 生产 `post_event` relaunch 分支逻辑与 main 对齐：`grace → _launch_runner_on_host → wait runner`。
- 原测试用 `set_runner_client(None)` + 并发 `_wait_for_launch(budget_s=5)` + 立即 cancel post。
- 全仓负载下观察窗口与 post 路由存在竞态；单独 3/3 通过、全仓偶发失败 → **测试同步问题为主**，非 Gate2/生产语义回归。
- 未改 `sessions.py` 生产 relaunch 语义；未改 TUN/Clash/OpenCodex/10100/240s。

### 修改
`tests/server/integration/test_session_host_launch.py::test_host_session_message_relaunches_offline_runner`：
1. `monkeypatch` grace = 0.0（保持）
2. **stage** `_get_runner_client` 恒返回 `None`（不依赖全局 runner 状态）
3. 并发 `_serve_one_launch(..., launched)` 作为 **可观察 barrier**（收 launch 帧并 ACK result）
4. `asyncio.wait(..., FIRST_COMPLETED, timeout=15)` 等待 barrier，再 cancel post
5. 仍断言：launch 帧 workspace、runner_id 旋转

无盲目 sleep、无限延长 timeout。

## 四、验证（本机；WSL 本会话不可用）

平台：Windows + `uv` + CPython 3.12.13（omnigent-python-runtime，含 `_sqlite3`）

| 套件 | 结果 |
|------|------|
| proxy/model-provider 定向（13） | **PASS** |
| 同上 + ambient `HTTP(S)_PROXY=http://172.31.80.1:17892` | **PASS** |
| `test_host_session_message_relaunches_offline_runner` ×10 | **0/10 fail** |
| host_launch `-k relaunch or offline or stopped_host` | **6 passed** |
| `test_codex_runtime_isolation` + `test_session_host_launch` 全模块 | **40 passed** |

证据文件：
- `proxy-directed.txt` / `proxy-with-ambient.txt`
- `relaunch-x10.txt` / `relaunch-suite.txt` / `bug-regression.txt`
- `fix.diff` / `cand-HEAD.txt` / `cand-status.txt` / `exits-final.txt`

## 五、未改动（硬约束）
- Gate 2 记录 / 冻结 SHA / STATUS
- TUN / Clash / OpenCodex / 10100 / 240s watchdog
- 旧 evidence（r1/r2/r3 / proxy-fix）未删
- PRE_MERGE_GATES 门槛未放宽
- 无 commit / push / merge / tag
- 凭据一律 `[REDACTED]`

## 六、修改文件清单
1. `omnigent/inner/codex_executor.py` — 非订阅路径剥离 ambient proxy
2. `tests/inner/test_codex_executor.py` — 环境隔离 + ambient 覆盖
3. `tests/inner/test_codex_runtime_isolation.py` — 矩阵 ambient 断言
4. `tests/server/integration/test_session_host_launch.py` — relaunch 同步 barrier

## 七、交给 Hermes
用**全新 RUN_ID** 在 clean main 与 candidate 双 worktree 重跑完整 Gate 1。  
候选 worktree 须保留本报告列出的未提交改动（勿 reset）。  
期望：上述两个 candidate-only nodeid 不再出现在 new-failures；**不要**据此在本报告中宣称 Gate 1 PASS。