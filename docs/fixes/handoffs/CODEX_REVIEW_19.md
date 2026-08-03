# Codex 只读验收 — 阶段 19

## 唯一裁决

**B) RECLASSIFY_DIAG_PREFLIGHT_READY_FOR_D2**

- 最终 primary：`DIAG_PREFLIGHT_READY_FOR_D2`
- Grok 冻结 primary：`DIAG_INCONCLUSIVE`（原 evidence 保持不改）
- RUN_ID：`20260730-192929-dc83140-grok-agent-observer-preflight-r1`
- Evidence：`C:\Users\Administrator\omnigent-diagnostics\20260730-192929-dc83140-grok-agent-observer-preflight-r1`
- 验收时 evidence：**仍存在**

Grok 按任务卡把 `observer_exit` 空值纳入严格 required-check，因此冻结为 `DIAG_INCONCLUSIVE` 是保守且合规的原始记录。Codex 只读复核后改判，是因为该空值只损害“退出码已落盘”这一形式字段，并未损害本卡的两个实质目标：

1. 六层 agent bundle 路径均保留 `spec_version=1` 和其余固定字段。
2. 冻结 observer 源码确实写出 5 条真实、连续、单调、命中 sentinel 的样本；零样本负向也被同一判定函数判为 FAIL。

本改判只表示**预检能力已就绪**，不表示 HTTP/session、D2 或 Gate 2 已通过，也不自动授权 Grok 运行 D2。

## 15 项核对表

| # | 核对项 | 结论 | Evidence 与说明 |
|---:|---|---|---|
| 1 | 全新 RUN_ID/evidence/runtime；未拼接旧 RUN | PASS | `RUN_ID.txt`、`identity-start.txt`、`precheck.txt`；诊断根下只有一个 `agent-observer-preflight` RUN，当前 evidence 内未命中阶段 14–18/r4 RUN 字符串。runtime 使用本 RUN_ID，验收时已不存在。 |
| 2 | HEAD/七 blob start=end | PASS | `identity-start.txt`、`identity-end.txt`、`candidate-source-blobs-start.txt`、`candidate-source-blobs-end.txt`：HEAD=`dc83140c73ceb12fa165753c1880c19f68da86f4`、分支正确，七 blob 全部 start=end 且等于任务卡期望值；验收时重新计算仍匹配 HEAD。 |
| 3 | 未启动禁止的产品层或测试层 | PASS | `identity-start.txt`、`identity-end.txt`、`native-identity-observe-only.txt`、`cleanup.txt`：server/host/runner/C/native Codex 均 False；evidence 未见 `omnigent run`、D0/D1/D2/Gate2、pytest 或 ruff 执行记录。 |
| 4 | pipeline 与 observer 各仅一次 | PASS | `preflight-start-marker.txt`、`pipeline-process-result.txt`、`observer-process-result.txt`：均为 `attempt=1_of_1`；只存在一组 pipeline/observer live evidence。 |
| 5 | 语法检查、marker 与脚本冻结 | PASS | `python-compile-check.txt`、`observer-node-check.txt` 均 exit=0；`driver-identities.txt` 先记录 SHA，随后 `preflight-start-marker.txt` 冻结。`preflight-required-files-check.txt` 记录 pipeline/observer SHA match；持久 `observer-source.mjs` 的实测 SHA 为 `2461c4b8...947893`，与 marker 相同。 |
| 6 | 六层固定字段 | PASS | `agent-source-config.yaml`、`agent-materialized-config.yaml`、`agent-bundle-config.yaml`、`server-validation-result.txt`、`artifact-roundtrip-meta.txt`、`agent-cache-config.yaml`、`agent-cache-load-result.txt`：六层均为 `1 / controller-preflight-cli0146 / codex / gpt-5.6-sol`。 |
| 7 | bundle/artifact 哈希、大小与根成员 | PASS | `agent-bundle-members.txt`：根 `config.yaml` count=1；`agent-bundle.tar.gz` 与 `artifact-roundtrip.tar.gz` 均为 334 bytes，实测 SHA-256 均为 `8d3f03a881a175f5f3bb31145635491b6a9a36cac829b0f40b72e935b3d04d57`。 |
| 8 | pipeline live 边界数与 ordinal | PASS | `pipeline-boundaries-live.jsonl`：11 个有效 JSON 对象，ordinal 精确为 1..11，UTC 单调、每层 `pass=true`；`pipeline-process-result.txt` exit=0、`first_failing_boundary=None`。 |
| 9 | observer 正向样本 | PASS | `observer-live.jsonl`：5 个有效 JSON 对象，ordinal 1..5，UTC 单调，sentinel_seen=5，所有 `query_exit=0`，同一 observer PID 12152；`sentinel-identity.txt` 与样本中的 sentinel PID/parent 一致。`observer_exit` 空值另见下文保留意见。 |
| 10 | 零样本负向 | PASS | `observer-zero-sample-negative-check.txt`：`zero_sample_data_line_count=0`、`zero_sample_required_check_pass=False`、`same_function=Test-ObserverLiveRequired`、fixture 未混入正式 live evidence且随后删除。 |
| 11 | required-check 早于 outcome；报告冻结 | PASS | `preflight-required-files-check.txt` 早于 `preflight-outcome.txt`；outcome/summary/report 早于 `required-evidence-final-check.txt`。final-check 中报告 size=7537、SHA=`005d8bcf...bd6fe`，与验收时实测一致。 |
| 12 | cleanup、runtime、PID、TUN、evidence | PASS | `pid-final-status.txt` 记录当时 observer/sentinel 均 dead；`runtime-final-status.txt` 记录目标绝对路径、TEMP containment、leaf、RUN_ID、非 reparse 和删除结果；验收时 runtime 不存在。`tun-status-start.txt`/`tun-status-end.txt` 为 Up→Up、只观察、未由 Grok 改变；evidence 仍在。 |
| 13 | final-check → manifest → leak-scan | PASS | 文件 UTC 顺序正确；`required-evidence-final-check.txt` 的 44 个索引项和 `evidence-manifest.txt` 的 45 个索引项经重新哈希均 0 mismatch；`leak-scan.txt` 是最后文件、扫描含仓库报告共 46 项、hits=0。 |
| 14 | 仓库写入范围 | PASS | `git-status-start.txt` 与 `git-status-end.txt` 字节/哈希相同；七个相关产品 blob 未变。handoffs 时间线显示本 RUN 窗口只新增 `GROK_DIAGNOSIS_19.md`；既有 `CODEX_TASK_19.md` 在 RUN 前已存在。 |
| 15 | 未冒充 Gate 2 PASS / mergeable / D2 授权 | PASS | `GROK_DIAGNOSIS_19.md`、`preflight-outcome.txt`、`run-summary.txt` 均未宣称 Gate 2 PASS；报告明确不可 merge、未自行运行或授权 D2。 |

## 六层 `spec_version` 结论

本 RUN 足以证明：对于任务卡固定的目录型 agent 输入，当前冻结工作树的以下**离线路径**不会丢失 `spec_version`：

```text
source
  -> canonicalize/materialize
  -> CLI bundle
  -> bundle 根 config.yaml
  -> validate_agent_bundle
  -> LocalArtifactStore put/get
  -> AgentCache.load / workdir config.yaml
```

四份持久配置文件内容和 SHA 完全相同；bundle 与 artifact roundtrip 的字节哈希也完全相同。不存在支持 `DIAG_AGENT_BUNDLE_PIPELINE` 的失败边界，因此本轮不应发 Hermes 修复 parser、bundler、LocalArtifactStore 或 AgentCache。

## Observer 正向、负向与空 exit

### 正向

`observer-source.mjs` 的 SHA 与业务前 marker 相同。源码在读取 sentinel PID 失败时会 exit 2；正常路径循环写入恰好 5 条 sample 后执行 `process.exit(0)`。实际 live evidence 恰好包含 5 条完整记录，全部来自同一 observer PID，sentinel/parent 可映射，查询 exit 全为 0，stderr 只有 BOM/空白而无语义内容。

因此 observer 的“能实时连续采样”能力已经实质证明。不能因为 PowerShell `Start-Process` 没把最终 ExitCode 写入结果文件，就把这 5 条样本改判为不存在或不可观察。

### 负向

零样本 fixture 得到 0 个数据行且 required-check=False；正式 live 文件有 5 个数据行，两者未混用。这关闭了阶段 18 把 BOM/空占位误当 nonempty PASS 的缺口。

### 保留意见

`observer_exit=` 仍是明确的编排记录缺陷。它不阻止本轮预检 readiness 改判，但下一次任何包含 observer 的正式卡必须在业务前验证 ExitCode 捕获；若正式 D2 再出现空 exit，其 required-check 必须 FAIL，不能再次由 readiness 推论代替业务 exit。

## 对阶段 18 根因范围的修订

阶段 18 的 `missing spec_version` 现在**不能再优先归因于通用离线 bundler/parser/LocalArtifactStore/AgentCache 路径**。根因范围已收窄到本 RUN 没有覆盖的边界：

- 阶段 18 诊断脚本实际构造的源 agent 是否真与其摘要一致；
- `run_chat` 的 HTTP multipart/session create 输入；
- session 侧存储、选择或下载的实际 bundle；
- 目录 agent 与 session 绑定过程中是否读到了另一份 `config.yaml`。

这仍不能表述成“已经证明是 HTTP/session 产品 bug”，因为阶段 18 没保留实际上传和 session 取回的 bundle，阶段 19 也没有启动 HTTP/server。

## 下一张卡建议

**下一张唯一建议：HTTP/session 只读 roundtrip 卡。**

该卡应使用全新 RUN，在不启动 host、runner、Controller C 或 native Codex 的前提下，只启动隔离 server，并对同一个固定 bundle 保存和核对：

1. CLI 准备发送的 multipart bundle 哈希及根 `config.yaml`；
2. session create 接收并验证后的 bundle 哈希；
3. artifact/session 实际存储的 bundle；
4. `/v1/sessions/{id}/agent/contents` 取回字节；
5. 对取回字节执行只读 parse，核对 `spec_version/name/harness/model`。

该卡若 PASS，之后才另发一张真正单次、可审计 D2 卡；若在明确产品函数/边界首次丢字段，再另发 Hermes 开发卡。无需仅为本轮空 observer exit 重跑整个预检，也不建议现在直接运行 D2。

## Gate 边界

- Gate 1：**PASS（相对 main）**，非全仓 GREEN。
- Gate 2 r4：**FAIL**。
- `DIAG_PREFLIGHT_READY_FOR_D2`：**不是 Gate 2 PASS，也不是 D2 PASS 或自动执行授权**。
- 当前仍**不可 merge**。
- 本验收未改源码、tests、政策、STATUS、TUN、认证或配置，未重跑 pipeline/observer/D2/C，未 commit/push/merge/tag。
