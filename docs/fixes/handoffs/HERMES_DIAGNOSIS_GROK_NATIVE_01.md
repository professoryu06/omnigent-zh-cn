# HERMES_DIAGNOSIS_GROK_NATIVE_01 — Grok Native 实现与验收报告

> 日期：2026-08-03（Windows + WSL Ubuntu-24.04）
> 执行者：Hermes（qwen3.8-max-preview → deepseek-v4-flash）
> 任务卡：`F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\CODEX_TASK_GROK_NATIVE_01.md`
> 状态：**全部 6 个 Task 完成，真实双轮验收 PASS，AgentCenter 唤起验证 PASS**
> 未 commit / push / merge / tag（符合任务卡红线）

---

## 1. CLI 接口调查结论（只读，已实测）

Grok CLI **0.2.106**（WSL Ubuntu-24.04，node v22.23.1）：

| 参数 | 作用 | 验收实测 |
|---|---|---|
| `--single <PROMPT>`（`-p`） | headless 单轮 | ✅ 双轮验收使用 |
| `--session-id <UUID>` | 新建会话指定 UUID | ✅ 第一轮使用 |
| `--resume [<ID>]` | 恢复会话 | ✅ 第二轮使用，**同一 sessionId 复用** |
| `--output-format json` | **单个多行 JSON 对象**（无 type 字段，含 text/sessionId/modelUsage） | ✅ 实测解析 |
| `--output-format streaming-json` | JSONL 流（type 判别） | ✅ 解析器兼容 |
| `--leader-socket <PATH>` | 自定义 leader socket（默认 ~/.grok/leader.sock） | ✅ per-session 隔离 |
| `-m <MODEL>` | 模型（默认 grok-4.5） | ✅ 记录 grok-4.5-build |
| `--cwd` / `--max-turns` | 工作目录 / 轮数上限 | 支持 |
| `grok models` | 认证预检 | ✅ 用于登录确认 |
| `grok login --device-code` | 无浏览器登录 | ✅ 用户已执行 |

**关键坑（实现中已处理）**：
1. **未认证时 exit code = 0**——不能信退出码，必须解析 stdout JSON 的 `type:"error"` / `Not signed in`。
2. **`--output-format json` 是单个多行 JSON 对象**，不是 JSONL——解析必须先整体 `json.loads`，失败再逐行扫（streaming-json 兼容）。
3. grok 的 auth 文件是 `$GROK_HOME/auth.json`；per-session GROK_HOME 子目录必须 symlink 根 auth.json 才能认证。

## 2. 隔离清单（全部满足）

- ✅ `GROK_HOME=/home/administrator/.grok-omnigent/sessions/<session-id>`（per-session 子目录）
- ✅ per-session `--leader-socket`（`<GROK_HOME>/leader.sock`）
- ✅ 确定性 grok session id：UUIDv5(conversation_id)，稳定可恢复
- ✅ `NO_PROXY=127.0.0.1,localhost` 强制
- ✅ 代理仅当 `OMNIGENT_GROK_PROXY` 设置时注入（HTTPS/HTTP/ALL_PROXY）
- ✅ spawn env deny-by-default：`clean_agent_env` 基座 + `GROK_`/`XAI_` 家族，**不含** ANTHROPIC_/DASHSCOPE_/OPENAI_/CODEX_/OPENCODE_
- ✅ 不读取、不写入用户真实 `~/.grok`（只 symlink 隔离根 auth.json，引用非复制）
- ✅ 不修改 TUN / 240s watchdog / 其他 Agent

## 3. 实现文件

| 文件 | 内容 |
|---|---|
| `omnigent/inner/grok_native_harness.py` | thin `create_app()`（headless CLI_SUBPROCESS 形态，对齐 hermes_harness） |
| `omnigent/inner/grok_native_executor.py` | `GrokNativeExecutor`：spawn `grok --single --output-format json`、JSON 解析（整体+逐行双策略）、auth-required 错误、session 管理 |
| `omnigent/grok_native.py` | `run_grok_native` + `_materialize_grok_agent_spec`（daemon 会话创建路径） |
| `omnigent/grok_native_bridge.py` | session id / GROK_HOME / leader socket / auth symlink / `build_grok_native_spawn_env` |
| `omnigent/harness_plugins.py` | 注册 `grok-native` harness（valid_harnesses/harness_modules/capabilities=CLI_SUBPROCESS/harness_labels/model_env_keys） |
| `omnigent/_wrapper_labels.py` | `GROK_NATIVE_WRAPPER_VALUE = "grok-native-ui"` |
| `omnigent/server/app.py` | `_ensure_default_grok_agent` seed（agent 列表 + /v1/agents） |

## 4. 测试

| 文件 | 覆盖 |
|---|---|
| `tests/test_grok_native_dispatch.py` | registry/module/alias/capabilities/catalog、spawn env 隔离、双 session 隔离 |
| `tests/inner/test_grok_native_isolation.py` | spawn env deny-by-default、auth 错误不泄漏 token、JSON 解析（含嵌套 unwrap） |
| `tests/runner/test_grok_native_session.py` | 第一轮 `--session-id`、第二轮 `--resume` 同 id |
| `tests/test_harness_dispatch.py` | `_HARNESS_MODULES` 路由、create_app 契约（**新建**，任务卡 Task 4 引用） |

**结果**：定向 44/44 通过（`test_grok_native_dispatch` + `inner/test_grok_native_isolation` + `runner/test_grok_native_session` + `test_harness_plugins` + `test_harness_dispatch`）；相关回归 129 passed / 1 failed。

**回归失败 1 项为 pre-existing**（stash 掉全部改动后仍失败，与 grok 无关）：
- `tests/test_harness_capabilities.py::test_catalog_rows_carry_setup_steps` — `acp:grok-code` 来自用户 `~/.omnigent/config.yaml` 里配置的 `grok agent stdio` ACP agent（任务卡提过"旧日志中的 grok-code"），其动态 catalog 行无 setup_steps。**未修改既有测试期望**（任务卡红线）。
- `tests/host/test_connect.py` 4 项失败同样 pre-existing（stash 验证一致）。

## 5. RUN_ID / Evidence

- 最终双轮验收：`grok-native-01-20260803T111125Z`（session `539829a7dc674491989944328425528d`）
- AgentCenter 唤起：`grok-native-01-agentcenter-20260803T112152Z`（session `9723a19b266f45619a143324fe13fd3f`）
- 原始嵌套 JSON 会话（sessionId/model 证据）：`f4118739d9604012a8f5ce8a5af0ecdd`
- Evidence 目录：`F:\codex-ai\git项目部署\tmp\omnigent-review\evidence\grok-native-01\`
  - `539829a7-final-session.json`（最终双轮，纯文本 sentinel）
  - `f4118739-raw-session.json`（原始 grok payload：sessionId/modelUsage）
  - `evidence-summary.txt`、`acceptance.log`、`agentcenter.log`、`server-state.txt`
  - 各 RUN 的 round1/round2 json + session.txt

### Task 5 成功标准核对

| 标准 | 结果 |
|---|---|
| 两个 sentinel 来自真实 assistant item | ✅ `GROK_NATIVE_OK` / `GROK_NATIVE_FOLLOWUP_OK` 均为 assistant message item |
| 第二轮复用同一 session | ✅ grok sessionId 两轮一致：`69cf0f4b-dcb0-5990-a67e-46ed3948e05c` |
| 模型记录为 grok-4.5 | ✅ modelUsage 键 `grok-4.5-build` |
| session 最终 idle | ✅ status=idle |
| 无 Windows tmux 崩溃 | ✅ headless CLI 子进程，无 tmux/PTY |
| 无 127.0.0.1:10100 连接 | ✅ 无 OpenCodex 访问 |
| Grok 子进程无 Claude/Qwen/Codex 凭据 | ✅ spawn env deny-by-default（测试 + ad-hoc 22/22） |
| evidence 落盘、leak-scan | ✅ 无 token 泄漏（错误消息只含登录命令） |

### Task 6 成功标准核对

| 标准 | 结果 |
|---|---|
| 现有 Agent 唤起 grok-native-ui | ✅ caller=`claude-native-ui`（agent_id 58a1bc5b…）→ target=`grok-native-ui` |
| 固定 sentinel | ✅ `GROK_AGENTCENTER_OK`（16.3s 返回） |
| 记录 caller/target/session/dispatch 时间线 | ✅ `grok-native-01-agentcenter-*.json`（dispatch 7.76s、send→assistant 16.3s） |
| assistant item 来源 | ✅ target session 的 assistant message（harness=grok-native） |

## 6. 认证 / 用户登录

- 用户已执行：`GROK_HOME=/home/administrator/.grok-omnigent grok login --device-code`（2026-08-03 11:00 前后）
- 预检：`grok models` → `You are logged in with grok.com.` / Default model: grok-4.5
- 未代登录、未复制 auth 文件（per-session 仅 symlink 根 auth.json）

## 7. 环境事实（复现用）

- WSL launcher（唯一可用）：`C:\Program Files\WSL\wsl.exe`（inbox System32 版坏，Store 版 ACL 拒绝）
- 调用模板：`"/c/Program Files/WSL/wsl.exe" -d Ubuntu-24.04 -e bash -lc '<cmd>'`
- 测试运行：`cd /mnt/f/codex-ai/omnigent-zh-next && .venv/bin/python -m pytest ...`（.venv 符号链接指向 WSL 内 python3.12）
- Omnigent server：`127.0.0.1:6767`（`--reload` 未生效，需手动重启加载注册；本次已重启）
- Host：`127.0.0.1:6767/v1/hosts` → `27dc0e70add5450b9901c03fd9e9417c` online，configured_harnesses 含 grok-native

## 8. 失败分类 / 遗留

- 无 DIAG_INCONCLUSIVE；CLI 接口稳定可审计。
- `tests/test_harness_dispatch.py` 原不存在（任务卡 Task 4 引用），已新建。
- 任务卡 Task 4 复跑引用的 `tests/inner/test_codex_runtime_isolation.py`、`tests/runner/test_codex_terminal_ensure_guard.py` **不存在于本工作树**（任务卡假设文件），已用实际存在的 `test_harness_plugins.py`/`test_harness_capabilities.py`/`test_harness_aliases.py`/`test_native_coding_agents.py`/`test_wrapper_labels.py` 补足回归面。
- 未 commit/push/merge/tag；未 Gate 2。
