# CODEX_TASK_GROK_NATIVE_01 — 新建可调度的 Grok Native

> 执行者：Hermes 3.8
>
> 类型：实现、定向测试、一次真实双轮验收

## 目标

在 Omnigent 中新增一个与 claude-native、qwen-native、codex-native 同级的 grok-native Agent。Controller 和其他 Agent 必须通过 AgentCenter 调度它，完成 Grok CLI 订阅路径的多轮会话。

本任务使用 WSL 内已有 Grok CLI，不改成 xAI API-key provider：

    Grok CLI 0.2.106
    model = grok-4.5

## 当前基线

- 工作树：F:\codex-ai\omnigent-zh-next
- WSL 路径：/mnt/f/codex-ai/omnigent-zh-next
- Omnigent server：http://127.0.0.1:6767
- WSL：Ubuntu-24.04，tmux 3.4，Node.js 22.23.1
- Grok CLI：/home/administrator/.local/opt/node-v22.23.1-linux-x64/bin/grok
- 当前内置 Agent 列表没有 grok-native
- 旧日志中的 grok-code 不算当前有效 Agent
- ~/.grok 中旧 OIDC 登录可能已过期；未认证时必须请求用户登录

## 硬约束

1. 不修改、删除或迁移用户原有 ~/.grok。
2. Grok Native 使用独立目录：GROK_HOME=/home/administrator/.grok-omnigent。
3. Grok 子进程不得继承或读取 ANTHROPIC_*、DASHSCOPE_*、OPENAI_*、Codex 私有 CODEX_HOME，不得访问 OpenCodex 127.0.0.1:10100。
4. 代理只作用于 Grok 子进程；不得修改 TUN、Clash Verge、全局代理或其他 Agent。
5. Grok CLI 未认证时，不得自动登录或复制 auth 文件；只报告用户执行：
   
       GROK_HOME=/home/administrator/.grok-omnigent grok login

6. 不跑完整 Gate 2，不改 240s idle watchdog，不改认证政策。
7. 不修改 Qwen、Claude、Codex 行为；不改既有测试期望。
8. 不提交、推送、合并或打 tag；凭据一律写成 [REDACTED]。

## 先调查真实 CLI 接口

完整读取并参考：

    omnigent/inner/qwen_native_harness.py
    omnigent/inner/qwen_native_executor.py
    omnigent/qwen_native.py
    omnigent/qwen_native_bridge.py
    omnigent/harness_plugins.py
    omnigent/cli_native.py
    omnigent/runner/native.py
    omnigent/runtime/harnesses/_runner.py

只读执行：

    grok --help
    grok agent --help
    grok sessions --help
    grok --version

确认稳定机器接口后再实现：

1. 优先使用 grok --single 配合 --session-id/--resume，若能保持同一会话。
2. 若 grok agent 或 leader/JSON 接口提供稳定双向流，可使用该接口。
3. 不得用屏幕抓取、固定 sleep 或复制 ~/.grok 伪造协议。

没有稳定可审计接口时，停止实现并报告 DIAG_INCONCLUSIVE。

## 目标架构

### Agent 注册

新增：

    agent_name = grok-native-ui
    harness    = grok-native
    display    = Grok
    model      = grok-4.5

它必须出现在内置 Agent 列表、/v1/agents、harness capability/dispatch 目录和 Controller 可选路由中。不得把裸 grok 映射为 codex-native、openai-agents 或 Windows tmux/native terminal。

### 进程与认证隔离

每个会话至少拥有：

    GROK_HOME=/home/administrator/.grok-omnigent[/sessions/<session-id>]
    model = grok-4.5
    NO_PROXY=127.0.0.1,localhost

如当前 TUN 需要桥接代理，只给 Grok 子进程设置：

    HTTPS_PROXY=http://172.31.80.1:17892
    HTTP_PROXY=http://172.31.80.1:17892
    ALL_PROXY=http://172.31.80.1:17892

不要把 GROK_CLI_CHAT_PROXY_BASE_URL 当作普通网络代理；除非调查证明订阅 CLI 必须使用它，否则不要设置。

其他 Agent 只能通过 AgentCenter/Omnigent dispatch 调用 grok-native-ui，不能共享 Grok 进程、tmux pane、leader socket 或 ~/.grok 文件。

## 实施任务

### Task 1：先写失败测试

新增测试至少覆盖：

- grok-native registry/module/alias 可解析。
- grok-native-ui 出现在 builtin agents 和 /v1/agents。
- spawn env 含独立 GROK_HOME、grok-4.5 和必要代理变量。
- spawn env 不含 Claude/Qwen/Codex/OpenCodex 变量。
- 两个 session 的 GROK_HOME、leader socket、session id 不相同。
- 未登录时返回清晰 auth-required 错误，绝不泄漏 token。

建议文件：

    tests/test_grok_native_dispatch.py
    tests/inner/test_grok_native_isolation.py
    tests/runner/test_grok_native_session.py

### Task 2：实现最小 Grok Native 闭环

按 Qwen Native 的模块边界新增必要文件，例如：

    omnigent/inner/grok_native_harness.py
    omnigent/inner/grok_native_executor.py
    omnigent/grok_native.py
    omnigent/grok_native_bridge.py

只实现启动、发送用户消息、接收真实 assistant 输出、完成事件、错误、取消和 resume；不要顺便重构其他 harness。若采用 --single/--resume，必须保存并复用 session id，不得每轮新开无上下文会话。

### Task 3：接入注册和 UI

按 Qwen Native 的真实接入点修改：

    omnigent/harness_plugins.py
    omnigent/harness_aliases.py（仅确有需要时）
    omnigent/cli_native.py（仅确有需要时）
    omnigent/runner/native.py（仅终端启动确有需要时）

若实现采用 headless CLI 子进程，不要伪造 native terminal 资源。Windows 不得调用 tmux/PTY；真实 Grok 测试必须在 WSL host 上运行。

### Task 4：定向测试

    cd /mnt/f/codex-ai/omnigent-zh-next
    .venv/bin/python -m pytest tests/test_grok_native_dispatch.py tests/inner/test_grok_native_isolation.py tests/runner/test_grok_native_session.py tests/test_harness_plugins.py tests/test_harness_dispatch.py -q

随后复跑：

    .venv/bin/python -m pytest tests/inner/test_codex_runtime_isolation.py tests/test_harness_dispatch.py tests/runner/test_codex_terminal_ensure_guard.py tests/host/test_connect.py tests/cli/test_backend.py -q

不得修改既有测试期望来掩盖回归。

### Task 5：真实 WSL 双轮验收

预检（不打印密钥）：

    GROK_HOME=/home/administrator/.grok-omnigent grok --version
    GROK_HOME=/home/administrator/.grok-omnigent grok models

未认证就停止，并报告用户执行登录命令。认证成功后创建全新 RUN_ID/evidence，通过 Omnigent grok-native-ui 在同一会话发送：

    第一轮：Reply with GROK_NATIVE_OK and stop.
    第二轮：Reply with GROK_NATIVE_FOLLOWUP_OK and stop.

成功标准：

- 两个 sentinel 都来自真实 assistant item，不接受 user 回显或标题。
- 第二轮复用同一 session 成功。
- 模型记录为 grok-4.5。
- session 最终 idle/completed。
- 无 Windows tmux 崩溃、无 127.0.0.1:10100 连接。
- Grok 子进程无 Claude/Qwen/Codex 凭据。
- evidence 实时落盘、cleanup 完成、leak-scan hits=0。

### Task 6：验证其他 Agent 可唤起 Grok

执行一次最小 Controller/AgentCenter 调度：由一个现有 Agent 请求 grok-native-ui 回复固定 sentinel，并记录 caller、target、session id、dispatch 时间线和 assistant item 来源。

## 交付物

1. Grok Native 源码和定向测试 diff。
2. docs/fixes/handoffs/HERMES_DIAGNOSIS_GROK_NATIVE_01.md，包含 CLI 接口调查、隔离清单、测试命令和结果、RUN_ID/evidence、是否需要用户登录及失败分类。
3. 不修改旧 diagnosis，不拼接旧 evidence。
4. 不 commit/push/merge/tag。

## Gate 边界

grok-native 通过不等于 Gate 1/Gate 2 通过；单次 full-run 不等于全仓 GREEN，不可据此 merge。若需要大范围 runner 生命周期改造，停止并另开 Hermes 实施卡。
