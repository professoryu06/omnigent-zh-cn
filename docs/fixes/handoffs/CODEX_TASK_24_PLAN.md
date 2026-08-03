# CODEX_TASK_24_PLAN — Windows Meta TUN fake-IP 下 Codex CLI 订阅网络兼容方案

> **For agentic workers:** 这是只读诊断后的方案，不是已实施修复。实现前必须按任务逐项建立证据；不得用一次 full-run 失败直接签署 Gate 2。

**Goal:** 找出 Codex CLI 0.146.0（Rust）在 Windows Meta TUN fake-IP 模式下无法完成 Codex 订阅 Responses WebSocket 的确切断点，并给出不关闭 TUN、不走 DIRECT、不影响 OpenCodex 的可回滚修复方案。

**Architecture:** 保持 Omnigent 与 OpenCodex 的配置隔离不变；只在 Omnigent 的 Codex 子进程边界验证并选择网络路径。优先使用 Meta 已暴露的本机 HTTP/SOCKS 代理作为 Codex child 的显式 per-process 出站路径，保留 `NO_PROXY=127.0.0.1,localhost` 以访问 Omnigent 本地 server；若代理无法完成 Responses WebSocket，再单独评估 Meta 的 TUN 兼容模式或 Codex CLI 版本/上游修复。任何 TUN 客户端改动都必须另卡并先获用户批准。

**Tech Stack:** Windows Winsock、Meta TUN、Codex CLI 0.146.0 Rust app-server、HTTPS/WebSocket、Python/临时 Rust 网络探针、pytest。

## Global Constraints

- 不修改 `C:\Users\Administrator\.codex\config.toml`。
- 不停止 OpenCodex PID 15536，不杀 `bun.exe`，不释放或占用 10100。
- 不关闭 TUN、不设置 `DIRECT`，不修改 Meta 配置；如果候选方案必须改 TUN，只能输出另行确认的方案，不在本任务实施。
- 不把 `https://api.openai.com/v1` 当成订阅默认 endpoint；Codex 订阅路径必须保持 `wss://chatgpt.com/backend-api/codex/responses`。
- native CLI 固定 0.146.0，任务卡约定 path/SHA；所有凭据输出为 `[REDACTED]`。
- 不改 `240s` idle watchdog，不跑完整 Gate 2，不 commit/push/merge/tag。
- 只读诊断可以运行 DNS/TCP/TLS/代理探针，但不得重跑 Controller C/full-run 作为“试错”。

## 1. 证据和当前结论

### 1.1 已确认的隔离边界

证据：

- r1：`C:\Users\Administrator\omnigent-diagnostics\20260731-044137-dc83140-hermes-isolation-fullrun-cli0146-r1\outcome.json`
- r2：`C:\Users\Administrator\omnigent-diagnostics\20260731-060535-dc83140-hermes-isolation-fullrun-cli0146-r2\outcome.json`
- 实现：`omnigent/inner/codex_executor.py`
- 测试：`tests/inner/test_codex_runtime_isolation.py`

两轮都支持以下结论：

- `harness=codex`、`module=omnigent.inner.codex_harness`、`gateway=None`。
- 没有 `127.0.0.1:10100` 连接；OpenCodex PID 15536 仍监听 10100。
- CLI 目标是 `wss://chatgpt.com/backend-api/codex/responses`。
- 用户 `~/.codex/config.toml` 未被 Omnigent 修改。
- native CLI 实际文件 SHA 为 `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb`，大小 `358650672`，版本 `0.146.0`。

因此，阶段 23 的配置隔离已经把“被 OpenCodex 10100 劫持”排除；本任务进入网络兼容诊断，不应重新修改隔离逻辑或 OpenCodex。

### 1.2 当前失败边界

- r1 `c-stderr-tail.txt`：Codex Rust `codex_api::endpoint::responses_websocket` 连接 `wss://chatgpt.com/backend-api/codex/responses` 报 `os error 11003`，随后 MCP endpoint 也失败；C exit=1，约 48 秒退出。
- r2：C 等满 240 秒，无 assistant/`turn/completed`，C 被 watchdog 脚本终止；没有 10100 连接。
- r1/r2 都没有真实 assistant `CONTROLLER_OK`，因此 Gate 2 仍为 NOT PASS。

### 1.3 当前主假设的边界

已知 Python 走相同主机的 TUN fake-IP 可以解析、建立 TCP、完成 TLS；当前只读探针也复现：

- `chatgpt.com` → `198.18.0.147` / `fdfe:dcba:9876::85`。
- `api.openai.com` → `198.18.0.29` / `fdfe:dcba:9876::1b`。
- Python TLS 均为 TLS 1.3。
- Meta 网卡地址为 `198.18.0.1` / `fdfe:dcba:9876::1`。
- Winsock catalog 当前只见标准 MSAFD/系统 provider，未见异常第三方 LSP。
- WinHTTP 显示 Direct access；本机 `verge-mihomo.exe` PID 15440 正在监听 `127.0.0.1:7897`，HTTP 和 SOCKS5 连接探针均可建立并得到远端 HTTP 响应。

因此可以确认“Python 成功 ≠ Rust WebSocket 成功”，但还不能把断点精确归因到 Rust `getaddrinfo`、IPv6/IPv4 选择、TCP/TLS、WebSocket upgrade 或代理变量。r1 的 `os error 11003` 更接近 DNS/Winsock 解析/连接阶段；r2 的纯 hang 说明还需要连接阶段的细粒度观测。

## 2. 代码核对结果与审计缺口

### 2.1 `codex_executor.py` 当前真实行为

- `omnigent/inner/codex_executor.py:126-145`：`OPENAI_BASE_URL`、`OPENAI_API_BASE` 被精确拒绝；用户 config 的 `openai_base_url`、`openai_api_base`、`model` 被清理。
- `omnigent/inner/codex_executor.py:402-445`：当前 allowlist 允许 `HTTP_*`、`HTTPS_*`、`ALL_PROXY*`、`NO_PROXY*`；本 checkout 并不是“把 `HTTPS_PROXY/ALL_PROXY` 全部 deny”。任务卡中“lines 420-421 deny ALL_PROXY/NO_PROXY”的描述与当前代码不一致，不能据此直接修改环境过滤。
- `_CodexAppServerSession.start()`：子进程使用私有 `CODEX_HOME` 并启动 `codex app-server`；r1 的 `isolation-evidence.json` 未捕获 private home/config hash/model argv，故网络结论可靠，但 full-run 的部分隔离审计字段仍不完整。

### 2.2 r2 证据债务

r2 `precheck.txt` 写入的 expected SHA 为 `4131304054935f300687269113634e22a4461d6271081775538096773669108a`，但实际 CLI SHA 为阶段 23 约定的 `bc343ba...`，因此 `cli_sha256_match=False`。r2 可证明“不连接 10100、OpenCodex 仍存活、跑到 240s”，但不应作为 binary identity 已冻结的强证据。后续探针必须使用真实 `bc343ba...`，并在 start/end 两处记录 path/size/SHA。

## 3. 必须先完成的最小诊断矩阵

不改源码、不跑 C；每个探针输出脱敏 JSON，记录时间、PID、环境摘要、地址族、endpoint 和 exit。

### 3.1 解析与地址族

- 使用 Windows `getaddrinfo`/Python `socket` 记录 A/AAAA、顺序、耗时和异常。
- 使用临时 Rust 探针（`std::net::ToSocketAddrs` 或与 CLI 相同的 resolver 依赖）对 `chatgpt.com:443` 做 IPv4-only、IPv6-only、双栈三组解析；不修改仓库源码，临时文件放 evidence/runtime。
- 明确区分 `WSANO_RECOVERY (11003)` 是名称解析失败，还是解析成功后被包装成 connect error；不能只根据错误字符串下结论。

### 3.2 TCP/TLS/WS 分层

- 对已解析的 fake IPv4/fake IPv6 地址分别做 TCP connect。
- 分别做带 SNI `chatgpt.com` 的 TLS 1.3 握手。
- 对相同 URL 做 WebSocket upgrade；记录 HTTP status、TLS 错误、WS close code。不要把普通 HTTPS 403 当成 WebSocket 成功。
- 需要保留“Python 成功、Rust 失败”的同一目标、同一时间窗口对照，避免只测不同 host 或不同网络路径。

### 3.3 child 环境与代理路径

- 从 Omnigent 实际传给 Codex child 的 env 生成脱敏快照；至少记录 `HTTPS_PROXY`、`HTTP_PROXY`、`ALL_PROXY`、`NO_PROXY`、`OPENAI_*`、`CODEX_HOME`，不记录值中的 token/认证。
- 分别用 `http://127.0.0.1:7897` 和 `socks5h://127.0.0.1:7897` 做最小 TCP/TLS/WS 探针；确认 7897 的协议类型、是否支持 CONNECT 和 WebSocket upgrade。
- 保持 `NO_PROXY=127.0.0.1,localhost`，确保本地 Omnigent server/host 不经过代理；不得把 chatgpt.com 加入 NO_PROXY。
- 证明 Codex 0.146.0 是否读取 `HTTPS_PROXY`/`ALL_PROXY`，不要只证明 curl 能走代理；优先使用临时 Rust client 或 CLI 的最小 app-server 连接观测。

### 3.4 路由与 TUN 只读状态

- 记录 Meta 网卡状态、198.18.0.0/15 和 `fdfe:dcba:9876::/18` 路由、默认路由、MTU、接口 metric。
- 记录 `127.0.0.1:7897` 的 owning process；当前已确认 PID 15440 为 `verge-mihomo.exe`，不得修改其配置。
- 不切换 fake-IP/redir-host/gVisor，不执行 `netsh winsock reset`；这些只能作为后续用户确认方案。

## 4. 候选方案对比

| 方案 | 改动点 | 翻墙/TUN影响 | 风险与可逆性 | 结论 |
|---|---|---|---|---|
| A. Omnigent child 显式使用 Meta 本机 HTTP/SOCKS 代理 | 仅在 Codex 子进程注入明确的 `HTTPS_PROXY`/`ALL_PROXY`，保留本地 `NO_PROXY`；不改 OpenCodex/TUN | 仍由 Meta 负责出站，避免 Rust 直接处理 fake-IP | 需要确认 7897 支持 Codex WebSocket；端口变化需配置化；只影响 Omnigent child，可回滚 | **首选**，前提是 Rust WS 代理探针成功 |
| B. Meta TUN 改为 Rust 兼容模式 | 调整 fake-IP/redir-host 或 gVisor 等 Meta 模式 | 可能影响整机流量，违反当前“先不动 TUN”边界 | 影响面大，需要用户批准；不能由 Omnigent 单进程隔离 | 只有 A 不可用时另开 TUN 方案卡 |
| C. 升级/替换 Codex CLI | 更换能兼容该 TUN/Winsock 的 0.146.x/后续版本，并固定新 SHA | TUN 不变 | 版本行为、订阅协议、SDK 兼容性不确定；必须重新完成 D0/D1 和 full-run | 作为上游兼容性方案，不是当前即时修复 |
| D. hosts 固定 chatgpt.com 实 IP | 修改 hosts/硬编码 CDN IP | 可能绕过 fake DNS，但仍不保证 TUN/WS | Anycast/CDN/IP 会变，证书/路由风险高，维护不可控 | **不推荐/拒绝** |
| E. DIRECT/关闭 TUN | 绕过代理 | 违反用户硬约束，且翻墙不可用 | 不允许 | **禁止** |

## 5. 推荐方案（单选）

推荐 **方案 A：Omnigent Codex child 使用显式、可配置的 Meta 本机代理；保留 TUN 和 OpenCodex 原样**。

理由：它是唯一能同时满足“必须使用 TUN 翻墙”“不能 DIRECT”“不能改 OpenCodex/10100”“只影响 Omnigent”的低影响路径。当前机器已经观察到 `verge-mihomo.exe` 在 `127.0.0.1:7897` 提供可连通的 HTTP/SOCKS5 端口，但必须先用 Rust/WebSocket 探针证明该端口能完成 Codex Responses WS；普通 curl 200/403 只能证明 HTTP 可达，不能作为最终成功标准。

方案 A 的实现边界：

1. 不读取或修改用户 `~/.codex/config.toml`。
2. 新增 Omnigent 专用、脱敏的 proxy 配置入口（例如 `HARNESS_CODEX_HTTPS_PROXY`），只注入 Codex child；禁止从任意全局环境隐式继承未知代理。
3. `NO_PROXY` 至少保留 `127.0.0.1,localhost`，不把 `chatgpt.com`/`api.openai.com` 排除。
4. 私有 `CODEX_HOME`、订阅 auth、模型 `gpt-5.6-sol`、native CLI path/SHA 逻辑保持不变。
5. 连接失败必须快速给出“proxy/TUN/network layer”结构化诊断，不把 240s idle 当作正常等待，也不自动改 TUN 或 DIRECT。

如果 Rust WS 代理探针失败，则不得强行实施 A；应转入方案 B 或 C 的独立决策卡，先由用户选择 TUN 兼容模式或 CLI 版本路线。

## 6. 后续实施步骤（本任务不执行）

### Task 1 — 网络分层探针

**Files:**
- Create only under new evidence/runtime: temporary Python/Rust probe scripts and JSON outputs。
- Do not modify `omnigent/` or `tests/`。

- [ ] 固定真实 CLI path/size/SHA（`bc343ba...`），记录 TUN/route/Winsock/7897 状态。
- [ ] 完成 DNS、IPv4/IPv6 TCP、TLS、WS 四层矩阵。
- [ ] 记录实际 child env，确认当前 `_clean_codex_env` 的代理行为，不凭任务卡旧行号推断。
- [ ] 只在 Rust WS 经 7897 成功时进入 Task 2。

### Task 2 — 方案 A 的最小实现卡

**Files:**
- Modify: `omnigent/inner/codex_executor.py:402-445` 的 child env 构造及相关配置解析。
- Test: `tests/inner/test_codex_runtime_isolation.py` 增加 proxy allow/deny、NO_PROXY 本地保留、无全局代理泄漏测试。

- [ ] 只接收显式 Omnigent proxy 配置，传给 Codex child；不改全局进程环境。
- [ ] 保留 subscription endpoint，不新增 OpenAI API base URL。
- [ ] 记录脱敏 proxy mode/host/port、私有 CODEX_HOME、CLI identity；不记录凭据。
- [ ] 测试 HTTP/SOCKS 两种已确认协议和 proxy 不可用时的清晰失败。

### Task 3 — 单次新 full-run

- [ ] 新 RUN_ID/evidence；不拼接 r1/r2。
- [ ] 模型 `gpt-5.6-sol`、CLI 0.146.0 正确 SHA、`HARNESS_CODEX_PATH` 在 server/host/C 前注入。
- [ ] TUN 只观察，OpenCodex PID 15536/10100 保持可用。
- [ ] 成功标准：真实 assistant `CONTROLLER_OK`、`turn/completed`、C exit=0、无 11003/10106/WS hang、无 10100、无 TerminalRegistry.launch、未触发 240s idle。
- [ ] cleanup、manifest、leak-scan 最后且 hits=0；报告不得宣称 Gate 2 PASS。

## 7. 验证判据

只有同时满足下列条件，才能把网络问题标记为解决：

1. Rust 探针和 Codex child 在同一网络窗口成功完成 WS upgrade。
2. Codex CLI 真实产生 assistant item `CONTROLLER_OK` 和 `turn/completed`。
3. C exit=0，且没有 240s timeout。
4. child 未连接 10100，OpenCodex 仍监听 10100。
5. 订阅认证、私有 `CODEX_HOME`、CLI path/size/SHA 全部可审计。
6. 至少一次失败/代理不可用测试证明不会静默 DIRECT 或污染用户 OpenCodex。

## 8. 回滚方案

- 方案 A 回滚：删除 Omnigent 专用 proxy 配置/环境入口，恢复 Codex child 原有 TUN 直连路径；不改用户 `config.toml`、Meta、OpenCodex 或 10100。
- 方案 B 回滚：仅在用户批准后恢复原 Meta 模式；由独立 TUN 卡记录前后配置和路由。
- 方案 C 回滚：恢复已验收的 CLI 0.146.0 path/SHA，并保留新旧版本 evidence 对照。
- 任何回滚都不得删 evidence，不得用 `netsh winsock reset` 作为默认回滚。

## 9. Gate 边界

本计划只处理 Codex CLI 在 TUN 下的网络兼容性。即使单次 full-run 通过，也只表示隔离链路和本次网络路径通过；Gate 1 仍是相对 main PASS，Gate 2 必须独立完成六轮验收，当前不可 merge。

## 10. Implementation record (2026-07-31)

- Implemented the Route-A child-only proxy boundary in `omnigent/inner/codex_executor.py`: the subscription child receives configurable `OMNIGENT_CODEX_PROXY` (default `http://127.0.0.1:7897`), ambient proxy variables are scrubbed/replaced, and `NO_PROXY` retains local Omnigent endpoints. `gateway=True` is excluded.
- Forwarded `OMNIGENT_CODEX_PROXY` through `omnigent/host/connect.py` and added isolation/host-forwarding tests.
- Focused isolation + BUG-1/2/3 regression set passed (44 tests). The broader Codex executor shard passed 154 tests with one unrelated pre-existing Windows real-home-auth failure. The focused proxy set after correcting the Codex 0.146.0 config key passed 26 tests.
- Corrected an investigation mistake: `network.proxy_url` is not a valid 0.146.0 override; the recognized shape is `features.network_proxy=true` plus `network_proxy.proxy_url=<url>`.
- Preserved fresh Route-A evidence roots `C:\Users\Administrator\omnigent-diagnostics\20260731-152542-dc83140-codex-proxy-fullrun-r1`, `...153045...-r2`, `...153704...-r3`, and `...154130...-r4`. They all failed before a real assistant response with Rust 10106/11003; no 10100 connection was observed, OpenCodex remained alive, and leak scans were zero. A direct in-process Codex app-server probe with the same native binary and proxy also failed to produce `turn/completed`.
- Route A is therefore implemented but **not accepted as a fix**. The current machine still needs a separate Codex-0.146.0/Clash proxy compatibility or upstream/CLI-version decision. This is not a Gate 2 verdict and does not authorize merge; do not alter TUN/OpenCodex or the 240-second watchdog as a workaround.
