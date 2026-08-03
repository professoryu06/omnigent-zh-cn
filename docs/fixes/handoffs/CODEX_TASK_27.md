# CODEX_TASK_27 — Codex-native TUI 接入只读诊断

## 角色

你是 Hermes 3.8，只读诊断执行者，不是实现者、Gate 2 签字人。

本卡只定位 Omnigent 拉起 Codex TUI 后没有产生 `thread/started` 的原因，
不得直接修改源码。诊断完成后停止，后续修复另发实施卡。

## 工作树与运行环境

- 代码仓库：`F:\codex-ai\omnigent-zh-next`
- 诊断文档仓库：`F:\codex-ai\git项目部署\tmp\omnigent-review`
- WSL：`Ubuntu-24.04`
- Omnigent server：`http://127.0.0.1:6767`
- 当前问题会话：`3c5c9e08ac684dfd9a0fce9975b329b3`
- 当前失败日志：
  `/home/administrator/.omnigent-zh-cn/logs/runner/runner-3c5c9e08ac684dfd9a0fce9975b329b3-20260803-114725-477646.log`

历史成功日志（只读对照，不得拼接成本 RUN 业务结果）：

- `/home/administrator/.omnigent-zh-cn/logs/runner/runner-conv_2d725b91fc83409c9d250b5d7b2-20260722-154256-280117.log`
- `/home/administrator/.omnigent-zh-cn/logs/runner/runner-conv_739669e5618e40949d18fa838c2-20260723-144730-276171.log`

## 已知事实

历史成功时序：

```text
app-server ready
→ Auto-created codex terminal
→ 约 3–6 秒出现 thread/started
```

当前 0.144.4 A/B：

```text
app-server listening/readyz/healthz
→ Auto-created codex terminal
→ TUI pane dead
→ 无 thread/started
→ startup timeout
```

当前 0.146.0 失败：

```text
Codex CLI login
→ Auto-created codex terminal
→ 未见 app-server ready
→ 无 thread/started
→ startup timeout
```

当前 0.144.4 Linux native binary：

- version：`codex-cli 0.144.4`
- SHA-256：`2b3edc9cdfd1717fba3dbc92817205a8a2c7511d459e456d4817eeff6f78ed7a`

当前代码相对历史成功基线新增或经过重构的重点：

- registry-driven native launch seam；
- provider seam / `_launch_native_terminal`；
- 私有 `CODEX_HOME` 和 hook 配置；
- TUI 参数新增 `--dangerously-bypass-hook-trust`；
- TUI 通过 `--remote ws://...` 连接 app-server。

## 本卡目标

确定失败发生在以下哪一层：

1. TUI 实际命令/参数错误；
2. Codex 路径或 PATH 混用 Windows shim；
3. 私有 `CODEX_HOME`、hook trust 或配置导致 TUI 早退；
4. tmux/PTY launcher 没有正确启动或立即回收 pane；
5. TUI 已启动但没有连上 `--remote` app-server；
6. app-server/TUI 协议版本不兼容；
7. 仍无法审计，归类 `DIAG_INCONCLUSIVE`。

## 执行边界

- 只读诊断；禁止修改 `omnigent/`、`tests/`、政策、配置和 TUN。
- 禁止修改 `~/.codex/config.toml`。
- 禁止停止、重启或修改 OpenCodex/bun/10100。
- 禁止修改代理、Meta TUN、认证和 240s idle watchdog。
- 禁止升级或降级 Codex CLI；固定使用 0.144.4 做本卡 TUI 诊断。
- 允许最多一次新的受控 TUI 诊断 RUN；不得重试同一业务失败。
- 禁止 D0/D1/D2、完整 Gate 2、pytest 全仓、commit/push/merge/tag。
- 不读取或输出凭据；所有报告中的凭据写成 `[REDACTED]`。
- evidence 必须持久保留，不得删除或拼接旧 RUN。

## 必须记录

在新的 evidence 根中实时落盘，并记录绝对路径：

1. RUN_ID、开始/结束时间、代码 HEAD start/end、工作树 dirty 摘要；
2. Codex 实际绝对路径、版本、大小、SHA-256（不能只记 `which codex`）；
3. `CODEX_HOME` 绝对路径及存在的配置文件名，不输出配置秘钥内容；
4. TUI 完整 argv（对可能的 token、cookie、Authorization 做脱敏）；
5. TUI 环境中 `PATH`、`CODEX_HOME`、`HOME`、`HARNESS_CODEX_PATH` 等变量的存在和值摘要；
6. app-server 的 `listening`、`readyz`、`healthz` 时间戳和端口；
7. `--remote` URL 是否被 TUI 使用；只记录 loopback 地址和端口；
8. tmux socket、target、pane PID、1s/3s/10s capture-pane 快照；
9. TUI 进程真实 exit code、stderr/stdout、pane dead 时间；
10. 是否出现 `thread/started`，若没有，记录最后一个可见事件；
11. cleanup 后 PID 是否 dead、端口是否释放、临时 runtime 是否删除；
12. final-check → manifest → leak-scan 顺序，leak hits 必须为 0。

## 诊断纪律

- 先 observer/preflight，再启动唯一一次受控 TUI RUN。
- 业务失败不能通过重试变成 PASS。
- 不能把 app-server ready 当成 TUI 成功；必须有真实 `thread/started`。
- 不能把用户消息回显、terminal resource created 或 cleanup exit 当成 assistant PASS。
- 若 TUI pane 很快 dead，必须优先保存 pane 输出和 exit code，再做任何清理。
- 若某项无法审计，报告中明确 `INCONCLUSIVE`，不得猜测。

## 分类输出

只选一个主分类：

- `DIAG_TUI_ARG_OR_ENV`：argv/env/path/config 明确错误；
- `DIAG_TUI_EARLY_EXIT`：TUI 明确早退，有真实 exit/stderr；
- `DIAG_CODEX_REMOTE_HANDSHAKE`：TUI 存活但 remote 连接/协议失败；
- `DIAG_APP_SERVER_PROTOCOL`：app-server ready，但协议事件不完整；
- `DIAG_INCONCLUSIVE`：关键 observer、stderr、exit 或时间线不可审计。

不得输出 `Gate 2 PASS`、`mergeable` 或“产品已修复”。

## 交付

1. 唯一仓库交付：
   `docs/fixes/handoffs/HERMES_DIAGNOSIS_27.md`
2. evidence 根建议：
   `C:\Users\Administrator\omnigent-diagnostics\<RUN_ID>-hermes-codex-tui-observer-r1`
3. 报告必须包含：
   - 主分类和理由；
   - 旧成功 vs 本 RUN 的差异表；
   - argv/path/version/SHA/CODEX_HOME/PATH；
   - pane 快照、stderr、exit code、remote 连接结果；
   - `thread/started` 是否出现；
   - cleanup/leak-scan 证据；
   - 下一张实施卡应改哪个文件、哪一层，以及为什么不能在本卡改代码。

## 成功标准

本卡不是要求业务成功。只有以下证据完整，诊断才可接受：

```text
TUI argv + path/SHA
→ pane/process timeline
→ stderr/exit code
→ app-server ready/remote handshake
→ thread/started true/false
```

否则主分类必须是 `DIAG_INCONCLUSIVE`。

