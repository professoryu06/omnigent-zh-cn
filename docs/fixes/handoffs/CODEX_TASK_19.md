# CODEX TASK 19 — Agent Bundle / Observer 只读预检

> **For agentic workers:** 本卡由 Grok 执行。它是阶段 18 后的根因预检卡，不是开发卡，也不是 D2/Gate 2 卡。只允许各执行一次离线 agent bundle pipeline 和 observer sentinel 预检；不得启动 Omnigent server、host、runner、Controller C 或 native Codex。

**Goal:** 在不运行 C/D2 的情况下，确定 `spec_version: 1` 是否能从源 `config.yaml` 完整经过实际 CLI materialize/bundle、server validation、artifact roundtrip 和 runner-side AgentCache load；同时证明下一张 D2 卡使用的 observer 能持续写出真实样本，并且零样本一定使 required-check 失败。

**Architecture:** 一个仓库外 Python 驱动只调用当前工作树的既有函数，按真实产品数据流逐层保存脱敏配置、哈希和解析结果；一个仓库外 Node observer 只观察一个诊断自有 sentinel 进程，实时 append JSONL。两个预检在语法检查并冻结 SHA 后各运行一次，之后先做 required-check，再写 outcome、cleanup、final-check、manifest 和 leak-scan。

**Tech Stack:** 原生 Windows PowerShell、工作树 `.venv\Scripts\python.exe`、Node.js、YAML、tar.gz、JSONL、SHA-256。

## Global Constraints

- **执行者：** Grok（只读诊断，不是实现者，不是 Gate 2 签字人）。
- **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`
- **分支：** `docs/fix-plans-core-secondary`
- **唯一仓库交付：** `docs/fixes/handoffs/GROK_DIAGNOSIS_19.md`
- **持久 evidence：** `C:\Users\Administrator\omnigent-diagnostics\$RUN_ID\`，完成后不得删除。
- **临时 runtime：** `%TEMP%\omnigent-agent-observer-preflight-$RUN_ID\`，仅在 cleanup 阶段删除。
- **只允许一次：** offline agent pipeline `1_of_1`；observer sentinel run `1_of_1`。
- **绝对禁止执行：** `omnigent run`、Controller C、D0、D1、D2、Omnigent server、host、runner、native Codex、完整 Gate 2、Gate 1、pytest、ruff。
- **绝对禁止修改：** `omnigent/`、`tests/`、政策、`STATUS.md`、旧 handoff、TUN、代理、认证、用户 Codex 配置。
- **禁止：** commit、push、merge、tag、PR/Issue 修改。
- 不得复制或拼接阶段 14–18/r4 evidence 作为本 RUN 结果；旧报告只能作为背景阅读。
- Gate 1=`PASS（相对 main）`，非全仓 GREEN；Gate 2 r4=`FAIL`；不可 merge。

---

## 1. 必读与本卡边界

### Files

- Read: `docs/fixes/handoffs/CODEX_TASK_18.md`
- Read: `docs/fixes/handoffs/GROK_DIAGNOSIS_18.md`
- Read: `docs/fixes/handoffs/CODEX_REVIEW_18.md`
- Read: `omnigent/chat.py`
- Read: `omnigent/cli.py`
- Read: `omnigent/spec/__init__.py`
- Read: `omnigent/spec/parser.py`
- Read: `omnigent/server/bundles.py`
- Read: `omnigent/stores/artifact_store/local.py`
- Read: `omnigent/runtime/agent_cache.py`

- [ ] **Step 1: 明确阶段 18 只可作为问题背景**

允许沿用：

```text
stage18_disposition=REJECT_PROTOCOL
stage18_business_audit=DIAG_INCONCLUSIVE
stage18_error=config.yaml missing required field: spec_version
stage18_local_claim=spec_version=1
stage18_observer_sample_count=0
```

不得沿用阶段 18 的 PID、sample、exit、bundle、runtime 或进程判断作为本 RUN 结果。

- [ ] **Step 2: 明确本卡不是 D2 授权**

本卡即使全部 PASS，也只能输出：

```text
DIAG_PREFLIGHT_READY_FOR_D2
```

它不等于 `DIAG_D1_READY_FOR_D2`、D2 PASS、Gate 2 PASS 或 mergeable；是否另发单次 D2 卡由 Codex 验收后决定。

---

## 2. 全新 RUN、identity 与冻结源

### Files

- Create outside repo: `C:\Users\Administrator\omnigent-diagnostics\$RUN_ID\`
- Create outside repo: `%TEMP%\omnigent-agent-observer-preflight-$RUN_ID\`
- Evidence: `RUN_ID.txt`
- Evidence: `identity-start.txt`
- Evidence: `identity-end.txt`
- Evidence: `candidate-source-blobs-start.txt`
- Evidence: `candidate-source-blobs-end.txt`
- Evidence: `git-status-start.txt`
- Evidence: `git-status-end.txt`
- Evidence: `precheck.txt`

- [ ] **Step 1: 一次性生成 RUN**

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$PYTHON = Join-Path $WORKTREE '.venv\Scripts\python.exe'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-dc83140-grok-agent-observer-preflight-r1'
$EVIDENCE_ROOT = "C:\Users\Administrator\omnigent-diagnostics\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-agent-observer-preflight-$RUN_ID"
```

`EVIDENCE_ROOT` 和 `RUNTIME_ROOT` 必须开始时均不存在；否则停止为 `DIAG_INCONCLUSIVE`，不得删除后复用或换 RUN 继续。

- [ ] **Step 2: start identity**

记录：

```text
HEAD=dc83140c73ceb12fa165753c1880c19f68da86f4
branch=docs/fix-plans-core-secondary
worktree=<absolute path>
RUN_ID=<new RUN>
pipeline_attempt=1_of_1
observer_attempt=1_of_1
controller_c_executed=False
server_started=False
host_started=False
runner_started=False
native_codex_started=False
```

- [ ] **Step 3: 冻结七个相关 blob**

| 文件 | 期望 blob |
|---|---|
| `omnigent/chat.py` | `6c65a6b9101f6e9c29a243fa73f98519e9bc9443` |
| `omnigent/cli.py` | `1a0e4ea9fae5def40d136c83fabb068aac0d93d9` |
| `omnigent/spec/__init__.py` | `46e0a6775a8452f2739295c8bb23fd1ff3cf7728` |
| `omnigent/spec/parser.py` | `8538aa87fb495c541bb2bc18b08ea915edfd0c85` |
| `omnigent/server/bundles.py` | `40451999b8b71e6fd010a4bdea91f81efdf3f93a` |
| `omnigent/stores/artifact_store/local.py` | `fc52f20a0b83626cdbfe4bbf36572f1978f3dd23` |
| `omnigent/runtime/agent_cache.py` | `774989fc6b2435850c7c95d256714884bbd3b878` |

对每个文件同时记录 `git hash-object`、`HEAD:<path>` 和 `match=True|False`。任一不匹配即停止为 `DIAG_INCONCLUSIVE`。

- [ ] **Step 4: precheck**

排除诊断驱动 self/ancestor 后，检查是否存在与本 RUN、旧 Task 18 runtime、Omnigent server/host/runner/C、预定 sentinel 有关的残留进程或路径。非零只记录，不 kill，并停止为 `DIAG_INCONCLUSIVE`。

- [ ] **Step 5: 只观察环境**

记录 TUN Meta start/end 状态，但不得开关或调用控制 API。native Codex 只允许记录既定 path、size、SHA，不得执行 `--version` 或任何 prompt：

```text
native_expected_size=358650672
native_expected_sha256=bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb
native_executed=False
```

---

## 3. 预检脚本语法冻结

### Files

- Create outside repo: `$RUNTIME_ROOT\agent-pipeline-preflight.py`
- Create outside repo: `$RUNTIME_ROOT\observer-preflight.mjs`
- Evidence: `driver-identities.txt`
- Evidence: `python-compile-check.txt`
- Evidence: `observer-node-check.txt`
- Evidence: `preflight-start-marker.txt`

- [ ] **Step 1: 脚本只可写在 runtime**

Python 驱动只能创建隔离 agent、调用既有函数、保存 evidence；Node observer 只能观察诊断自有 sentinel。不得 monkey-patch 产品模块，不得覆盖函数，不得写 repo。

- [ ] **Step 2: 业务前语法检查**

```powershell
& $PYTHON -m py_compile "$RUNTIME_ROOT\agent-pipeline-preflight.py"
node --check "$RUNTIME_ROOT\observer-preflight.mjs"
```

记录命令、UTC、exit、stdout/stderr size+SHA。语法通过后记录两个脚本的 absolute path、size、SHA-256。

语法修复只允许发生在 `preflight-start-marker.txt` 创建前；创建 marker 后，脚本 SHA 必须冻结，禁止编辑和重试。

- [ ] **Step 3: 创建 start marker**

仅在两个语法检查均 PASS 后首次写：

```text
pipeline_attempt=1_of_1
observer_attempt=1_of_1
scripts_frozen=True
```

---

## 4. Offline agent bundle pipeline（仅一次）

### Files

- Create outside repo: `$RUNTIME_ROOT\agent-source\config.yaml`
- Evidence: `agent-source-config.yaml`
- Evidence: `agent-source-meta.txt`
- Evidence: `agent-canonicalized-meta.txt`
- Evidence: `agent-materialized-config.yaml`
- Evidence: `agent-materialized-meta.txt`
- Evidence: `agent-bundle.tar.gz`
- Evidence: `agent-bundle-members.txt`
- Evidence: `agent-bundle-config.yaml`
- Evidence: `server-validation-result.txt`
- Evidence: `artifact-roundtrip.tar.gz`
- Evidence: `artifact-roundtrip-meta.txt`
- Evidence: `agent-cache-config.yaml`
- Evidence: `agent-cache-load-result.txt`
- Evidence: `pipeline-boundaries-live.jsonl`
- Evidence: `pipeline-process-result.txt`

- [ ] **Step 1: 创建无秘密的固定 source**

`$RUNTIME_ROOT\agent-source\config.yaml` 内容必须精确为：

```yaml
spec_version: 1
name: controller-preflight-cli0146
description: Stage 19 offline bundle preflight
executor:
  type: omnigent
  config:
    harness: codex
    model: gpt-5.6-sol
prompt: Reply with CONTROLLER_OK and stop.
```

该配置不包含认证、代理值或用户秘密，因此可以原样持久保存在 evidence。

- [ ] **Step 2: 按真实 CLI 数据流执行一次**

Python 驱动必须按以下顺序调用工作树函数；每完成一个边界立即向 `pipeline-boundaries-live.jsonl` append 一行并 flush，字段至少包含 `ordinal`、`utc`、`stage`、`path_or_key`、`size`、`sha256`、`spec_version`、`name`、`harness`、`model`、`pass`：

1. `omnigent.chat._canonicalize_local_agent_path(source_dir)`
2. `omnigent.chat._materialize_override_bundle(canonical, ChatOverrides())`
3. `omnigent.chat._validate_agent_spec(materialized)`
4. `omnigent.chat._bundle_agent(materialized)`
5. 从 tar.gz 中读取根 `config.yaml`
6. `omnigent.server.bundles.validate_agent_bundle(bundle_bytes, enforce_handler_allowlist=False)`
7. `bundle_location('ag_stage19_preflight', bundle_bytes)`
8. `LocalArtifactStore($RUNTIME_ROOT\artifact-store).put(key, bundle_bytes)`
9. `LocalArtifactStore.get(key)`，保存为 `artifact-roundtrip.tar.gz`
10. `AgentCache(store, $RUNTIME_ROOT\agent-cache).load('ag_stage19_preflight', key, expand_env=False)`
11. 从 `LoadedAgent.workdir\config.yaml` 读取并保存 `agent-cache-config.yaml`

`_cleanup_materialized_override_bundle(materialized)` 必须放在 `finally`，但 cleanup 不得覆盖 pipeline 的 business exit/exception。

- [ ] **Step 3: 每层严格断言**

以下值必须在 source、materialized、bundle config、server validation spec、artifact roundtrip、AgentCache spec/cache config 六层全部成立：

```text
spec_version=1
name=controller-preflight-cli0146
harness=codex
model=gpt-5.6-sol
```

同时必须满足：

```text
bundle_member_config_yaml_count=1
bundle_config_at_root=True
bundle_sha256=artifact_roundtrip_sha256
bundle_size=artifact_roundtrip_size
pipeline_ordinals_continuous=True
pipeline_stage_count=11
```

任一边界失败时，记录 `first_failing_boundary=<exact stage>`、异常类型和脱敏消息；禁止修脚本后再跑 pipeline。

- [ ] **Step 4: 边界解释**

若六层均 PASS，只能说明当前离线路径未丢 `spec_version`。不得因此宣称阶段 18 错误不存在，也不得宣称 HTTP/session/host/runner 远端路径已通过。

---

## 5. Observer sentinel 预检（仅一次）

### Files

- Create outside repo: `$RUNTIME_ROOT\sentinel.pid`
- Evidence: `observer-source.mjs`
- Evidence: `observer-live.jsonl`
- Evidence: `observer-stderr.txt`
- Evidence: `observer-process-result.txt`
- Evidence: `observer-required-check.txt`
- Evidence: `observer-zero-sample-negative-check.txt`

- [ ] **Step 1: 启动诊断自有 sentinel**

使用当前 Node 创建一个存活约 8 秒、不联网、不读 repo、不启动产品的 sentinel，并立即记录 PID、parent PID、创建 UTC 和命令 SHA。禁止使用 Omnigent/Codex 进程充当 sentinel。

- [ ] **Step 2: observer 实时 append**

冻结后的 `observer-preflight.mjs` 每约 1 秒采样一次，共至少 4 次。每一行必须在采样时直接 append+flush 到 `observer-live.jsonl`，字段至少包含：

```text
ordinal
utc
observer_pid
sentinel_pid
sentinel_alive
sentinel_parent_pid
query_exit
query_error_sanitized
```

observer 应通过 Windows 进程查询确认 sentinel PID/parent，而不是只相信启动驱动保存的 PID。

- [ ] **Step 3: observer required-check**

在写 observer outcome 前解析 JSONL，严格要求：

```text
data_line_count>=4
ordinals_exactly_1_to_N=True
utc_monotonic=True
sentinel_seen_count>=3
query_exit_nonzero_count=0
observer_exit=0
observer_stderr_empty=True
observer_sha_start=observer_sha_end
```

空文件、BOM、空行、header 或占位对象都不算 sample。

- [ ] **Step 4: 零样本负向自检**

在 runtime 创建一个仅含 BOM/空行的临时 fixture，对它调用与正式 required-check **同一个判定函数**，必须得到：

```text
zero_sample_data_line_count=0
zero_sample_required_check_pass=False
```

随后只删除 runtime 内的 fixture；不得把 fixture 混入正式 live evidence，不得事后补写正式 sample。

---

## 6. Outcome 与分类矩阵

### Files

- Evidence: `preflight-required-files-check.txt`
- Evidence: `preflight-outcome.txt`
- Evidence: `run-summary.txt`

- [ ] **Step 1: required-check 必须先于 outcome**

`preflight-required-files-check.txt` 必须逐项记录所有必需文件的 existence、真实 data-line count、size、SHA、ordinal 连续性和判定。以下任一情况必须 FAIL：

- pipeline 或 observer live JSONL 零数据行；
- pipeline stage 少于 11；
- observer sample 少于 4；
- 任一 config 不含 `spec_version: 1`；
- bundle/artifact hash 不一致；
- business exit/exception 未记录；
- 脚本 SHA 漂移；
- 零样本负向 fixture 被错误判 PASS。

- [ ] **Step 2: 只选一个 primary**

| 条件 | primary |
|---|---|
| identity、协议、evidence、cleanup 或 required-check 不可审计 | `DIAG_INCONCLUSIVE` |
| agent pipeline 首次在明确边界丢失/改变 `spec_version`，或既有 validator/cache load 在该明确边界失败 | `DIAG_AGENT_BUNDLE_PIPELINE` |
| agent pipeline 全 PASS，但 observer 正向采样或零样本负向自检失败 | `DIAG_OBSERVER_PIPELINE` |
| agent pipeline、observer 正向与零样本负向自检全部 PASS | `DIAG_PREFLIGHT_READY_FOR_D2` |

不得输出 `DIAG_RUNNER_SPAWN`、`EARLY_EXIT`、`STALL`、`RELAY`、`TRANSIENT_R4` 或任何 Gate verdict，因为本卡没有运行这些业务层。

- [ ] **Step 3: Hermes 边界**

只有 `DIAG_AGENT_BUNDLE_PIPELINE` 且 evidence 明确指出**首个失败的产品函数/边界**时，报告才可建议 Codex 另发 Hermes 开发卡；Grok 不得自行改源码。

若离线 pipeline 全 PASS，报告必须说明下一步仍需由 Codex 决定是否先做 HTTP/session roundtrip 只读卡，或直接授权新的单次 D2 卡；不得自行运行。

---

## 7. Cleanup、final-check 与持久 evidence

### Files

- Evidence: `cleanup.txt`
- Evidence: `pid-final-status.txt`
- Evidence: `runtime-final-status.txt`
- Evidence: `tun-status-start.txt`
- Evidence: `tun-status-end.txt`
- Evidence: `required-evidence-final-check.txt`
- Evidence: `evidence-manifest.txt`
- Evidence: `leak-scan.txt`

- [ ] **Step 1: finally cleanup**

仅清理本 RUN 创建的 sentinel/observer 子进程和 `$RUNTIME_ROOT`。逐 PID 记录创建 UTC、角色和最终 dead 状态。删除 runtime 前验证：

- absolute resolved path 位于 `%TEMP%`；
- leaf 以 `omnigent-agent-observer-preflight-` 开头；
- 非 reparse point；
- 路径包含本 RUN_ID。

不得 kill 非本 RUN 进程，不得删除 `EVIDENCE_ROOT`。

- [ ] **Step 2: end identity**

HEAD、branch、七个 blob、非允许范围 git status 必须 start=end。TUN 只记录 start/end，必须写 `tun_state_changed_by_grok=False`。

- [ ] **Step 3: 冻结报告前结果**

cleanup 完成后首次写 `preflight-outcome.txt`、`run-summary.txt` 和 `GROK_DIAGNOSIS_19.md`。之后不得修改这些文件。

- [ ] **Step 4: final-check、manifest、leak-scan**

顺序必须是：

```text
preflight-required-files-check
  -> cleanup/end identity
  -> preflight-outcome + run-summary + GROK_DIAGNOSIS_19
  -> required-evidence-final-check
  -> evidence-manifest
  -> leak-scan（evidence 最后文件）
```

final-check 必须重新计算全部必需文件哈希。manifest 列出在它之前已经冻结的全部 evidence 文件及仓库报告哈希；manifest 不递归记录自身。leak-scan 扫描 manifest 在内的所有此前 evidence，至少检测 token、API key、Authorization、Bearer、Cookie、代理值和用户认证内容，要求 `hits=0`。

---

## 8. `GROK_DIAGNOSIS_19.md` 必须包含

- 唯一 primary；
- RUN_ID、evidence absolute path、是否仍存在；
- `pipeline_attempt=1_of_1`、`observer_attempt=1_of_1`；
- 明确 `controller_c_executed=False`、`server/host/runner/native_codex_started=False`；
- 七个 blob start=end；
- 六层 agent 配置对照表：source、materialized、bundle、server validation、artifact roundtrip、AgentCache；
- 每层 `spec_version/name/harness/model` 和 bundle/artifact SHA；
- 若失败，精确的 `first_failing_boundary` 和 evidence 文件指针；
- observer sample count、ordinal 范围、sentinel seen count、exit/stderr；
- 零样本负向自检必须为 FAIL；
- required-check、cleanup、manifest、leak-scan 顺序与结果；
- 是否建议另发 Hermes 卡或下一张只读/D2 卡；
- Gate 边界：Gate 1 相对 main PASS、Gate 2 r4 FAIL、本卡不是 Gate 2 PASS、不可 merge。

## 9. 唯一交付与停止条件

仓库内只允许新增：

```text
docs/fixes/handoffs/GROK_DIAGNOSIS_19.md
```

完成后保留 evidence，向 Codex 交回只读验收并立即停止。不得继续运行 HTTP/session、C/D2 或任何 Gate。
