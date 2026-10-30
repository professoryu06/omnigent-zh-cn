# CODEX_REVIEW_GROK_NATIVE_01

日期：2026-08-03  
角色：Codex 只读监控 / 规划 / 审查 Agent  
工作树：`F:\codex-ai\omnigent-zh-next`  
分支：`integration/omnigent-zh-20260731`  
HEAD：`c2982266f1d702d83d47f9352bbe5e0aa8c987f9`  

## 唯一裁决

**REWORK_REQUIRED_GROK_NATIVE_01（不接受为完成，Gate 2 不通过）**。

本轮真实功能链路确实跑通了：最终双轮 Grok 响应和一次 AgentCenter 唤起均有真实 assistant item，第二轮复用了同一个 Grok sessionId，模型记录为 `grok-4.5-build`。但实现与任务卡的两个硬约束不一致，不能把 `REVIEW_GROK_NATIVE_01_COMPLETE` 当作已验收完成，也不能进入合并流程。

## 已复核的真实证据

Evidence 目录仍存在：

`F:\codex-ai\git项目部署\tmp\omnigent-review\evidence\grok-native-01\`

最终双轮：`grok-native-01-20260803T111125Z`，Omnigent session `539829a7dc674491989944328425528d`。  
AgentCenter：`grok-native-01-agentcenter-20260803T112152Z`，target session `9723a19b266f45619a143324fe13fd3f`。

`539829a7-final-session.json` 可见：

- `GROK_NATIVE_OK`、`GROK_NATIVE_FOLLOWUP_OK` 均为 assistant message item；
- 两轮业务结果为 completed，最终 session 为 idle；
- `f4118739-raw-session.json` 中两轮 `sessionId` 均为 `69cf0f4b-dcb0-5990-a67e-46ed3948e05c`；
- `modelUsage` 键为 `grok-4.5-build`；
- AgentCenter JSON 中 `GROK_AGENTCENTER_OK` 来自目标 session 的 assistant message，`sentinel_ok=true`。

## 测试复跑

在 WSL Ubuntu-24.04 的候选仓库 `.venv/bin/python` 中复跑：

```text
tests/test_grok_native_dispatch.py
tests/inner/test_grok_native_isolation.py
tests/runner/test_grok_native_session.py
tests/test_harness_plugins.py
tests/test_harness_dispatch.py
```

结果：**44 passed**。Hermes 报告正文也是 44/44；任务反馈顶部写成 54/54，数字不一致，需要补齐审计说明。

相关回归复跑：

```text
tests/test_harness_capabilities.py
tests/test_native_coding_agents.py
tests/test_harness_aliases.py
tests/test_wrapper_labels.py
```

结果：**85 passed, 1 failed**。失败仍为：
`tests/test_harness_capabilities.py::test_catalog_rows_carry_setup_steps`，动态用户配置中的 `acp:grok-code` 缺少 `setup_steps`。这不是本次 Grok native 源码改动造成的；Hermes 报告称 stash 验证仍失败。另有报告记录的 `tests/host/test_connect.py` 4 项既有 Windows 环境失败。本次没有修改测试期望。

## 阻塞问题 1：所谓 headless 仍创建了 tmux/PTY 资源

任务卡和实现注释要求 `grok-native` 为 headless CLI subprocess，不创建 tmux/PTY。可是最终原始 session 证据中明确出现：

`evidence/grok-native-01/539829a7-final-session.json`

```text
resource_id: terminal_tui_main
metadata.tmux_socket: /tmp/omnigent-terminal-t2vd2dr5/tmux.sock
metadata.terminal_transport: control
```

同样的 `terminal_tui_main` 资源也出现在：
`evidence/grok-native-01/f4118739-raw-session.json`。

代码路径解释了该矛盾：

- `tests/test_grok_native_dispatch.py` 明确断言 `is_native_harness("grok-native") is False`；
- `omnigent/runner/app.py` 的通用非 native 分支对 `not is_native_harness(harness_name)` 自动调用 `_auto_create_repl_terminal`；
- `omnigent/runner/native/orchestration.py` 中 `_auto_create_repl_terminal` 使用 terminal registry，并把 `terminal_name` 设为 `tui`，通过 tmux/control transport 提供 REPL。

因此，Grok vendor CLI 本身没有走 native terminal，并不等于整个 session 没有 tmux/PTY。当前证据与报告中的“无 tmux/PTY”结论不自洽。在 Windows 上，这条通用 REPL 路径还可能重新触发 `tmux/PTY not supported on Windows`；在 WSL 上则会额外占用 tmux 资源。

**要求返工：**为 headless CLI harness 增加明确的“禁止自动 REPL terminal”能力/标记，并在 runner 的通用分支跳过 `grok-native`；新增测试确认 Grok session 不产生 `terminal_tui_main` / tmux resource。不要把 `grok-native` 加入 `NATIVE_HARNESSES`，也不要伪造 vendor native terminal。

## 阻塞问题 2：代理隔离实现与报告不符

任务要求是：只有显式设置 `OMNIGENT_GROK_PROXY` 时才向 Grok 子进程注入代理。当前共享过滤器 `omnigent/inner/agent_env.py:35-44, 89-97` 默认允许 `HTTP_*`、`HTTPS_*`、`ALL_PROXY`、`NO_PROXY`。

`omnigent/grok_native_bridge.py:159-174` 和
`omnigent/inner/grok_native_executor.py:352-370` 都先调用 `clean_agent_env()`，只有在 `OMNIGENT_GROK_PROXY` 非空时才覆盖代理变量；未设置时没有删除继承值。因此父进程已有的 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY` 会原样进入 Grok 子进程。

只读验证（传入模拟父环境）得到：

```text
{'HTTP_PROXY': 'http://inherited.invalid',
 'HTTPS_PROXY': 'http://inherited.invalid',
 'ALL_PROXY': 'http://inherited.invalid',
 'NO_PROXY': 'x'}
```

这直接违反报告第 2 节“代理仅当 `OMNIGENT_GROK_PROXY` 设置时注入”。当前用户的 WSL 启动脚本还会设置代理变量，所以该缺陷不是理论问题，可能令 Grok 意外复用 Claude/Qwen 的代理路径。

**要求返工：**在 Grok bridge/executor 的最终环境构造中先删除大写及小写代理变量，再强制 `NO_PROXY=127.0.0.1,localhost`；仅当 `OMNIGENT_GROK_PROXY` 非空时同时注入 HTTP/HTTPS/ALL_PROXY。补充“父环境有代理但未设置 Grok 专用代理时，子进程无代理；设置后才有代理”的回归测试。

## 其他审计结论

| 项目 | 结论 |
|---|---|
| Grok CLI JSON / streaming-json 解析 | 定向测试和原始 payload 支持整体 JSON + 逐行回退，实测可用 |
| per-session GROK_HOME / leader socket / UUIDv5 | 代码与两轮 session 证据基本一致 |
| auth | 未发现代登录或复制真实 auth 的证据；报告称 per-session 仅 symlink 隔离根 auth |
| 其他 provider 凭据 | 代码按 Grok/XAI 家族过滤，禁止前缀测试通过；但代理继承问题仍未关闭 |
| `grok-native` 是否注册 NativeCodingAgent | 未注册，符合任务约束 |
| 10100 / OpenCodex | 本轮 evidence 未显示 10100 连接，不能据此扩大为全局网络结论 |
| 240s watchdog / TUN | 本轮没有证据表明改动；仍需保持原边界 |
| 仓库状态 | 未 commit/push/merge；候选仓库仍有本任务相关未提交改动及其他未跟踪文件，不能合并 |

## Gate 2 边界

本轮只是 Grok native 的定向实现与两轮功能验收，不是 AgentCenter Gate 2 六轮验收。并且目前还有上述两个实现阻塞问题、相关回归 1 项失败、任务数字统计不一致。因此：

- **Gate 2：不通过 / 未签字；**
- **不可 merge；**
- 不得把两轮 Grok 成功写成全仓 GREEN 或 Gate 2 PASS；
- 不需要重跑已经成功的两轮真机验收，先由 Hermes 按本报告修复两个阻塞点并新增回归测试；
- 修复后再由 Codex 只读复核：定向测试、headless 无 REPL/tmux 证据、代理负向/正向测试，之后另开独立 Gate 2 卡。

本审查未修改源码、测试、TUN、认证、watchdog，也未 commit/push/merge/tag。
