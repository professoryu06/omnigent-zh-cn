# CODEX_TASK_28_PLAN — Codex TUI 启动期远程握手韧性与网络监控方案

日期：2026-08-03  
角色：Codex 只读审查/规划；本文件不授权实施、测试或修改 TUN。

## 1. 审查结论

### 1.1 机制结论

对现有证据的机制审查结论为：**ACCEPT_WITH_NOTES**。

证据足以支持以下主分类：`DIAG_CODEX_REMOTE_HANDSHAKE`。

- 失败侧的 Codex TUI 进程仍存活，但在 runner 的 30 秒等待窗口内没有建立 remote 连接并产生 `thread/started`。
- `task27-run-r2\success-vs-fail-timeline.txt` 与 `tui-bootstrap-diff.txt` 的时间关系支持：启动期网络等待约 58–63 秒，而失败侧的等待落在 `Auto-created` 之后的 30 秒窗口内；成功侧则在窗口开始前吸收了主要等待。
- 受控 RUN `r27-observer-20260803-hermes-codex-tui-observer-r1\tui-timeline.txt` 显示同一 0.144.4 binary、同一启动参数/私有 `CODEX_HOME` 下，`raw.githubusercontent.com` 约 2 秒完成，probes 约 5.2 秒完成，`thread/start` 约 8.65 秒出现，并继续进入 `gpt-5.6-sol` 模型流。这排除了“参数/环境必然错误”和“app-server 协议必然不兼容”。

因此，当前最准确的大白话是：**Codex 本身能启动，偶发被启动阶段的远程同步网络等待拖过了 Omnigent 的握手窗口；这是网络瞬态与启动时序耦合，不是已经证明的稳定代码缺陷。**

### 1.2 必须先修正的审计缺口

`HERMES_DIAGNOSIS_27.md` 不是冻结一致的报告：

1. 开头写“用户因额度中止，未执行受控 RUN”，主分类写 `DIAG_INCONCLUSIVE`；
2. 后文 §9 又写明执行了 `r27-observer-20260803`，并给出成功的 `thread/start`、模型流和 cleanup；
3. 后文分类定案又改为 `DIAG_CODEX_REMOTE_HANDSHAKE`；
4. `observer.log` 中的 `[obs] TUI_PID ... exited at t=4` 与 `final-procs.txt` 的 pane PID `dead=0`、以及持续到 28 秒以上的 TUI 时间线不一致，疑似观察脚本追踪了错误的父 PID，但需要在报告中明确解释。

所以：**接受证据支持的机制结论，不接受当前报告文本作为已冻结的单一版本。** 在进入实现卡前，须由诊断交付者重写报告头部/结论，保留受控 RUN 的唯一 RUN_ID，并说明 PID 记录差异。若严格要求“报告文本本身单分类且无矛盾”，在修订前应暂记 `DIAG_INCONCLUSIVE`，而不是把它当成新代码缺陷。

### 1.3 “阻塞落点决定成败”的边界

这个判断在时间线上成立，但它描述的是**触发条件**，不是唯一根因：

- 远程请求慢于 30 秒且落在 `thread/started` 等待窗口内，会导致 runner 先超时并终止 app-server；
- 同样的慢请求若发生在窗口开启前，可能被 launch 阶段吸收，后续仍能成功；
- 因此真正需要治理的是“可选远程同步不能阻塞 TUI 建立 thread”，以及网络规则对该域名的稳定性，而不是简单把 30 秒改大。

## 2. 监控计划（只观察，不执行配置变更）

下一次用户从 Web UI 重试 Codex 时，建立一个新的、独立的 RUN_ID；不得拼接旧 evidence。记录以下时间戳（统一 UTC 或本地时区并在 manifest 声明）：

| 监控项 | 观察内容 | 判定信号 |
|---|---|---|
| TUI 启动网络 | `raw.githubusercontent.com` 的解析、fake-IP、TCP/TLS、请求完成/超时 | 完成时间 ≤10s 为正常；>30s 或无完成事件为启动阻塞 |
| Clash/TUN 规则 | 只读记录该域命中的规则、代理/直连、fake-IP 映射和错误 | 规则改变或落入直连是网络侧线索；不改规则、不关 TUN |
| app-server | listening、readyz、WebSocket client connected、`thread/start` | app-server ready 但无 client/thread 是 TUI/网络握手问题 |
| runner 窗口 | `Auto-created`、等待开始、30s timeout、kill 的相对顺序 | 证明阻塞是否落在 30s 窗口内 |
| bridge | `state.json`、`server.json`、`startup_error.json` 的出现时间和内容 | state/server 在 timeout 前出现是修复生效信号；只出现 startup_error 是失败信号 |
| 进程/cleanup | TUI、app-server、tmux pane 的真实 PID、退出码、dead 状态 | 父 PID 与 pane PID 必须分别记录，避免复现 observer.log 的歧义 |

监控 RUN 的最低可审计文件：`run-meta`、完整 argv/path/SHA、TUI timeline、app-server stdout/stderr、runner log、bridge 文件时间线、pane PID/exit、final-check、cleanup、leak-scan。凭据全部 `[REDACTED]`。

建议使用三个互斥结果：

1. **READY**：raw 请求完成、probes 完成、`thread/start` ≤30s；无需代码修复，可进入一次产品 full-run；
2. **NETWORK_STALL**：raw 请求或同类远程同步 >30s，且 `thread/start` 缺失；进入网络规则卡；
3. **PROTOCOL_OR_LAUNCH**：远程请求 ≤10s、app-server ready，但仍无 WebSocket/thread；才进入 Omnigent 启动链代码卡。

## 3. 下一张实施卡的方案边界

### 3.1 网络侧优先方案

另发网络实施卡，针对当前 Clash 配置中 `raw.githubusercontent.com` 的实际规则添加**域名级代理放行**（例如现有配置语法中的 `DOMAIN-SUFFIX`/等价规则，目标为现有代理节点），而不是全局改成直连、关闭 fake-IP 或关闭 TUN。具体文件和行号必须由实施者先读取当前生效配置后填写，不能凭空猜路径。

验收：在 TUN 保持开启、OpenCodex/10100 不动的情况下，新 RUN 中该域名请求稳定完成，TUI 在 30 秒内产生 `thread/start`。只允许影响该域名的路由，需保留回滚前后配置摘要和 checksum。

### 3.2 产品侧韧性方案（网络卡无效或仍有偶发阻塞时）

先确认 Codex CLI 0.144.4 是否支持关闭/降级远程插件同步的配置键；不得自行发明键名。若确认支持，实施卡可在 Omnigent 生成的**私有 session `CODEX_HOME`** 中增加可配置的 `remote_plugin_sync=off|best-effort`（具体键名以 CLI 0.144.4 文档/日志为准），不触碰用户 `~/.codex/config.toml`。

Omnigent 侧候选改动范围：

- `omnigent/codex_native_app_server.py:560-678`：构造私有 `CODEX_HOME`、写入 session config、启动 app-server 的入口；只允许在私有配置中注入经过 CLI 验证的远程同步策略，并记录脱敏的策略值；
- `omnigent/codex_native_forwarder.py:6429-6459`（常量 `:67`）：保留 30 秒语义，增加“远程启动阻塞/无 client/无 thread”可区分的错误与 elapsed telemetry；**不得把增大 `_THREAD_START_TIMEOUT_SECONDS` 当修复**；
- 如需处理可选同步失败，优先在 app-server 启动链暴露 fail-open/快速失败状态，而不是延迟或吞掉 `thread/started`。

若 CLI 没有受支持的关闭/降级开关，则不应在 Omnigent 中模拟或拦截 Codex 内部请求；此时唯一安全方向仍是 Clash 域名规则，或升级到有该开关的受控 CLI 版本（须另卡、另证据）。

### 3.3 不建议的方向

- 不调大 `_THREAD_START_TIMEOUT_SECONDS` 作为修复；这只会把失败推迟，并可能放大资源泄漏窗口。
- 不改 `~/.codex/config.toml`、不杀 OpenCodex、不释放/占用 10100、不关闭或切换 TUN。
- 不把一次成功的 r27 observer RUN 写成 Gate 2 PASS、全仓 GREEN 或 mergeable。

## 4. 实施顺序与通过门槛

1. **先修订 HERMES_DIAGNOSIS_27.md**：统一为受控 RUN 的唯一结论，解释 observer PID 差异；保留全部 evidence，不重跑旧 RUN。
2. **只读监控卡**：用户下一次 Web UI 重试，完成第 2 节的时间线和 Clash 规则观察。
3. 若结果为 `NETWORK_STALL`，先做域名级 Clash 规则实施卡；若为 `READY`，不改源码，直接进入单次 full-run 卡。
4. 仅当规则已正确且仍出现 `PROTOCOL_OR_LAUNCH`，才开产品侧韧性实施卡，新增针对私有 CODEX_HOME/远程同步策略的测试。
5. 实施后再开单次 full-run；full-run 通过也不等于 Gate 2 PASS。

## 5. 当前边界

- Gate 1 仍为相对 main 的 PASS，非全仓 GREEN；
- Gate 2 仍未签字，不可 merge；
- 本计划不改源码、不改配置、不重跑测试、不删除 evidence。

