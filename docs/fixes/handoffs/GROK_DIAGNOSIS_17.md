# GROK DIAGNOSIS 17 — Codex CLI 0.146.0 D0/D1 重新基线

> **角色：** Grok（只读诊断执行者）  
> **任务卡：** `docs/fixes/handoffs/CODEX_TASK_17.md`（**未执行**已失效的 `CODEX_TASK_16.md`）  
> **唯一仓库交付：** 本文件  

---

## 1. RUN / 路径 / 时间窗

| 项 | 值 |
|---|---|
| **RUN_ID** | `20260730-171141-dc83140-grok-cli0146-d0d1-r1` |
| **Evidence（持久保留）** | `C:\Users\Administrator\omnigent-diagnostics\20260730-171141-dc83140-grok-cli0146-d0d1-r1` |
| **Runtime** | `%TEMP%\omnigent-cli0146-d0d1-20260730-171141-dc83140-grok-cli0146-d0d1-r1`（**已删除**） |
| **时间窗（UTC 约）** | 09:11 建 RUN → 09:13 D0 → 09:15 D1 → 09:16 cleanup/leak |
| **报告写入时 evidence 存在** | **True** |

未拼接阶段 14/15/16 或 r4 的 PID/事件/退出码/证据正文。

---

## 2. 唯一诊断分类

```text
DIAG_D1_READY_FOR_D2
```

证据：`DIAGNOSIS.txt`。

**含义：** 固定 native **Codex CLI 0.146.0** 在本 RUN 的 D0 one-shot 与 D1 app-server 均可产生可信 assistant 输出；**不是** Gate 2 PASS，**不**表示产品 D2/r4 已修复，**不**证明 TUN 是根因。

**D2：** `NOT_EXECUTED_BY_TASK_DESIGN`

---

## 3. Identity / native / 预检

| 检查 | 结果 |
|---|---|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` start=end |
| branch | `docs/fix-plans-core-secondary` |
| 八 blob | start/end `all_match=True` |
| 预检 | self/ancestor 排除后 **count=0 / pass=True** |
| `.codex-tmp` start/end | 空=空 |
| **NATIVE** | `...\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe` |
| version / size / SHA | **0.146.0** / **358650672** / `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb` |
| shim | **False**；未用 sandbox-bin / Desktop / PATH 动态选择 |
| native start=end | **True** |

---

## 4. TUN / 代理 / 10100

| 项 | 结果 |
|---|---|
| TUN start | 强制数组：`meta_up=True`，`Meta=Up` |
| TUN end | 强制数组：`meta_up=True`，`Meta=Up` |
| 派生 | `meta_up_at_start=True`，`meta_up_at_end=True`，`tun_state_changed=False` |
| 操作 | **仅观察，未开关/重配** |
| 代理 env | 均为 present=False（`environment-presence.txt`） |
| 10100 LISTEN start/end | False / False |

---

## 5. D0 — 0.146.0 one-shot（一次）

| 项 | 结果 |
|---|---|
| exit | **0** |
| timeout | **False** |
| duration | ~35.3s |
| json_lines | 4 |
| assistant/final sentinel | **True** |
| 10100/426 | **False** |
| **D0_PASS** | **True** |

**审计注记：** D0 业务结果以直播 `D0_RESULT pass=True exit=0 sentinel=True json=4 d0426=False` 与 `d0-pass.txt=True` 为准。  
中间因 PowerShell **大小写不敏感** 将 `$ev` 列表覆盖 `$EV` 证据根变量，导致 `d0-meta/events/timeline/error` 首次写入失败；**未重跑 D0**，仅据直播结果与 registry PID **补写**脱敏摘要文件，并在 `d0-meta.txt` 标明 `reconstruction_note`。若验收方认为流正文不可审计，可改判 `DIAG_INCONCLUSIVE` 并要求全新 RUN；本执行者维持 D0 业务 PASS 记录。

---

## 6. D1 — 0.146.0 app-server（一次）

| 项 | 结果 |
|---|---|
| initialize / thread/start / turn/start | **True** |
| terminal_kind | **`turn_completed`** |
| assistant_item | **True** |
| assistant_sentinel | **True** |
| userMessage 回显计 PASS | **否** |
| error_method | **False** |
| 10100 / 426 | **False / False** |
| frame_count | 37 |
| duration | ~25.9s |
| process exit | **-1**（业务终态后由诊断驱动停止；与业务 PASS 分开记录） |
| **D1_PASS** | **True** |

### 10100/426 分析（摘要）

- `responses_websocket`：**False**  
- `ws://127.0.0.1:10100/v1/responses`：**False**  
- HTTP/WS 426：**False**  
- app-server `error` method：**False**  
- D0 同类现象：**False**  
- 边界：只写本 RUN 事实；不宣称 TUN 唯一根因  

---

## 7. Cleanup / manifest / leak-scan

| 项 | 结果 |
|---|---|
| 本 RUN PID | 已终止（`run-pids.txt` / `cleanup.txt`） |
| runtime_deleted | **True** |
| private home 精确删除 | 有绝对路径/叶名/归属/reparse/逐项结果 |
| `.codex-tmp` | start=end 空 |
| evidence 根 | **仍存在、未删** |
| evidence-manifest | 完整 |
| leak-scan | **最后文件**；计数相等；hits=0；`pass=True` |

---

## 8. Gate / merge / 禁止项

- Gate 1：相对 main **PASS**，非全仓 GREEN  
- Gate 2 r4：仍 **FAIL**  
- 本诊断 **不是** Gate 2 PASS  
- **不可 merge**  
- 未改源码/tests/政策/STATUS/旧 handoff/TUN/代理/认证  
- 未执行 D2、完整 Gate 2、pytest、Ruff  
- 未 commit/push/merge/tag  
- 原生 Windows PowerShell + Node 协议探针；无 WSL/tmux  

---

## 9. 下一步（唯一）

分类为 **`DIAG_D1_READY_FOR_D2`**：交回 **Codex** 另发**独立 D2 卡**——在固定 **CLI 0.146.0 同一 native SHA**、记录 TUN 只观察、不拉长 idle 的前提下，执行**单次** Omnigent C，并做 1 秒级 spawn 观测。  
本卡 **停止，不自行执行 D2**。

---

**报告完成。停止，交回 Codex 只读验收。**
