# CODEX REVIEW 17 REWORK — CLI 0.146.0 可审计 D0/D1 只读验收

> **验收者：** Codex（只读验收/编排）  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **验收对象：** `docs/fixes/handoffs/GROK_DIAGNOSIS_17_REWORK.md`  
> **任务卡：** `docs/fixes/handoffs/CODEX_TASK_17_REWORK.md`  
> **RUN_ID：** `20260730-180739-dc83140-grok-cli0146-d0d1-r2`  
> **Evidence：** `C:\Users\Administrator\omnigent-diagnostics\20260730-180739-dc83140-grok-cli0146-d0d1-r2`  
> **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`

## 1. 验收结论

**ACCEPT_WITH_NOTES**

接受 Grok 的唯一诊断分类：

```text
DIAG_D1_READY_FOR_D2
```

阶段 17 原验收中“D0 流和 pass 文件不可审计”的核心缺口已经关闭：

- D0 使用 Node `spawn(shell:false)` 实时写入脱敏 event JSONL；
- D0 真实 process result、raw stream size/SHA、required-file check 均已持久化；
- `d0-pass.txt` 在 required check 之后首次创建；
- D1 只在本 RUN 的 D0 可审计 PASS 后执行；
- D1 使用实时 frame JSONL，真实 assistant item、assistant sentinel 和 `turn/completed` 均可复核；
- `d1-pass.txt` 在 D1 required check 之后首次创建；
- 没有使用阶段 14/15/16/17/r4 evidence 拼接本 RUN；
- 没有执行 D2。

该分类只表示：固定 CLI `0.146.0` 在本 RUN、TUN 开启且只观察的条件下，D0/D1 可用并已达到另开单次 D2 卡的前置条件。

它不表示 Gate 2 PASS，不证明 r4 产品路径的 240 秒 idle 已修复，也不证明 TUN 是根因或唯一修复。

本次验收没有重跑 D0、D1、D2、pytest、Ruff、Gate 1 或 Gate 2；没有修改源码、tests、政策、`STATUS.md`、旧 handoff、TUN/代理/认证配置；没有删除或改写本 RUN evidence；没有 commit/push/merge/tag。

---

## 2. D0 可审计 PASS

### 2.1 实时 event 链

`d0-events-live-sanitized.jsonl`：

- 非空，5 条记录；
- ordinal=`1..5`，连续；
- JSON parse failure=`0`；
- stdout 的 4 条 JSON 事件依次为：
  1. `thread.started`
  2. `turn.started`
  3. `item.completed` / `agent_message`
  4. `turn.completed`
- 额外记录 `output_last_message` / `final_message`；
- ordinal 3 的 `agent_message`：`is_user_message=false`、`is_assistant_or_final=true`、`sentinel_match=true`；
- ordinal 5 的 final message：role=`assistant`、`sentinel_match=true`。

因此 sentinel 来源是可信 assistant/final 输出，不是 userMessage 或输入回显。

### 2.2 真实进程结果

`d0-process-result.txt`：

```text
pid=32268
exit_code=0
timeout=false
duration_ms=23768
stdout_bytes=368
stderr_bytes=182
json_line_count=4
json_parse_fail_count=0
assistant_or_final_event=true
assistant_or_final_sentinel=true
```

`d0-stream-hashes.txt` 的 stdout size=`368` 与 process result 一致，并记录了 raw stdout/stderr 的 SHA-256；raw 正文只存在于已删除 runtime，没有写入 evidence。

### 2.3 required-check 与 pass 顺序

只读文件时间：

```text
d0-required-files-check.txt = 2026-07-30T10:10:27.8871047Z
d0-pass.txt                 = 2026-07-30T10:10:27.8876373Z
```

required check 早于 pass 文件。

重新计算 required check 中 7 个文件的 size/SHA：

```text
entries=7
bad=0
```

`d0-pass.txt` 明确记录：

```text
D0_PASS=True
attempt=1_of_1
exit=0
timeout=False
assistant_or_final_event=True
assistant_or_final_sentinel=True
required_files_pass=True
```

没有阶段 17 那种事后重建标记或缺失的 pass 文件。

### 2.4 D0 stderr 备注

`d0-error-sanitized.txt` 记录：

```text
provider_error_like=true
contains_10100_or_426=false
```

但没有保存更细的脱敏错误类别。这是审计质量备注。

由于 D0 真实 exit=0、timeout=false、assistant/final sentinel=true、JSON parse failure=0，且 D1 随后取得可信业务 PASS，该 stderr 标记不足以推翻任务卡定义的 D0 PASS。不得根据该布尔值猜测具体根因。

---

## 3. D1 可审计 PASS

### 3.1 D0 前置成立

`d0-pass.txt` 创建于：

```text
2026-07-30T10:10:27.8876373Z
```

D1 的固定身份和真实 spawn 均发生在其后：

```text
d1 identity = 2026-07-30T10:11:22.7015480Z
d1 spawn    = 2026-07-30T10:11:22.776Z
```

没有“先跑 D1、后补 D0 pass”。

### 3.2 实时 frame 链

`d1-frames-live-sanitized.jsonl`：

- 非空，37 条；
- ordinal=`1..37`，连续；
- JSON parse failure=`0`；
- `initialize`、`thread/start`、`turn/start` response 可映射；
- ordinal 16/17 是 `userMessage`，`sentinel_match=false`；
- ordinal 18 是真实 `agentMessage item/started`；
- ordinal 19–32 是 agentMessage delta；
- ordinal 33 是 `agentMessage item/completed`、phase=`final_answer`、`sentinel_match=true`；
- ordinal 37 是 `turn/completed`；
- app-server `error` method count=`0`；
- 10100/426=`false`。

因此 userMessage 没有计入 PASS，assistant sentinel 与 terminal 均属于可信业务链。

### 3.3 required-check 与 pass 顺序

```text
d1-required-files-check.txt = 2026-07-30T10:11:44.7193924Z
d1-pass.txt                 = 2026-07-30T10:11:44.7204431Z
```

required check 早于 pass 文件。

重新计算 required check 中 9 个文件的 size/SHA：

```text
entries=9
bad=0
```

`d1-pass.txt`：

```text
D1_PASS=True
attempt=1_of_1
terminal_kind=turn_completed
assistant_item=True
assistant_sentinel=True
required_files_pass=True
frame_count=37
userMessage_not_counted=True
```

---

## 4. D1 驱动语法修复

`driver-identities.txt` 同时记录了：

- D1 driver 初始 SHA；
- `d1_driver_sha256_after_syntax_fix`；
- `d1_driver_note=syntax_fix_before_first_successful_spawn`；
- `shell=false`；
- `windowsHide=true`。

可接受理由：

- 语法错误发生在 Node driver 解析阶段；
- 在语法修复前没有可信 native app-server spawn 或业务 turn；
- 本 RUN 只记录一个真实 D1 app-server PID：`1800`；
- D1 protocol steps 对该 PID 标记 `attempt=1_of_1`；
- 没有失败业务 turn 后重试的 evidence。

因此该操作属于“首次业务 spawn 前修复诊断驱动”，不计作 D1 业务重试。

验收备注：以后最好在 RUN 开始前使用 `node --check` 冻结 driver 语法；若 driver 在 RUN 中修改，必须继续像本轮一样同时记录修改前后 SHA 和首次 native spawn 时间。

---

## 5. 业务终态与进程终态

D1 业务终态：

```text
terminal=turn_completed
assistant_item=true
assistant_sentinel=true
business_done_utc=2026-07-30T10:11:44.309Z
```

D1 进程终态：

```text
exit_code=-1
process_close_utc=2026-07-30T10:11:44.712Z
process_stop_note=stopped_by_diagnosis_driver_after_business_wait
```

业务终态早于诊断驱动停止进程。报告没有把 cleanup 产生的 `-1` 冒充业务失败或业务成功。

---

## 6. Identity、native、TUN 与仓库范围

### Identity

- HEAD start=end=`dc83140c73ceb12fa165753c1880c19f68da86f4`
- branch start=end=`docs/fix-plans-core-secondary`
- 八个冻结 blob start/end 均 `match=True`
- 当前重新计算八个 blob仍全部匹配
- `git-status-start.txt` 与 `git-status-end.txt` 排除 UTC 后差异数=`0`

### Native

| 项 | 结果 |
|---|---|
| version | `codex-cli 0.146.0` |
| size | `358650672` |
| SHA-256 | `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb` |
| shim | `False` |
| start=end | `True` |
| D0/D1 same native | `True` |
| 当前只读复核 | path/size/SHA/version 仍匹配 |

没有使用旧 sandbox binary、Desktop binary 或 PATH wrapper。

### TUN / 10100

- start/end：`Meta=Up`
- `meta_up_at_start=True`
- `meta_up_at_end=True`
- `tun_state_changed=False`
- adapter hash、ifIndex、默认路由记录一致
- 10100 LISTEN start/end=`False`
- TUN/10100 全程只观察

### 仓库范围

本 RUN 前后 tracked 状态和文件大小没有漂移。Handoffs 目录在 git status 中整体折叠为未跟踪目录，不能逐文件证明唯一新增；但没有 evidence 表明 Grok 修改了源码、tests、政策、`STATUS.md` 或配置。

---

## 7. Cleanup、final check、manifest 与 leak-scan

### Cleanup

- D0 PID `32268`：dead=True
- D1 PID `1800`：dead=True
- runtime 已删除，当前仍不存在
- 两个 private home 有绝对路径、叶名、归属、reparse 判断和逐项删除结果
- `.codex-tmp` start=end 空，当前子项数仍为 0
- `leftover=0`
- evidence 根仍存在

### Final required check 备注

`required-evidence-final-check.txt` 有 48 个文件条目。

重新计算发现 1 项不一致：

```text
file=run-summary.txt
recorded_size=124
actual_size=151
recorded_sha=d5a61117afa439d0c07570e657531659326514ad90ce3748955317863f1c72fc
actual_sha=cce640dad21aa52723a3da200a051f95244af339c21c71b5af1134249b21d575
```

原因是 final check 后又写入了最终版 `run-summary.txt`。这说明该检查对 summary 不是最终快照。

不降级为 `DIAG_INCONCLUSIVE` 的理由：

- D0/D1 live、required-check、pass 文件均未在各自 pass 后漂移；
- 变化只涉及汇总文件；
- 后续 manifest 已记录最终 `run-summary.txt` 的 size=151 和实际 SHA；
- 重新计算 manifest 51 个条目的 size/SHA，`bad=0`；
- leak-scan 扫描的是最终 summary。

下一张 D2 卡必须调整顺序：先完成最终 summary，再运行 final required check，再生成 manifest 和 leak-scan；final check 之后禁止修改任何被检查 evidence。

### Manifest / leak-scan

- manifest 声明 51 个条目，实际 51 条
- 独立重算 51 个 size/SHA，`bad=0`
- evidence 最终 53 个文件：51 个 manifest 条目 + manifest 自身 + leak-scan
- leak-scan：52 files present=52 files scanned
- prompt/credential/auth-config/symlink-target hits 均为 0
- `pass=True`
- `leak-scan.txt` 是 evidence 最后修改文件

---

## 8. 原阶段 17 缺口关闭表

| 原缺口 | REWORK 证据 | 结论 |
|---|---|---|
| D0 live 流未保留 | `d0-events-live-sanitized.jsonl`，5 条连续记录 | 已关闭 |
| D0 process result 仅事后转述 | 独立 `d0-process-result.txt` | 已关闭 |
| D0 raw 流不可冻结 | size/SHA 在 runtime 删除前落证 | 已关闭 |
| `d0-pass.txt` 不存在 | required-check 后首次创建 | 已关闭 |
| sentinel 来源不可审计 | `agent_message` 与 assistant final 双重命中 | 已关闭 |
| D1 可能拼接旧 RUN | 同 RUN、D0 pass 后新 D1 | 已关闭 |
| pass 可能事后重建 | live → result/hash → required-check → pass | 已关闭 |
| final check 应为最终快照 | summary 在 check 后更新 | 未完全关闭，记非阻断备注 |

---

## 9. Gate、merge 与下一步

- Gate 1：**PASS（相对 main）**，不是全仓 GREEN。
- Gate 2 r4：仍为 **FAIL**。
- `DIAG_D1_READY_FOR_D2`：不是 Gate 2 verdict。
- 当前：**不可 merge**。

下一步唯一建议：执行 `docs/fixes/handoffs/CODEX_TASK_18.md`，使用全新 RUN_ID，仅运行一次 Omnigent Controller C/D2，固定：

- CLI `0.146.0` native path/SHA；
- `HARNESS_CODEX_PATH` 在 server/host/runner 启动前注入；
- 模型 `gpt-5.6-sol`；
- TUN start/end 只观察；
- 产品 240 秒 idle watchdog 不变；
- 约 1 秒粒度观测 runner/App Server spawn 与事件 relay；
- live evidence、required-check、独立 outcome 文件；
- 禁止完整 Gate 2 六轮。

若 D2 指向源码问题，Grok 只能报告，交回 Codex 另发 Hermes 开发卡。

