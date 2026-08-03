# CODEX REVIEW 14 REWORK — 阶段 14 native Codex 返工诊断只读验收

> **验收者：** Codex（只读验收/编排）
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
> **验收对象：** `docs/fixes/handoffs/GROK_DIAGNOSIS_14_REWORK.md`
> **报告声称的证据根：** `C:\Users\Administrator\omnigent-diagnostics\20260730-1452-dc83140-grok-codex-idle-diag-r2`

## 1. 验收结论

**REJECT**

`GROK_DIAGNOSIS_14_REWORK.md` 的叙述如果有原始证据支撑，其 D0 → D1 → 停止 D2 的流程与任务卡分类矩阵基本一致；但是，本次只读验收时，报告指定的 evidence 根及其父目录均不存在，无法读取任何 start/end、预检、D0、D1、cleanup 或 leak-scan 原始证据。

因此本次不能接受 Grok 主张的正式分类：

```text
DIAG_APP_SERVER_PROTOCOL
```

当前唯一可审计的正式分类必须保持为：

```text
DIAG_INCONCLUSIVE
```

这不是将报告叙述反向证明为错误，而是原始证据不可用导致无法验收。恢复原 evidence 且确认未被改写后可以重新验收；若无法恢复，必须使用全新 RUN_ID 重做诊断。

本验收没有修改源码、tests、政策、`STATUS.md` 或旧 handoff，没有重跑 D0/D1/D2、pytest、Ruff、Gate 1 或 Gate 2，也没有 commit/push/merge/tag。

---

## 2. 当前可独立核对的 identity

当前工作树只读核对结果：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- 分支：`docs/fix-plans-core-secondary`
- 八个当前工作树 blob 与任务卡冻结值一致：

| 文件 | 当前 blob | 结果 |
|---|---|---|
| `omnigent/server/routes/_workspace_validation.py` | `5bf5e587b9177a9ecbce572b11656edac31ea7fe` | 匹配 |
| `omnigent/server/routes/sessions.py` | `0375e5f951d82c01c9f67e8cf7b41a90aff10330` | 匹配 |
| `tests/server/routes/test_workspace_validation.py` | `63291bfa4bc47c196e04a218c82b782ecb613786` | 匹配 |
| `tests/server/routes/test_workspace_validation_helpers.py` | `4cae0f53cb724c991a1c502c2919e37da7b7737a` | 匹配 |
| `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` | 匹配 |
| `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` | 匹配 |
| `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` | 匹配 |
| `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` | 匹配 |

这只能证明**验收时当前状态**匹配冻结值。由于 evidence 中的 `identity-start/end.txt`、`candidate-source-blobs-start/end.txt` 和 `git-status-start/end.txt` 不存在，不能独立证明 Grok RUN 的 start=end。

`CODEX_REVIEW_14.md` 之后、写入本验收文件之前，handoffs 中按文件创建/修改时间可见的新增交付只有：

- `GROK_DIAGNOSIS_14_REWORK.md`

这支持“仓库交付范围表面上只有 REWORK 报告”，但不能替代 RUN 内 git-status start/end 证据。

---

## 3. Evidence 根缺失

只读检查结果：

```text
C:\Users\Administrator\omnigent-diagnostics\
```

不存在；因此下面的报告声称均无法独立验收：

1. 是否未续写或拼接 `20260730-1415-...-diag`、r4 evidence。
2. 预检是否正确排除诊断驱动 self/ancestor。
3. 排除后是否确为 `count=0/pass=True`，以及非零是否会停止。
4. `which`、vendor native 路径、版本和 SHA-256 是否来自真实 RUN。
5. D0 的 exit、timeout、last-message sentinel 是否可信。
6. D1 是否真有对应 turn 的 `turn/completed`、`error`，且没有 assistant/model item。
7. `userMessage` 和输入 sentinel 是否确实未被计入 PASS。
8. `assistant_sentinel=False`、`D1_PASS=False` 后是否确实未执行 D2。
9. PID 清单、逐 PID dead、runtime 删除、端口 N/A、`.codex-tmp` start/end 空集。
10. 删除动作的绝对路径、叶名、reparse 检查和逐项结果。
11. `leak-scan.txt` 是否为 evidence 最后文件、计数是否相等、hits 是否为 0、报告是否写在 scan 之后。

当前只能观察到：

- 报告所述 runtime 路径当前不存在。
- 当前 `.codex-tmp` 存在且直接子项数为 0。

这两个“当前状态”不能证明 Grok RUN 的 cleanup 和 leak-scan 流程曾按任务卡执行。

---

## 4. Native Codex 身份核对

报告声称：

- `shutil.which("codex")` 为 `C:\Users\Administrator\AppData\Roaming\npm\codex.CMD`
- D0/D1 均固定到 vendor native `codex.exe`
- native 版本为 `codex-cli 0.142.5`
- SHA-256 为 `645f5a1a0347abb2b31fae4e594c198ad00e3a4b4a999dcfa3a66c0d0f8cd43b`

验收时：

- `C:\Users\Administrator\AppData\Roaming\npm\codex.CMD` 不存在。
- 当前 `Get-Command codex` 指向 WindowsApps Codex 应用资源。
- 当前可读取的 WindowsApps `codex.exe` SHA-256 为 `b88f944ef63556527caae2ad43f80b88b8be174dc09b09d9b037fc94240a0e91`，与报告声称的 vendor native 不同。

这可能是 RUN 后环境变化，不能据此反证 Grok 当时的记录；但在原 evidence 缺失时，也无法证明 D0/D1 使用了同一份报告所称 native binary。

---

## 5. D0、D1、D2 与分类矩阵

### 5.1 报告内部逻辑

仅按 `GROK_DIAGNOSIS_14_REWORK.md` 的文字：

- D0：native one-shot exit=0、非 timeout、last-message sentinel 命中。
- D1：initialize/thread/start/turn/start 成功，出现 `error` 和 `turn/completed`，但没有 assistant/model item，`assistant_sentinel=False`，所以 `D1_PASS=False`。
- D2：因为 D1 不通过而未执行。

这比上一轮修正了两个关键逻辑错误：

- 没有把 `userMessage item/completed` 或输入 sentinel 回显当成模型成功。
- D1 不通过后没有继续执行 D2。

任务卡矩阵将“D0 通过，但 D1 initialize/thread/turn 或事件通道失败”映射为 `DIAG_APP_SERVER_PROTOCOL`。所以，**如果原始证据与报告完全一致**，该分类在语义上合理；不应仅因为没有 assistant 输出就自动改为 `DIAG_ENVIRONMENT_OR_MODEL`，因为报告声称同一 native、认证和模型的 D0 one-shot 已成功。

### 5.2 正式验收分类

但本次无法读取 D0/D1 原始 frames、meta、exit、sentinel 和 identity，所以不能确认上述前提。任务卡同时规定，身份、时间线、清理、泄漏或证据任一不可信时必须分类为 `DIAG_INCONCLUSIVE`。

因此：

- **叙述层条件分类：** `DIAG_APP_SERVER_PROTOCOL` 合理。
- **本次正式可审计分类：** `DIAG_INCONCLUSIVE`。
- **不改判为：** `DIAG_ENVIRONMENT_OR_MODEL`，因为现有报告叙述不足以支持该改判；同时也不能用缺失证据正式排除它。

---

## 6. 相对 `CODEX_REVIEW_14` 的缺口对照

| 上一轮缺口 | REWORK 报告声称 | 本次验收 |
|---|---|---|
| 预检 count=1 后未停止 | 排除 self/ancestor 后 count=0/pass=True | **无法验收**：预检文件缺失 |
| D1 把 userMessage/输入 sentinel 当成功 | 已要求 assistant sentinel；userMessage 不计 | **文字已修，证据无法验收** |
| D1 无可信 turn 终态 | 声称收到 `turn/completed` | **无法验收**：frames 缺失 |
| D1 不通过仍执行 D2 | 声称 D1_FAIL 后停止，D2 未跑 | **文字已修，证据无法验收** |
| D0/D1 executable 未统一 | 声称均固定同一 vendor native | **无法验收**：identity 文件缺失，当前环境已不同 |
| D2 5–7 秒采样不足 | D2 未执行 | 本轮 N/A；以后 D2 仍须 1 秒观测 |
| cleanup 只有汇总 | 声称有逐目标绝对路径/reparse/结果 | **无法验收**：cleanup 文件缺失 |
| 报告早于最终 leak-scan | 声称 scan 后才写报告 | **无法验收**：leak-scan 与时间线缺失 |

结论：REWORK 报告在**文字设计**上关闭了上一轮大部分缺口，但没有保留下来可供只读验收的原始 evidence，因此缺口不能标为“已审计关闭”。

---

## 7. Gate 与 merge 状态

- Gate 1：**PASS（相对 main）**，不是全仓 GREEN。
- Gate 2 r4：仍为 **FAIL**，当前仍在诊断/修复。
- 阶段 14 REWORK：不是 Gate 2 verdict，更不是 Gate 2 PASS。
- 当前不可 merge。
- 未创建新 Tag、未发版。

---

## 8. 下一步唯一建议

选择：**继续环境/CLI 路径，不发 Hermes 源码修复卡，也不执行 D2。**

具体入口：

1. 优先恢复原 evidence 根的原始、未改写副本并重新只读验收；若无法恢复，用全新 RUN_ID 重做阶段 14 REWORK，必须保留 evidence。
2. 在可审计 RUN 中继续定位 native `app-server` 的 `error + turn/completed` 但无 agent item，重点核对 `127.0.0.1:10100/v1/responses` 的 `426 Upgrade Required`、代理、认证和 app-server/exec 配置差异。
3. 只有 D1 获得真实 assistant/model item、assistant sentinel 和可信 turn 终态，且原始证据完整时，才能另开带 `HARNESS_CODEX_PATH=native` 的单次 D2 + 1 秒 spawn 观测卡。

在此之前不要修改 Omnigent spawn/fail-loud 源码，不要重跑完整 Gate 2，不要把本诊断写成 Gate 2 PASS。

验收停止。
