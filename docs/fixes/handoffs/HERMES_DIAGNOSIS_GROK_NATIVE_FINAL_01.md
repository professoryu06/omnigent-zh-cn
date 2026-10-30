# HERMES_DIAGNOSIS_GROK_NATIVE_FINAL_01 — Grok Native 最终专项验收

- 执行者：Hermes 3.8（Grok 专项验收执行者，非签字人）
- 运行模型：`deepseek-v4-flash` via `deepseek`
- 验收日期：2026-08-04（UTC 17:22–17:27）
- 任务卡：`CODEX_TASK_GROK_NATIVE_FINAL_01`
- 范围：**仅 Grok Native**；不涉及 Claude/Codex/Qwen/其他 Agent/全仓测试/全局 Gate 2

---

## 1. RUN 身份与 evidence

- **RUN_ID**：`grok-native-final-01-20260804T0110Z`（全新，未拼接旧业务结果）
- **evidence 根**：`C:\Users\Administrator\omnigent-diagnostics\grok-native-final-01-20260804T0110Z\`
- 工作树：`F:\codex-ai\omnigent-zh-next`，branch `integration/omnigent-zh-20260731`，HEAD `c2982266f1d702d83d47f9352bbe5e0aa8c987f9`
- agent：`grok-native-ui`（`133499537450decf0a3fc425c686a02f`），harness `grok-native`，model `grok-4.5`
- host：`27dc0e70add5450b9901c03fd9e9417c`；server：`127.0.0.1:6767`
- workspace：`/home/administrator/omnigent-workspaces`
- 凭据/auth/代理值全部 `[REDACTED]`

## 2. G1 认证确认 ✅

- 私有 `GROK_HOME=/home/administrator/.grok-omnigent`
- `grok models` → **`You are logged in with grok.com.`**（默认模型 grok-4.5）
- auth.json 存在（size=1743，mtime 01:01:18——用户本次登录产物）；内容未读取
- 未代登录；token 过期时由用户 device-code 登录（本次为用户完成）

## 3. G2 一次最小真实调用 ✅

- 全新 session `81b019719b3e462e956095c028cf5d46`
- sentinel `GROK_NATIVE_FINAL_OK` → **真实 assistant item**（t=10s）
- session **idle**；**resources 仅 1 个 `default/environment`**
- 无 `terminal_tui_main`、tmux socket、PTY、control transport

## 4. G3 多轮可用性（同 sessionId 双轮）✅

- 全新 session `b9c65f226f344057bea9931d24c62442`
- 第一轮 `GROK_NATIVE_ROUND1_OK` → 真实 assistant（t=8s）；第二轮 `GROK_NATIVE_ROUND2_OK` → 真实 assistant（t=8s）
- 两轮均 idle，无 runner error
- **同一 Grok sessionId 复用证据**：grok session home `f5b6f340-1f8f-5e6c-ba81-6f2ad2addc2d` 唯一（01:23:32–01:23:45 时间戳覆盖两轮时刻）；`session_search.sqlite` 的 `session_docs` 表记录 `session_id=f5b6f340…` 且 content 含 ROUND1 消息+回复——第一轮 `--session-id f5b6f340` 创建、第二轮 `--resume f5b6f340` 复用（确定性 UUIDv5 机制 + 唯一 home + 双轮内容写入同一 home）
- 对照：G2 的 grok home `424ae5a8…`（01:23:09–01:23:19）与 G3 不同

## 5. G4 AgentCenter 唤起 ✅

- caller：`claude-native-ui`（`58a1bc5b…`，session `a26ebfa7…`，idle）
- target：`grok-native-ui`（session `f9ccb3f3…`，经 `parent_session_id` 唤起 = AgentCenter 父子 dispatch）
- sentinel `GROK_AGENTCENTER_FINAL_OK` → **真实 assistant item**（t=9s）
- target idle；**resources 仅 1 个 `default/environment`**（无终端资源）
- dispatch 时间线：caller 创建 → target 创建（0.1s）→ sentinel 202 queued → assistant 9s

## 6. G5 代理隔离 ✅

- 父环境构造 6 个代理变量（HTTP/HTTPS/ALL_PROXY 大小写）+ `NO_PROXY=x`
- 未设 `OMNIGENT_GROK_PROXY`
- `GrokNativeExecutor._build_spawn_env()` 实测：**spawn env proxy keys 仅 `['NO_PROXY']`**；`NO_PROXY == 127.0.0.1,localhost` **strict True**；`OMNIGENT_GROK_PROXY absent`
- 无 HTTP_PROXY/HTTPS_PROXY/ALL_PROXY 及小写版本泄漏

## 7. G6 清理与证据 ✅

- **旧失败 harness 回收**：3 个旧认证失败 RUN 的 harness（conv-2ad65cc8/conv-79c3815e/conv-f6659329，PID 592995/595367/597954）SIGTERM→SIGKILL→**回收后确认全部 PID dead**
- **leak-scan（最后执行，三类分离）**：
  - [A] vendor grok CLI 子进程（--single/--resume）：**0**（LEAK_A_PASS）
  - [B] 预期常驻 harness：10（precheck 1 + Gate2 六轮 6 + FINAL G2/G3/G4 3，全部 idle 会话正常常驻，产品语义）
  - [C] 观察工具：单独记录（脚本自身）
  - 端口：6767 正常 / **10100 未监听**
- **evidence 实际计数：20 文件**（G2×5 + G3×6 + G4×6 + manifest + sessions.txt + G4-target-create.json）——与 manifest、本报告一致

## 8. 唯一结论

### `GROK_NATIVE_READY_FOR_USE`

G1–G6 全部通过：认证有效、单轮/多轮/AgentCenter 三种调用路径均真实 assistant + idle + 资源仅 environment、代理隔离成立、旧残留已回收、vendor CLI 0 泄漏、evidence 一致。**Grok Native 在 Omnigent 中可稳定使用。**

## 9. 边界声明

- 本结论**仅针对 Grok Native**，不扩大为全仓 GREEN 或全局 Gate 2 PASS。
- 已知保留项：`test_catalog_rows_carry_setup_steps` pre-existing 失败（用户 `acp:grok-code` 动态行），与 Grok 无关。
- 未修改源码/测试/配置/TUN/Clash/OpenCodex/10100/认证/240s watchdog；未 commit/push/merge/tag；未删除旧 evidence。
- Gate 2 签字权归 Codex。

## 10. 证据位置

- RUN evidence：`C:\Users\Administrator\omnigent-diagnostics\grok-native-final-01-20260804T0110Z\`（20 文件）
- grok session home：`/home/administrator/.grok-omnigent/sessions/`（f5b6f340=G3、424ae5a8=G2；历史保留）
- runner 日志：`/home/administrator/.omnigent-zh-cn/logs/runner/runner-{G2,G3,G4 sid}-*.log`
