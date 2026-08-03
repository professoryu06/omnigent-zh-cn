# CODEX_TASK_24: Codex CLI ↔ Meta TUN fake-IP 不兼容 — 排查与方案

**状态**: 待 Codex 排查 + 出方案（不实施）
**前置**: CODEX_TASK_23 隔离修复已完成并通过单测 + 两轮 full-run 证据
**授权边界**: 只读排查 + 方案输出；不修源码、不跑 Gate 2、不 commit/push/merge

---

## 1. 背景

CODEX_TASK_23 隔离修复已落地（`omnigent/inner/codex_executor.py` +80 行，
`tests/inner/test_codex_runtime_isolation.py` 18 tests 全绿，BUG-1/2/3 回归 37 tests 全绿）。

两轮 full-run 均确认**隔离链路 PASS**：
- harness=codex, module=omnigent.inner.codex_harness, gateway=None
- Codex CLI 未连接 `127.0.0.1:10100`
- 目标 endpoint 为 `wss://chatgpt.com/backend-api/codex/responses`
- OpenCodex PID 15536 仍监听 10100
- 用户 `~/.codex/config.toml` 未被修改

但**业务端到端 FAIL**：Codex CLI 无法完成订阅直连请求。

## 2. 失败证据

### r1 (20260731-044137)
- Evidence: `C:\Users\Administrator\omnigent-diagnostics\20260731-044137-dc83140-hermes-isolation-fullrun-cli0146-r1\`
- C exit=1，CLI 报 `os error 11003` (WSANO_RECOVERY)
- 分类: `DIAG_NETWORK_DNS_WINSOCK`

### r2 (20260731-060535)
- Evidence: `C:\Users\Administrator\omnigent-diagnostics\20260731-060535-dc83140-hermes-isolation-fullrun-cli0146-r2\`
- C 240s 超时无响应（CLI hang 在连接阶段，未报错）
- runner log 在 `starting background turn` 后断流
- 分类: `DIAG_NETWORK_HANG`（推断，待 Codex 确认）

## 3. 已验证的环境事实

| 检查项 | 结果 |
|--------|------|
| `nslookup chatgpt.com` | `198.18.0.131` + `fdfe:dcba:9876::70`（TUN fake-IP 段） |
| Python `socket.create_connection(('chatgpt.com', 443))` | ✅ 0.00s |
| Python TLS 握手 | ✅ TLSv1.3, 1.09s |
| `api.openai.com` 解析 | `198.18.0.29`（fake-IP） |
| Meta TUN 接口 | 活跃（`netsh interface show interface`） |
| `~/.codex/auth.json` | 存在，`auth_mode` + `tokens{access_token,refresh_token,id_token,account_id}` 完整 |
| Winsock catalog | 标准 MSAFD Tcpip 三项，未见异常 LSP |

**结论**: Python 走 TUN 完全正常；Codex CLI（Rust 二进制）在 fake-IP 模式下
要么报 `os error 11003`，要么无限 hang。

## 4. 用户硬约束

- 本机**必须**走 TUN 代理才能翻墙，不能关 TUN
- 不能把 `chatgpt.com` / `api.openai.com` 设为 DIRECT（直连出不去）
- 不能修改 `~/.codex/config.toml`
- 不能杀 OpenCodex PID 15536，不能动 10100
- 不能改 TUN 客户端本身（Meta 配置）— 如要改，需先出方案给用户确认

## 5. 待 Codex 排查的问题

1. **根因定位**: Codex CLI 0.146.0 (Rust) 在 Windows fake-IP 模式下 hang/11003 的
   具体调用栈。是 `getaddrinfo` 不认 `198.18.0.0/15`？是 `rustls` 证书校验失败？
   还是 WebSocket 握手阶段被 TUN 拦截？
2. **代理变量路径**: Codex CLI 是否支持 `HTTPS_PROXY` / `ALL_PROXY`？
   `_clean_codex_env()` 当前 deny 了 `ALL_PROXY` / `NO_PROXY`
   （`omnigent/inner/codex_executor.py:420-421`），是否需要放行？
3. **TUN 模式切换**: Meta 是否支持从 fake-IP 切到 redir-host / tun-stack=gvisor
   而不影响翻墙？切换后 Codex CLI 是否能正常解析？
4. **本地 HTTP 代理**: Meta 是否同时暴露了 HTTP/SOCKS 端口（7890/7891/1080）？
   `netstat` 当前未见监听，需确认 Meta 配置。如果有，让 Codex CLI 走
   `HTTPS_PROXY=http://127.0.0.1:<port>` 是否能绕过 fake-IP？
5. **hosts 文件硬编码**: 把 `chatgpt.com` 真实 IP 写进 hosts 是否可行？
   OpenAI 是否用 CDN/Anycast 导致 IP 频繁变化？

## 6. 方案输出要求

按以下结构交付 `CODEX_TASK_24_PLAN.md`：

1. **根因**（带证据：CLI 日志片段 / Rust 源码引用 / strace 等价物）
2. **候选方案对比表**（≥3 个方案，列：改动点、风险、对用户翻墙的影响、可逆性）
3. **推荐方案**（单选，说明理由）
4. **实施步骤**（精确到文件路径 + 行号 + 命令）
5. **验证判据**（full-run 必须看到 `CONTROLLER_OK` + `turn/completed` + C exit=0）
6. **回滚方案**

## 7. 不要做

- 不要修源码（包括 `codex_executor.py`、TUN 配置、Meta 配置）
- 不要跑 Gate 2 六轮
- 不要 commit / push / merge / tag
- 不要碰 `~/.codex/config.toml`、OpenCodex、10100
- 不要声称 Gate 2 PASS

## 8. 交接证据根

- `C:\Users\Administrator\omnigent-diagnostics\20260731-044137-dc83140-hermes-isolation-fullrun-cli0146-r1\`
- `C:\Users\Administrator\omnigent-diagnostics\20260731-060535-dc83140-hermes-isolation-fullrun-cli0146-r2\`
- `F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\CODEX_TASK_23.md`
- `F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\CODEX_TASK_23_PLAN.md`
- `F:\codex-ai\git项目部署\tmp\omnigent-review\omnigent\inner\codex_executor.py`
- `F:\codex-ai\git项目部署\tmp\omnigent-review\tests\inner\test_codex_runtime_isolation.py`
