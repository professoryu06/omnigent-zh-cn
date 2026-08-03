# NEXT-AGENT PROMPT — grok-native（CODEX_TASK_GROK_NATIVE_01 续作）

> 用途：把本文件全文作为下一位实现 Agent（Codex/Grok）的任务提示词。技术语言，无大白话。

---

## PROMPT START

你接管 `CODEX_TASK_GROK_NATIVE_01`（任务卡：`F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\CODEX_TASK_GROK_NATIVE_01.md`；交接文档：同目录 `HANDOFF_GROK_NATIVE_01.md`）。实现工作树：`F:\codex-ai\omnigent-zh-next`，分支 `integration/omnigent-zh-20260731`。Hermes 已完成只读调查，未写任何实现代码。

### 环境事实（已验证，直接使用，勿重复探测）
- WSL launcher（唯一可用）：`C:\Program Files\WSL\wsl.exe`。inbox `System32\wsl.exe` 报「系统找不到指定的路径。」；Store WindowsApps 版 rc=5。调用模板（MSYS）：`"/c/Program Files/WSL/wsl.exe" -d Ubuntu-24.04 -e bash -lc '<cmd>'`。wsl.exe 输出可能 UTF-16LE，需转码。
- WSL 内：user=`administrator`，node `v22.23.1`，grok CLI `0.2.106`。
- 隔离认证目录：`GROK_HOME=/home/administrator/.grok-omnigent`。旧 `~/.grok` 不得读写。

### Grok CLI 机器接口（v0.2.106，已调查）
- headless 单轮：`grok -p <PROMPT> -m grok-4.5 --output-format json`
- 会话：`-s <UUID>` 新建；`-r [<SESSION_ID>]` 恢复；`--leader-socket <PATH>` 会话隔离
- 其他：`--cwd`、`--max-turns`、`--json-schema`、`--permission-mode`；子命令 `agent stdio|headless`、`sessions list/search/delete`、`leader list/info/kill`、`models`（可作认证预检）、`inspect --json`
- **未认证信号**：stdout JSON `{"type":"error","message":"Not signed in. ..."}`，且 **exit code = 0**。判定失败必须解析 stdout JSON `"type":"error"`，不得依赖退出码。
- 认证预检命令：`GROK_HOME=/home/administrator/.grok-omnigent grok models`；未认证输出含 `You are not authenticated.`

### 第一步（强制门）
执行认证预检。若未认证：**立即停止实现**，仅输出需用户执行的登录命令（`GROK_HOME=/home/administrator/.grok-omnigent grok login --device-code` 或 `export XAI_API_KEY=[REDACTED]`），不得代登录、不得写代码。已认证才进入实现。

### 架构决策（已定，勿推翻）
- 形态：headless **CLI_SUBPROCESS**（对齐 `omnigent/inner/hermes_harness.py` + `omnigent/inner/hermes_executor.py`），**不是** qwen-native 的 NATIVE_TUI/tmux。禁止伪造 native terminal。
- harness canonical id：`grok-native`；AgentCenter 暴露 agent 名：`grok-native-ui`。
- 隔离：spawn env 经 `omnigent/inner/agent_env.py:clean_agent_env` + per-session `GROK_HOME`；`--leader-socket` 指到 per-session 路径，避免与真实 `~/.grok/leader.sock` 串扰。

### 参考接入点（已通读）
- `omnigent/harness_plugins.py` — `HarnessContribution`（`valid_harnesses`/`aliases`/`harness_modules`/`model_env_keys`/`spawn_env_builders`/`harness_labels`/`native_agents`/`native_providers`）
- `omnigent/runtime/harnesses/__init__.py` — `_HARNESS_MODULES`
- `omnigent/harness_aliases.py` — `canonicalize_harness`/`is_native_harness`
- `omnigent/native_coding_agents.py` — native coding agent registry
- `omnigent/server/app.py`（≈L430–678）— `NATIVE_CODING_AGENTS` seed + `_materialize_<key>_agent_spec`
- `omnigent/server/routes/builtin_agents.py` — `/v1/agents`
- 待确认：`grok-native-ui` 的确切 registry 落点，以现有 `claude-native-ui` 落点为对齐基准。

### 执行顺序
1. Task 1：新建 `tests/test_harness_dispatch.py`，写 dispatch / isolation / session 三组失败测试（RED）。
2. Task 2：最小闭环——thin `create_app()` harness 模块 + headless executor（spawn env 隔离 + JSON 错误解析 + session 管理）。
3. Task 3：注册 contribution（canonical `grok-native`）+ `_HARNESS_MODULES` + AgentCenter agent `grok-native-ui`。
4. Task 4：定向测试 GREEN + 回归复跑 `pytest`。
5. Task 5：WSL 真实双轮验收（轮 1 `-s <uuid>`，轮 2 `-r <uuid>` 验证会话延续；预检认证先行）。
6. Task 6：验证其他 Agent 经 AgentCenter 可唤起 `grok-native-ui`。
7. 产出 `HERMES_DIAGNOSIS_GROK_NATIVE_01.md` + 四段式完成报告。

### 红线
- 禁止修改 TUN、240s watchdog、其他 Agent 的任何代码。
- 禁止 Gate 2、commit、push、merge、tag。
- 未认证不代登录；凭据一律 `[REDACTED]`；输出不得泄露 token/密钥/连接串。
- 不读取旧 `~/.grok` 内容。

## PROMPT END
