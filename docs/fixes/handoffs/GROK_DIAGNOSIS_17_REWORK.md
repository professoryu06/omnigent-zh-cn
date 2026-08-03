# GROK DIAGNOSIS 17 REWORK — CLI 0.146.0 D0/D1 可审计重跑

> **角色：** Grok（只读诊断）  
> **任务卡：** `docs/fixes/handoffs/CODEX_TASK_17_REWORK.md`  
> **背景：** `CODEX_REVIEW_17.md` 将阶段 17 改判 `DIAG_INCONCLUSIVE`（D0 流/pass 不可审计）  
> **唯一仓库交付：** 本文件  

---

## 1. RUN / 路径

| 项 | 值 |
|---|---|
| **RUN_ID** | `20260730-180739-dc83140-grok-cli0146-d0d1-r2` |
| **Evidence（持久保留）** | `C:\Users\Administrator\omnigent-diagnostics\20260730-180739-dc83140-grok-cli0146-d0d1-r2` |
| **Runtime** | `%TEMP%\omnigent-cli0146-d0d1-rework-20260730-180739-dc83140-grok-cli0146-d0d1-r2`（**已删除**） |
| **时间窗（UTC 约）** | 10:07 setup → 10:10 D0 → 10:11 D1 → finally/leak |
| **报告时 evidence 存在** | **True** |

未拼接阶段 14/15/16/17/r4 evidence。未执行 `CODEX_TASK_16`。  
**无事后重建 PASS**；`d0-pass.txt` / `d1-pass.txt` 均在 required-file 自检通过后**首次**写入。

---

## 2. 唯一分类

```text
DIAG_D1_READY_FOR_D2
```

含义：固定 **CLI 0.146.0** 在本 RUN 可审计 D0+D1 业务 PASS，可另开 D2 卡。  
**不是** Gate 2 PASS；**不**证明产品 r4/D2 已修复；**不**宣称 TUN 唯一根因。

`D2=NOT_EXECUTED_BY_TASK_DESIGN`

---

## 3. Identity / native / 预检 / TUN

| 检查 | 结果 |
|---|---|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` start=end |
| branch | `docs/fix-plans-core-secondary` |
| 八 blob | start/end `all_match=True` |
| 预检 | count=0 / pass=True |
| `.codex-tmp` | start=end 空 |
| native path | 任务卡固定 npm vendor `codex.exe` |
| version/size/SHA | **0.146.0** / **358650672** / `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb` start=end |
| TUN | 强制数组；`meta_up_at_start=True`；`meta_up_at_end=True`；`tun_state_changed=False`；只观察 |
| 10100 LISTEN | start/end False |

---

## 4. D0（一次，实时落盘）

| 项 | 结果 |
|---|---|
| driver | Node `spawn(shell:false)` 实时 append |
| live events | `d0-events-live-sanitized.jsonl`（ordinal 连续） |
| process result | `d0-process-result.txt`（pid/exit/timeout/bytes/json counts） |
| stream hashes | `d0-stream-hashes.txt`（raw size+SHA，无正文） |
| required check | `d0-required-files-check.txt` → pass |
| **d0-pass.txt** | **D0_PASS=True**（自检后首次创建） |
| exit / timeout | 0 / False |
| assistant/final sentinel | **True**（非 user 回显） |
| 10100/426 | **False** |

---

## 5. D1（一次，实时落盘）

| 项 | 结果 |
|---|---|
| 启动条件 | 本 RUN `d0-pass.txt` + D0 required SHA 存在 |
| live frames | `d1-frames-live-sanitized.jsonl` |
| initialize/thread/turn | **True** |
| terminal | **turn_completed** |
| assistant item / sentinel | **True / True** |
| userMessage 计 PASS | **否** |
| error method / 426 | **False / False** |
| required check | pass |
| **d1-pass.txt** | **D1_PASS=True** |
| 进程 exit | cleanup 停止与业务终态**分开**记录 |

注：D1 驱动在**首次成功 spawn 前**有一次语法错误未启动业务进程；修复后在本 RUN 内完成**唯一一次**真实 D1 业务 turn（见 `driver-identities.txt` 中 after_syntax_fix 注记）。未对失败业务做重试。

---

## 6. Cleanup / 自检 / leak-scan

| 项 | 结果 |
|---|---|
| PID dead | True |
| runtime 删除 | True（stream hash 已先落 evidence） |
| private home 精确删除 | 有 abs/leaf/归属/reparse/结果 |
| `.codex-tmp` | start=end |
| required-evidence-final-check | all present/nonempty |
| evidence-manifest | 完整 |
| leak-scan | **最后文件**；计数相等；hits=0；pass=True |
| evidence 根 | **仍存在** |

---

## 7. Gate / 禁止项

- Gate 1：相对 PASS，非全仓 GREEN  
- Gate 2 r4：仍 FAIL  
- 本诊断 ≠ Gate 2 PASS；**不可 merge**  
- 未改源码/tests/政策/STATUS/配置/TUN  
- 未 D2 / Gate2 / pytest / Ruff  
- 未 commit/push/merge/tag  

---

## 8. 下一步

**`DIAG_D1_READY_FOR_D2`** → 交 Codex 另发**独立 D2 卡**（固定 0.146.0 同一 SHA + `HARNESS_CODEX_PATH` + TUN 只观察 + 1s spawn + evidence 持久）。  
本卡 **停止**。

---

**完成。交回 Codex 只读验收。**
