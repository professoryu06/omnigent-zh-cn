# GROK_FIX_RELAUNCH_RACE_20260806-103154-5c8b9ce-grok-relaunch-race-fix

- **RUN_ID**: `20260806-103154-5c8b9ce-grok-relaunch-race-fix`
- **执行者**: Grok
- **候选 HEAD**: `5c8b9ce96f7552d380276fe6de04651f2b19531a`（**未** commit）
- **证据根**: `C:\Users\Administrator\omnigent-diagnostics\20260806-103154-5c8b9ce-grok-relaunch-race-fix\`
- **对照 r6 full-run**: `C:\Users\Administrator\omnigent-diagnostics\20260805-164315-5c8b9ce-hermes-gate1-r6\`
- **本报告不得写成 Gate 1 PASS / Gate 2 PASS / 可 merge**

## 1. 根因最终判断

**主因：测试同步缺陷（asgiref 帧观察 + grace/connect wait 在全仓负载下不稳定），不是生产 relaunch 逻辑必现漏触发。**

证据链：

| 来源 | 现象 |
|------|------|
| r6 full-run | cand 失败：`launch_frame is None`；日志仍有 `Waiting up to 3.0s for host-bound runner…`（grace 未按测试意图短路） |
| r6 定向 20× | 20/20 通过 → 非确定性逻辑错误 |
| 生产 `post_event` | `runner_client is None and conv.host_id` → `_launch_runner_on_host` 语义正确 |
| 旧测试 | 仅靠 host `receive_output` 观察帧；grace=0 monkeypatch 在 full-suite 日志中仍见 3.0s wait；post 后 cancel 与 asgiref 静默窗口竞态 |

分类：**测试等待/Mock barrier 不稳定**（为主）。生产在 offline + host-bound 路径上会触发 relaunch；全仓压力下测试未能可靠观察到。

未发现必须改 `sessions.py` / `runner/app.py` 才能保证“会调用 `_launch_runner_on_host`”的确定性生产漏触发。

## 2. 修改了哪些文件

| 文件 | 变更 |
|------|------|
| `tests/server/integration/test_session_host_launch.py` | 重写 `test_host_session_message_relaunches_offline_runner` 同步模型 |
| `omnigent/server/routes/sessions.py` | **未改** |
| `omnigent/runner/app.py` | **未改** |

## 3. 为什么不是简单加 sleep

修复手段：

1. **triggered Event**：wrap `_launch_runner_on_host`，进入生产 relaunch 即 `launch_triggered.set()`（与 asgiref 帧队列解耦）。
2. **frame Event**：并发 `_serve_one_launch(overall_timeout_s=20, poll_timeout_s=0.5)` ACK 帧；quiet slice 继续轮询，**有限总预算**，非无限 timeout。
3. **状态断言**：`runner_id` 旋转（replace_runner_id 完成语义）。
4. **短路 offline wait**：patch `_get_runner_client` 与 `_wait_for_runner_client` 恒返回 `None`，消除 grace 3s / connect 30s 在 suite 负载下的假死窗口（r6 日志中的 3.0s wait 正是此路径）。
5. `await asyncio.sleep(0)` 仅用于让 frame 接收 task 先被调度，**不是**等待业务时间。

禁止项核对：无盲目 `sleep(N)`、无无限 timeout、无“失败就重试凑绿”。

## 4. 触发/完成事件如何保证

| 信号 | 含义 | 实现 |
|------|------|------|
| **已触发** | 生产进入 relaunch | `launch_triggered` Event on `_launch_runner_on_host` 入口 |
| **已完成（帧）** | host 收到并 ACK `host.launch_runner` | `frame_seen` + `HostLaunchRunnerFrame` holder |
| **已完成（状态）** | session 绑定新 runner | `conv.runner_id != original` 且 `runner_token_` 前缀 |

断言顺序：先要求 `launch_triggered`，再要求 `launch_frame is not None`，再要求 runner_id 旋转。可区分：

- 未触发 → offline 分支未进；
- 触发但无帧 → 发送/asgiref 观察问题；
- 帧到但 id 未转 → replace 失败。

## 5. 验证结果

平台：Windows + uv + CPython 3.12.13（sqlite 可用）；代理 env 清空。未跑完整 Gate 1 / Gate 2。

| 套件 | 结果 |
|------|------|
| `test_host_session_message_relaunches_offline_runner` ×50 | **0/50 fail**；`launch_frame=None` / “did not fire” 信号 **0** |
| `tests/server/integration/test_session_host_launch.py` 全文件 | **EXIT=0** |
| + `test_host_session_binding.py` 定向 | **EXIT=0** |
| compileall（改动测试文件） | **EXIT=0** |

每次 ×50 独立 log：`relaunch-x50-logs/runNN.txt`（不覆盖）。

## 6. 是否仍出现 launch_frame=None

**定向 50× 中：否。**

## 7. 是否建议 Hermes 重跑完整 Gate 1

**是。** 本修复只证明 relaunch 用例在定向负载下稳定；full-suite 压力仍需 Hermes 用**全新 RUN_ID** 双树完整 Gate 1 验收。

建议 Hermes：

1. 保留本 worktree 未提交改动（含本文件 + 既有 R5 proxy 修复）；
2. `RUN_ID=YYYYMMDD-HHMMSS-5c8b9ce-hermes-gate1-r7` 重跑完整 Gate 1；
3. 重点看 `test_host_session_message_relaunches_offline_runner` 是否仍出现在 new-failures。

## 8. 硬约束

- 未改 STATUS / Gate2 / PRE_MERGE_GATES / 冻结 SHA  
- 未改 TUN / Clash / OpenCodex / 10100 / 240s  
- 未删旧 evidence  
- 未 commit / push / merge / tag  
- 凭据 [REDACTED]