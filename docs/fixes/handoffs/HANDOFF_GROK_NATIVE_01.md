# HANDOFF — grok-native（CODEX_TASK_GROK_NATIVE_01）

> 交接时间：2026-08-03（Windows）
> 交出方：Hermes（qwen3.8-max-preview / alibaba-coding-plan），**只读诊断角色**
> 状态：**实现暂停**——用户因额度不足要求先交接。尚未写任何 grok-native 源码 / 测试 / 注册 / 验收脚本。
> 任务卡：`F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\CODEX_TASK_GROK_NATIVE_01.md`
> 实现工作树：`F:\codex-ai\omnigent-zh-next`（分支 `integration/omnigent-zh-20260731`，交接时 `git status` 干净）

---

## 0. 一句话现状

WSL 已恢复可用、Grok CLI 机器接口已调查清楚、参考模块接入点已通读；**唯一硬阻塞是 Grok 在隔离 `GROK_HOME` 下未认证**（需用户本人登录，Hermes 不得代登录）。下一位 Agent 从「写失败测试 → 实现最小闭环 → 注册 dispatch → 定向回归 → WSL 真实双轮验收」开始，但第一步必须先复核认证状态。

---

## 1. 任务目标与硬约束（摘自任务卡，勿改）

- 新建可被其他 Agent 经 AgentCenter 调用的 **`grok-native-ui`**，底层用 WSL 内 Grok CLI 订阅 + `grok-4.5`。
- 保持 `~/.grok`、Claude、Qwen、Codex、OpenCodex(10100) **完全隔离**。
- 先调查 CLI 真实机器接口 → 写失败测试 → 实现最小闭环 → 注册/dispatch → 定向回归 → WSL 真实双轮验收 → AgentCenter 唤起验证 → 报告。
- **禁止**：修改 TUN、240s watchdog、其他 Agent；禁止 Gate 2、commit、push、merge、tag。
- **未认证时不得代用户登录**，只报告需执行的登录命令。
- 涉密一律 `[REDACTED]`，输出不得泄露 token/密码/密钥/连接串。

---

## 2. 已完成（含证据）

### 2.1 WSL 恢复（关键环境事实）
- inbox `C:\Windows\System32\wsl.exe` 报「系统找不到指定的路径。」exit=1 —— **不可用**。
- Store `C:\Program Files\WindowsApps\MicrosoftCorporationII.WindowsSubsystemForLinux_2.7.10.0_x64__8wekyb3d8bbwe\wsl.exe` 直接执行 Access is denied / rc=5 —— **不可用**。
- **可用 launcher：`C:\Program Files\WSL\wsl.exe`**（独立安装版）。
  - `--version` exit=0；`--list --verbose` exit=0；`Ubuntu-24.04` 状态 **Running**。
- 调用模板（MSYS/git-bash）：
  ```bash
  "/c/Program Files/WSL/wsl.exe" -d Ubuntu-24.04 -e bash -lc '<command>'
  ```
- WSL 内事实：user=`administrator`，node `v22.23.1`，grok 二进制存在。

### 2.2 Grok CLI 真实机器接口（v0.2.106，只读调查完成）
核心 headless 单轮 + 会话参数：
| 参数 | 作用 |
|---|---|
| `-p, --single <PROMPT>` | headless 单轮，stdout 输出 |
| `-s, --session-id <SESSION_ID>` | 指定新会话 UUID |
| `-r, --resume [<SESSION_ID>]` | 按 ID 恢复会话 |
| `-c, --continue` | 继续最近会话 |
| `--fork-session` | fork 会话 |
| `--output-format json\|streaming-json` | 结构化输出 |
| `--leader-socket <PATH>` | 自定义 leader socket（默认 `~/.grok/leader.sock`），可用于会话隔离 |
| `-m, --model <MODEL>` | 指定模型（默认 `grok-4.5`） |
| `--cwd <CWD>` | 工作目录 |
| `--max-turns <N>` | 轮数上限 |
| `--prompt-file <PATH>` / `--prompt-json <JSON>` | 备选 prompt 输入 |
| `--json-schema <SCHEMA>` | 结构化输出约束 |
| `--permission-mode <MODE>` / `--always-approve` / `--allow` / `--deny` | 工具策略 |

子命令：`grok agent stdio`、`grok agent headless`、`grok sessions list/search/delete`、`grok leader list/info/kill`、`grok models`（可当认证预检）、`grok inspect --json`。

**未认证信号（真实捕获，机器可读）**：
```json
{"type":"error","message":"Not signed in. To authenticate without a browser, run:\n  grok login --device-code\n\nAlternatively, set the XAI_API_KEY environment variable or run `grok login` on a machine with a browser."}
```
> ⚠️ **陷阱**：该未认证单轮探针进程退出码为 `single_json_rc=0`（**exit code = 0**）。**不能依赖 exit code 判断成功/失败，必须解析 stdout JSON 的 `"type":"error"`**。这是实现 executor 时必须处理的关键点。

### 2.3 认证预检（隔离 GROK_HOME）
- 隔离目录：`GROK_HOME=/home/administrator/.grok-omnigent`。
- `grok models`（隔离 HOME）输出：
  ```
  You are not authenticated.
  Default model: grok-4.5
  Available models:
    * grok-4.5 (default)
  ```
- 旧 `~/.grok` 仅做元数据存在性检查，**未读取内容**，保持隔离。

### 2.4 参考模块接入点（已通读）
| 文件 | 作用 |
|---|---|
| `omnigent/harness_plugins.py` | `HarnessContribution` 注册中心：`valid_harnesses`/`aliases`/`harness_modules`/`model_env_keys`/`spawn_env_builders`/`harness_labels`/`native_agents`/`native_providers`；`harness_catalog()`、`load_object()` |
| `omnigent/harness_aliases.py` | `canonicalize_harness`、`is_native_harness`、`native_terminal_name` |
| `omnigent/runtime/harnesses/__init__.py` | `_HARNESS_MODULES` 解析；`-native` 变体经此路由到 `create_app` |
| `omnigent/inner/hermes_harness.py` | **CLI_SUBPROCESS harness 模板**（thin `create_app`）——Grok 应对齐此形态 |
| `omnigent/inner/hermes_executor.py` | **headless CLI executor 模板**（per-session HOME + `clean_agent_env` 隔离） |
| `omnigent/inner/agent_env.py` | `clean_agent_env` 环境隔离 |
| `omnigent/native_coding_agents.py` | native coding agent registry |
| `omnigent/server/app.py` (≈430–678) | `NATIVE_CODING_AGENTS` seed + `_materialize_<key>_agent_spec` |
| `omnigent/server/routes/builtin_agents.py` | `/v1/agents` builtin agents 路由 |
| `omnigent/inner/executor.py` | Executor 基类 |
| `omnigent/inner/qwen_native_harness.py` / `qwen_native_executor.py` / `qwen_native_bridge.py` | qwen-native（**NATIVE_TUI/tmux 形态**，仅参考 bridge dir/env 注入，不作为 Grok 形态蓝本） |

### 2.5 关键架构决策
- **Grok 走 headless CLI_SUBPROCESS（对齐 `hermes` harness/executor），不走 qwen-native 的 NATIVE_TUI/tmux**。任务卡禁止伪造 native terminal / Windows tmux，且 Grok `-p --output-format json` 天然适合 headless。
- 命名拆解：任务卡要的 `grok-native-ui` 是 **AgentCenter 里可被唤起的 agent 名**；底层 harness 建议命名 `grok-native`（canonical，CLI_SUBPROCESS）。`-ui` 通过 native coding agent registry + server materialize 暴露为 agent，而非依赖 tmux pane。
- ⚠️ 未决：`grok-native-ui` 作为 agent 的确切 registry 落点（`native_coding_agents.py` vs `native_agents` contribution vs server seed）需下一位 Agent 依据任务卡原文与现有 `claude-native-ui` 落点确认。

---

## 3. 阻塞项

1. **Grok 未认证（硬阻塞，唯一）**：隔离 `GROK_HOME=/home/administrator/.grok-omnigent` 下未登录。真实双轮验收与 AgentCenter 唤起验证均被阻塞。
   - 需**用户本人**在 WSL 内执行其一：
     ```bash
     GROK_HOME=/home/administrator/.grok-omnigent grok login --device-code
     # 或
     export XAI_API_KEY=[REDACTED]
     ```
   - Hermes/下一 Agent **不得代登录**。
2. 尚未创建失败测试、grok-native 源码、dispatch 注册、AgentCenter 注册、验收脚本。
3. `tests/test_harness_dispatch.py` 不存在，需按任务卡新建。

---

## 4. 环境与工具链事实（避免重踩）

- Shell：MSYS/git-bash。PowerShell/cmd 内建不可用，用 POSIX。
- `wsl.exe` 输出常为 **UTF-16LE**，需 `iconv -f UTF-16LE -t UTF-8` 或写文件再转码。
- 跑 `.bat`：直接执行 `/c/temp/x.bat` 可靠；**勿用** `cmd.exe //c "C:\temp\x.bat"`（传参不可靠）。
- PowerShell：用 `-File C:/temp/x.ps1`（**正斜杠**），勿用反斜杠。
- Windows：`10.0.19045.3803`。
- Hermes 模型：`qwen3.8-max-preview`（provider `alibaba-coding-plan`）。**`qwen3.8-max-review` 不存在**（API 返回 `Model not exist.`），勿再尝试切换。`qwen3.8-max` 可用。
- `.env`（`E:\hermes\profiles\daimaxiufu\.env`）含 `ALIBABA_CODING_PLAN_API_KEY`、`DASHSCOPE_API_KEY`，值一律 `[REDACTED]`，勿读取/打印/提交。
- Omnigent backend 诊断时 `127.0.0.1:6767` 存活（`wslrelay.exe` PID 28820 监听）。

---

## 5. 下一位 Agent 的执行顺序

1. **复核认证**：`GROK_HOME=/home/administrator/.grok-omnigent grok models`。若仍 `You are not authenticated.` → 停下，只报告登录命令，不实现。若已认证 → 继续。
2. Task 1：写失败测试（dispatch / isolation / session 三组），新建 `tests/test_harness_dispatch.py`。
3. Task 2：实现最小 grok-native 闭环（harness thin `create_app` + headless executor，**解析 stdout JSON `"type":"error"`，勿信 exit code**；隔离 env 经 `clean_agent_env` + per-session HOME / `GROK_HOME`）。
4. Task 3：注册/dispatch——`harness_plugins` contribution（canonical `grok-native`）+ `_HARNESS_MODULES` + AgentCenter agent `grok-native-ui`（依现有 `claude-native-ui` 落点对齐）。
5. Task 4：定向测试 + 回归复跑（`pytest`）。
6. Task 5：WSL 真实双轮验收（预检认证 → 双轮 `--single`，第二轮 `--resume <id>` 或 `-s` 同 session 验证会话延续）。
7. Task 6：验证其他 Agent 可经 AgentCenter 唤起 `grok-native-ui`。
8. 写 `HERMES_DIAGNOSIS_GROK_NATIVE_01.md` + 四段式完成报告。

**红线（全程）**：不改 TUN / 240s watchdog / 其他 Agent；不 Gate 2、不 commit/push/merge/tag；不代登录；密钥 `[REDACTED]`。

---

## 6. 给下一位 Agent（Codex/Grok）的技术提示词

见本目录 `HANDOFF_GROK_NATIVE_01_NEXT_AGENT_PROMPT.md`。
