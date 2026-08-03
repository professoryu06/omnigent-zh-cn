# CODEX_TASK_22 — Full-Run r2 新 Bug 排查确认 + 出方案（只排查，不实施）

> 来源：Hermes full-run r2 只读诊断（RUN_ID `20260730-172454-dc83140-hermes-d2-run-cli0146-r2`）
> 前置：`HERMES_DIAGNOSIS_21.md`（同目录）
> 角色边界：Hermes 只读诊断执行者，不实施修复。
> **Codex 本轮任务：排查确认根因 + 输出修复方案。不实施、不 commit、不 merge。**

---

## 背景

用户授权 Hermes 执行"第二方式"：完整走完 `omnigent run … -p "Reply with CONTROLLER_OK and stop."`。
经过 6 轮排障（旧 host_id 缓存 → GBK 崩溃 → env allowlist → 临时 ASCII 修补），最终突破到 runner 启动，
但 runner 在 harness 路由阶段崩溃，native Codex CLI 从未被 spawn。

**结论：失败不能归咎于 Codex CLI。失败发生在产品内部的 harness 路由层。**

---

## 需 Codex 确认的 Bug

### BUG-2（核心阻塞）：harness 路由错误 — codex harness 走了 tmux/PTY 路径

**现象：**
- Agent config 已正确设置 `executor.config.harness: codex`
- Runner 启动成功（pid=20864），session 创建成功，用户消息投递成功，turn 已启动
- 但 runner 随后调用 `omnigent/inner/terminal.py:1882` → `omnigent/terminals/registry.py:221`
- 抛出 `RuntimeError: Native terminal harnesses (tmux/PTY) are not supported on Windows.`
- Runner 崩溃，无事件输出，CLI 240s idle watchdog 触发，exit=1

**Runner 日志关键行：**
```
codex gateway routing recognized (model=gpt-5.6-sol)
...
RuntimeError: Native terminal harnesses (tmux/PTY) are not supported on Windows.
Run an SDK-based harness via `omnigent run <agent.yaml>`
(e.g. the claude-sdk, cursor, copilot, or codex harness) or use the web UI.
```

**Agent config（冻结副本在 evidence 目录）：**
```yaml
spec_version: 1
executor:
  type: omnigent
  config:
    harness: codex
    model: gpt-5.6-sol
```

**需 Codex 回答：**
1. `executor.config.harness: codex` 是否应该让 runner 走 SDK/subprocess 路径（`codex_native_executor.py`）而非 tmux/PTY？
2. 如果是，路由逻辑哪里断了？是 `runner/app.py` 的 harness 分发没读 `executor.config.harness`，还是 `inner/loader.py` 的映射缺 codex？
3. 如果不是（即 `executor.type: omnigent` 在 Windows 上就是不支持），那正确的 Windows agent config 应该怎么写？
4. 错误消息说 "e.g. the codex harness" 暗示 codex harness 应该可用——这是文档/实现不一致还是 config 格式问题？

**关键代码路径（供排查）：**
- `omnigent/runner/app.py` — runner 主循环，harness 分发入口
- `omnigent/inner/loader.py` — executor/harness 加载器
- `omnigent/inner/codex_native_executor.py` — codex SDK harness 实现
- `omnigent/inner/terminal.py:1882` — 崩溃点（tmux/PTY 创建）
- `omnigent/terminals/registry.py:221` — terminal 注册表（Windows 拒绝）
- `omnigent/spec/parser.py` — agent spec 解析（`executor.config.harness` 字段）

---

### BUG-1（已绕过，仍需产品修复）：Host daemon GBK 编码崩溃

**现象：**
- `omnigent/host/connect.py:1878` 输出 `✓ Connected as ...`
- Windows 中文 locale 下 daemon 子进程 stdout 是 GBK
- `_RUNNER_ENV_ALLOWLIST`（connect.py:261）和 `_LOCAL_DAEMON_ENV_ALLOWLIST`（cli.py:354）不含 `PYTHONUTF8`
- Daemon 无法继承父进程的 `PYTHONUTF8=1` → `UnicodeEncodeError: 'gbk' codec can't encode character '\u2713'`
- Tunnel 断开 → 10s 重连 → 无限崩溃循环

**方案选项（供 Codex 评估，选一个或组合，写入方案文档）：**
- A：banner/日志全部 ASCII-safe（`✓` → `[OK]`）
- B：daemon spawn 时强制 `PYTHONUTF8=1`（加入 allowlist 或硬编码）
- C：daemon stdout 用 `errors="replace"` 或显式 UTF-8 wrapper
- D：组合（Hermes 倾向 B+C，但由 Codex 定）

---

### BUG-3（已知，C-only r1 发现）：multipart POST /v1/sessions 不 launch runner

详见 `HERMES_DIAGNOSIS_21.md` "根因" 一节。multipart 带 `host_id` 创建 session 后直接 return，不发 `host.launch_runner`。

---

### BUG-4（新发现，Responses/10100 诊断）：opencodex 劫持 Codex CLI API 地址

**诊断 RUN：** `20260731-035708-dc83140-hermes-responses10100-cli0146-r1`
**Evidence：** `C:\Users\Administrator\omnigent-diagnostics\20260731-035708-dc83140-hermes-responses10100-cli0146-r1\`

**现象：**
- Grok full-run 中 runner 已启动、harness=codex、native CLI 0.146.0 已 spawn、BUG-1/2/3 主链路通过
- 失败发生在 spawn 之后：`stream disconnected before completion`，`@url:http://127.0.0.1:10100/v1/responses`
- 伴随 `OS error 10106`（WSAEPROVIDERFAILEDINIT）

**根因：**
`~/.codex/config.toml` 被 `@bitkyc08/opencodex` 自动注入：
```toml
# Auto-injected by opencodex
openai_base_url = "http://127.0.0.1:10100/v1"
model = "gpt-5.6-luna"
```

Codex CLI 0.146.0 读到后把 Responses WebSocket 发到 `127.0.0.1:10100`——但 10100 上是 opencodex 的 proxy dashboard（bun.exe PID 15536），不支持 Responses API：
- HTTP GET `/v1/responses` → **404**
- WS upgrade `/v1/responses` → **426 Upgrade Required**

**Omnigent 侧代码路径：**
- `codex_harness.py:302`：`base_url_override=os.environ.get("HARNESS_CODEX_GATEWAY_BASE_URL") or None`
- `codex_executor.py:2196-2220`：`base_url_override` 有值时覆盖；为 None 时 Codex CLI 完全信任 config.toml
- 本 RUN 未设 `HARNESS_CODEX_GATEWAY_BASE_URL` → Codex CLI 走了被劫持的 config.toml

**修复方案（不动 opencodex，不删 config.toml）：**

> 核心原则：**opencodex 继续正常使用，omnigent 走自己的路，互不干扰。**

1. **运维侧（立即可做）：** omnigent 启动 server/host/C 前注入环境变量：
   ```bash
   HARNESS_CODEX_GATEWAY_BASE_URL="https://api.openai.com/v1"   # 或实际 gateway 地址
   ```
   Codex CLI 读到 env 后无视 config.toml 的 `openai_base_url`，opencodex 不受影响。

2. **产品侧（长期）：** `codex_executor.py` spawn Codex CLI 时，应始终通过 `-c openai_base_url=<resolved>` 或 env 覆盖，
   防止任何第三方工具（opencodex 或类似）通过 config.toml 劫持 API 地址。
   当前 `base_url_override=None` 时完全信任 config.toml 是设计缺陷。

3. **model 覆盖：** config.toml 还有 `model = "gpt-5.6-luna"`（非 gpt-5.6-sol）。
   omnigent spawn 时必须通过 `-c model=gpt-5.6-sol` 或 `HARNESS_CODEX_MODEL` 强制覆盖，
   不能被 config.toml 的默认值影响。

4. **不动的：**
   - `~/.codex/config.toml` — 不删不改（opencodex 依赖它）
   - opencodex bun.exe — 不杀
   - 10100 端口 — 让它继续占着，omnigent 不走它
   - TUN — 不关（OS error 10106 是次要问题，主因修完大概率自愈）

**次要问题（待主因修复后复测）：**
- OS error 10106（WSAEPROVIDERFAILEDINIT）：Winsock 层失败，可能是 Meta TUN + opencodex LSP 交互
- 若主因修复后仍复现，考虑 `netsh winsock reset`

**分类：** `DIAG_LOCAL_PROCESS_PORT_CONFLICT`（primary）+ `DIAG_AUTH_OR_MODEL_CONFIG`（secondary）

---

## Evidence

持久保留于 `C:\Users\Administrator\omnigent-diagnostics\20260730-172454-dc83140-hermes-d2-run-cli0146-r2\`：

| 文件 | 内容 |
|---|---|
| `run-summary.json` | 完整运行摘要 + 失败链 + bug 列表 |
| `agent-config.yaml` | 冻结的 agent 配置 |
| `logs/runner/runner-conv_*.log` | Runner 日志（含 RuntimeError traceback） |
| `logs/host/host-20260731-014625-*.log` | Host daemon 日志（GBK 崩溃 + 修补后稳定） |
| `logs/server/server-20260731-013611-*.log` | Server 日志（130KB） |
| `logs/cli/cli-*.log` | CLI 日志 |
| `precheck.json` / `tun-check.json` / `identity.json` | 环境快照 |

---

## 约束提醒

- **Codex 本轮只排查 + 出方案，不实施、不 commit、不 push、不 merge**
- 交付物：一份方案文档（可写在 `docs/fixes/handoffs/CODEX_TASK_22_PLAN.md`），含：
  - BUG-2 根因确认（路由断在哪个文件哪一行）
  - BUG-2 修复方案（改哪些文件、怎么改、影响面）
  - BUG-1 修复方案（选 A/B/C/D 或自定义）
  - BUG-3 是否本轮一并出方案
  - 验证计划（修完后怎么跑 full-run 验证 CONTROLLER_OK）
- Hermes 不实施修复、不签 Gate 2、不 commit/push/merge
- 模型固定 `gpt-5.6-sol`；native CLI 固定 `0.146.0`
- 240s idle watchdog 不改
- 凭据一律 `[REDACTED]`
- 方案确认后，由后续任务卡安排实施和验证

---

*生成时间：2026-07-31T02:05Z*
*Hermes 只读诊断执行者*
