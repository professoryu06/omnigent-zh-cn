# GROK DIAGNOSIS 14 REWORK — 固定 native Codex 分层诊断

> **角色：** Grok（阶段 14 诊断返工执行者）  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **依据：** `CODEX_REVIEW_14.md` REJECT（原 `DIAG_RUNNER_SPAWN` 改判 `DIAG_INCONCLUSIVE`）+ `CODEX_TASK_14.md` 矩阵  
> **本文件为唯一仓库交付**

---

## 1. RUN 身份

| 项 | 值 |
|---|---|
| **RUN_ID** | `20260730-1452-dc83140-grok-codex-idle-diag-r2` |
| **Evidence** | `C:\Users\Administrator\omnigent-diagnostics\20260730-1452-dc83140-grok-codex-idle-diag-r2` |
| **Runtime** | `%TEMP%\omnigent-codex-idle-diag-20260730-1452-dc83140-grok-codex-idle-diag-r2`（已删除） |
| **HEAD** | `dc83140c73ceb12fa165753c1880c19f68da86f4`（start/end 一致） |
| **MODEL** | 固定 `gpt-5.6-sol`（未换模型） |
| **Native Codex** | `...\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe` |
| **native SHA-256** | `645f5a1a0347abb2b31fae4e594c198ad00e3a4b4a999dcfa3a66c0d0f8cd43b` |
| **native version** | `codex-cli 0.142.5` |
| **shutil.which("codex")** | `C:\Users\Administrator\AppData\Roaming\npm\codex.CMD`（PATH shim，**本 RUN 未用于 D0/D1**） |

**未拼接** 旧 RUN `20260730-1415-...-diag` 或 r4 evidence。  
**本报告不是 Gate 2 verdict。**

---

## 2. 唯一诊断分类

```text
DIAG_APP_SERVER_PROTOCOL
```

证据：`DIAGNOSIS.txt`。

### 含义（对照矩阵）

- **D0 通过：** 同一 native binary + 同一认证 + `gpt-5.6-sol` 的 one-shot 可达。  
- **D1 未通过 rework 完成条件：** 虽完成 `initialize` / `thread/start` / `turn/start` 映射，并收到 `turn/completed` 与 `error` 通知，但 **无 assistant/model item**，**assistant sentinel=False**；`userMessage` 回显 **未**计为 PASS。  
- **D2 未执行**（D1 不通过即停止）。  

因此不能进入 runner/spawn 分类；也不能再主张原 r1 的 `DIAG_RUNNER_SPAWN`。本轮正式分类落在 **App Server 路径上无法取得可信模型业务终态（无 assistant 输出）**，相对 exec one-shot 成功形成对照。

**不是** Gate 2 PASS/FAIL 裁决。

---

## 3. 预检（修正点 1）

`precheck-leftover-pids.txt`：

- 记录 self/ancestor PID 集合并 **排除诊断驱动自身**。  
- 命中旧 r4/旧 diag/当前 RUN 字符串的进程：仅诊断 shell 自身（ownership=`DIAG_DRIVER_SELF_OR_ANCESTOR`，`excluded_from_count=True`）。  
- **`count=0` / `pass=True`** → 允许继续。  
- 只检查、不 kill。

`.codex-tmp` start：**空集**，允许继续。

---

## 4. CLI 固定（修正点 2–5）

| 项 | 值 |
|---|---|
| 默认 which | `...\npm\codex.CMD`（opencodex/npm shim） |
| 固定 executable | vendor native `codex.exe`（上表路径） |
| 版本 / SHA-256 | 0.142.5 / `645f5a1a...` |
| D0/D1 | 均直接 argv 使用 native，**不走 PATH** |
| D2 | 未执行；若执行将设置 `HARNESS_CODEX_PATH=<native>`（见驱动与 `codex-executable-identity.txt`） |

未记录 prompt/credential 正文或 auth Target。

---

## 5. D0 — native one-shot

| 项 | 结果 |
|---|---|
| exe | NATIVE |
| model | `gpt-5.6-sol` |
| exit | **0** |
| timeout | **False** |
| duration | ~46.1s |
| sentinel (`OMNIGENT_DIAG_R2_D0_OK_91ab`) | **True**（来自 `-o` last-message；非 user 回显误计） |
| **D0_PASS** | **True** |

说明：stdout 泵在本驱动中字节为 0，但 exit=0 且 last-message sentinel 命中；按任务“可信最终结果 + sentinel”计为通过。私有 home：`omnigent-codex-home-d0-1b066e`。

---

## 6. D1 — native app-server（严格终态）

| 项 | 结果 |
|---|---|
| exe | NATIVE `app-server` |
| private home | `omnigent-codex-home-d1-f841d3` |
| initialize | **True** |
| thread/start | **True** |
| turn/start | **True** |
| 业务事件 | **True**（含 `turn/started`；非仅 MCP） |
| **terminal_kind** | **`turn_completed`**（`method=turn/completed`） |
| 同 turn `method=error` | **观测到**（摘要未落正文） |
| assistant/model item | **未观测** |
| **assistant_sentinel** | **False** |
| userMessage item/completed | 出现，**明确不计入 PASS** |
| exit | 1（探针结束后终止 app-server） |
| timeout | False |
| duration | ~27.4s |
| frame_count | 17 |
| **channel_ok**（RPC+终态帧） | True |
| **D1_PASS**（rework：须 assistant sentinel 或可信 provider fail 终态语义） | **False** |

### D1 不通过原因（可审计）

1. 已等到 **`turn/completed`**，满足“有终态帧”字面条件。  
2. 但 **无 assistant/model 输出 item**，sentinel 未出现在 assistant 输出。  
3. 观测到 **`error` 方法** 后紧接 `turn/completed`，业务上不是“模型成功返回 sentinel”。  
4. stderr 脱敏：`responses_websocket` → `ws://127.0.0.1:10100/v1/responses` **426 Upgrade Required**（与 r1 同类噪声；D0 exec 仍成功）。  
5. 按 rework：**D1 不通过 → 禁止 D2**。已遵守。

详见 `d1-meta.txt`、`d1-frames-sanitized.txt`、`d1-fail-rationale.txt`。

---

## 7. D2 — 未执行

| 项 | 状态 |
|---|---|
| 执行 | **否** |
| 停止依据 | D1_PASS=False（无 assistant sentinel；error+turn/completed 不足以按 rework 放行） |
| HARNESS_CODEX_PATH 实测 runner 继承 | **未测**（无 D2） |
| 1s spawn 观测 | **未测** |

---

## 8. 与 r1 / Codex 验收缺口对照

| 验收缺口 | 本 REWORK |
|---|---|
| 预检 count≠0 仍继续 | **已修**：self 排除后 count=0/pass=True |
| D1 用 userMessage 当 terminal / 输入 sentinel 当成功 | **已修**：要求 `turn/completed` 且 assistant_sentinel；userMessage 不计 |
| D1 不通过仍跑 D2 | **已修**：未执行 D2 |
| 产品侧未固定 HARNESS_CODEX_PATH | 本 RUN 在 D0/D1 固定 native；**D2 未跑**故产品继承仍待下卡 |
| 5–7s 采样不足 | D2 未跑；驱动已设计 1s 窗口（未触发） |
| 删除动作无逐项目录 | **已写** `codex-tmp-delete-actions.txt`（绝对路径/叶名/reparse/结果） |
| 报告早于 leak-scan | **本报告在 leak-scan 之后撰写** |

---

## 9. Identity / cleanup / leak-scan

| 检查 | 结果 |
|---|---|
| HEAD / 八 blob start=end | 一致 / `all_match=True` |
| `.codex-tmp` start/end | 均为空，`set_equal_start=True` |
| 删除 | 仅本 RUN `omnigent-codex-home-d0-*` / `d1-*`；目标非 reparse 根；不跟随 Target |
| PID | d0=40480、d1=1152 **dead** |
| runtime | **deleted** |
| port | NOT_APPLICABLE（无 D2） |
| leftover | 0 |
| leak-scan | 最后文件；31==31；hits=0；`pass=True` |

---

## 10. Gate / merge 状态

- Gate 1：仍 **PASS（相对 main）**，非全仓 GREEN。  
- Gate 2 r4：仍 **FAIL**。  
- 本诊断：**不是** Gate 2 PASS，**不可 merge**。  
- 未改源码/tests/政策/STATUS/旧 handoff；未跑 pytest/Ruff/Gate1/完整 Gate2；未 commit/push/merge/tag。

---

## 11. 下一步（唯一建议）

**继续环境/CLI + App Server 模型可达性卡（仍不急着发 Hermes spawn 源码卡）：**

1. 在 **native app-server** 路径上单独复现：为何 D0 `exec` 有 sentinel，而 D1 `app-server` 只有 `error` + `turn/completed`、无 agent item。  
2. 排查 `127.0.0.1:10100` 426 与 ChatGPT/本地代理对 **app-server** 与 **exec** 的差异（只读配置，不改产品源码除非确认）。  
3. 仅当 D1 在 **assistant sentinel + turn/completed** 下稳定 PASS 后，再开 **带 `HARNESS_CODEX_PATH=native` 的单次 D2**，用 1s spawn 观测区分未 spawn / 早退 / 存活无事件。  
4. 若固定 native 且 D1 业务成功后 D2 仍 idle，再发 Hermes 最小 spawn/fail-loud 卡（入口仍为 `codex_harness.py` / `codex_executor.py`）。

---

## 12. 完成声明

- 全新 RUN_ID / evidence / runtime；未拼接旧 RUN。  
- 预检 count=0；native 固定并记录 which/SHA/version。  
- D0 通过；D1 严格终态判定后 **失败**；**未执行 D2**。  
- 分类唯一：`DIAG_APP_SERVER_PROTOCOL`。  
- finally + leak-scan 后写本报告。  

**停止，交回 Codex 只读验收。**
