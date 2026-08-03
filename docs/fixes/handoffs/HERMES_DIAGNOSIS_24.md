# HERMES_DIAGNOSIS_24 — Codex CLI Rust 网络栈 vs Meta TUN fake-IP 只读诊断

**RUN_ID**: `20260731-064535-dc83140-hermes-diag24-r1`
**Evidence**: `C:\Users\Administrator\omnigent-diagnostics\20260731-064535-dc83140-hermes-diag24-r1\`
**日期**: 2026-07-31
**角色**: Hermes 只读诊断，不实施修复
**分类**: `DIAG_RUST_TUN_PROXY_COMPATIBLE`

---

## 1. CLI Identity

| 字段 | 值 |
|------|-----|
| path | `C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe` |
| version | codex-cli 0.146.0 |
| size | 358650672 |
| SHA-256 | `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb` |
| SHA match | ✅ True |

## 2. 环境预检

| 检查项 | 结果 |
|--------|------|
| Meta TUN 接口 | ✅ 已连接，MTU 9000 |
| Meta 网卡 IPv4 | 198.18.0.1 |
| Meta 网卡 IPv6 | fdfe:dcba:9876::1 |
| 198.18.0.0/15 路由 | 活跃（198.18.0.0/30 via Meta Tunnel） |
| WinHTTP proxy | 直接访问（无代理） |
| Winsock catalog | 标准 MSAFD Tcpip，无异常 LSP |
| 127.0.0.1:7897 | PID 15440 `verge-mihomo.exe`（Clash Verge） |
| 127.0.0.1:10100 | PID 15536 `bun.exe`（OpenCodex）✅ 存活 |

## 3. DNS / 地址族矩阵

### Python `socket.getaddrinfo`

| host | A (IPv4) | AAAA (IPv6) | 耗时 | 错误 |
|------|----------|-------------|------|------|
| chatgpt.com | 198.18.0.147 | fdfe:dcba:9876::85 | 10.05ms | 无 |
| api.openai.com | 198.18.0.29 | fdfe:dcba:9876::1b | 1.42ms | 无 |

**结论**: Python DNS 解析正常，返回 TUN fake-IP，无 11003。

### Rust 探针

**不可用**：本机无 `cargo`/`rustc`，无法编译 Rust 探针。记录为真实限制，不伪造结果。

## 4. TCP / TLS 分层测试

### Python 直连（经 TUN fake-IP）

| host | 地址族 | TCP ms | TLS ms | TLS 版本 | 错误 |
|------|--------|--------|--------|----------|------|
| chatgpt.com | IPv4 (198.18.0.147) | 0.41 | 2792.45 | TLSv1.3 | 无 |
| chatgpt.com | IPv6 (fdfe:dcba:9876::85) | 1.37 | 1443.54 | TLSv1.3 | 无 |
| api.openai.com | IPv4 (198.18.0.29) | 12.68 | 1821.88 | TLSv1.3 | 无 |
| api.openai.com | IPv6 (fdfe:dcba:9876::1b) | 20.97 | 1340.15 | TLSv1.3 | 无 |

**结论**: Python TCP/TLS 在 IPv4 和 IPv6 fake-IP 上全部成功。

## 5. WebSocket 测试

目标：`wss://chatgpt.com/backend-api/codex/responses`

| 路径 | TCP | TLS | WS upgrade | HTTP status | 错误 |
|------|-----|-----|-----------|-------------|------|
| 直连 TUN | ✅ 10.37ms | ✅ TLSv1.3 1037ms | ✅ 537ms | **401 Unauthorized** | 无（401 = 无 auth token，正常） |
| HTTP proxy 7897 | ✅ CONNECT 200 | ✅ TLSv1.3 2303ms | ✅ 523ms | **401 Unauthorized** | 无 |
| SOCKS5 proxy 7897 | ✅ reply 0x00 | ✅ TLSv1.3 2362ms | ✅ 524ms | **401 Unauthorized** | 无 |

**结论**: Python 三条路径均完成 TCP → TLS → WS upgrade。服务端返回 401 是因为未携带订阅 auth token，属于预期行为。**网络层对 Python 完全通畅。**

## 6. 本机代理测试（127.0.0.1:7897）

| 协议 | CONNECT/握手 | TLS | WS upgrade | 结论 |
|------|-------------|-----|-----------|------|
| HTTP CONNECT | `HTTP/1.1 200 Connection established` | ✅ | ✅ 401 | 可用 |
| SOCKS5 | method=0x00 (no-auth), reply=0x00 (success) | ✅ | ✅ 401 | 可用 |

**结论**: `verge-mihomo.exe` 的 7897 端口同时支持 HTTP CONNECT 和 SOCKS5，且能完成 WebSocket upgrade。

## 7. Codex 子进程环境审计

### `_clean_codex_env()` 当前真实行为（codex_executor.py:402-446）

**allowlist 前缀**（放行）：`OPENAI_`、`HTTP_`、`HTTPS_`、`ALL_PROXY`、`NO_PROXY`、`SSL_`、`REQUESTS_`、`CODEX_HOME`、`XDG_`、`LANG`、`LC_`

**deny exact**（拒绝）：`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_API_BASE`

⚠️ **任务卡旧描述"420-421 deny ALL_PROXY/NO_PROXY"与当前代码不一致**。当前代码 **放行** 所有代理变量。

### 实际 child env 快照（脱敏）

当前父进程（Omnigent 运行环境）**没有设置任何代理变量**，因此 child env 中：

| 变量 | 值 |
|------|-----|
| HTTPS_PROXY | ❌ 不存在 |
| HTTP_PROXY | ❌ 不存在 |
| ALL_PROXY | ❌ 不存在 |
| NO_PROXY | ❌ 不存在 |
| OPENAI_BASE_URL | ❌ 不存在（被 deny） |
| OPENAI_API_BASE | ❌ 不存在（被 deny） |
| CODEX_HOME | ❌ 不存在（由 Omnigent 运行时注入私有路径） |
| HARNESS_CODEX_PATH | ❌ 不存在（由 full-run 脚本注入） |
| SSL_CERT_FILE | `E:\hermes\hermes-agent\venv\Lib\site-packages\certifi\cacert.pem` |

**总计 9 个 key 传入 child，其中 0 个代理变量。**

**结论**: Codex CLI 子进程当前**没有任何代理配置**，必须直接走 TUN fake-IP 出站。

## 8. r1 错误精确定位

```
codex_api::endpoint::responses_websocket: failed to connect to websocket:
IO error: 在数据库查找中出现一个不可恢复的错误。 (os error 11003),
url: wss://chatgpt.com/backend-api/codex/responses
```

- 错误码：`os error 11003` = `WSANO_RECOVERY`（Winsock DNS 数据库不可恢复错误）
- 出现位置：Rust `codex_api` crate → `responses_websocket` → 连接阶段
- 重试 4 次均失败（04:48:50 → 04:48:56）
- MCP endpoint 也同时失败（`http/request failed`）

## 9. 失败层定位

| 层 | Python | Rust (Codex CLI) | 结论 |
|----|--------|-------------------|------|
| DNS getaddrinfo | ✅ 10ms | ❌ 11003 / hang | **断点在此** |
| TCP connect | ✅ 0.4-21ms | 未到达 | — |
| TLS handshake | ✅ TLSv1.3 | 未到达 | — |
| WS upgrade | ✅ 401 | 未到达 | — |

**根因**: Rust 的异步 DNS 解析器（tokio `getaddrinfo` 或 `hickory-dns`）在 Windows TUN fake-IP 环境下触发 `WSANO_RECOVERY`。Python 的同步 `getaddrinfo` 走相同 Winsock 路径但成功，说明差异在于：
1. Rust 可能使用不同的 `getaddrinfo` flags（如 `AI_ADDRCONFIG`）
2. Rust 异步运行时可能在 blocking thread pool 中调用 DNS，与 TUN 的 Winsock 注入存在竞态
3. r2 的 240s hang 表明行为不确定——有时返回错误，有时静默丢包

## 9.1 历史可用基线（用户确认）

| 状态 | 时间 | OpenCodex | 源码隔离 | TUN | Codex CLI 行为 | 结果 |
|------|------|-----------|----------|-----|----------------|------|
| **A（历史 OK）** | 安装 OpenCodex 之前 | ❌ 未安装 | ❌ 未修复 | ✅ 开启 | Omnigent 唤起 → 直接登录账号 → 正常使用 | ✅ 成功 |
| **B（OpenCodex 安装后）** | 安装 OpenCodex 之后 | ✅ 已安装 | ❌ 未修复 | ✅ 开启 | `~/.codex/config.toml` 被注入 `openai_base_url=127.0.0.1:10100/v1` + `model=gpt-5.6-luna`；CLI 走 OpenCodex 代理出站 | ⚠️ 能用但走 10100 |
| **C（隔离修复后）** | CODEX_TASK_23 之后 | ✅ 已安装 | ✅ 私有 CODEX_HOME | ✅ 开启 | 清洗配置 → 不再连 10100 → 回退订阅直连 → 自己连 `chatgpt.com` | ❌ 11003 / 240s hang |

**关键推论**：
- 状态 A 证明：**同一个 `codex.exe`（同 SHA）在 TUN 下曾经成功直连 `chatgpt.com`**。"Rust 天生不兼容 TUN"不成立。
- 状态 B → C 的变化：隔离修复移除了 `openai_base_url`，CLI 从"经 10100 代理出站"变为"自己直面 TUN fake-IP"。
- 状态 A → B/C 的环境变化：Clash Verge 配置 `clash-verge.yaml` 创建于 **2026-07-30 22:29**（昨晚），使用 `tun.stack: gvisor` + `dns.enhanced-mode: fake-ip`。用户之前可用的 TUN 配置大概率不是 gvisor/fake-ip 组合。

## 9.2 Clash Verge 配置分析（根因候选）

```yaml
# C:\Users\Administrator\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\clash-verge.yaml
tun:
  enable: true
  stack: gvisor          # ← 用户态网络栈，Rust 异步 IO 兼容性差
  auto-route: true
  dns-hijack: [any:53]
dns:
  enhanced-mode: fake-ip # ← DNS 返回假 IP 198.18.0.0/16
  fake-ip-range: 198.18.0.1/16
  fake-ip-range6: fdfe:dcba:9876::1/64
```

- `gvisor` 在用户态拦截所有网络包，Rust tokio 异步运行时的 socket 处理与 gvisor 存在竞态
- `fake-ip` 让 DNS 返回 `198.18.x.x`，Rust `getaddrinfo` 拿到后在 gvisor 里走不通 → 11003 / hang
- Python 同步 socket 与 gvisor 兼容良好 → 全层通过
- 配置文件创建于 2026-07-30，用户历史可用时期的 TUN 配置大概率不同（可能是 `system` 栈或非 fake-ip）

## 10. 假设验证状态

| 假设 | 状态 | 证据 |
|------|------|------|
| Python 成功 ≠ Rust 成功 | ✅ 已证实 | Python 全层通过，Rust 11003/hang |
| 断点在 DNS/Winsock 层 | ✅ 已证实 | 11003 = WSANO_RECOVERY，TCP/TLS/WS 未到达 |
| 7897 代理可完成 WS | ✅ 已证实 | HTTP CONNECT + SOCKS5 均成功 |
| child env 无代理变量 | ✅ 已证实 | 9 keys，0 proxy |
| `_clean_codex_env` deny 代理 | ❌ 已否定 | 当前代码放行 HTTP_/HTTPS_/ALL_PROXY/NO_PROXY |
| Rust 探针复现 | ❌ 未验证 | 本机无 cargo/rustc |
| Codex CLI 是否读取 HTTPS_PROXY | ❌ 未验证 | 需要 Rust 探针或实际注入测试 |

## 11. 方案对比

| 方案 | 改动点 | 翻墙影响 | 风险 | 可逆性 | 结论 |
|------|--------|----------|------|--------|------|
| **A. child 注入 HTTPS_PROXY=127.0.0.1:7897** | `codex_executor.py` child env 构造 | 无（仍走 Meta） | 需确认 CLI 读取该变量；端口变化需配置化 | 删配置即回滚 | **推荐** |
| B. Meta TUN 改 redir-host/gVisor | Meta 配置 | 可能影响全局 | 影响面大，需用户批准 | 可恢复 | A 不可用时备选 |
| C. 升级 Codex CLI | 换二进制 | 无 | 版本兼容性不确定 | 可回退 | 上游修复后考虑 |
| D. hosts 硬编码 IP | 改 hosts | 无 | Anycast IP 变化，维护不可控 | 可删 | **不推荐** |
| E. 关 TUN / DIRECT | — | 翻墙不可用 | 违反硬约束 | — | **禁止** |

## 12. 唯一推荐方案

**方案 A：Omnigent Codex child 显式注入 `HTTPS_PROXY=http://127.0.0.1:7897`**

理由：
1. 7897 已证实支持 HTTP CONNECT + SOCKS5 + WS upgrade
2. `_clean_codex_env` 已放行 `HTTPS_` 前缀，不需要改 allowlist
3. 只需在 child env 构造时注入一个变量，改动最小
4. 不影响 TUN、OpenCodex、10100、用户全局配置
5. 回滚 = 删除注入逻辑

**前提条件**（实施前必须验证）：
- Codex CLI 0.146.0 的 Rust HTTP 客户端（reqwest）是否读取 `HTTPS_PROXY` 环境变量
- 如果 reqwest 使用 `native-tls`（Windows SChannel），代理行为可能不同
- 建议：先手动设置 `HTTPS_PROXY=http://127.0.0.1:7897` 跑一次 `codex app-server` 最小连接测试

**是否需要用户批准修改 TUN**: 否。方案 A 不触碰 TUN/Meta。

## 13. 回滚方案

- 删除 Omnigent 专用 proxy 注入逻辑
- Codex child 恢复无代理直连（回到当前状态）
- 不改 `~/.codex/config.toml`、Meta、OpenCodex、10100
- evidence 永久保留

## 14. Gate 边界声明

- 本诊断**不是** Gate 2 验收
- Gate 1 仍为"相对 main PASS"
- Gate 2 仍为 **NOT PASS**，不可 merge
- 即使方案 A 实施后单次 full-run 通过，也只代表隔离链路 + 网络路径通过
- Gate 2 六轮独立验收仍须完成

## 15. Evidence 文件清单

| 文件 | 内容 |
|------|------|
| `RUN_ID.txt` | 本轮 RUN_ID |
| `precheck.txt` | CLI identity + Meta/路由/Winsock/7897/10100 |
| `probe_dns_tcp_tls.py` | DNS/TCP/TLS 探针脚本 |
| `dns_tcp_tls_matrix.json` | DNS/TCP/TLS 分层结果 |
| `probe_ipv6.py` | IPv6 专项探针 |
| `ipv6_matrix.json` | IPv6 TCP/TLS 结果 |
| `probe_ws.py` | WebSocket 三路径探针 |
| `ws_matrix.json` | WS 分层结果（直连/HTTP/SOCKS5） |
| `probe_child_env.py` | child env 模拟脚本 |
| `child_env_audit.json` | 实际 child env 脱敏快照 |
| `env_audit_current.json` | 当前父进程代理变量 |
| `manifest.txt` | 本清单（final-check 后写入） |
| `leak-scan.txt` | 凭据泄漏扫描（最后执行） |
