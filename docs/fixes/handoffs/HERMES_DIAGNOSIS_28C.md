# HERMES_DIAGNOSIS_28C — Gate 2 前环境清洁检查

- 执行者：Hermes 3.8（只读审计执行者，非 Gate 2 签字人）
- 运行模型：`deepseek-v4-flash` via `deepseek`
- 审计日期：2026-08-03 18:41
- 任务卡：`docs/fixes/handoffs/CODEX_TASK_28C`（Gate 2 前环境清洁检查）
- 背景：28A READY + 28B FULLRUN_PASS 已验收；本卡核查 idle 会话残留是否阻塞 Gate 2

---

## 1. 唯一分类

### `GATE2_ENV_READY`（2026-08-03 18:55 复查升级）

**原判定 `GATE2_ENV_DIRTY` 已解决**：用户授权关闭后，两个 idle 会话已通过产品 API（`DELETE /v1/sessions/{id}`）删除 + 进程树清理，环境已清洁（详见 §6 清理记录）。**当前允许进入 Gate 2（环境维度）**。

## 2. 八项审计结果

| # | 检查项 | 结果 |
|---|---|---|
| 1 | 28A 会话存在性 | ✅ 存在，status=`idle`，items=3，runner_token_19bb9b09… |
| 2 | 28B 会话存在性 | ✅ 存在，status=`idle`，items=10，runner_token_aa21bfeb… |
| 3 | 端口监听 | ⚠️ **51481（28A）+ 42755（28B）均在监听**（codex 进程持有） |
| 4 | PID/父子进程 | ✅ 完整链：runner(363062)→harness(363120)→node shim(363201)→codex(363209) / runner(367233)→…→codex(376367)；**无孤儿** |
| 5 | 异常文件 | ✅ 28A 无 startup_error/dead_letter；28B 无 startup_error，仅 `dead_letter.jsonl` = **usage 遥测**（`external_session_usage`，`ConnectError` 遥测上报未送达，非业务失败；payload 为 token 统计 gpt-5.6-sol） |
| 6 | OpenCodex/10100 | ✅ 未运行（10100 无监听），全程未触碰 |
| 7 | 工作树 HEAD/改动 | ℹ️ omnigent-review HEAD `dc83140`（07-23）dirty 含 21+ M/A 文件；omnigent-zh-next HEAD `c2982266`（07-31 18:48）dirty 含 3 M + grok 未跟踪文件——**均为既有开发状态，非本次审计引入，未修改任何文件** |
| 8 | 旧 evidence | ✅ 5 个 evidence 根全部存在（task27-r1/r2、r27、r28a、r28b）；3 份报告（27/28A/28B）齐全未删 |

## 3. 任务卡四项必答

### 3.1 当前是否允许进入 Gate 2？

**否（环境层面）**。存在 2 个活跃 idle 会话占用端口。**需要用户先关闭 28A/28B 会话，或另发授权关闭卡**后复查，才能满足环境清洁。此判定不涉及代码/测试质量——Gate 2 的产品/质量维度签字权仍归 Codex。

### 3.2 idle 会话是否属于正常产品状态？

**是**。证据：
- 两会话 status=`idle`，items 完整（28A: 3 条；28B: 10 条含 user/assistant/tool 全链路）
- 两会话均成功建立 thread（state.json 存在：28A thread `019fc719-…`，28B thread `019fc72b-…`）
- 两会话均无 startup_error.json（启动成功信号）
- pane_reaper 配置 `idle_timeout=3600.0s`（1 小时）——idle 会话保留 app-server/TUI 属产品设计（28A/28B 报告均已说明），非异常残留
- 28B 会话 idle 后曾自然完成 turn/completed → idle 转换，生命周期健康

### 3.3 51481/42755 是否是真实泄漏？

**否**。二者均为**存活会话的 app-server 监听端口**，进程归属清晰（28A: 363209←363201←363062 runner；28B: 376367←376360←375662 runner），处于产品 idle 语义下的正常存活。**不是孤儿进程、不是端口泄漏、不是僵尸资源**。28B 报告中的 `LEAK_HITS=1` 已确认为此误报（把存活会话端口当泄漏）。会话关闭后端口将随之释放。

### 3.4 边界声明

- **不宣称 Gate 2 PASS、全仓 GREEN 或 mergeable。**
- 本次为环境清洁审计；Gate 2 质量/产品签字权归 Codex。
- 审计全程只读：未杀进程、未关会话、未删 bridge/runtime/evidence、未改任何文件。

## 4. 证据位置

- 本卡审计输出：`C:\Users\Administrator\omnigent-diagnostics\task28c-audit-output.txt`（见审计脚本 stdout，会话内留存）
- 会话证据：`r28a-observer-20260803-hermes-codex-tui-monitor-r1\`、`r28b-fullrun-20260803-hermes-codex-fullrun-r1\`（均未删）
- bridge：`/home/administrator/.omnigent/codex-native/6ec25c30…`（28A）、`2e14a18e…`（28B）

## 5. 建议的下一步

1. ~~用户关闭 28A/28B 两个会话~~ ✅ **已完成（2026-08-03 18:55）**：产品 API DELETE 两会话 + 进程树清理（见 §6）。
2. ✅ 复查通过：端口释放、进程退出、会话 404、bridge 清理 → **分类升级 `GATE2_ENV_READY`**。
3. 由 Codex 决定 Gate 2 流程。

## 6. 清理记录（用户授权，2026-08-03 18:53–18:55）

- **产品路径删除**：`DELETE /v1/sessions/24385a29…` → 200 `{"deleted":true}`；`DELETE /v1/sessions/2758b86e…` → 200 `{"deleted":true}`。会话即 404。
- **产品清理边界发现**：DELETE 后 10+ 秒，runner harness（363120/376103）与 codex app-server（363209/376367）**未自动回收**——产品 runner-side cleanup 为 best-effort，不杀已删除会话的 harness 子进程树。
- **进程树清理（用户明确授权"直接删除"）**：SIGTERM 后补 SIGKILL，覆盖 app-server shim/binary、TUI/tmux、MCP bridge 子进程、runner harness。**仅限 28A/28B bridge-dir 归属进程，未触碰其他**。
- **终态确认**：51481/42755 释放；28A/28B 进程全部退出；会话 404；10100 未监听（OpenCodex 未触碰）；6767 正常；bridge 目录已由产品删除清理。
- 备注：bridge 目录在清理时已不存在（产品 DELETE 已删 bridge 文件），进程树清理为纯进程回收。

## 7. 边界声明（原 §3.4，保留）

- **不宣称 Gate 2 PASS、全仓 GREEN 或 mergeable。**
- 本次为环境清洁审计；Gate 2 质量/产品签字权归 Codex。
- 审计全程除 §6 授权清理外均为只读；清理仅限 28A/28B 归属进程。
