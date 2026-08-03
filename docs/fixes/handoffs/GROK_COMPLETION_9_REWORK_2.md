# GROK COMPLETION 9 REWORK 2 — UTF-8 前台 host 拓扑 Gate 2

**执行者：** Grok（Gate 2 执行者；不自签 merge）  
**日期：** 2026-07-30  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_9_REWORK_2.md`  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

---

## 1. 唯一结论

### Gate 2 = **FAIL**

| 维度 | 结果 |
|------|------|
| 0136 预清理 | **CLEANUP_OK=true**（见独立 cleanup 目录） |
| Preflight | **ELIGIBLE=true** |
| Server | READY + 连续观察 10s（health=200） |
| Foreground host | **HOST_ONLINE=true**（`process=online` 且 `host_status=online`） |
| UTF-8 环境 | 所有子进程启动前：`PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`、`OMNIGENT_DATA_DIR`、`NO_PROXY` |
| C | **exit=1（可信）**；server/host 前后均存活；无 `CONTROLLER_OK` |
| C 错误 | `Failed to launch a runner ... (400): workspace must be an absolute path starting with /` |
| 其余五轮 | **未执行**（C 业务失败且生命周期健康 → FAIL 停止） |
| 清理 | 本 RUN server/host **dead**；port **free**；runtime **deleted**；leftover=0 |
| leak-scan | **最后写入**；`files_present_before_scan=32` = `files_scanned=32`；hits=0 |

**四态分界：**  
server/host 生命周期可信 + exit 可信 + 清理完整 + 业务断言失败 → **FAIL**（非 INVALID）。

**Gate 1** 仍为 **PASS（相对 main）**，非全仓 GREEN。  
**不可 merge。** 须 Codex 只读验收。

---

## 2. 0136 精确预清理

**清理记录目录：**  
`C:\Users\Administrator\gate2-evidence\cleanup-0136-before-rework2-20260730-015537\`

| 步骤 | 结果 |
|------|------|
| 精确枚举 | 匹配 `-m omnigent.host._daemon_entry` 且 `--server http://127.0.0.1:65525` 的 **非 shell** 进程（最终 count=0） |
| `host stop --server http://127.0.0.1:65525 --daemon-only --force` | **exit=0**；stdout：`Stopped ... daemon pid=6760; sessions_stopped=0.` |
| 0136 runtime 删除 | **gone** |
| 端口 65525 | 可 bind（无 LISTEN 占用） |
| **CLEANUP_OK** | **true**（`CLEANUP_SUMMARY.txt`） |

未按进程名批量 kill；未触碰其它 server URL。  
**0136 永久保持 INVALID（上轮）**；本轮不改写旧 evidence。

---

## 3. 正式 RUN

| 项 | 值 |
|----|-----|
| **RUN_ID** | `20260730-0202-dc83140-grok-gate2-r2` |
| **Evidence** | `C:\Users\Administrator\gate2-evidence\20260730-0202-dc83140-grok-gate2-r2` |
| **PORT** | `54040`（新端口，非 65525） |
| **Server PID** | `36968` |
| **Host PID** | `31948`（foreground `host --server ... --non-interactive`） |
| **驱动** | 单次前台 PowerShell：`omnigent-gate2-driver-r2b.ps1` + `GATE2_WORKTREE` |

### 同日被丢弃的不完整尝试（不拼接）

| RUN | 结果 | 原因 |
|-----|------|------|
| `…0159-…-r2` | INVALID | `New-ChildProcess` 参数名 `$args` 与 PS 自动变量冲突 → server 未收到参数；**不**作为正式结论 |
| **`…0202-…-r2`** | **FAIL** | 正式 RUN |

仓库内**仅新建**本文件。

---

## 4. 身份与保护

| 项 | 值 |
|----|-----|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| workspace / model / idle / serve | 与任务卡期望一致（`identity-start/end.txt`） |

---

## 5. Preflight（固定 pin）

| 用途 | harness | model | auth |
|------|---------|-------|------|
| C/R | `codex`（非 native） | `gpt-5.6-sol` | Codex subscription present |
| E-pos / E-pos-strict | `codex-native` | `gpt-5.6-sol` | 同上 |
| E-neg | `claude-native`（cap=warn） | `claude-opus-4-8` | Claude OAuth `loggedIn=true` |

CLI：工作树 `.venv\Scripts\omnigent-zh.exe`。  
环境名（仅名）：`OMNIGENT_DATA_DIR`、`NO_PROXY`、`PYTHONUTF8`、`PYTHONIOENCODING` present=true。

---

## 6. Server / Host 生命周期

| 阶段 | 证据 |
|------|------|
| Server READY | `server-ready.txt`；lifecycle `ready_poll_*` → health=200 |
| 观察 10s | `observe_1..10` 均 health=200 |
| Host 启动 | `host --server http://127.0.0.1:54040 --non-interactive` + UTF-8 env |
| Host online | `host-status-online.json` 摘要：`process=online`，`host_status=online`，host_id=`host_5c910bce291e474dbd00306c6ce50fb4` |
| Host 日志 | Connected / Listening（无 GBK/codec 错误） |
| C 前/后 | before_c / after_c：server 与 host 均未退出，health=200 |

---

## 7. 六轮

| 轮次 | 状态 | exit | 说明 |
|------|------|------|------|
| **C** | **FAIL** | **1** | runner 启动 400：`workspace must be an absolute path starting with /` |
| E-pos … R | 未跑 | — | 按卡停止 |

### C 命令摘要（脱敏）

```text
<CLI> run <RUNTIME>/agents/controller.yaml -p ping --server http://127.0.0.1:54040
cwd=<RUNTIME>/workspaces/controller
STRICT=unset  timeout=180  env=UTF-8+OMNIGENT_DATA_DIR+NO_PROXY
```

`c.meta.txt`：cli_exit=1 timeout=false；health_before/after=200；host_alive_before/after=true。

**根因（事实，不修源码）：**  
在 Windows 上 session workspace 为 `C:\...` 绝对路径；server 侧校验要求路径以 `/` 开头，导致 launch runner 400。此为**业务/平台路径契约失败**，生命周期与证据链可信 → **FAIL**。

---

## 8. AC

`ac-verdicts.txt`：AC-1…AC-6 均 **NOT_PASS**（六轮未完成）；**OVERALL=FAIL**。  
无 Phase2 送达声明。

---

## 9. 清理与泄漏扫描

| 项 | 结果 |
|----|------|
| server/host dead | true |
| port free | true |
| runtime deleted | true |
| leftover processes | 0 |
| leak-scan 顺序 | **最后**创建 |
| files_present_before_scan | **32** |
| files_scanned | **32** |
| prompt_body_hits | **0** |
| secret_pattern_hits | **0** |

创建 `leak-scan.txt` 后未再写 evidence。

---

## 10. 禁止项遵守

- 未改源码/tests/政策/STATUS/旧 handoff/旧 evidence  
- 未跑 pytest/Ruff/Gate 1  
- 未拼接 0130/0134/0136/0159  
- 未批量 kill；预清理仅精确 65525 daemon + 本 RUN 自有 PID  
- 未 commit/push/merge/tag  
- **未**自行批准 merge  

---

## 11. 交回 Codex

| 项 | 状态 |
|----|------|
| Gate 1 | PASS（相对 main）；非全仓 GREEN |
| Gate 2 | **FAIL**（RUN `20260730-0202-dc83140-grok-gate2-r2`） |
| Merge | **不可 merge** |
| 建议后续（本卡不修） | Windows workspace 路径契约：server/runner 接受 `C:\` 或 Gate 2 在 POSIX 环境执行；新任务卡 + 新 RUN_ID |

**停止。**
