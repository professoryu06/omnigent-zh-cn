# CODEX_REVIEW_GROK_NATIVE_FIX_02

日期：2026-08-04  
角色：Codex 只读监控 / 规划 / 审查 Agent  
工作树：`F:\codex-ai\omnigent-zh-next`  
分支：`integration/omnigent-zh-20260731`  
HEAD：`c2982266f1d702d83d47f9352bbe5e0aa8c987f9`  

## 裁决

**ACCEPT_WITH_NOTES：修复可进入独立 Gate 2 卡的前置观察阶段；本文件不签 Gate 2 PASS。**

本轮不需要重新跑已经成功的 Grok 双轮业务验收，但必须在新的独立卡中加入一次短时、全新 session 的 headless 资源观察，作为 Gate 2 前置条件。原因是上一次真实证据确实出现过 `terminal_tui_main`/tmux，而本次只有机制测试，没有修复后的真机会话资源证据。

## 阻塞 1 复核：headless 不再自动建 REPL/tmux

代码链路已闭合：

- `omnigent/harness_plugins.py` 增加 `HarnessContribution.headless_harnesses`，内置注册 `grok-native`，并用 `_merge_set` 聚合；
- `omnigent/harness_aliases.py` 暴露 `HEADLESS_HARNESSES` 和 `is_headless_harness()`；
- `omnigent/runner/app.py` 通用 REPL 创建条件新增 `and not is_headless_harness(harness_name)`；
- `grok-native` 保持 `is_native_harness(...) is False`，没有被伪装成 vendor native/TUI harness。

这正好切断此前的控制流：非 native → `_auto_create_repl_terminal` → `terminal_tui_main`/tmux。

新增测试覆盖了集合归属和谓词正负例，机制上足够关闭“新建 session 自动建 REPL”的路径。

保留一个低优先级边界：`_recreate_repl_terminal()` 仍会重建已经存在的 REPL。如果要保证旧的、修复前已产生终端资源的 Grok session 也绝不重建，应额外在该路径加 headless guard；新 Gate 2 卡必须使用全新 Grok session，不能把旧 session 当作 headless 证据。

## 阻塞 2 复核：代理继承隔离

`omnigent/grok_native_bridge.py` 与 `omnigent/inner/grok_native_executor.py` 均按以下顺序处理：

1. `clean_agent_env()` 取得基础环境；
2. 删除大写和小写的 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`、`NO_PROXY`；
3. 强制 `NO_PROXY=127.0.0.1,localhost`；
4. 只有 `OMNIGENT_GROK_PROXY` 非空时，才注入 HTTP/HTTPS/ALL_PROXY 三件套。

这闭合了原审查发现的父环境代理泄漏路径。新增负向测试覆盖“父环境有代理、专用变量为空”，新增正向测试覆盖“专用变量覆盖继承值”。

## 测试与证据核对

- 定向测试证据：`C:\Users\Administrator\omnigent-diagnostics\grokfix-r2-pytest.txt`，**47 passed**；包含 3 个新回归测试。
- `py_compile` 7 文件通过。
- 相关回归：**90 passed / 1 pre-existing failed**，失败为用户配置 `acp:grok-code` 动态 catalog 行缺少 `setup_steps`，与本次修复无关；不得修改测试期望掩盖。
- `grokfix-verification-r2.txt` / `grokfix-verification-r3.txt` 是脚本和代码路径核对结果，明确说明没有修复后的真机 Grok session 资源快照。
- 当前没有新的 `terminal_tui_main`/tmux 负向真机证据，因此不能把“无 tmux”写成已实测事实。

## 是否需要重跑真机

不需要重跑已经通过的“两轮 Grok 响应 + AgentCenter 唤起”业务验收；那部分验证的是 CLI、session resume 和 AgentCenter 路由，修复没有改变 Grok CLI 解析或 session 管理。

需要新增一次**单轮、全新 session 的短时观察卡**，验证：

- `harness=grok-native`；
- assistant sentinel 真实返回，session 最终 idle；
- session resources 中不存在 `terminal_tui_main`；
- 不存在 `tmux_socket`、`terminal_transport=control` 或其他 REPL/PTY 资源；
- 同时记录子进程最终环境的代理键：无 `OMNIGENT_GROK_PROXY` 时没有 HTTP/HTTPS/ALL_PROXY，有该变量时只出现指定值；
- 证据实时落盘，不能事后根据代码补写结论。

该观察应作为独立 Gate 2 卡的第一项；若失败，停止后续 Gate 2 六轮。

## Gate 2 边界与下一步

可以另开独立 Gate 2 卡，但卡头必须写明：

- 本修复不是 Gate 2 PASS；
- 47 定向测试通过不等于全仓 GREEN；
- 相关回归仍有 1 个已知环境前置失败；
- 首先执行全新 session 的 headless/tmux 观察，再决定是否进入 Gate 2 六轮；
- 不得 merge，直到 Gate 2 六轮独立验收完成。

本审查未修改源码、测试、TUN、Clash、OpenCodex、10100 或认证，未 commit/push/merge/tag。
