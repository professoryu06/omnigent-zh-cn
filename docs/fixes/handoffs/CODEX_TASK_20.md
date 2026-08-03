# CODEX TASK 20 — Hermes HTTP / Session Bundle 只读回环诊断

> **For agentic workers:** 本卡仅由 Hermes 执行。它是阶段 19 之后的只读边界诊断，不是开发卡、不是 D2 卡、不是 Gate 2 卡。只允许启动一个隔离 Omnigent server，并对一个固定 bundle 做一次 multipart session create 与只读回取；禁止 host、runner、Controller C、native Codex 及任何源码修改。

## Goal

在全新、持久 evidence RUN 中，把同一个无秘密 agent bundle 从客户端上传前一直跟踪到：

```text
source config
  -> CLI materialize / bundle
  -> POST /v1/sessions multipart ingress
  -> server validate_agent_bundle
  -> session-scoped agent + LocalArtifactStore
  -> GET /v1/sessions/{id}/agent
  -> GET /v1/sessions/{id}/agent/contents
  -> retrieved config.yaml
```

判断阶段 18 的 `config.yaml missing required field: spec_version` 是否能在真实 HTTP/session 路径复现，并精确指出首个失败边界。若全链一致，只能判定 HTTP/session 预检已就绪，之后才可另发单次 D2 卡。

## Architecture

- 原生 Windows PowerShell 编排一个隔离 server、单端口和一个外部 Python HTTP 驱动。
- Python 驱动调用当前工作树的真实 CLI bundle 函数生成唯一请求 bundle，通过 `httpx.Client(trust_env=False)` 发出一次 multipart create，再执行两次只读 GET。
- 请求 bundle、artifact 文件和下载 bundle均按字节保存并计算 SHA-256；每个业务边界实时 append+flush 到 JSONL。
- server stdout/stderr 原文只放临时 runtime；持久 evidence 只保留脱敏状态、哈希、固定无秘密配置和必要响应字段。

## Global Constraints

- **执行者：** Hermes（只读诊断者，不是实现者，不是 Gate 2 签字人）。
- **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`
- **分支：** `docs/fix-plans-core-secondary`
- **唯一仓库交付：** `docs/fixes/handoffs/HERMES_DIAGNOSIS_20.md`
- **Omnigent CLI：** `F:\codex-ai\git项目部署\tmp\omnigent-review\.venv\Scripts\omnigent-zh.exe`
- **Python：** `F:\codex-ai\git项目部署\tmp\omnigent-review\.venv\Scripts\python.exe`
- **持久 evidence：** `C:\Users\Administrator\omnigent-diagnostics\$RUN_ID\`，完成后不得删除。
- **临时 runtime：** `%TEMP%\omnigent-http-session-roundtrip-$RUN_ID\`，仅在 finally cleanup 删除。
- **只允许：** server 启动 `1_of_1`、HTTP driver `1_of_1`、session multipart POST `1_of_1`、agent GET `1_of_1`、contents GET `1_of_1`。
- **绝对禁止：** `omnigent run`、host、runner、Controller C、native Codex、D0、D1、D2、完整 Gate 2、Gate 1、pytest、ruff。
- **绝对禁止修改：** `omnigent/`、`tests/`、政策、`STATUS.md`、旧 handoff、TUN、代理、认证、用户 Codex 配置。
- **禁止：** commit、push、merge、tag、PR/Issue 修改。
- 不得复制或拼接阶段 14–19/r4 evidence 作为本 RUN 业务结果。
- Gate 1=`PASS（相对 main）`，非全仓 GREEN；Gate 2 r4=`FAIL`；不可 merge。

---

## 1. 必读与阶段边界

### Read

- `docs/fixes/handoffs/CODEX_TASK_19.md`
- `docs/fixes/handoffs/GROK_DIAGNOSIS_19.md`
- `docs/fixes/handoffs/CODEX_REVIEW_19.md`
- `omnigent/chat.py`
- `omnigent/cli.py`
- `omnigent/server/schemas.py`
- `omnigent/server/bundles.py`
- `omnigent/server/routes/sessions.py`
- `omnigent/stores/artifact_store/local.py`
- `omnigent/runtime/agent_cache.py`
- `tests/server/helpers.py`

允许沿用的背景事实只有：

```text
stage19_review=RECLASSIFY_DIAG_PREFLIGHT_READY_FOR_D2
offline_source_to_agent_cache_spec_version=1
offline_bundle_sha_equals_artifact_roundtrip_sha=True
stage18_business_audit=DIAG_INCONCLUSIVE
stage18_error=config.yaml missing required field: spec_version
```

阶段 19 的 bundle、PID、runtime、sample、exit 和哈希不得充当本 RUN 结果。

本卡 PASS 也不自动授权 D2；Hermes 完成报告后必须停止，交回 Codex 只读验收。

---

## 2. 全新 RUN、路径、端口

### Evidence

- `RUN_ID.txt`
- `identity-start.txt`
- `identity-end.txt`
- `git-status-start.txt`
- `git-status-end.txt`
- `candidate-source-blobs-start.txt`
- `candidate-source-blobs-end.txt`
- `precheck.txt`
- `port-start.txt`
- `port-end.txt`

一次性生成并冻结：

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$OMNIGENT_CLI = Join-Path $WORKTREE '.venv\Scripts\omnigent-zh.exe'
$PYTHON = Join-Path $WORKTREE '.venv\Scripts\python.exe'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-dc83140-hermes-http-session-roundtrip-r1'
$EVIDENCE_ROOT = "C:\Users\Administrator\omnigent-diagnostics\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-http-session-roundtrip-$RUN_ID"
$DATA_ROOT = Join-Path $RUNTIME_ROOT 'data'
$AGENT_SOURCE = Join-Path $RUNTIME_ROOT 'agent-source'
$DRIVER = Join-Path $RUNTIME_ROOT 'http-session-roundtrip.py'
```

要求：

1. `EVIDENCE_ROOT`、`RUNTIME_ROOT` 开始时均不存在；若已存在，停止为 `DIAG_INCONCLUSIVE`，不得删除后复用。
2. 只分配一个动态 loopback 端口。正式启动前若端口被占用，停止，不得换端口续跑。
3. `runtime`、端口、RUN_ID 不得与旧 RUN 共用。
4. 仓库只允许新增 `HERMES_DIAGNOSIS_20.md`。

预检必须排除本诊断 self/ancestor 后搜索旧诊断、同 RUN、拟用端口、Omnigent server/host/runner/C 与 native Codex 残留。要求：

```text
count=0
pass=True
```

非零只记录，不 kill，进入 cleanup 并判 `DIAG_INCONCLUSIVE`。

---

## 3. Identity 与九个相关 blob

start/end 必须记录 HEAD、branch、worktree、RUN_ID、端口、执行者和次数限制。

下列工作树 blob 必须 start=end 且等于期望值：

| 文件 | 期望 `git hash-object` |
|---|---|
| `omnigent/chat.py` | `6c65a6b9101f6e9c29a243fa73f98519e9bc9443` |
| `omnigent/cli.py` | `1a0e4ea9fae5def40d136c83fabb068aac0d93d9` |
| `omnigent/server/schemas.py` | `ea6ebbfb8ae85108c08f4b3ac3166a6623c3b043` |
| `omnigent/server/routes/sessions.py` | `0375e5f951d82c01c9f67e8cf7b41a90aff10330` |
| `omnigent/server/bundles.py` | `40451999b8b71e6fd010a4bdea91f81efdf3f93a` |
| `omnigent/stores/artifact_store/local.py` | `fc52f20a0b83626cdbfe4bbf36572f1978f3dd23` |
| `omnigent/runtime/agent_cache.py` | `774989fc6b2435850c7c95d256714884bbd3b878` |
| `omnigent/server/app.py` | `f31cb4661f5acf3b580508346c3a31155afdfbf6` |
| `tests/server/helpers.py` | `955636ad7a0d20a3e097052c878ba26f2aa1b885` |

对每项同时记录：

```text
worktree_blob=<hash>
head_blob=<hash or absent>
expected_worktree_blob=<hash>
worktree_match=True
```

本工作树已有用户改动，因此只要求本卡相关内容 `start=end`，不得把 dirty tree 误报为本 RUN 修改，也不得清理或覆盖既有改动。

---

## 4. TUN、环境与产品进程限制

### Evidence

- `tun-status-start.txt`
- `tun-status-end.txt`
- `environment-presence.txt`
- `child-environment-contract.txt`
- `forbidden-process-check-start.txt`
- `forbidden-process-check-end.txt`

TUN 只观察 Meta start/end；不得开关、重启、重配或调用控制 API。记录：

```text
meta_up_at_start=True|False
meta_up_at_end=True|False
tun_state_changed_by_hermes=False
```

共同子进程环境必须在 server 和 driver 启动前构造：

```text
OMNIGENT_DATA_DIR=<本 RUN DATA_ROOT>
NO_PROXY=127.0.0.1,localhost
no_proxy=127.0.0.1,localhost
PYTHONUTF8=1
PYTHONIOENCODING=utf-8
```

只记录代理变量是否存在，禁止记录代理值、token、Cookie、Authorization 或 Codex 认证内容。Python HTTP 客户端必须额外使用：

```python
httpx.Client(base_url=server_url, trust_env=False, timeout=30.0)
```

本卡不需要 `HARNESS_CODEX_PATH`，且必须证明：

```text
host_started=False
runner_started=False
controller_c_executed=False
native_codex_started=False
d0_d1_d2_gate2_executed=False
```

若 server 意外触发任何上述禁止进程，立即停止业务、进入 cleanup，并判 `REJECT_PROTOCOL`。

---

## 5. 固定 agent、驱动预检与冻结

### Runtime

- `$AGENT_SOURCE\config.yaml`
- `$DRIVER`

### Evidence

- `agent-source-config.yaml`
- `driver-source.py`
- `driver-identity.txt`
- `driver-pycompile-check.txt`
- `business-start-marker.txt`

固定无秘密 source 必须精确为：

```yaml
spec_version: 1
name: controller-http-session-cli0146
description: Stage 20 HTTP session bundle roundtrip
executor:
  type: omnigent
  config:
    harness: codex
    model: gpt-5.6-sol
prompt: Reply with CONTROLLER_OK and stop.
```

该内容无秘密，可原样持久保存。

Python 驱动必须在任何产品进程启动前：

1. 保存完整源文件副本到 evidence；
2. 用工作树 Python 执行 `-m py_compile`；
3. 记录 absolute path、size、SHA-256、Python version、compile exit；
4. 验证 exit 捕获机制：`WaitForExit()` 后 `.ExitCode` 必须是明确整数；
5. 创建 `business-start-marker.txt` 后冻结脚本 SHA，禁止再编辑或重试。

语法错误只允许在 marker 创建前修复。marker 后任何脚本漂移均为 `DIAG_INCONCLUSIVE`。

---

## 6. 隔离 server：仅启动一次

### Evidence

- `server-command-sanitized.txt`
- `server-lifecycle-live.jsonl`
- `server-ready.txt`
- `server-process-result.txt`
- `artifact-tree-at-ready.txt`

使用共同环境启动一次：

```text
omnigent-zh.exe server --host 127.0.0.1 --port <SERVER_PORT> --no-open
```

要求：

- server PID、PPID、create UTC 和 executable 可映射；
- server 原始 stdout/stderr 只写 runtime；
- evidence 每约 1 秒 append+flush UTC、ordinal、PID/alive、port LISTEN、health status、stdout/stderr 累计 bytes；
- READY = process alive + port LISTEN + `/health` 200；
- READY 后再连续观察 10 秒，每秒 `/health` 200；
- health 请求显式 no-proxy；
- `DATA_ROOT` 位于本 RUN runtime，数据库与 artifacts 不得落到用户全局目录；
- READY 后、业务 POST 前冻结 `artifact-tree-at-ready.txt`，列出相对路径、size、SHA，不记录内容。

server 启动/READY 失败时不得重启、换端口或同 RUN 续跑；判 `DIAG_INCONCLUSIVE`。

server 是本卡唯一允许的 Omnigent 产品进程。

---

## 7. 单次 HTTP/session roundtrip

### Evidence

- `request-materialized-config.yaml`
- `request-bundle.tar.gz`
- `request-bundle-members.txt`
- `request-bundle-config.yaml`
- `request-bundle-meta.txt`
- `http-session-boundaries-live.jsonl`
- `http-driver-process-result.txt`
- `session-create-response-sanitized.json`
- `session-agent-response-sanitized.json`
- `artifact-tree-after-create.txt`
- `stored-artifact-match.txt`
- `retrieved-bundle.tar.gz`
- `retrieved-bundle-members.txt`
- `retrieved-bundle-config.yaml`
- `retrieved-bundle-meta.txt`
- `http-error-sanitized.txt`

### 7.1 构造唯一请求 bundle

HTTP 驱动只调用当前工作树既有函数：

1. `omnigent.chat._canonicalize_local_agent_path(source_dir)`
2. `omnigent.chat._materialize_override_bundle(canonical, ChatOverrides())`
3. `omnigent.chat._validate_agent_spec(materialized)`
4. `omnigent.chat._bundle_agent(materialized)`
5. 从 tar.gz 读取根 `config.yaml`
6. `omnigent.server.bundles.validate_agent_bundle(bundle_bytes, enforce_handler_allowlist=False)`

`_cleanup_materialized_override_bundle(materialized)` 放在 `finally`，不得覆盖业务异常。

上传前必须满足：

```text
spec_version=1
name=controller-http-session-cli0146
harness=codex
model=gpt-5.6-sol
root_config_yaml_count=1
request_bundle_size>0
request_bundle_sha256=<nonempty>
```

否则不发 HTTP，判 `DIAG_INCONCLUSIVE`。

### 7.2 只发一次 multipart create

固定请求：

```text
POST /v1/sessions
metadata={}
bundle filename=agent.tar.gz
bundle content-type=application/gzip
Origin header absent
```

Python 等价形状：

```python
client.post(
    "/v1/sessions",
    data={"metadata": json.dumps({})},
    files={"bundle": ("agent.tar.gz", request_bundle, "application/gzip")},
)
```

只允许一次 POST，禁止重试。记录 HTTP status、elapsed、response bytes/SHA、脱敏错误和返回字段名。成功必须是 201，且 response 含非空 `session_id`、`agent_id`、`agent_name`；持久 evidence 对两个 id 只保存 SHA-256，不保存原值。

### 7.3 核对真实 artifact

POST 返回后立即再次枚举 `$DATA_ROOT\artifacts`：

- 记录相对路径、size、SHA；
- 与 READY 时快照做集合差；
- 找出 SHA/size 与 `request-bundle.tar.gz` 完全相等的新 artifact；
- 要求匹配数恰好为 1；
- 只读复制匹配 artifact 到 evidence 后再次核对 hash，不得修改 artifact。

若 POST=201 但找不到唯一匹配 artifact，归入 session/artifact 边界失败，不得以 GET 成功掩盖。

### 7.4 两次只读 GET

只允许：

```text
GET /v1/sessions/{session_id}/agent
GET /v1/sessions/{session_id}/agent/contents
```

`agent` GET 必须 200，并核对：

```text
name=controller-http-session-cli0146
harness=codex
model=gpt-5.6-sol
```

若响应结构不直接暴露某字段，明确记为 `NA_not_exposed`，不得猜测。

`contents` GET 必须 200、`Content-Type` 为 gzip、`X-Agent-Name` 正确、`X-Agent-Session-Scoped=true`。下载字节保存为 `retrieved-bundle.tar.gz`，并要求：

```text
retrieved_sha256=request_sha256
retrieved_size=request_size
retrieved_root_config_yaml_count=1
retrieved_spec_version=1
retrieved_name=controller-http-session-cli0146
retrieved_harness=codex
retrieved_model=gpt-5.6-sol
```

禁止 POST message/event，禁止启动 runner，禁止 DELETE session；server 停止和 runtime 删除即完成隔离 cleanup。

### 7.5 Live evidence

`http-session-boundaries-live.jsonl` 必须在边界发生时直接 append+flush，不得事后重建。每行至少包含：

```text
ordinal
utc
stage
http_method
path_template
status
size
sha256
spec_version
name
harness
model
pass
error_sanitized
```

至少覆盖以下顺序，ordinal 必须精确连续、UTC 单调：

1. `source_config`
2. `materialized_config`
3. `request_bundle`
4. `request_bundle_validation`
5. `session_create_response`
6. `stored_artifact_match`
7. `session_agent_response`
8. `session_contents_response`
9. `retrieved_bundle`
10. `retrieved_config`
11. `end_to_end_hash_compare`

失败后可记录失败边界与 cleanup，但不得修脚本、补 live 行或重试业务请求。

---

## 8. Exit、required-check 与分类矩阵

### Evidence

- `http-required-files-check.txt`
- `http-session-outcome.txt`
- `run-summary.txt`

HTTP driver 必须用可靠的进程等待方式捕获明确整数 exit。以下字段不得为空：

```text
driver_attempt=1_of_1
driver_pid=<int>
driver_exit=<int>
driver_timed_out=True|False
driver_started_utc=<utc>
driver_ended_utc=<utc>
```

外层预算为 120 秒。若超时，只终止本 RUN driver；不得重试。server 的 finally 终止属于 cleanup，必须单独记录，不得冒充业务 exit。

`http-required-files-check.txt` 必须在 `http-session-outcome.txt` 之前创建，并逐项重读实际文件，核对：

- 所有必需 evidence 非空；
- driver source SHA 与 marker/final 相同；
- driver exit 明确；
- live JSONL 有效数据行不少于 11、ordinal 连续、UTC 单调；
- POST/GET 各恰好一次；
- request/stored/retrieved bundle hash 与 size；
- 三份 root config 的固定字段；
- artifact READY/POST 后快照可审计；
- server READY+10s；
- 无 host/runner/C/native/D0/D1/D2/Gate；
- 无事后重建 live evidence。

只选一个 primary：

| 条件 | primary |
|---|---|
| 违反硬约束、重试、改源码、启动禁止进程、事后重建 live evidence | `REJECT_PROTOCOL` |
| identity、exit、时间线、required-check、cleanup、hash 或证据不可审计 | `DIAG_INCONCLUSIVE` |
| 上传前 bundle 合格，但 multipart POST 首次在解析/校验前后失败，未创建 session-scoped agent | `DIAG_HTTP_MULTIPART_INGRESS` |
| POST=201，但 session-agent 绑定、artifact 唯一匹配或 contents 回取首次失败/错配 | `DIAG_SESSION_ARTIFACT_ROUNDTRIP` |
| POST/agent/contents 均成功，但回取 bundle/config 首次丢失或改变固定字段 | `DIAG_SESSION_BUNDLE_MUTATION` |
| 所有 HTTP/session/artifact/hash/config 断言均通过 | `DIAG_HTTP_SESSION_READY_FOR_D2` |

失败分类必须写：

```text
first_failing_boundary=<exact live stage>
first_failing_product_function=<function or unknown>
request_bundle_was_valid=True|False
session_created=True|False
artifact_exact_match=True|False
retrieved_exact_match=True|False
```

不得输出 runner spawn、early exit、stall、relay、Gate verdict，因为本卡没有执行这些层。

---

## 9. Cleanup、冻结与 leak-scan

### Evidence

- `cleanup.txt`
- `pid-final-status.txt`
- `runtime-final-status.txt`
- `required-evidence-final-check.txt`
- `evidence-manifest.txt`
- `leak-scan.txt`

`finally` 只清理本 RUN 创建的 driver/server 子进程、唯一端口和 runtime。逐 PID 记录 PID、PPID、create UTC、role、cleanup action、final dead。

删除 runtime 前必须验证：

```text
resolved_absolute_path_under_TEMP=True
leaf_starts_with_omnigent-http-session-roundtrip=True
leaf_contains_RUN_ID=True
reparse_point=False
```

不得 kill 非本 RUN 进程，不得删除 evidence。cleanup 后要求：

```text
all_run_pids_dead=True
server_port_free=True
runtime_exists=False
evidence_exists=True
leftover_count=0
```

顺序必须为：

```text
http-required-files-check
  -> finally cleanup / end identity / TUN end
  -> http-session-outcome + run-summary + HERMES_DIAGNOSIS_20.md
  -> required-evidence-final-check
  -> evidence-manifest
  -> leak-scan（evidence 最后文件）
```

报告、outcome、summary 写入后冻结；final-check 记录其 size/SHA，之后不得修改。

manifest 覆盖在它之前的全部 evidence 与仓库报告哈希，不递归记录自身。leak-scan 扫描此前所有 evidence 和报告，至少检测 token、API key、Authorization、Bearer、Cookie、代理值与用户认证内容，要求：

```text
scanned_count=expected_count
hits=0
leak_scan_is_last=True
```

---

## 10. `HERMES_DIAGNOSIS_20.md` 必须包含

- 唯一 primary；
- RUN_ID、evidence 绝对路径、是否仍存在；
- server/driver/POST/GET 均 `1_of_1`；
- HEAD、branch、九 blob start=end；
- TUN 只观察、环境只记录存在性；
- 明确 host/runner/C/native/D0/D1/D2/Gate2 均未执行；
- source/materialized/request/stored/retrieved 五层对照表；
- 每层 size、SHA、`spec_version/name/harness/model`；
- multipart status、agent status、contents status 与必要响应头；
- live ordinal/data line 数与 driver exit；
- 若失败，首个失败 stage、可映射产品函数与 evidence 文件；
- required-check、cleanup、manifest、leak-scan 结果；
- 下一步只能二选一：
  - `DIAG_HTTP_SESSION_READY_FOR_D2`：建议 Codex 另发单次 D2 卡；
  - 明确产品边界失败：建议 Codex 另发 **Grok 窄修复卡**，本卡不写补丁。
- Gate 边界：本卡不是 D2 PASS、不是 Gate 2 PASS、不可 merge。

## 11. 完成标准

- [ ] 全新 RUN/evidence/runtime/端口，未拼接旧 RUN。
- [ ] server、driver、POST、agent GET、contents GET 各仅一次。
- [ ] 请求前 bundle 已验证含 `spec_version: 1`。
- [ ] READY+10s 后才 POST。
- [ ] artifact READY/POST 快照可审计，唯一 hash 匹配。
- [ ] request/stored/retrieved 字节与配置逐层可对照。
- [ ] live JSONL 实时落盘、ordinal 连续、非事后重建。
- [ ] driver exit 是明确整数，business 与 cleanup exit 分离。
- [ ] 未启动 host/runner/C/native Codex，未执行 D0/D1/D2/Gate。
- [ ] required-check 早于 outcome。
- [ ] 本 RUN PID dead、端口 free、runtime 删除、evidence 保留。
- [ ] report/outcome/summary 在 final-check 前冻结。
- [ ] leak-scan 最后且 hits=0。
- [ ] 仓库仅新增 `HERMES_DIAGNOSIS_20.md`。
- [ ] 未修改源码/tests/政策/STATUS/TUN/认证/配置；未 commit/push/merge/tag。
- [ ] 未冒充 Gate 2 PASS 或 mergeable。

完成后立即停止并交回 Codex 只读验收。
