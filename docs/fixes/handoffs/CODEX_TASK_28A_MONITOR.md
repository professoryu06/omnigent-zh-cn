# CODEX_TASK_28A — Codex TUI 启动期网络监控卡

## 角色

执行者只负责只读观察和证据整理，不是实现者。Codex 负责最终验收。

## 前置结论

- 阶段 27 机制结论暂按 `DIAG_CODEX_REMOTE_HANDSHAKE` 处理，但 `HERMES_DIAGNOSIS_27.md` 必须先统一“受控 RUN 已执行”与最终分类的矛盾。
- 受控 RUN 已证明同一 Codex CLI 0.144.4、argv、私有 `CODEX_HOME` 可以在约 8.65 秒建立 `thread/start`。
- 失败侧疑似是 `raw.githubusercontent.com` 启动期请求在 TUN fake-IP 下挂起约 58–63 秒，超过 Omnigent 的 30 秒 thread 等待窗口。

## 本卡唯一目标

在用户从 Omnigent Web UI 重试一次 Codex 会话时，判断当前问题属于：

1. `READY`：启动网络正常，30 秒内建立 `thread/start`；
2. `NETWORK_STALL`：启动期远程请求再次超过 30 秒；
3. `PROTOCOL_OR_LAUNCH`：远程请求正常，但 app-server ready 后仍无 TUI WebSocket/thread。

## 硬约束

- 不改源码、tests、STATUS、政策或配置。
- 不改 `~/.codex/config.toml`。
- 不开关或重配 TUN/Clash，不改代理规则。
- 不杀 OpenCodex，不动 10100。
- 不重跑 D0/D1/D2，不跑完整 Gate 2，不执行 full-run。
- 不删除旧 evidence；新 RUN 使用全新 RUN_ID。
- 凭据一律 `[REDACTED]`。

## 必须记录

### 1. 启动身份

- CLI 版本、绝对路径、size、SHA-256；
- 完整 argv（脱敏）；
- app-server 端口、TUI pane PID、app-server PID；
- `CODEX_HOME` 及 bridge 目录。

### 2. 时间线

至少记录：

- TUI 启动时间；
- `raw.githubusercontent.com` 解析/fake-IP/TCP/TLS/完成或超时；
- terminal probes 完成；
- app-server listening/readyz；
- WebSocket client connected；
- `thread/start` 或 `thread/started`；
- runner 等待开始、30 秒超时、cleanup；
- TUI pane 真实 PID 与退出码。

### 3. Clash/TUN 只读状态

- 记录 `raw.githubusercontent.com` 命中的现有规则、代理/直连和 fake-IP；
- 只能观察，禁止修改规则或切换模式。

### 4. Bridge 与 cleanup

- `state.json`、`server.json`、`startup_error.json` 的出现时间；
- cleanup 后 PID 是否 dead、端口是否释放、runtime 是否清理；
- evidence 仍存在；leak-scan 最后执行且 hits=0。

## 判定标准

### READY

- raw 请求完成且不超过 10 秒；
- probes 完成且不超过 10 秒；
- `thread/start`/`thread/started` 在 30 秒内出现；
- bridge 出现正常 state/server；
- 无 app-server 协议错误。

### NETWORK_STALL

- raw 或同类 Codex 启动远程请求超过 30 秒或无完成事件；
- app-server 已 ready，但 `thread/start` 缺失；
- 时间线明确落入 runner 的 30 秒等待窗口。

### PROTOCOL_OR_LAUNCH

- raw 请求和 probes 正常；
- app-server ready；
- 仍无 WebSocket client、`thread/start` 或 TUI 早退；
- 必须分离业务退出与 cleanup 退出。

## 交付

唯一仓库交付：

`docs/fixes/handoffs/HERMES_DIAGNOSIS_28A.md`

报告必须包含：

- RUN_ID、evidence 绝对路径、evidence 是否仍存在；
- 身份、时间线、Clash/TUN 只读状态、bridge、cleanup、leak-scan；
- 三分类中唯一分类及证据指针；
- 不得宣称 Gate 2 PASS、全仓 GREEN 或 mergeable；
- 若未发生用户重试，必须明确写 `DIAG_INCONCLUSIVE`，不得用历史证据代替本 RUN。

## 后续路由

- `READY`：由 Codex 另发单次 full-run 卡；
- `NETWORK_STALL`：由 Codex 另发域名级 Clash 规则卡，不先改 Omnigent 源码；
- `PROTOCOL_OR_LAUNCH`：由 Codex 另发产品侧启动韧性实施卡；
- `INCONCLUSIVE`：补齐缺失证据，不进行修复猜测。

