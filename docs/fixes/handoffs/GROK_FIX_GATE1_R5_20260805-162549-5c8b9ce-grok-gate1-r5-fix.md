# GROK_FIX_GATE1_R5_20260805-162549-5c8b9ce-grok-gate1-r5-fix

- **RUN_ID**: `20260805-162549-5c8b9ce-grok-gate1-r5-fix`
- **执行者**: Grok
- **候选 HEAD**: `5c8b9ce96f7552d380276fe6de04651f2b19531a`（**未** commit / push / merge / tag）
- **工作树**: candidate review worktree（含 R2–R4 未提交修复 + 本轮 R5）
- **证据根**: `C:\Users\Administrator\omnigent-diagnostics\20260805-162549-5c8b9ce-grok-gate1-r5-fix\`
- **r4 evidence（保留）**: `C:\Users\Administrator\omnigent-diagnostics\20260805-092214-5c8b9ce-hermes-gate1-r4\`
- **本报告明确不得宣称 Gate 1 PASS**；完整 Gate 1 由 Hermes 用全新 RUN_ID 在 clean main × candidate 双 worktree 重跑。

## 一、r4 暴露问题与结论摘要

| # | 失败 | 根因 | 本轮处理 |
|---|------|------|----------|
| 1 | `TestSubscriptionProxyRoute::test_custom_model_provider_does_not_inherit_subscription_proxy` | ambient `NO_PROXY` 含 `172.31.80.1` 未剥离；实现只 pop HTTP(S)/ALL_PROXY | **生产 + 测试**补齐 NO_PROXY 契约 |
| 2 | `test_host_session_message_relaunches_offline_runner` | 测试 helper `receive_output(timeout=3.0)` 在全仓压力 quiet gap 上抛 asgiref TimeoutError | **测试同步**（overall budget + Event barrier）；**未改生产 relaunch 语义** |

## 二、NO_PROXY 清理契约（产品）

| 路径 | gateway | model_provider_override | HTTP(S)/ALL_PROXY | NO_PROXY / no_proxy |
|------|---------|-------------------------|-------------------|---------------------|
| 默认订阅 | F | None | 受控 subscription proxy（默认 `http://127.0.0.1:7897` 或 `OMNIGENT_CODEX_PROXY`） | **仅** `localhost,127.0.0.1,::1`（**替换** ambient，不 merge） |
| openai pin | F | openai | 同上 + pin | 同上 loopback only |
| Databricks/custom | F | 非 openai | **全部剥离** | **全部剥离**（不重建） |
| gateway | T | None | **全部剥离** | **全部剥离** |
| gateway + override | T | any | OSError 互斥 | — |

**所有路径禁止**把宿主代理 IP `172.31.80.1`、其它宿主代理地址带入 Codex child env。  
订阅路径的 proxy URL 本身可以是 `127.0.0.1:7897`（产品默认），但 **NO_PROXY 不得** 含该 host 以外的 ambient 条目，也不得 merge WSL 宿主 `NO_PROXY`。

### 是否修改生产代码
**是** — `omnigent/inner/codex_executor.py`：
- 新增 `_strip_ambient_proxy_env`：剥离 `HTTP_PROXY/HTTPS_PROXY/ALL_PROXY` 及小写，以及 `NO_PROXY/no_proxy`
- `_configure_codex_subscription_proxy`：先 strip，再注入受控 proxy，`NO_PROXY` **只**设为 product loopback（不再 merge ambient）
- non-subscription 分支调用 `_strip_ambient_proxy_env`（覆盖 custom/gateway）

## 三、relaunch 竞态根因

**判定：测试同步缺陷为主，非生产 relaunch 语义竞态。**

- 生产路径：`post_event` → grace=0 → `_launch_runner_on_host`（先 `replace_runner_id` + send frame，再 wait result）逻辑与 main 一致。
- 失败形态：asgiref `ApplicationCommunicator.receive_output(timeout=3.0)` 在 quiet >3s 时抛 `TimeoutError`。
- R4 barrier 用了 `_serve_one_launch`，其 **硬编码 3s 单次 receive**；全仓压力下 post/DB 调度使 launch frame 晚于 3s 到达 → barrier 失败，即使外层 15s wait 也救不回。
- 独立重跑 8/8、本轮 20/20 通过；未改 `sessions.py` / `runner/app.py` 生产逻辑。

### 测试修复
- `_serve_one_launch`：改为 **overall_timeout_s + poll_timeout_s** 事件驱动轮询；quiet slice `continue`，有限总预算，非盲目 sleep / 无限 timeout。
- offline relaunch 测试：`asyncio.Event` 完成 barrier + 显式 ACK launch result。

## 四、验证结果（Windows；sqlite 可用 CPython 3.12.13）

| 套件 | 结果 |
|------|------|
| proxy/model-provider 定向 | **EXIT=0** |
| 同上 + 完整 ambient（HTTP(S)/ALL/NO_PROXY 大小写 + 172.31.80.1） | **EXIT=0** |
| `test_codex_runtime_isolation` 全模块 | **EXIT=0** |
| relaunch offline ×20 | **0/20 fail** |
| isolation + host_launch 回归 | **EXIT=0** |
| compileall（改动模块） | **EXIT=0** |

未跑完整 Gate 1 / Gate 2 / full-run。

证据文件：`proxy-directed.txt`、`proxy-with-ambient-full.txt`、`isolation.txt`、`relaunch-x20.txt`、`bug-regression.txt`、`compileall.txt`、`fix.diff`、`exits.txt`。

## 五、candidate-only 风险

- r4 两个 candidate-only 的 **确定性根因** 已在本轮处理。
- 仍可能的残余风险：
  1. 其它未覆盖的宿主环境变量污染（若未来再扩展 allowlist）
  2. 全仓压力下 **其它** asgiref 3s 硬超时 helper（本轮只硬化了 `_serve_one_launch` 与该 relaunch 用例）
- **不得**据此宣称 Gate 1 PASS 或可 merge。

## 六、修改文件
1. `omnigent/inner/codex_executor.py` — NO_PROXY 契约 + ambient strip
2. `tests/inner/test_codex_executor.py` — ambient NO_PROXY 覆盖
3. `tests/inner/test_codex_runtime_isolation.py` — 矩阵 + WSL NO_PROXY 断言
4. `tests/server/integration/test_session_host_launch.py` — launch barrier overall budget + Event

**未改**：`sessions.py`、`runner/app.py`、STATUS、Gate2、PRE_MERGE_GATES、冻结 SHA、TUN/Clash/OpenCodex/10100/240s。

## 七、硬约束
- 未删旧 evidence；未 commit/push/merge/tag；凭据 `[REDACTED]`。

## 八、交给 Hermes
用**全新 RUN_ID** 在 clean main 与 candidate 双 worktree 重跑完整 Gate 1。  
候选须保留本报告所列未提交改动（勿 reset）。  
期望 new-failures 不再含上述两个 nodeid；**不要**在本报告层宣称 Gate 1 PASS。