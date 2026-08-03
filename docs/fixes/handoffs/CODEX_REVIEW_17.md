# CODEX REVIEW 17 — CLI 0.146.0 D0/D1 重新基线只读验收

> **验收者：** Codex（只读验收/编排）  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **验收对象：** `docs/fixes/handoffs/GROK_DIAGNOSIS_17.md`  
> **任务卡：** `docs/fixes/handoffs/CODEX_TASK_17.md`  
> **RUN_ID：** `20260730-171141-dc83140-grok-cli0146-d0d1-r1`  
> **Evidence：** `C:\Users\Administrator\omnigent-diagnostics\20260730-171141-dc83140-grok-cli0146-d0d1-r1`  
> **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`

## 1. 验收结论

**REJECT**

不接受 Grok 主张的：

```text
DIAG_D1_READY_FOR_D2
```

改判为：

```text
DIAG_INCONCLUSIVE
```

核心原因只有一个：**D0 的业务 PASS 没有可独立复核的持久证据。**

本 RUN 的 D1 原始脱敏帧、时间线和 terminal 链条可信；identity、native、TUN、cleanup、manifest 和 leak-scan 也基本可信。但 `CODEX_TASK_17.md` 明确要求 D0 和 D1 都必须可审计，且分类矩阵规定 evidence 任一关键层不可审计时必须是 `DIAG_INCONCLUSIVE`。

因此：

- 本轮不能进入 D2；
- 不另发 D2 卡；
- 不得把本 RUN 的 D1 与下一 RUN 的 D0 拼接；
- 下一步必须使用全新 RUN_ID，重新执行一次 D0 和一次 D1；
- 本轮 evidence 必须继续持久保留，不得删除或改写。

本次验收没有重跑 D0、D1、D2、pytest、Ruff、Gate 1 或 Gate 2；没有修改源码、tests、政策、`STATUS.md`、旧 handoff、TUN/代理/认证配置；没有 commit/push/merge/tag。

---

## 2. D0 审计缺口

### 2.1 可以确认的事实

以下 D0 前置或外围事实有持久 evidence：

- D0 command contract 在运行前已写入；
- 固定 executable、版本、大小和 SHA 与任务卡相符；
- D0 private home 已创建；
- PID `17448` 被登记，cleanup 后 `dead=True`；
- 报告主动披露了 PowerShell `$ev`/`$EV` 大小写不敏感冲突；
- 没有发现第二次 D0 或重试的持久证据。

这些事实可以证明“D0 进程被计划并启动过”，但不能独立证明“D0 业务 PASS”。

### 2.2 缺失的关键原始依据

Evidence 内没有：

- 报告和 `d0-meta.txt` 所引用的 `d0-pass.txt`；
- 持久化的原始 `D0_RESULT pass=True exit=0 sentinel=True json=4 d0426=False` 行；
- D0 四条脱敏事件各自的真实 event type、item type 和 UTC；
- 可核验的原始 stdout/stderr byte count；
- 可证明 sentinel 来自 assistant/final item、而非输入回显的逐事件元数据；
- D0 原始流的保留文件或可独立验证的业务结果记录。

只读全文搜索只找到：

- `d0-meta.txt` 中的 `D0_PASS=True`；
- `d0-events-sanitized.txt` 中的重建布尔；
- `d0-timeline.txt` 中的 `event=reconstructed_from_live_result`；
- `d0-error-sanitized.txt` 中对未保留直播结果的文字转述；
- `run-summary.txt` 中再次汇总的 `D0_PASS=True`。

这些文件都来自同一次事后重建，不是互相独立的证据源。

### 2.3 重建文件不能替代原始审计链

`d0-meta.txt` 明确写道：

```text
reconstruction_note=d0-meta rewritten after PS variable case collision lost intermediate evidence files; facts taken from live D0_RESULT line and d0-pass.txt; not a second D0 run
```

但：

- `D0_RESULT` 没有持久化；
- `d0-pass.txt` 不存在；
- runtime 已按设计删除；
- 因此验收方无法重新检查 exit、事件角色、sentinel 来源和 426 判断。

这不是“D0 已证明失败”，而是“D0 的成败无法通过保留证据独立复核”。

### 2.4 与任务卡的冲突

`CODEX_TASK_17.md` 要求：

- `d0-meta.txt` 记录真实 exit、timeout、duration、首 stdout/JSON/业务事件、可信 assistant/final 和 sentinel；
- `d0-events-sanitized.txt` 与 `d0-timeline.txt` 来自真实运行；
- D0 PASS 必须同时证明 exit=0、timeout=False、可信结果存在、sentinel=True；
- identity、顺序、exit、cleanup、leak-scan 或 evidence 任一不可审计时，分类必须为 `DIAG_INCONCLUSIVE`。

本 RUN 的重建摘要无法关闭上述证据要求，所以不能接受 `DIAG_D1_READY_FOR_D2`。

---

## 3. D1 子结论

D1 本身的持久 evidence 可以支持：

```text
D1_PASS=True
```

证据链为：

1. `initialize` response 可映射；
2. `thread/start` response 可映射；
3. `turn/start` response 可映射；
4. 先出现 `userMessage item/started` 与 `item/completed`；
5. 后出现真实 `agentMessage` 的 `item/started`；
6. 出现多条 `item/agentMessage/delta`；
7. 出现 `agentMessage item/completed`；
8. assistant sentinel 命中；
9. 最后出现 `turn/completed`；
10. 未见 app-server `error` method 或 10100/426。

`d1-frames-sanitized.txt` 保留了 37 个脱敏 frame，`d1-timeline.txt` 保留了 UTC、累计 bytes、frame count、assistant item、sentinel 和 terminal 的演进。

D1 进程 exit=`-1` 已与业务终态分开记录，发生在可信 `turn/completed` 之后，由诊断驱动停止；不推翻 D1 业务 PASS。

但 D1 PASS 不能用于：

- 反推 D0 PASS；
- 替代 D0 `exec --json` 的可审计结果；
- 把本轮整体分类提升为 `DIAG_D1_READY_FOR_D2`；
- 授权执行 D2。

---

## 4. Identity、八个 blob 与仓库范围

只读核对结果：

- HEAD start=end=`dc83140c73ceb12fa165753c1880c19f68da86f4`
- branch start=end=`docs/fix-plans-core-secondary`
- 八个冻结 blob start/end 均 `match=True`
- 当前重新计算的八个 blob 仍匹配
- `git-status-start.txt` 与 `git-status-end.txt` 排除 UTC 后差异数为 0

| 文件 | 冻结/当前 blob | 结果 |
|---|---|---|
| `omnigent/server/routes/_workspace_validation.py` | `5bf5e587b9177a9ecbce572b11656edac31ea7fe` | 匹配 |
| `omnigent/server/routes/sessions.py` | `0375e5f951d82c01c9f67e8cf7b41a90aff10330` | 匹配 |
| `tests/server/routes/test_workspace_validation.py` | `63291bfa4bc47c196e04a218c82b782ecb613786` | 匹配 |
| `tests/server/routes/test_workspace_validation_helpers.py` | `4cae0f53cb724c991a1c502c2919e37da7b7737a` | 匹配 |
| `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` | 匹配 |
| `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` | 匹配 |
| `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` | 匹配 |
| `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` | 匹配 |

现有工作树原本就包含大量用户/项目未提交改动；本 RUN 的 start/end 状态和大小没有漂移。由于 handoffs 目录在 git status 中整体折叠为未跟踪目录，status 文件不能逐文件证明唯一新增，但没有证据显示本 RUN 修改了 tracked 源码、tests 或政策文件。

---

## 5. 预检与 native 固定

### 预检

- 诊断驱动 self/ancestor PID 已登记并标记 `DIAG_DRIVER_SELF_OR_ANCESTOR`；
- 排除后 `count=0`、`pass=True`；
- `.codex-tmp` start 直接子项为空；
- 当前只读复核 `.codex-tmp` 直接子项仍为空。

### Native

| 项 | 结果 |
|---|---|
| 路径 | `C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe` |
| 版本 | `codex-cli 0.146.0` |
| 大小 | `358650672` bytes |
| SHA-256 | `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb` |
| shim | `False` |
| start=end | `True` |
| D0/D1 同一路径与 SHA | `True` |

Evidence 明确记录 PATH 候选是 npm wrapper，但实际固定的是 vendor native；没有使用旧 sandbox binary、Desktop binary 或 PATH 动态入口。

---

## 6. TUN 与 10100

- TUN start：`Meta=Up`、`meta_up=True`
- TUN end：`Meta=Up`、`meta_up=True`
- `meta_up_at_start=True`
- `meta_up_at_end=True`
- `tun_state_changed=False`
- start/end adapter hash、ifIndex 和默认路由记录一致
- 10100 LISTEN start/end 均为 `False`
- Grok 只观察，没有开关或重配 TUN

阶段 15 的单对象 `.Count` 派生字段问题在本轮已关闭。

允许的边界仍然只是：

```text
本 RUN、TUN 开启状态下，新 CLI 的 D1 app-server 可用。
```

不得写成 TUN 已被证明是根因或唯一修复。

---

## 7. Cleanup、manifest 与 leak-scan

- 本 RUN 记录 PID `17448`、`29008`，最终均 `dead=True`
- runtime 已删除，当前仍不存在
- `.codex-tmp` start=end 空集
- 两个 private home 有绝对路径、叶名、归属、reparse 判断和逐项删除结果
- 10100/TUN 标记 observe-only
- `leftover=0`
- evidence 根仍存在

Manifest：

- 声明 `file_count=44`
- 实际包含 44 条文件记录
- 重新计算 44 个 size/SHA，`bad=0`
- evidence 最终共有 46 个文件，即 44 个被记录文件 + manifest 自身 + leak-scan

Leak-scan：

- 扫描前 45 个文件，扫描 45 个文件
- prompt/credential/auth-config/symlink-target hits 均为 0
- `pass=True`
- `leak-scan.txt` 是 evidence 最后修改文件

这些部分可信，但不能修补 D0 业务证据缺失。

---

## 8. TASK 16、D2 与 Gate 边界

- 没有发现执行已失效 `CODEX_TASK_16.md` 的证据。
- D2=`NOT_EXECUTED_BY_TASK_DESIGN`
- D2 port=`NOT_APPLICABLE`
- 本轮没有执行完整 Gate 2。

当前状态：

- Gate 1：**PASS（相对 main）**，不是全仓 GREEN。
- Gate 2 r4：仍为 **FAIL**。
- 阶段 17：改判 `DIAG_INCONCLUSIVE`，不是 Gate 2 verdict。
- 当前：**不可 merge**。

---

## 9. 下一步唯一建议

执行 `docs/fixes/handoffs/CODEX_TASK_17_REWORK.md`：

- 使用全新 RUN_ID/evidence/runtime；
- 固定同一 CLI `0.146.0` native 和 SHA；
- 重新执行一次 D0；
- D0 的脱敏事件流、exit、sentinel 来源和独立结果文件必须在判 PASS 前持久化；
- 禁止用事后重建摘要替代丢失证据；
- 仅 D0 可审计 PASS 后，再在同一新 RUN 执行一次 D1；
- 仍不得执行 D2。

只有该 REWORK 被 Codex 验收为 `DIAG_D1_READY_FOR_D2` 后，才会另发新的单次 D2 卡。

