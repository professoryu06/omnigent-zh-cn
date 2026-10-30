# GROK_GATE1_RACE_OBSERVATION_20260806-001202-5c8b9ce-grok-gate1-race-obs

- **RUN_ID**: `20260806-001202-5c8b9ce-grok-gate1-race-obs`
- **性质**: 低成本定向观察（**不改代码**、不跑完整 Gate 1、不宣称 Gate 1 PASS）
- **执行者**: Grok
- **候选 HEAD**: `5c8b9ce96f7552d380276fe6de04651f2b19531a`（含既有未提交 R5 修复，本卡未再修改）
- **clean main HEAD**: `81594243f7a17303b9ba477b938ac323f938c2e4`
- **旧 full-run 只读参考**: `C:\Users\Administrator\omnigent-diagnostics\20260805-165707-5c8b9ce-hermes-gate1-r5\`
- **本证据根**: `C:\Users\Administrator\omnigent-diagnostics\20260806-001202-5c8b9ce-grok-gate1-race-obs\`

## 0. 环境说明

| 项 | 值 |
|----|-----|
| 请求平台 | WSL2 Ubuntu-24.04 / Python 3.12.3 / uv |
| **实际平台** | **Windows host**（本会话 `wsl.exe` 无可用发行版，无法进入 Ubuntu-24.04） |
| Python | CPython 3.12.13（omnigent-python-runtime，含 sqlite） |
| 依赖 | 各树独立 `UV_PROJECT_ENVIRONMENT` + `uv run` |
| 代理 | 固定剥离 `HTTP(S)_PROXY` / `ALL_PROXY` / `NO_PROXY` 大小写，避免宿主代理差 |
| 未改动 | TUN / Clash / OpenCodex / 10100 / 240s / 源码 / 测试 / STATUS / PRE_MERGE_GATES |

> 结论外推时请注意：本观察是 **孤立定向进程**，不是 full-suite 压力环境。full-run 下的 flaky 窗口可能仍存在。

## 1. 三个测试 × 20 次成功率（candidate vs main）

| 测试 | cand first directed | cand 20× | main first directed | main 20× | 成功率差异 |
|------|---------------------|----------|---------------------|----------|------------|
| `test_host_session_message_relaunches_offline_runner` | PASS (in 3-test batch 8.08s) | **20/20** (avg ~4.95s) | PASS (batch 14.37s) | **20/20** (avg ~4.92s) | 无 |
| `test_ws_tunnel_status_reports_registration` | PASS | **20/20** (avg ~4.74s) | PASS | **20/20** (avg ~5.18s) | 无 |
| `test_create_app_metrics_middleware_counts_http_requests` | PASS | **20/20** (avg ~4.40s) | PASS | **20/20** (avg ~4.67s) | 无 |

明细 JSON：
- `cand/summary.json`、`main/summary.json`
- 每次完整 stdout：`cand/*__runNN.txt`、`main/*__runNN.txt`（**不覆盖**）
- 汇总：`combined-summary.json`

**本观察窗口内：0 次失败；无 TimeoutError / CancelledError / asgiref 3s 超时出现在定向重跑中。**

## 2. 是否仍存在确定性失败？

**在孤立 20× 定向重跑中：否。** 双侧 60/60 通过。

**对照 r5 full-run（只读）**：三例均为 **candidate-only 出现一次**（main 同环境 full-run 未挂这三例），且与全仓压力/调度相关，**不能**用“20 次通过”否定 full-run 压力下的偶发失败。

| 测试 | r5 full-run cand | r5 full-run main | 孤立 20× cand | 孤立 20× main |
|------|------------------|------------------|---------------|---------------|
| relaunch offline | FAIL 1× | PASS | 20/20 | 20/20 |
| ws_tunnel_status | FAIL 1× | PASS | 20/20 | 20/20 |
| metrics middleware | FAIL 1× | PASS | 20/20 | 20/20 |

## 3. 是否属于真实竞态？

**是（测试/时序敏感），不是确定性生产回归证据。**

### 3.1 relaunch offline
- **r5 失败形态**：`launch_frame is None` — barrier 未观察到 `host.launch_runner`；日志仍有 `Waiting up to 3.0s for host-bound runner…`（全仓路径上 grace 仍可能为 3s 或与其它测试交错）。
- **根因分类**：测试同步 / asgiref 静默窗口 / 全仓负载下 event-loop 延迟。R5 虽加 overall budget + Event，**全仓压力仍偶发** → load-dependent flaky。
- **孤立 20×**：双侧全绿 → 无确定性实现断点。

### 3.2 ws_tunnel_status_reports_registration
- **r5 失败形态**：`_wait_until_registered` 中 `await asyncio.sleep(0.01)` 被 `CancelledError` → 包装为 `TimeoutError`（asyncio timeout 取消 future 的标准链）。
- **根因分类**：注册轮询 + 超时取消竞态；典型 flaky，**非**业务断言失败。
- **孤立 20×**：双侧全绿。

### 3.3 metrics middleware `requests_last_1s`
- **r5 失败形态**：`assert after.requests_last_1s >= 1` 实际为 `0`，同时 `total_started/completed` 已 +1。
- **根因分类**：**1 秒滑动窗口**与测试执行时序竞态（请求已计数 total，但 last_1s 桶边界/时钟导致 0）。测试同步脆弱，非 HTTP 中间件未接线。
- **孤立 20×**：双侧全绿。

## 4. 是否需要修改生产代码？

**当前证据不支持“必须改生产代码才能消掉这三例”**：
- main 与 cand 孤立定向行为一致（20/20）；
- full-run 失败形态是 timeout/cancel/窗口计数，不是稳定业务错误。

若后续 full-run 仍高频挂，优先：
1. **测试同步**（barrier、注册等待、metrics 断言改 `total_*` 或固定时钟）；
2. 仅当压力下生产路径可复现丢失 launch/注册时，再考虑生产最小加固。

**本卡未改生产代码。**

## 5. 是否只需调整测试同步？

**倾向：是（优先测试层）**。

| 测试 | 建议方向（观察结论，非本卡实施） |
|------|----------------------------------|
| relaunch | 保持 Event barrier；确保 grace=0 生效；避免与 3s 单次 receive 竞态（R5 已部分做） |
| ws_tunnel_status | 用 registry Event/waiter 替代 sleep 轮询+硬超时，或放宽/可观测的注册完成信号 |
| metrics | 断言 `total_started/completed` 而非易碎的 `requests_last_1s`，或注入可控时钟 |

## 6. 对 Gate 1 的影响

| 问题 | 回答 |
|------|------|
| 能否把 20× 通过写成 Gate 1 PASS？ | **不能** |
| 三例是否证明 candidate 确定性回归？ | **不能**；更像 full-suite flaky / 时序敏感 |
| 是否消除 candidate-only 风险？ | **未消除 full-run 风险**；仅说明孤立可绿 |
| 下一步 | Hermes 用**全新 RUN_ID** 在 clean main × candidate 重跑完整双树 Gate 1；分类权在 Codex |

## 7. shared semantic mismatch 日志核对（只读 r5，不重跑 Gate 1）

### 7.1 relaunch 相关：TimeoutError vs CancelledError

r5 cand 日志中常见链（标准 asyncio 行为，**非**业务语义分叉）：

```text
except exceptions.CancelledError as exc:
    raise TimeoutError from exc
```

即：wait/timeout 取消 future 时先 `CancelledError`，再包装为 `TimeoutError`。  
`test_ws_tunnel_status_reports_registration` 在 r5 即表现为该链。  
`test_host_session_message_relaunches_offline_runner` 在 r5 主断言是 **AssertionError (launch_frame is None)**，stderr 侧伴有 3.0s grace wait 日志。

→ **shared fingerprint 若把 TimeoutError 与 CancelledError 判为不同语义，对这类链会过度敏感**；归一化应折叠为同一 timeout-cancel 家族。

### 7.2 `delete_session_evicts_mcp_startup_cache`：随机 session ID

r5 **两侧均失败**，形态相同，仅随机 ID 不同：

| 侧 | 断言 |
|----|------|
| cand | `assert 'conv_012ef4e9290b4515a2ae9d60f4b5a065' in {}` |
| main | `assert 'conv_321d57fc28124f409c0617d5f684d7af' in {}` |

均为：`session["id"]` **不在** `_session_mcp_startup_cache`（cache 为空 `{}`）。  
→ **共享失败**；指纹差异仅来自随机 `conv_*` 文本，**不是** candidate 新增回归。语义对比应归一化 session id。

证据摘录：`semantic-mismatch-notes.txt`。

## 8. 硬约束核对

- 未修改源码 / 测试 / STATUS / PRE_MERGE_GATES / Grok R5 修复内容  
- 未删旧 evidence  
- 未跑完整 Gate 1 / Gate 2 / full-run  
- 未 commit / push / merge / tag  
- 凭据未读取、报告无真实凭据  

## 9. 回答清单（强制）

1. **20 次成功率**：三测 cand/main 均为 **20/20**。  
2. **确定性失败**：定向窗口内 **无**。  
3. **真实竞态**：full-run 形态支持 **时序/负载 flaky**；孤立重跑不能复现。  
4. **是否需改生产**：**当前不必要**（证据不足）。  
5. **是否只需测同步**：**优先是**。  
6. **Gate 1 影响**：**不能**据此宣称 Gate 1 PASS；需 Hermes 全量双树重跑定案。