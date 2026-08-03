# GROK DIAGNOSIS 14 — Codex harness 240s idle 分层诊断

> **角色：** Grok（诊断执行者，不是 Gate 审查者）  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **本文件为唯一仓库交付**

---

## 1. RUN 身份与时间窗

| 项 | 值 |
|---|---|
| **RUN_ID** | `20260730-1415-dc83140-grok-codex-idle-diag` |
| **Evidence** | `C:\Users\Administrator\omnigent-diagnostics\20260730-1415-dc83140-grok-codex-idle-diag` |
| **Runtime** | `%TEMP%\omnigent-codex-idle-diag-20260730-1415-dc83140-grok-codex-idle-diag`（已 finally 删除） |
| **HEAD** | `dc83140c73ceb12fa165753c1880c19f68da86f4`（start/end 一致） |
| **MODEL** | 固定 `gpt-5.6-sol`（未换模型） |
| **时间窗（UTC 约）** | identity-start ~06:15 → D0 ~06:23 → D1 ~06:26 → D2 ~06:29–06:33 → cleanup/report |
| **D2 端口** | `50581`（已 free） |

**本报告不是 Gate 2 verdict。** 不得据此宣称 Gate 2 PASS。

---

## 2. 唯一诊断分类

```
DIAG_RUNNER_SPAWN
```

证据见 evidence 根 `DIAGNOSIS.txt`（唯一主分类）。

**含义（对照矩阵）：** D0 与 D1 可信通过，说明同一机器上原生 Codex one-shot 与原始 `codex app-server` 协议/事件通道可用；D2 单次 Omnigent C 在产品拓扑下复现 240s idle，过程中出现 runner 会话与新的 `omnigent-codex-home-*`，但**全程未观测到可归属本 RUN 的 App Server（`codex`/`app-server`）子进程**，仅见无关既有 `codex.exe`（PID 23160，PPID 不在本 RUN 树、CPU 计数冻结）。因此断点落在 **Omnigent runner/executor 启动或维持 App Server 子进程** 一层，而非环境/模型不可达，也非“事件已产生但 CLI 丢失”的 relay 证明。

**不是：** Gate 2 PASS/FAIL 正式裁决；不是完整六轮 Gate 2。

---

## 3. D0 — 原生 Codex one-shot

| 项 | 结果 |
|---|---|
| CLI | 原生 `codex.exe` 0.142.5（vendor win32-x64）；`auth.json`/`config.toml` 存在性 True；私有 `CODEX_HOME` 链接+复制 |
| 调用 | `codex exec --json -m gpt-5.6-sol -s read-only --ephemeral`，120s 预算 |
| **exit** | **0** |
| **timeout** | **False** |
| **duration** | **~30.3s** |
| 首 stdout/JSON/事件 | 均 PRESENT |
| JSON 事件类型 | `thread.started`, `turn.started`, `item.completed`, `turn.completed` |
| **sentinel** | **True**（`OMNIGENT_DIAG_D0_OK_7f3a9c2e`） |
| **D0_PASS** | **True** |

备注（脱敏）：stderr 曾出现本地 `ws://127.0.0.1:10100/v1/responses` 的 `426 Upgrade Required`，但 one-shot 仍在预算内成功完成。  
工具性说明：早期内联驱动因 PS `$HOME` 只读变量/脚本内中文路径编码失败未真正启动进程；有效测量为 UTF-8 路径文件 + native exe 的一次正式 D0（`d0-meta.txt`）。

---

## 4. D1 — 原始 `codex app-server` 协议

| 项 | 结果 |
|---|---|
| 私有 home | 新叶名 `omnigent-codex-home-d382a765`（与 D0 不复用） |
| argv | `codex app-server`（native），cwd=工作树，sandbox=`read-only`，model=`gpt-5.6-sol` |
| **initialize** | **ok=True** |
| **thread/start** | **ok=True** |
| **turn/start** | **ok=True**（turn_hash 记录） |
| 业务事件 | **True**（含 `turn/started`、`item/started`、`item/completed` 等） |
| 探针 terminal 标记 | `item/completed`（探针在首个含 completed 的 method 上提前结束；**非严格 turn/completed 终态**） |
| duration | ~24.6s；timeout=False |
| frame_count | 15 |
| **D1_PASS（事件通道）** | **True（可信：init/thread/turn 映射 + 多帧业务事件）** |

限制：探针把 `item/completed` 当作 terminal 提前结束，可能未等到 `turn/completed`；但 **JSONL 事件通道工作** 已充分证明。stderr 同样见 10100/426 脱敏记录。  
按任务卡：D0+D1 可信 → 允许进入 D2。

---

## 5. D2 — 单次 Omnigent C 对照

| 项 | 结果 |
|---|---|
| 拓扑 | server `127.0.0.1:50581` READY+10s health=200；foreground host 双 online；`OMNIGENT_DATA_DIR`/UTF-8/`NO_PROXY` 传入 |
| workspace | drive absolute、单反斜杠、路径含 RUN_ID（`d2-workspace-contract.txt`） |
| agent | name=`controller-diag` harness=`codex` model=`gpt-5.6-sol`（仅 meta/SHA，无正文） |
| 预算 | **300s**（**未**调高产品 240s idle watchdog） |
| **cli exit** | **1**（可信，非 timeout 杀死） |
| **duration** | **~259.6s** |
| **idle_watchdog_hit** | **True** |
| 错误摘要（脱敏） | `Error: turn exceeded the 240s harness idle watchdog (run_turn emitted no events for 240s; likely a wedged LLM or tool call)` |
| sentinel | False |
| old400 (0202) | **False** |
| server/host 结束时 | 仍 alive；health_end=200 |

### 进程/时间线要点

- C 启动后 ~12s：`.codex-tmp` 新出现 **`omnigent-codex-home-qos19h69`** → 产品侧 executor `start()` 的私有 home 路径已走通。
- 全程 `process=online` / `host_status=online`，session id 命中持续为 1。
- Runner 树存在：`omnigent-zh` → `python`（C 与 host 下均有）。
- **未见** PPID 落在本 RUN runner 树上的 `codex.exe`/`app-server`；唯一全局 `codex.exe` 为 **既有** PID 23160（诊断开始前即存在，CPU 计数冻结，非本 RUN 子进程）。
- CLI stderr：`Launching your agent…` 后无业务事件，直至 240s idle 失败。

**D2 诊断现象：** 与 Gate 2 r4 C 同类（可信 exit=1 + idle watchdog）；**本卡不把它写成 Gate FAIL/PASS**。

---

## 6. 未执行层与停止依据

| 层 | 状态 | 依据 |
|---|---|---|
| D0 | 已执行且通过 | — |
| D1 | 已执行且事件通道可信 | — |
| D2 | 已执行（单次 C） | D0∧D1 通过后执行 |
| E-pos / E-neg / R / 六轮 Gate2 | **禁止且未执行** | 任务卡边界 |
| pytest / Ruff / Gate1 | **禁止且未执行** | 任务卡边界 |

---

## 7. 历史状态（不得改写）

- **Gate 1：** 仍为 **PASS（相对 main）**，**非**全仓 GREEN。  
- **Gate 2 r4：** 仍为 **FAIL**（exit 可信、`run_turn` 240s 无事件；`old400=0` 仅表示旧 0202 路径误拒未复现）。  
- **0202 / r3：** 历史 FAIL/INVALID 不变。  
- **不可 merge。**

本诊断 **未** 拼接 0130/0134/0136/0159/0202/r3/r4 的 PID/session/stdout/AC 作为本 RUN 证据。

---

## 8. Identity / blob / git status

| 检查 | 结果 |
|---|---|
| HEAD start/end | `dc83140c73ceb12fa165753c1880c19f68da86f4` 一致 |
| 八个候选 blob start/end | 全部 MATCH / `all_match=True` |
| git status | 仅记录路径/状态/大小；本轮仓库仅**新增**本报告（其余既有 M/?? 与 start 对照为工作树既有脏状态，非本诊断写入源码） |

---

## 9. `.codex-tmp` 与清理

| 项 | 结果 |
|---|---|
| start 集合 | **空**（允许继续） |
| 本 RUN 新建 home | D0 `…80cb2467`、D1 `…d382a765`、D2 `…qos19h69` |
| 删除 | 仅精确删除上述叶目录；reparse 只删链接本身；未删 `.codex-tmp` 父目录 |
| end 集合 | **空** = start（`set_equal_start=True`） |
| PID | 本 RUN 相关目标 dead（清理时排除诊断 shell 自进程） |
| runtime | **已删除**（路径含完整 RUN_ID） |
| 端口 50581 | **free** |
| leftover（RUN_ID/端口） | **0** |

证据：`cleanup.txt`、`codex-tmp-start/end.txt`、`codex-tmp-delete-actions.txt`。

---

## 10. leak-scan

在 identity-end、分类、cleanup 之后生成 `leak-scan.txt`（evidence **最后**文件）：

- 扫描 evidence 全部文件；`files_present_before_scan == files_scanned`
- prompt 正文 hits、credential/token/cookie/header 值 hits、auth/config 正文 hits、symlink Target hits 目标均为 **0**
- 若 scan 失败则分类应降为 `DIAG_INCONCLUSIVE`（本 RUN 以 scan 结果为准）

---

## 11. 根因分层结论（给 Codex / Hermes）

| 层 | 结论 |
|---|---|
| 环境/模型/auth | **排除为根因**：D0 30s 内 sentinel 成功 |
| App Server 协议本身 | **排除为根因**：D1 initialize/thread/turn + 多帧事件 |
| Omnigent C 产品路径 | **复现 idle**：launch 成功、home 新建、runner 在线，**无本 RUN App Server 子进程可观测** → **`DIAG_RUNNER_SPAWN`** |
| 单纯加长 idle | **不建议**（无“模型持续产出可观测进度仅阈值过短”证据） |

### 高度可疑差异（供开发卡，本轮不改代码）

1. **CLI 解析路径：** D0/D1 使用 **native** `…\codex-win32-x64\…\codex.exe`；产品侧通常 `shutil.which("codex")`，本机 PATH 上存在 **opencodex shim**（`AppData\Roaming\npm\codex.cmd`）。若 runner 走到 shim 而非 native，可能导致 app-server 子进程行为/存活与 D1 不一致。  
2. **源码焦点文件（只读建议）：**  
   - `omnigent/inner/codex_executor.py` — `_CodexAppServerSession.start()` / `run_turn()` / `_reader_loop()`  
   - `omnigent/runtime/harnesses/_scaffold.py` — `_guarded_run_turn()`（240s idle）  
   - runner 侧 session 启动 / harness 选择（`omnigent/runner/` 相关）  
3. **建议失败测试（Hermes 另卡）：**  
   - 断言 `codex` harness 启动后存在 **PPID 属于 runner 树** 的 `codex app-server` 子进程，且在 N 秒内 stdout 有 JSONL；  
   - 子进程失踪/立即退出时 **fail-loud**（不得 silent 直至 240s idle）；  
   - Windows 上 `which("codex")` 解析到 shim 时的显式处理或锁定 native path。

---

## 12. 下一步（二选一）

**推荐：Hermes 最小源码修复卡**（非本诊断范围）：

- 修 runner/codex executor 的 App Server **spawn/存活/可观测性**；  
- 增加“无子进程 / 子进程早死 / 无 JSONL”的最小失败测试；  
- **禁止**用拉长 idle 冒充修复；  
- 修复后由 Codex 另发 **全新 RUN_ID** 的 Gate 2 六轮卡（不可拼接本诊断）。

备选：若后续发现 PATH/shim 属机器配置问题，可先发 **环境/CLI 配置卡** 固定 `codex` 解析到与 D0/D1 相同的 native binary，再用新诊断 RUN 验证；**仍不**等于 Gate 2 PASS。

---

## 13. 禁止项遵守声明

- 未修改 `omnigent/`、`tests/`、政策、STATUS、旧 handoff/evidence。  
- 未跑 pytest、Ruff、Gate 1、完整 Gate 2。  
- 未换模型、未拉长产品 idle、未拼接旧 RUN。  
- 未 commit/push/merge/tag。  
- 未宣称 Gate 2 PASS。

---

**完成：** 交回 Codex **只读验收**。本诊断停止。
