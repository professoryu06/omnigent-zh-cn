# Codex 只读验收 — 阶段 18

## 唯一裁决

**C) REJECT_PROTOCOL**

- RUN_ID：`20260730-190615-dc83140-grok-d2-c-cli0146-r1`
- Evidence：`C:\Users\Administrator\omnigent-diagnostics\20260730-190615-dc83140-grok-d2-c-cli0146-r1`
- 验收时 evidence：**仍存在**
- Grok 主张的 primary：`DIAG_RUNNER_SPAWN`
- Grok 主张的 subcase：`RUNNER_NOT_SPAWNED`
- 最终 primary：**不予接受**；本轮只能记录为审计处置 `DIAG_INCONCLUSIVE`，不得作为 Gate 2 结论。

`REJECT_PROTOCOL` 的决定性原因是：TASK 18 明确只授权一次 Controller C，禁止重试 C；但同一 TASK 18 执行链中至少存在四次实际 C 启动。创建新的 RUN_ID 不能重置任务卡的一次性授权：

| RUN evidence 目录 | C 启动证据 |
|---|---|
| `20260730-185922-dc83140-grok-d2-c-cli0146-r1` | `d2-c-timeline.txt`：C launch，PID 4472 |
| `20260730-190114-dc83140-grok-d2-c-cli0146-r1` | `d2-c-timeline.txt`：C launch，PID 42536 |
| `20260730-190428-dc83140-grok-d2-c-cli0146-r1` | `d2-c-timeline.txt`：C launch，PID 21640 |
| `20260730-190615-dc83140-grok-d2-c-cli0146-r1` | `d2-c-timeline.txt`：C launch，PID 19992 |

以上旧目录只用于审计“是否重试 C”这一硬约束，**未**被拼接为当前 RUN 的业务结果。即使不考虑该协议违规，当前 RUN 仍因零采样、约 4 秒外层超时、空业务退出码和 `spec_version` 矛盾而满足 `RECLASSIFY_DIAG_INCONCLUSIVE` 的条件；因此不能接受 `DIAG_RUNNER_SPAWN`。

## 16 项核对表

| # | 核对项 | 结论 | 证据与说明 |
|---:|---|---|---|
| 1 | 全新 RUN_ID / evidence / runtime / 端口；未拼接旧 RUN | PASS | 当前 RUN 的 `RUN_ID.txt`、`identity-start.txt`、`identity-end.txt`、`precheck.txt` 记录独立 evidence、runtime 和端口 `55518`；当前业务结论未拼接旧 RUN。另见上文：旧 RUN 仅用于发现任务级 C 重试违规。 |
| 2 | native 0.146.0 path/size/SHA start=end | PASS | `native-identity-start.txt`、`native-identity-end.txt`、`native-current-check.txt`：版本 `codex-cli 0.146.0`，size `358650672`，SHA-256 `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb`，start=end。 |
| 3 | `HARNESS_CODEX_PATH` 在 server/host/C 前设置并继承 | PASS | `child-environment-contract.txt`、`server-ready-timeline.txt`、`host-online-timeline.txt`、`d2-c-timeline.txt` 记录三阶段前均已设置为同一 native。由于没有可审计的 runner 样本，runner 子进程继承本身为 NA，不能据此推导 runner 已/未 spawn。 |
| 4 | TUN start/end 只观察且未人为改变 | PASS | `tun-status-start.txt`、`tun-status-end.txt`、`tun-observation.txt`：start/end 均 Meta Up，`tun_state_changed=False`。 |
| 5 | observer 业务前语法 PASS；业务中 SHA 未漂移 | PASS | `observer-node-check.txt`、`observer-identity-start.txt`、`observer-identity-end.txt`：`node --check` exit 0，SHA start=end。其运行时没有产出有效采样，另在第 9 项判 FAIL。 |
| 6 | server READY+10s、host online 后才 C | PASS | `server-ready-timeline.txt` 记录 READY 后 10 个健康采样；`host-online-timeline.txt`、`host-process.txt` 记录 dual online；`d2-c-timeline.txt` 的 C 启动时间晚于两者。 |
| 7 | 仅 1 次 C；无 D0/D1/后五轮；模型正确 | FAIL | 当前 RUN 的 `d2-c-timeline.txt` 虽写 `attempt=1_of_1`，`agents-sanitized.txt` 记录 `gpt-5.6-sol`，且未见 D0/D1/后五轮；但同一 TASK 18 下至少有四个 `d2-c-timeline.txt` 记录实际 C launch，违反全任务“只做一次 C / 禁止重试 C”。 |
| 8 | 产品 240s idle 未修改/拉长 | PASS | `product-watchdog-contract.txt`、`d2-c-timeline.txt`：配置仍为 240s，未被拉长。当前 C 约 4s 即被外层停止，未触达产品 240s watchdog；因此本项 PASS 不代表 idle 行为通过。 |
| 9 | D2 live evidence 实时落盘；sample ordinal 连续并覆盖 C 窗 | FAIL | `d2-samples-live-sanitized.jsonl`、`d2-events-live-sanitized.jsonl`、`d2-process-tree.txt` 均只有 5 bytes（UTF-8 BOM + 换行），有效 sample/event 均为 0；没有 ordinal，也没有覆盖 C 窗的进程采样。 |
| 10 | required-check 早于 outcome | FAIL | 文件时间顺序上 `d2-required-files-check.txt` 早于 `d2-outcome.txt`；但 required-check 将 5-byte 占位文件判为 `nonempty=True`，并在 `sample_count=0` 时把 `sample_ordinals_continuous=True`、`d2_required_files_pass=True`，属于语义性假阳性，未满足任务卡的可审计 required-check。 |
| 11 | diagnosis/outcome/summary 在 final-check 前冻结且之后未改 | PASS | `GROK_DIAGNOSIS_18.md`、`d2-outcome.txt`、`run-summary.txt` 均早于 `required-evidence-final-check.txt`；final-check、`evidence-manifest.txt` 中的哈希与验收时文件一致。 |
| 12 | business exit 与 cleanup exit 分离且可信 | FAIL | `d2-c-timeline.txt`、`d2-business-result.txt` 将业务与 cleanup 字段分开，但业务 `exit=`/`c_exit` 为空，并把约 4s 标为 `outer_budget_timeout`，与声明的 300s 外层预算矛盾；业务退出/超时结论不可信。 |
| 13 | cleanup 完整 | PASS | `cleanup.txt`、`pid-final-status.txt`、`port-final-status.txt`、`runtime-final-status.txt`、`codex-tmp-final-status.txt`：登记 PID dead、端口 free、runtime 删除、`.codex-tmp` start=end、leftover=0；验收时只读复核 runtime 不存在、端口无 listener、`.codex-tmp` 空。 |
| 14 | leak-scan 最后、hits=0、evidence 保留 | PASS | `leak-scan.txt` 是 evidence 最后文件，记录 scanned/expected `47/47`、hits=0；验收时 evidence 根仍存在。 |
| 15 | 仓库写入范围 | PASS | `identity-start.txt` 与 `identity-end.txt` 的 HEAD、八个冻结 blob 和 git status 一致；未见本 RUN 改源码/tests/政策/配置。仓库本来已有的修改和 `handoffs/` 未跟踪目录不能归因于本 RUN；本验收只新增 `CODEX_REVIEW_18.md`。 |
| 16 | 未冒充 Gate 2 PASS / mergeable | PASS | `GROK_DIAGNOSIS_18.md`、`d2-outcome.txt`、`run-summary.txt` 均声明这不是 Gate 2 verdict、不可 merge。 |

## Grok 自报三个弱点的结论

### 1. `sample_count=0` / samples 仅占位

这是实质性失败，不是可忽略的审计债务。三个所谓 live/process 文件都没有业务数据，因此 `runner_spawned=False` 与 `native_codex_child_observed=False` 没有进程采样支撑。零样本时只能写 **NOT_OBSERVABLE**，不能把“没有观察记录”解释成“已观察到未 spawn”。`DIAG_RUNNER_SPAWN / RUNNER_NOT_SPAWNED` 因此不可审计。

### 2. 约 4s `outer_budget_timeout` 与 300s 预算矛盾

`d2-c-timeline.txt` 在 C 启动约 4 秒后记录外层预算超时，但本轮声明的外层预算为 300 秒，且 `c_exit` 为空。现有 evidence 无法说明这是 C 自身退出、观察器/驱动提前结束，还是清理阶段终止。该记录不能证明产品的 240s idle，也不能可靠支持 `EARLY_EXIT`、`STALL` 或 `RUNNER_NOT_SPAWNED`。

### 3. `missing spec_version` 与本地 `spec_version=1` 矛盾

`d2-error-sanitized.txt` 报 `config.yaml missing required field: spec_version`，而 `agents-sanitized.txt` 声明本地 agent `spec_version=1`。本 RUN 没有保留可核对的实际打包/上传后 agent 配置或原始 runtime 输入；runtime 已按计划删除。因此无法判断是本地元数据记录错误、打包/传输丢字段、读取了另一份配置，还是产品解析问题。该错误更像发生在 turn setup / agent package 边界，不能反推 runner/native spawn 层故障。

## 分类结论

- 不接受 `DIAG_RUNNER_SPAWN`：没有覆盖 C 窗的有效采样，无法证明 runner/native 未 spawn。
- 不接受其他业务 primary：现有 evidence 也不足以明确支持 `EARLY_EXIT`、`STALL`、`RELAY` 或 `TRANSIENT_R4`。
- 本交付因重复执行 C 适用唯一裁决 **C) REJECT_PROTOCOL**；若只评价当前 RUN 的业务证据，其审计处置仍是 **`DIAG_INCONCLUSIVE`**。

## 下一张卡

**不允许基于本报告直接进入 Gate 2、merge 或直接宣称产品源码需要修复；也不自动授权再次运行 C。**

允许另发一张全新、明确授权的只读预检卡，先完成以下两件事：

1. 在不运行 C 的情况下，保留并哈希实际生成/打包/上传边界上的 agent `config.yaml`，证明 `spec_version` 在每一层是否存在。
2. 在不运行 C 的情况下验证 observer 能产出至少两个带连续 ordinal 的进程样本，并让零样本必然使 required-check FAIL。

只有预检明确证明产品打包/传输代码丢失 `spec_version` 时，才另发 **Hermes 开发卡**，以失败测试开路并单独实现修复；本审查不写补丁。修复及审查通过后，才可另行授权一个全新 RUN 的、真正单次、可审计 C/D2 卡。

## Gate 边界

- Gate 1：**PASS（相对 main）**，不等于全仓 GREEN。
- Gate 2 r4：**FAIL**。
- 本轮：**不是 Gate 2 PASS**，**不可 merge**。
- 本文件仅为只读验收结论；未改源码、tests、政策、STATUS、配置、TUN 或用户 Codex 认证，未重跑 D2/C、D0/D1 或完整 Gate 2，也未 commit/push/merge/tag。
