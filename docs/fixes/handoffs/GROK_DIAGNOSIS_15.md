# GROK DIAGNOSIS 15 — native App Server 10100/426 可审计复诊（TUN 已开启）

> **角色：** Grok（只读诊断执行者）  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **任务卡：** `docs/fixes/handoffs/CODEX_TASK_15.md`  
> **本文件为唯一仓库交付**

---

## 1. RUN 身份与 evidence 保留

| 项 | 值 |
|---|---|
| **RUN_ID** | `20260730-160451-dc83140-grok-appserver-426-r1` |
| **Evidence（持久保留）** | `C:\Users\Administrator\omnigent-diagnostics\20260730-160451-dc83140-grok-appserver-426-r1` |
| **Runtime** | `%TEMP%\omnigent-appserver-426-20260730-160451-dc83140-grok-appserver-426-r1`（已删除） |
| **时间窗（UTC 约）** | 08:04 创建 → 08:10 D0 → 08:15 D1 → 08:16 cleanup/leak |
| **报告写入时 evidence 存在** | **True**（只读确认） |

未拼接、未恢复、未引用 `20260730-1415-...` / `20260730-1452-...-r2` / r4 evidence 正文。

**本诊断不是 Gate 2 verdict。**

---

## 2. 唯一诊断分类

```text
DIAG_D1_READY_FOR_D2
```

证据：`DIAGNOSIS.txt`。

含义：在用户已开启 TUN、且本轮未改动 TUN/代理/认证的前提下，同一 native Codex 的 D0 one-shot 与 D1 app-server 均取得真实 assistant/model 输出与 sentinel；**本轮按任务设计未执行 D2**。  
该分类 **不是** Gate 2 PASS，也 **不** 授权本轮跑 D2。

### 关于 TUN / 426

| 观察 | 结果 |
|---|---|
| TUN start | `Meta` adapter **Up**（`tun-status-start.txt`） |
| TUN end 原始行 | `adapter_name=Meta\|status=Up`，`up_tun_like_adapter_count=1` |
| 本机事后只读 | `Meta` 仍为 **Up**（诊断未关闭/重配 TUN） |
| D0 是否出现 10100/426 | **False** |
| D1 是否出现 `responses_websocket` | **False** |
| D1 是否 `ws://127.0.0.1:10100/v1/responses` | **False** |
| D1 是否 HTTP/WS 426 | **False** |
| D1 是否 error method | **False** |
| 10100 LISTEN start/end | **False / False** |

**边界结论（不宣称唯一根因）：** 在 **本 RUN、TUN 开启且未由本诊断改动** 的条件下，native D0/D1 **均未观测到** 先前报告的 `127.0.0.1:10100/v1/responses` **426**，且 D1 出现真实 assistant item + sentinel + `turn/completed`。  
由于阶段 14 REWORK 的 evidence 已丢失、且本轮未做“关 TUN 对照”，**不得**声称已严格证明 TUN 是唯一根因；只能写 **“TUN 开启状态下可用（本 RUN）”**。

注：`tun-status-end.txt` 中 `meta_up_at_end`/`tun_state_changed` 布尔字段与同文件 adapter 行不一致（脚本对单对象 `.Count` 的瑕疵）；以 **adapter 行与事后只读** 为准：Meta 保持 Up。

---

## 3. Identity / 预检

| 检查 | 结果 |
|---|---|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` start=end |
| branch | `docs/fix-plans-core-secondary` |
| 八 blob | start/end `all_match=True` |
| 预检 | self/ancestor 排除后 **count=0 / pass=True** |
| `.codex-tmp` start | **空** |
| 默认 which | 环境中 `Get-Command codex` / PATH 可能不可用；本 RUN **固定 native 绝对路径** |

---

## 4. Native Codex 固定

| 项 | 值 |
|---|---|
| **NATIVE_CODEX_PATH** | `C:\Users\Administrator\.codex\.sandbox-bin\codex.exe` |
| 版本 | `codex-cli 0.144.0-alpha.4` |
| SHA-256 | `b88f944ef63556527caae2ad43f80b88b8be174dc09b09d9b037fc94240a0e91` |
| is_cmd_bat_shim | **False** |
| D0/D1 同一路径与 SHA | **True** |

---

## 5. D0 — native one-shot（一次）

| 项 | 结果 |
|---|---|
| exit | **0** |
| timeout | **False** |
| duration | ~42.5s |
| json_lines | 4 |
| assistant/final sentinel | **True** |
| 10100/426 | **False** |
| **D0_PASS** | **True** |

---

## 6. D1 — native app-server（一次；无 D2）

| 项 | 结果 |
|---|---|
| initialize / thread/start / turn/start | **True / True / True** |
| terminal_kind | **`turn_completed`** |
| assistant_item | **True** |
| assistant_sentinel | **True** |
| userMessage 回显计入 PASS | **否** |
| error_method | **False** |
| 10100 / 426 | **False / False** |
| frame_count | 33 |
| duration | ~32.9s |
| **D1_PASS** | **True** |
| **D2** | **`NOT_EXECUTED_BY_TASK_DESIGN`** |

---

## 7. Cleanup / leak-scan

| 项 | 结果 |
|---|---|
| 本 RUN PID | 已终止（见 `run-pids.txt` / `cleanup.txt`） |
| runtime_deleted | **True** |
| D2 port | NOT_APPLICABLE |
| 10100 / TUN | 仅观察、未操作 |
| `.codex-tmp` start/end | 空 = 空，`set_equal` |
| evidence 根 | **未删除，仍存在** |
| evidence-manifest | 已生成 |
| leak-scan | **最后文件**；计数相等；hits=0；`pass=True` |

---

## 8. Gate / merge 状态

- **Gate 1：** PASS（相对 main），**非**全仓 GREEN。  
- **Gate 2 r4：** 仍为 **FAIL**，仍在修复。  
- **本诊断：** 不是 Gate 2 PASS。  
- **不可 merge。**  
- 未修改源码/tests/政策/STATUS/认证/代理/TUN；未 commit/push/merge/tag。

---

## 9. 下一步（唯一）

分类为 **`DIAG_D1_READY_FOR_D2`**：交回 **Codex** 编写**独立**任务卡——在固定同一 native + 记录 TUN 状态前提下，执行**单次** Omnigent C / D2，并做 **1 秒级 spawn 观测**（区分未 spawn / 早退 / 存活无事件）。  
本卡 **不得** 自行执行 D2。

---

## 10. 完成声明

- 全新 RUN_ID / evidence / runtime；evidence 持久保留。  
- TUN 由用户开启；本诊断只记录、不改动。  
- D0 一次 PASS；D1 一次 PASS（真实 assistant sentinel）；**未执行 D2**。  
- 本 RUN 未观测 10100/426；不宣称 TUN 为唯一根因。  
- 唯一分类：`DIAG_D1_READY_FOR_D2`。  

**停止，交回 Codex 只读验收。**
