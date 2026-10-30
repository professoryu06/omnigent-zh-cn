# CODEX_TASK_GROK_NATIVE_FINAL_01

## 目标

只确认 **Grok Native 在 Omnigent 中是否可以稳定使用**。本卡不验收 Claude、Codex、Qwen、其他 Agent、全仓测试或整体 Gate 2。

## 当前已完成

- Grok CLI 可被 Omnigent 唤起；
- 双轮 Grok session 已成功；
- AgentCenter 唤起已成功；
- Grok headless 不再创建 tmux/PTY；
- Grok 代理继承泄漏已修复；
- 前置 headless 观察已通过。

## 待办清单

### G1：认证确认

- 使用私有 `GROK_HOME=/home/administrator/.grok-omnigent`；
- `grok models` 显示已登录；
- 认证值、auth 内容和代理值不得写入报告；
- 若 token 过期，由用户重新执行 device-code 登录，Hermes 不代登录。

### G2：一次最小真实调用

- 新建全新 Grok session；
- 发送 `GROK_NATIVE_FINAL_OK`；
- 真实 assistant item 返回；
- session 进入 idle；
- resources 只有 `default/environment`；
- 无 `terminal_tui_main`、tmux socket、PTY 或 control transport。

### G3：Grok 多轮可用性

- 新建独立 session；
- 第一轮发送 `GROK_NATIVE_ROUND1_OK`；
- 第二轮发送 `GROK_NATIVE_ROUND2_OK`；
- 两轮都是真实 assistant item；
- 第二轮复用同一 Grok CLI sessionId；
- 两轮均无 runner error，最终 idle。

### G4：AgentCenter 调用

- 由现有可用 Agent 唤起 `grok-native-ui`；
- 记录 caller、target、session、dispatch 时间线；
- 返回 `GROK_AGENTCENTER_FINAL_OK`；
- target session 资源仍只有 environment，无终端资源。

### G5：代理隔离

- 父环境构造 HTTP/HTTPS/ALL_PROXY；
- 未设置 `OMNIGENT_GROK_PROXY` 时，Grok 子进程不得出现这些键及其小写版本；
- `NO_PROXY` 必须严格为 `127.0.0.1,localhost`；
- 如做显式代理正向检查，只记录键名和脱敏值，不访问不必要的外部服务。

### G6：清理与证据

- 每次使用全新 RUN_ID 和 evidence 根；
- 不拼接旧 RUN 业务结果；
- vendor Grok CLI 子进程最终为 0；
- 预期常驻 harness、观察脚本、旧残留分别记录；
- 回收旧失败 session 的残留 harness，并记录 PID dead；
- evidence 文件数量、manifest、报告三处一致；
- leak-scan 最后执行；
- 凭据全部 `[REDACTED]`。

### G7：Codex 只读复核

- Hermes 写唯一诊断报告；
- Codex 复核 G1–G6；
- 唯一结论只能是：
  - `GROK_NATIVE_READY_FOR_USE`
  - `GROK_NATIVE_REWORK_REQUIRED`
  - `GROK_NATIVE_INCONCLUSIVE`

## 执行约束

- 不修改源码、tests、配置、TUN、Clash、OpenCodex、10100 或 240s watchdog；
- 不删除既有 evidence；
- 不 commit、push、merge、tag；
- 不把本卡结论扩大为全仓 GREEN 或全局 Gate 2 PASS。

## 并行安排

Hermes 可开 3 个只读子 agent：

1. 认证与私有 `GROK_HOME` 核对；
2. 资源、workspace、tmux/PTY 证据核对；
3. evidence 数量、PID cleanup、leak-scan 核对。

真实 Grok session 必须由 Hermes 主 agent 顺序执行，避免并发污染。

## 交付

唯一报告：

`F:\codex-ai\git项目部署\tmp\omnigent-review\docs\fixes\handoffs\HERMES_DIAGNOSIS_GROK_NATIVE_FINAL_01.md`

完成后停止，等待 Codex 只读复核。
