# Codex 只读验收 — 阶段 20

## 唯一裁决

**ACCEPT_WITH_NOTES**

接受 Hermes 的业务主分类：

```text
DIAG_HTTP_SESSION_READY_FOR_D2
```

- RUN_ID：`20260730-144404-dc83140-hermes-http-session-roundtrip-r1`
- Evidence：`C:\Users\Administrator\omnigent-diagnostics\20260730-144404-dc83140-hermes-http-session-roundtrip-r1`
- 验收时 evidence：**仍存在**
- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- 分支：`docs/fix-plans-core-secondary`

本 ACCEPT 只接受以下窄结论：

> 在本 RUN 的隔离 server、固定无秘密 bundle 和一次 multipart create 路径中，上传前、LocalArtifactStore、session 绑定和 `/agent/contents` 回取的 bundle 字节完全一致；`spec_version: 1` 未在 HTTP/session 路径丢失，阶段 18 的 missing-spec-version 错误未复现。

它不接受以下扩大表述：

- 阶段 18 已证明是旧 evidence 拼接；
- runner、native Codex、event relay 或 240 秒 idle 已通过；
- D2 或 Gate 2 已通过；
- 当前可 merge。

本轮存在三项协议/审计债务，见下文。它们不足以推翻独立保存的三份 bundle 字节、四份 config 和真实 HTTP 响应，但下一张 D2 卡不得重复这些缺口。

---

## 1. 核对表

| # | 核对项 | 结论 | Evidence 与说明 |
|---:|---|---|---|
| 1 | 全新 RUN/evidence/runtime/端口，未拼接旧 RUN | PASS_WITH_NOTE | `RUN_ID.txt`、`identity-start.txt`、`port-start.txt`；路径均带本 RUN_ID。首次进程预检曾发现用户自有 `codex.exe`，关闭后同 RUN 继续，违反任务卡“非零即停”的严格流程，见保留意见 1。 |
| 2 | HEAD、branch、九 blob start=end | PASS | `identity-start.txt`/`identity-end.txt`、`candidate-source-blobs-start.txt`/`end.txt`；九项完整 hash 均 start=end。Codex 重新计算当前九项工作树 hash，仍与任务卡一致。 |
| 3 | TUN 只观察 | PASS | `tun-status-start.txt`/`end.txt`：Meta False→False，`tun_state_changed_by_hermes=False`。本卡只走 loopback HTTP，不据此评价 Codex provider 网络。 |
| 4 | 环境隔离/no-proxy | PASS | `child-environment-contract.txt`、`server-command-sanitized.txt`：`OMNIGENT_DATA_DIR` 指向本 RUN runtime，loopback NO_PROXY，driver 源码使用 `httpx.Client(..., trust_env=False)`。 |
| 5 | driver 业务前编译、SHA 冻结 | PASS | `driver-pycompile-check.txt` exit=0；`driver-identity.txt`、`business-start-marker.txt` 与 required-check 的 SHA 一致；持久 `driver-source.py` 可读。 |
| 6 | server 仅启动一次、隔离 data root | PASS_WITH_NOTE | command/PID/port/data root 可映射，后续真实 POST/GET 成功。`server-lifecycle-live.jsonl` 只有 1 条聚合记录，不符合“约每秒一条”的原卡要求，见保留意见 2。 |
| 7 | READY+10s 后才 POST | PASS_WITH_NOTE | `server-ready.txt` UTC=`14:51:29.083779Z`，`artifact-tree-at-ready.txt` 写于约 10 秒后，POST live UTC=`14:52:18.134536Z`；顺序和等待长度成立。但没有 10 条逐秒 health live 行，只能由聚合字段和时间戳佐证。 |
| 8 | 上传前 bundle 有效 | PASS | `request-bundle-meta.txt`、`request-bundle-config.yaml`、live ordinal 1–4：root config count=1，`spec_version=1`、name/harness/model 正确，offline validation PASS。 |
| 9 | POST 只执行一次且 201 | PASS | live JSONL 只有一个 POST stage；`session-create-response-sanitized.json` 有非空 session/agent id hash，agent name 正确。 |
| 10 | session-scoped artifact 唯一匹配 | PASS | `artifact-tree-at-ready.txt`/`after-create.txt`、`stored-artifact-match.txt`：新增匹配数=1，stored size=340，SHA=`91b2f24a...245a`。 |
| 11 | agent GET 只执行一次且 200 | PASS | live ordinal 7、`session-agent-response-sanitized.json`：name 和 harness 正确；持久 id 仅保存 hash。 |
| 12 | contents GET 只执行一次且 200 | PASS | live ordinal 8、`retrieved-bundle-meta.txt`：gzip、正确 X-Agent-Name、session-scoped=true。 |
| 13 | 五层字节/字段一致 | PASS | Codex 独立重算：request/stored/retrieved bundle 均 340 bytes 且 SHA=`91b2f24a...245a`；source/materialized/request-root/retrieved-root config 均 228 bytes 且 SHA=`e8c07543...cec6`，固定字段全部正确。 |
| 14 | live JSONL 实时结构与次数 | PASS | 11 个有效 JSON 对象，ordinal 1..11 连续，UTC 单调，POST=1、GET=2、全部 `pass=true`；驱动使用 append+flush+fsync。 |
| 15 | driver exit/业务与 cleanup 分离 | PASS | `http-driver-process-result.txt`：attempt=1_of_1、exit=0、timeout=False、duration=1.38s。server cleanup 另记于 `cleanup.txt`。 |
| 16 | 未启动 host/runner/C/native 或 Gate | PASS | start/end forbidden check、outcome 与报告均为 False；没有 D0/D1/D2/Gate 业务 evidence。 |
| 17 | required-check 早于 outcome | PASS_WITH_NOTE | 文件时间顺序正确，核心 hash/count/exit 均重读。它没有检查缺失的 `server-process-result.txt`，也把单行 lifecycle 当作满足，见保留意见 2/3。 |
| 18 | cleanup 完整 | PASS | server PID dead、port free、runtime 删除、evidence 保留、leftover=0。验收时 runtime 仍不存在，evidence 仍存在。 |
| 19 | outcome/report 冻结、manifest 可复核 | PASS | final-check 记录 outcome/summary/report 最终 SHA；Codex 对 manifest 49 个 hash 条目独立重算，mismatch=0。 |
| 20 | leak-scan 最后且 hits=0 | PASS | `leak-scan.txt` 为最后文件，scanned/expected=50/50、hits=0。 |
| 21 | 仓库写入范围 | PASS_WITH_NOTE | start/end git status 字节一致；报告创建于 RUN 窗口，九个产品 blob无漂移。因整个 `handoffs/` 已被 git 折叠为未跟踪目录，git status 本身不能逐文件证明唯一新增，但没有 evidence 表明修改了源码/tests/政策/STATUS。 |
| 22 | Gate 边界 | PASS | 报告明确非 D2 PASS、非 Gate 2 PASS、不可 merge。 |

---

## 2. 独立数据复核

Codex 直接从持久 evidence 重新计算：

### Bundle

| 文件 | Size | SHA-256 |
|---|---:|---|
| `request-bundle.tar.gz` | 340 | `91b2f24a5bb164fb5f10bf77ccc3d2e48fb4645dc90bd70dbb13252b794e245a` |
| `stored-artifact-match.tar.gz` | 340 | `91b2f24a5bb164fb5f10bf77ccc3d2e48fb4645dc90bd70dbb13252b794e245a` |
| `retrieved-bundle.tar.gz` | 340 | `91b2f24a5bb164fb5f10bf77ccc3d2e48fb4645dc90bd70dbb13252b794e245a` |

### Root config

以下四份均为 228 bytes，SHA-256 均为：

```text
e8c0754348f2f626137f446de9352d3d5c701a4a2cda42ea45e500dd2eb6cec6
```

- `agent-source-config.yaml`
- `request-materialized-config.yaml`
- `request-bundle-config.yaml`
- `retrieved-bundle-config.yaml`

四份均实际包含：

```text
spec_version=1
name=controller-http-session-cli0146
harness=codex
model=gpt-5.6-sol
```

因此本 RUN 的核心结论不是只依赖 Hermes 报告摘要，而是有可独立重算的字节证据。

---

## 3. 保留意见

### 3.1 首次 precheck 非零后同 RUN 继续

`precheck.txt` 和 `forbidden-process-check-start.txt` 明确记载：首次发现用户自有 `codex.exe` PID 1156，用户关闭后再次检查为 0。

严格按 `CODEX_TASK_20.md`，首次非零应停止为 `DIAG_INCONCLUSIVE`，不应在同 RUN 继续。这是协议偏差。

不改判为 REJECT 的窄理由：

- 该进程在 server/driver/business marker 前已由用户关闭；
- 本卡没有调用 native Codex，也不以“未观察到 codex child”作为业务结论；
- 核心结论来自随后隔离 data root 内的真实 HTTP 字节、artifact 和回取 bundle。

下一张卡必须执行**一次性 precheck**：非零立即停止，不得要求用户在 RUN 中关闭后续跑。

### 3.2 server lifecycle 不是逐秒 live

`server-lifecycle-live.jsonl` 只有一条聚合对象：

```text
ordinal=1
health_ok_10s=10
```

它没有提供任务卡要求的 10 条逐秒 health 样本。READY 到 artifact snapshot 的 UTC 相差约 10 秒，且 39 秒后真实 POST/GET 均成功，所以 server 对本次 HTTP 业务确实可用；但“10/10 每秒健康”本身没有完全按协议落证。

下一张 D2 卡必须要求：

- server lifecycle 至少 10 条 READY 后逐秒数据；
- host lifecycle 至少覆盖 online 等待；
- D2 observer 从 C 前至少 1 秒到业务终态/外层预算逐秒落盘；
- 零样本或聚合占位必使 required-check FAIL。

### 3.3 两个声明文件缺失

任务卡 Files 列表包含：

- `server-process-result.txt`
- `http-error-sanitized.txt`

本 evidence 未创建这两项，且 required-check 未检查。

`http-error-sanitized.txt` 在成功路径可合理视为 NA；`server-process-result.txt` 的关键信息由 `server-ready.txt`、`pid-final-status.txt` 和 `cleanup.txt` 补足。它们不推翻 HTTP 字节结论，但 required-check 不应声称“所有必需 evidence”无条件齐全。

下一张卡必须明确：成功路径也创建空语义明确的 error 文件；所有声明文件必须逐项检查。

---

## 4. 对阶段 18 根因范围的修订

阶段 20 足以排除本工作树当前通用路径中的以下优先嫌疑：

```text
CLI materialize/bundle
  -> multipart POST /v1/sessions
  -> validate_agent_bundle
  -> session-scoped agent binding
  -> LocalArtifactStore
  -> GET /agent/contents
```

因此阶段 18 的 `missing spec_version` 更可能是：

- 阶段 18 诊断输入/agent 形态不正确；
- 阶段 18 多次试跑或编排器选择了另一份 config；
- C/D2 后续 runner 装载或 workspace/cache 选择了非预期 bundle；
- 旧阶段 18 evidence 本身不足以审计。

不能仅凭本 RUN 宣称具体是哪一项。下一张单次 D2 必须保存真实请求 bundle hash、session contents hash、runner 下载/缓存边界和实际进程采样，继续沿数据流定位。

---

## 5. 下一步

**允许进入一张全新 RUN、Hermes 执行的单次 Controller C/D2 诊断卡。**

前提：

- 不复用阶段 18 或 20 的 PID、端口、runtime、exit、sample；
- 固定 CLI `0.146.0` native path/size/SHA；
- 模型 `gpt-5.6-sol`；
- `HARNESS_CODEX_PATH` 在 server/host/C 前注入；
- 产品 240 秒 idle watchdog 不变；
- TUN 只观察，并在 RUN 前由用户确保与 D0/D1 基线一致；
- agent 使用已验证的 `spec_version: 1` 目录形态；
- observer 真正逐秒落盘，退出码必须为整数；
- 只运行一次 C，禁止完整 Gate 2 六轮。

若 D2 首次在明确产品函数/边界失败，Codex 再另发 **Grok 窄修复卡**。本验收不写产品补丁。

## Gate 边界

- Gate 1：**PASS（相对 main）**，非全仓 GREEN。
- Gate 2 r4：**FAIL**。
- `DIAG_HTTP_SESSION_READY_FOR_D2`：不是 D2 PASS、不是 Gate 2 PASS。
- 当前：**不可 merge**。
- 本验收未重跑 HTTP、D0、D1、D2、pytest、Ruff 或 Gate；未改源码/tests/政策/STATUS/TUN/认证；未 commit/push/merge/tag。
