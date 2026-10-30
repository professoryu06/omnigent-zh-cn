# Omnigent 项目全过程、Gate 验收与源码基线

更新日期：2026-08-04  
项目主理：Codex  
交付仓库：`github.com/professoryu06/omnigent-zh-cn.git`  
Gate 2 基线：`5c8b9ce96f7552d380276fe6de04651f2b19531a`

## 一、当前结论

- Gate 2 六轮验收：**GATE2_PASS**。
- Gate 2 RUN：`20260803-232354-gate2-sixrounds-r5`。
- Evidence：`C:\Users\Administrator\omnigent-diagnostics\20260803-232354-gate2-sixrounds-r5\`。
- Gate 2 证明的是冻结基线上的 AgentCenter C/E/R 六轮行为，尤其是 `codex-native` Phase 2 prompt apply。
- Gate 1：r1 判定 **GATE1_INCONCLUSIVE**，因为当前环境 `wsl.exe -l/-d` 返回“系统找不到指定的路径”，尚未进入 Linux 全仓测试；当前仍不可 merge、不可宣称全仓 GREEN。
- `claude-native` 仍为 warn-only；本轮没有把它宣称为真实 prompt 已送达。

## 二、项目经过（按问题演化）

### 1. D0/D1 基线阶段

早期诊断先验证 native Codex CLI 的身份、D0 sentinel 和 D1 assistant/turn 完成语义。阶段 14 暴露 app-server 协议边界：D0 能过，但 D1 没有真实 assistant item；后续阶段 15、17 固定 native CLI 0.146.0，建立了可审计的 D0/D1 PASS。

经验：用户消息回显、title 或 cleanup exit 都不能当作 assistant PASS；业务 exit 必须和清理 exit 分开；每次返工必须新 RUN_ID、新 evidence，不能拼接旧证据。

### 2. D2、agent pipeline 与 HTTP/session 阶段

阶段 18 发现 runner 没有 spawn，且 `config.yaml missing required field: spec_version`；阶段 19 证明离线路径六层配置不会丢失 `spec_version`，但 observer 的形式 required-check 失败，因此保留 `INCONCLUSIVE` 边界；阶段 20 的 HTTP/session roundtrip 证明 POST、agent GET、contents GET 以及五层 SHA 一致，问题收窄到产品 runner/CLI 链路而不是配置传输。

经验：先把配置、bundle、artifact、AgentCache 和 observer 单独验通，再进入产品 C/D2；零样本负向必须是独立证据，不能混入正向 live stream。

### 3. BUG-1/2/3 修复阶段

审查确认并纳入基线的修复包括：

- **BUG-1：Windows GBK 崩溃**。连接提示改为 ASCII；runner/daemon 环境 allowlist 增加 `PYTHONUTF8`、`PYTHONIOENCODING`；不使用全局 `errors="replace"` 掩盖错误。
- **BUG-2：裸 `codex` 误进 tmux/native terminal**。裸 `codex` 路由到 SDK harness；只有显式 `codex-native` 才允许 native terminal；Windows 继续拒绝 tmux/PTY，不伪造支持；unknown harness 保持兼容性 fail-open。
- **BUG-3：multipart session 不启动 runner**。multipart `host_id` 创建路径与 JSON 语义对齐，完成 workspace 校验、原子绑定和 runner launch。

定向回归曾达到 13、18、96 passed 等阶段性结果；最终 Gate 2 使用冻结基线的独立六轮，不把单次 full-run 当作 Gate 2。

### 4. Codex/OpenCodex 隔离与 TUN 阶段

发现 `~/.codex/config.toml` 被 OpenCodex 注入 `127.0.0.1:10100` 和非目标模型，导致 Omnigent Codex CLI 与 OpenCodex 冲突。隔离方案采用私有 `CODEX_HOME`、配置清洗、模型/网关覆盖和环境 deny/allow 规则，确保：

- OpenCodex 可继续使用，不杀 bun、不释放 10100；
- Omnigent 使用独立的 Codex subscription 路径；
- 不读取或污染用户主 `config.toml`。

随后确认 Windows Rust CLI 与 Clash TUN fake-IP 存在网络瞬态风险；Route-A 代理注入并未被接受为最终修复。WSL/tmux 是 native PTY 的稳定运行环境。阶段 27/28 的对照显示，Codex TUI 启动期 `raw.githubusercontent.com` 偶发 60 秒阻塞会撞上 30 秒 runner 窗口，但受控重跑和 28A/28B 已证明当前链路能够正常建立 thread、模型流和 `CONTROLLER_OK`。

### 5. Gate 2 前置、冻结与六轮验收

- 28C：清理 28A/28B 归属的 app-server/TUI/runner 进程，确认端口释放和无真实孤儿；OpenCodex/10100 未触碰。
- 28D：选择 `omnigent-review` 中文交付仓作为 Gate 2 基线，`omnigent-zh-next` 仅作上游参考/实验场。
- 冻结提交：源码修复 `e691d08`，文档与 handoff `c3c4eba`，冻结记录 `5c8b9ce`。
- r5 六轮：C、E-pos、E-pos-strict、E-neg-warn、E-neg-strict、R 全部按独立 workspace 执行；Codex-native receipt 的字符数/SHA 与实际 prompt 一致；Claude-native 严格模式按设计 fail-loud。
- 环境清理和 verification 链均 PASS；最终签字为 **GATE2_PASS**。

## 三、Gate 2 实际修复/验证了什么

Gate 2 不是一次普通聊天测试，而是验证 AgentCenter 的执行语义：

1. 角色配置能正确解析成 `claude-sdk`、`codex-native` 等 harness。
2. 不同 agent 使用独立 workspace 和 sentinel。
3. `codex-native` 的 prompt 通过私有 `codex-home/config.toml` 的 `developer_instructions` 送达，并由 receipt SHA 证明。
4. 严格环境变量能传入 runner；失败路径不会假装成功。
5. Claude-native 的能力边界会明确告警，而不是静默声称 prompt 已应用。
6. runner、server、host 和 cleanup 的证据可以独立审计。

## 四、源码基线与关键文件

### Commit 1：`e691d08`

主题：`codex isolation, prompt delivery fail-loud, ws_tunnel, session and workspace fixes`。共 44 个源码/测试文件，关键生产文件：

- `omnigent/inner/codex_executor.py`：私有 Codex 环境、OpenCodex/10100 隔离、配置清洗和订阅路径。
- `omnigent/inner/native_prompt_delivery.py`：native prompt 能力矩阵和 fail-loud 规则。
- `omnigent/codex_native_app_server.py`：Codex app-server 转发与启动边界。
- `omnigent/harness_aliases.py`：裸 `codex` 与显式 `codex-native` 分流。
- `omnigent/runner/app.py`：session/terminal guard、runner 状态和 native 路由。
- `omnigent/server/routes/sessions.py`：JSON/multipart session 创建与 runner launch。
- `omnigent/server/routes/_workspace_validation.py`：workspace 和权限校验。
- `omnigent/runner/transports/ws_tunnel/serve.py`：WebSocket/tunnel 生命周期。
- `omnigent/host/connect.py`、`omnigent/cli.py`：Windows 编码和 daemon 环境转发。
- `omnigent/inner/codex_native_executor.py` 及其他 native executor：统一 prompt 能力提示。

配套测试覆盖 Codex isolation、native prompt delivery、harness dispatch、terminal ensure、multipart host launch、workspace cache、runner idle-active work、WS tunnel 和 Windows host connect。

### Commit 2：`c3c4eba`

主题：冻结 Gate 规则、STATUS、进度/清理/WSL 文档以及完整 handoff 链。所有诊断报告和任务卡仍保留在 `docs/fixes/handoffs/`，不删除旧 RUN。

### Commit 3：`5c8b9ce`

主题：记录 Gate 2 基线冻结 SHA 和 manifest。后续 Gate 2 验收必须从该 SHA 的独立 worktree 运行。

## 五、证据与文档保存规则

- 原始 evidence 永久保留在 `C:\Users\Administrator\omnigent-diagnostics\`，不复制凭据、不删除旧 RUN。
- 仓库原始任务卡/诊断/验收记录在 `docs/fixes/handoffs/`。
- Obsidian 只保存项目摘要、源码索引、证据路径和经验，不保存 token/auth 内容。
- 每次返工必须使用新 RUN_ID；旧 RUN 只能作为背景，不能拼接成新结论。
- 任何“PASS”必须说明范围：D0/D1、单次 full-run、Gate 2 或 Gate 1，不能混用。

## 六、当前待办

1. 修复/恢复 Ubuntu-24.04 WSL，使 `wsl -d Ubuntu-24.04 -- uname -a` 成功；本次 r1 evidence：`C:\Users\Administrator\omnigent-diagnostics\20260804-001420-5c8b9ce-grok-gate1-r1\`。
2. 在全新 clean Linux/WSL worktree 上重开新 RUN_ID，完成 Gate 1 全仓 pytest、Ruff、compile，并与 clean main 做新增失败对比。
3. 若 Gate 1 无新增失败，整理并提交本轮 STATUS/BASELINE/handoff 文档。
4. 做独立 merge-readiness 审查；在此之前不可 merge/push/tag。
5. 后续产品化再处理：Claude-native 真正 prompt apply、DELETE session 子进程回收、Windows REPL unsupported terminal 噪声，以及 TUN 网络瞬态韧性。

## 七、最终边界

当前准确表述是：**Gate 2 已通过，Gate 1 r1 为 INCONCLUSIVE（WSL 不可用），项目不可 merge。** 只有 WSL 恢复后的 Gate 1、工作树整理、merge-readiness 和用户最终批准全部完成，才可以进入发布或合并流程。
