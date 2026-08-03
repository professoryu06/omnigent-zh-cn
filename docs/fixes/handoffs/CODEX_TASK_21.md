# CODEX TASK 21 — Hermes 单次 Controller C / D2 可审计诊断

> **For agentic workers:** 本卡仅由 Hermes 执行。它是阶段 20 验收后的单次 D2 诊断卡，不是开发卡、不是完整 Gate 2 卡。只允许一次 Omnigent Controller C；任何前置、observer 或 evidence 条件不满足时必须在 C 前停止，禁止通过重试修复同一 RUN。

## Goal

在固定 native Codex CLI `0.146.0`、固定 agent、单一隔离 server/host 和未改动的产品 `240s` idle watchdog 下，只执行一次 Controller C，确定真实产品链路首次落在哪个结果：

```text
agent/session 正常
  -> runner 未 spawn
  -> runner spawn 但 native 未 spawn
  -> native 早退
  -> native 存活但无事件并命中 240s idle
  -> runner/App Server 有事件但 relay 丢失
  -> 单次真实 assistant sentinel 成功
```

同时关闭阶段 18 的四个审计缺口：

- agent 必须是阶段 20 已验证的 `spec_version: 1` 目录形态；
- observer 必须先通过正向 sentinel 与零样本负向预检；
- C 业务 exit/timeout 必须是明确值，禁止约 4 秒误标 300 秒 timeout；
- live sample 必须逐秒实时落盘，零样本/聚合占位必然 FAIL。

## Architecture

- 原生 Windows PowerShell 编排一个全新隔离 server、一个 foreground host 和一次 `omnigent run`。
- 一个业务前通过 `node --check` 和 sentinel 预检的 Node observer，以约 1 秒粒度实时 append+flush 进程树、server/host/C 状态、runner/native identity 和可观察事件。
- `HARNESS_CODEX_PATH` 在 server、host、C 前固定为同一 vendor native。
- agent source、预计算 bundle、session `/agent/contents`、runner/cache 可观察边界都保存脱敏 config/hash，以区分“session 字节正确”和“runner 实际加载错误”。
- 原始 prompt、stdout/stderr 正文只放 runtime；持久 evidence 只放脱敏事件、hash、identity 和结果。

## Global Constraints

- **执行者：** Hermes（只读诊断者，不是实现者，不是 Gate 2 签字人）。
- **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`
- **分支：** `docs/fix-plans-core-secondary`
- **唯一仓库交付：** `docs/fixes/handoffs/HERMES_DIAGNOSIS_21.md`
- **Omnigent CLI：** `F:\codex-ai\git项目部署\tmp\omnigent-review\.venv\Scripts\omnigent-zh.exe`
- **模型：** `gpt-5.6-sol`
- **固定 native：** `C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`
- **native version：** `codex-cli 0.146.0`
- **native size：** `358650672`
- **native SHA-256：** `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb`
- **产品 idle watchdog：** `240s`，禁止调高、关闭、绕过或 monkey-patch。
- **外层预算：** `300s`，从 C 真实 spawn 后开始；禁止提前约 4 秒误判 timeout。
- **次数：** server `1_of_1`、host `1_of_1`、Controller C `1_of_1`；禁止换 RUN/端口/模型重试本任务。
- **TUN：** 只观察；本卡为保持阶段 17 D0/D1 基线，业务前必须已经 `Meta=Up`。Hermes 不得开关；若不是 Up，在 C 前停止。
- **平台：** 原生 Windows；禁止 WSL、tmux、容器或远程 Linux。
- **禁止执行：** D0、D1、其余 Gate 2 五轮、完整 Gate 2、Gate 1、pytest、Ruff。
- **禁止修改：** `omnigent/`、`tests/`、政策、`STATUS.md`、旧 handoff、TUN、代理、认证、用户 Codex 配置。
- **禁止：** commit、push、merge、tag、PR/Issue 修改。
- **Evidence：** `C:\Users\Administrator\omnigent-diagnostics\$RUN_ID\`，必须持久保留。
- Gate 1=`PASS（相对 main）`、非全仓 GREEN；Gate 2 r4=`FAIL`；不可 merge。

---

## 1. 必读与授权边界

### Read

- `docs/fixes/handoffs/CODEX_TASK_18.md`
- `docs/fixes/handoffs/GROK_DIAGNOSIS_18.md`
- `docs/fixes/handoffs/CODEX_REVIEW_18.md`
- `docs/fixes/handoffs/CODEX_TASK_19.md`
- `docs/fixes/handoffs/CODEX_REVIEW_19.md`
- `docs/fixes/handoffs/CODEX_TASK_20.md`
- `docs/fixes/handoffs/HERMES_DIAGNOSIS_20.md`
- `docs/fixes/handoffs/CODEX_REVIEW_20.md`
- `omnigent/chat.py`
- `omnigent/host/connect.py`
- `omnigent/runner/_entry.py`
- `omnigent/runner/app.py`
- `omnigent/inner/loader.py`
- `omnigent/inner/codex_native_executor.py`
- `omnigent/codex_native_app_server.py`
- `omnigent/native_server_harness.py`

允许沿用的背景事实：

```text
stage17_rework=D0_PASS_and_D1_PASS_on_cli_0.146.0
stage18=REJECT_PROTOCOL_and_business_inconclusive
stage19=offline_agent_observer_preflight_ready
stage20=ACCEPT_WITH_NOTES_DIAG_HTTP_SESSION_READY_FOR_D2
```

不得沿用旧 RUN 的 PID、端口、thread、turn、exit、sample、sentinel 或文件作为本 RUN 结果。

本卡是新的唯一一次 C 授权。完成一次 C 后，无论成功、失败或 evidence 不完整，必须停止，不得再生成新 RUN 补测。

---

## 2. 用户前置与一次性 precheck

Hermes 开始创建 RUN 前，用户应已：

- 关闭独立运行的 Codex CLI/旧诊断窗口；
- 开启 Meta TUN；
- 不操作 Omnigent/TUN/代理直到本 RUN cleanup。

Hermes 只观察，不替用户关闭或开启任何项。

生成 RUN 后，precheck 只执行一次。排除诊断 orchestrator 的 self/ancestor 后，检查：

- 旧诊断 server/host/runner/C；
- 固定 native path 对应的活跃进程；
- 本 RUN runtime/evidence/端口；
- `.codex-tmp` 直接子项；
- 旧 Task 18/21 相关进程和 pidfile。

必须：

```text
forbidden_count=0
runtime_exists=False
evidence_exists=False
port_free=True
codex_tmp_child_count=0
precheck_pass=True
```

任一不满足：

```text
PRECHECK_STOP
controller_c_executed=False
primary=DIAG_INCONCLUSIVE
```

立即写最小 evidence、cleanup、报告并停止。**不得让用户在同 RUN 关闭进程后重新 precheck 并继续。**

---

## 3. 全新 RUN、路径和端口

一次性冻结：

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$OMNIGENT_CLI = Join-Path $WORKTREE '.venv\Scripts\omnigent-zh.exe'
$PYTHON = Join-Path $WORKTREE '.venv\Scripts\python.exe'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-dc83140-hermes-d2-c-cli0146-r1'
$EVIDENCE_ROOT = "C:\Users\Administrator\omnigent-diagnostics\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-d2-c-cli0146-$RUN_ID"
$DATA_ROOT = Join-Path $RUNTIME_ROOT 'data'
$AGENT_DIR = Join-Path $RUNTIME_ROOT 'agents\controller'
$WORKSPACE_C = Join-Path $RUNTIME_ROOT 'workspaces\controller'
$OBSERVER_PATH = Join-Path $RUNTIME_ROOT 'd2-observer.mjs'
$NATIVE_CODEX_EXE = 'C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe'
$CODEX_MODEL = 'gpt-5.6-sol'
$SHORT_USER_MESSAGE = 'Reply with CONTROLLER_OK and stop.'
```

分配一个动态 loopback 端口并冻结。若 server 启动前端口被占用，停止；不得换端口续跑。

### Evidence

- `RUN_ID.txt`
- `identity-start.txt`
- `identity-end.txt`
- `git-status-start.txt`
- `git-status-end.txt`
- `candidate-source-blobs-start.txt`
- `candidate-source-blobs-end.txt`
- `precheck.txt`
- `codex-tmp-start.txt`
- `codex-tmp-end.txt`
- `port-start.txt`
- `port-end.txt`

---

## 4. 冻结十二个产品 blob

下列工作树 blob 必须 start=end 且等于期望值：

| 文件 | 期望 `git hash-object` |
|---|---|
| `omnigent/chat.py` | `6c65a6b9101f6e9c29a243fa73f98519e9bc9443` |
| `omnigent/cli.py` | `1a0e4ea9fae5def40d136c83fabb068aac0d93d9` |
| `omnigent/host/connect.py` | `8623a24d520875c5df3a70bdc04e10b807ad5915` |
| `omnigent/runner/app.py` | `969fdeab8c2a7f2975631ac6b04e2a3ef53d9fc0` |
| `omnigent/runner/_entry.py` | `74c66a56dc9e4e06ff1dafb837e7e6a8f60542cf` |
| `omnigent/inner/loader.py` | `c9d357376057038e3fc0b4af8d4003ea7126ec61` |
| `omnigent/inner/codex_native_executor.py` | `867e5cec5bfcc38c3792a262bc32ed26a1649f46` |
| `omnigent/codex_native_app_server.py` | `3baba076d52bc4c86e69921be3f59a24384816b2` |
| `omnigent/native_server_harness.py` | `e88f04c8ca141131037da86b961b0cde1a0621dd` |
| `omnigent/runner/transports/ws_tunnel/serve.py` | `325a3758a5dc6b1aa47be38ec7f436716d9bf5e5` |
| `omnigent/server/routes/sessions.py` | `0375e5f951d82c01c9f67e8cf7b41a90aff10330` |
| `omnigent/server/routes/_workspace_validation.py` | `5bf5e587b9177a9ecbce572b11656edac31ea7fe` |

记录 worktree blob、HEAD blob、expected blob、match。任一工作树 blob 不匹配时，在 C 前停止为 `DIAG_INCONCLUSIVE`。

不得清理或覆盖工作树已有用户改动。

---

## 5. Native、TUN 与共同环境

### Evidence

- `native-discovery.txt`
- `native-identity-start.txt`
- `native-identity-end.txt`
- `tun-status-start.txt`
- `tun-status-end.txt`
- `environment-presence.txt`
- `child-environment-contract.txt`
- `product-watchdog-contract.txt`

native start/end 必须满足：

```text
path=<固定绝对路径>
version=codex-cli 0.146.0
size=358650672
sha256=bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb
shim=False
```

TUN 只观察：

```text
meta_up_at_start=True
meta_up_at_end=True
tun_state_changed_by_hermes=False
```

若 start 不是 Up，在 C 前停止，不得由 Hermes 开启。

所有产品进程启动前构造共同环境：

```text
OMNIGENT_DATA_DIR=<DATA_ROOT>
NO_PROXY=127.0.0.1,localhost
no_proxy=127.0.0.1,localhost
PYTHONUTF8=1
PYTHONIOENCODING=utf-8
HARNESS_CODEX_PATH=<固定 native path>
```

必须分别证明：

```text
HARNESS_CODEX_PATH_set_before_server=True
HARNESS_CODEX_PATH_set_before_host=True
HARNESS_CODEX_PATH_set_before_C=True
```

只记录代理变量存在性和固定 loopback NO_PROXY，不记录代理凭据、token、Cookie 或完整用户环境。

产品 watchdog 必须从当前产品配置只读核对为 240 秒；禁止注入覆盖值。

---

## 6. 固定 agent 与上传前证据

创建 `$AGENT_DIR\config.yaml`，内容精确为：

```yaml
spec_version: 1
name: controller-d2-cli0146-stage21
description: Stage 21 single Controller D2
executor:
  type: omnigent
  config:
    harness: codex
    model: gpt-5.6-sol
prompt: Reply with CONTROLLER_OK and stop.
```

`WORKSPACE_C` 必须为本 RUN 内 Windows drive-absolute 路径。

在产品启动前，使用与阶段 20 相同的当前工作树函数只做一次离线只读预计算：

```text
canonicalize -> materialize -> validate -> bundle -> root config parse
```

保存：

- `agent-source-config.yaml`
- `agent-precomputed-bundle.tar.gz`
- `agent-precomputed-config.yaml`
- `agent-precomputed-meta.txt`
- `agent-workspace-contract.txt`

必须：

```text
spec_version=1
name=controller-d2-cli0146-stage21
harness=codex
model=gpt-5.6-sol
root_config_count=1
```

此预计算只证明输入，不得把预计算 bundle 冒充 C 实际上传/runner 实际下载。

---

## 7. Observer 源码、正向预检和零样本负向

### Evidence

- `observer-source.mjs`
- `observer-identity.txt`
- `observer-node-check.txt`
- `observer-sentinel-live.jsonl`
- `observer-sentinel-result.txt`
- `observer-zero-sample-negative-check.txt`
- `observer-business-marker.txt`

observer 只能：

- 每约 1 秒查询本 RUN PID/children、路径、创建 UTC、alive/exit、CPU/IO；
- 查询本 RUN server health、host status、session/runner 可观察状态；
- 读取本 RUN stdout/stderr 累计 bytes 和脱敏事件类别；
- 实时 append+flush+fsync evidence；
- 不修改产品、数据库业务字段、TUN、代理或认证。

业务前必须：

1. `node --check` exit=0；
2. 冻结 path/size/SHA；
3. 对诊断自有 sentinel 做一次至少 3 秒正向观察：
   - 有效 sample `>=3`
   - ordinal 精确 `1..N`
   - UTC 单调
   - sentinel seen `>=2`
   - observer exit 为整数 0
4. 用同一 required-check 函数对 BOM/空行 fixture 验证：
   - data line count=0
   - required-check=False

任一失败，禁止启动 server/host/C，判 `DIAG_INCONCLUSIVE`。

正/负向预检通过后创建 `observer-business-marker.txt` 并冻结 SHA。此后不得编辑 observer。

---

## 8. Server READY 与逐秒证据

### Evidence

- `server-command-sanitized.txt`
- `server-lifecycle-live.jsonl`
- `server-ready.txt`
- `server-process-result.txt`

启动一次：

```text
omnigent-zh.exe server --host 127.0.0.1 --port <SERVER_PORT> --no-open
```

READY 必须为 process alive + port LISTEN + `/health` 200。

READY 后必须有至少 10 条、约每秒一条的真实 live JSON：

```text
ordinal
utc
monotonic_elapsed_ms
server_pid
alive
port_listen
health_status
stdout_bytes
stderr_bytes
```

要求：

```text
ready_health_sample_count>=10
ordinals_continuous=True
utc_monotonic=True
all_health_200=True
```

禁止用单条 `health_ok_10s=10` 聚合占位替代。

失败时不得重启 server或换端口；禁止进入 host/C。

---

## 9. Foreground host online 与逐秒证据

### Evidence

- `host-command-sanitized.txt`
- `host-lifecycle-live.jsonl`
- `host-online.txt`
- `host-process-result.txt`

使用共同环境启动一次 foreground host：

```text
omnigent-zh.exe host --server <SERVER_URL> --non-interactive
```

最多等待 30 秒，以约 1 秒粒度记录：

```text
host_pid/alive
host_process_state
host_status_api
server_health
```

只有以下均成立才允许 C：

```text
host_process_alive=True
process=online
host_status=online
host_live_sample_count>=2
```

失败时不得重启 host；禁止进入 C。

---

## 10. 单次 Controller C

### Evidence

- `d2-samples-live-sanitized.jsonl`
- `d2-events-live-sanitized.jsonl`
- `d2-c-timeline.txt`
- `d2-process-tree.txt`
- `d2-business-result.txt`
- `d2-spawn-window.txt`
- `d2-agent-session-boundaries.txt`
- `d2-event-relay.txt`
- `d2-error-sanitized.txt`
- `d2-stream-hashes.txt`
- `c-process-result.txt`

observer 必须从 C 启动前至少 1 秒开始采样。

使用共同环境、cwd=`WORKSPACE_C`，只执行一次：

```text
omnigent-zh.exe run <AGENT_DIR> -p "Reply with CONTROLLER_OK and stop." --server <SERVER_URL>
```

固定：

```text
attempt=1_of_1
OMNIGENT_STRICT_PROMPT=unset
outer_budget_s=300
product_idle_watchdog_s=240_UNCHANGED
```

### 10.1 C exit

必须使用可靠等待：

- 真实 spawn 后记录 PID/create UTC；
- 进程自然退出时 `WaitForExit()` 后读取整数 ExitCode；
- 仅当单调计时达到 300 秒且 C 仍 alive 才标 `outer_budget_timeout=True`；
- 约 4 秒不得标 300 秒 timeout；
- cleanup kill 的 exit 单独记录。

### 10.2 逐秒 sample

每条至少记录：

```text
ordinal
utc
monotonic_elapsed_ms
server_pid/alive/health
host_pid/alive/status
c_pid/alive/exit_if_known
session_id_hash/status
runner_pid/ppid/create_utc/alive/exit_if_known
native_pid/ppid/create_utc/alive/exit_if_known
native_path/size/sha_if_observed
runner_event_count
app_server_event_count
relay_event_count
cli_event_count
stdout_bytes
stderr_bytes
```

不可观察字段必须写 `NOT_OBSERVABLE`，不得伪造为 False/0。

要求：

```text
sample_count>=3
ordinal_exact_1_to_N=True
utc_monotonic=True
c_window_covered=True
observer_exit_is_integer=True
observer_sha_unchanged=True
```

若 C 持续到 240 秒 idle，samples 必须覆盖整个窗口，不能只记录开头或结尾。

### 10.3 事件

事件 JSONL 每个可观察事件实时 append：

```text
ordinal
utc
source
category
method_or_type
session_hash
thread_hash
turn_hash
is_user_message
is_assistant_or_final
sentinel_match
terminal_kind
error_code
http_ws_status
raw_line_size
raw_line_sha256
```

userMessage 或输入回显不得计为 assistant sentinel。

### 10.4 Agent/session/runner 边界

session id 一旦可得，只读保存：

- server `/v1/sessions/{id}/agent/contents` bundle size/SHA 和 root config 固定字段；
- C 实际 session agent name/harness；
- runner 下载/AgentCache/workdir config 的可观察 hash/字段；不可观察写 `NOT_OBSERVABLE`；
- 若再次出现 missing `spec_version`，必须同时指出：
  - session contents 是否仍含 1；
  - runner 实际加载 config 是否可读；
  - 首个报错 UTC 在 runner/native spawn 前或后。

不得把阶段 20 bundle 复制为本 RUN 实际 session contents。

### 10.5 真实 success

只有以下全部成立才算单次业务 PASS：

```text
c_exit=0
outer_budget_timeout=False
product_idle_timeout=False
real_assistant_or_final_item=True
assistant_sentinel_CONTROLLER_OK=True
user_message_not_counted=True
server_healthy_at_terminal=True
host_online_at_terminal=True
```

---

## 11. Required-check 必须早于 outcome

### Evidence

- `d2-required-files-check.txt`

required-check 必须逐项重读所有本卡声明 evidence，记录 exists、size、SHA、真实 data line count 和语义判定。

以下任一项必须 FAIL：

- 任一声明文件缺失；成功路径的 error 文件也必须存在并明确 `error=None`；
- server READY 后逐秒 sample 少于 10；
- host sample 少于 2；
- D2 sample 少于 3、ordinal 不连续或未覆盖 C；
- observer/host/C exit 为空或不是整数；
- POST/session/runner 边界被阶段 20 文件代替；
- C attempt 不为 1_of_1；
- 240 秒 watchdog 被修改；
- native observed path/SHA 与固定值不一致；
- live evidence 是 BOM/空行/聚合占位；
- driver/observer SHA 漂移；
- business exit 与 cleanup exit 混用；
- 在业务结束后补写伪 live 行。

只有 required-check PASS 才允许业务分类；否则：

```text
primary=DIAG_INCONCLUSIVE
```

不得由报告推理替代缺失的 exit/sample。

---

## 12. 唯一分类矩阵

只选一个 primary：

| 条件 | primary |
|---|---|
| 违反一次 C、改 240s、改源码、启动后修 observer、事后重建 live evidence、删除 evidence | `REJECT_PROTOCOL` |
| identity/environment/native/exit/sample/required-check/cleanup 任一不可审计 | `DIAG_INCONCLUSIVE` |
| session contents 正确，但 runner 实际加载/选择的 agent config 首次错误，或在 native spawn 前明确报 agent load/spec/cache 错误 | `DIAG_RUNNER_AGENT_LOAD` |
| C 已可信启动但 runner 始终未 spawn | `DIAG_RUNNER_NOT_SPAWNED` |
| runner 已 spawn但固定 native child 始终未 spawn | `DIAG_NATIVE_NOT_SPAWNED` |
| 固定 native 已 spawn但在首个可信业务事件前退出 | `DIAG_CODEX_CHILD_EARLY_EXIT` |
| 固定 native 持续存活、无可信业务事件并真实命中未改 240s idle | `DIAG_CODEX_CHILD_STALL` |
| runner/App Server 已有本 turn 事件，但 Omnigent relay/CLI 缺对应事件 | `DIAG_EVENT_RELAY` |
| 一次 C 满足全部真实 success 条件 | `DIAG_D2_SINGLE_PASS` |

附带一个 subcase，但不得替代 primary：

```text
AGENT_SPEC_OR_CACHE
RUNNER_NOT_SPAWNED
RUNNER_SPAWNED_NATIVE_NOT_SPAWNED
NATIVE_EARLY_EXIT
NATIVE_ALIVE_NO_EVENTS
RUNNER_EVENTS_RELAY_MISSING
CONTROLLER_OK
```

单次 PASS 不得称为 Gate 2 PASS。由于 Gate 2 r4 先前 FAIL，只能说明本次 D2 路径成功，后续是否重跑完整 Gate 2 由 Codex 另行决定。

---

## 13. Cleanup 与冻结顺序

### Evidence

- `cleanup.txt`
- `pid-final-status.txt`
- `runtime-final-status.txt`
- `required-evidence-final-check.txt`
- `evidence-manifest.txt`
- `leak-scan.txt`
- `DIAGNOSIS.txt`
- `d2-outcome.txt`
- `run-summary.txt`

`finally` 只清理本 RUN 的 observer、C、runner、native child、host、server 和 runtime。逐 PID 记录 PID/PPID/create UTC/role/action/final dead。

删除 runtime 前验证：

```text
resolved_under_TEMP=True
leaf_prefix=omnigent-d2-c-cli0146-
leaf_contains_RUN_ID=True
reparse_point=False
```

cleanup 后：

```text
all_run_pids_dead=True
server_port_free=True
runtime_exists=False
codex_tmp_start_equals_end=True
leftover_count=0
evidence_exists=True
```

顺序：

```text
live evidence
  -> d2-business-result
  -> d2-required-files-check
  -> cleanup/end identity
  -> DIAGNOSIS + d2-outcome + run-summary + HERMES_DIAGNOSIS_21.md
  -> required-evidence-final-check
  -> evidence-manifest
  -> leak-scan（最后文件）
```

final-check 必须覆盖所有声明文件和报告的最终 size/SHA。之后不得修改任何已检查文件。

manifest 覆盖所有此前 evidence 和仓库报告。leak-scan 扫描所有此前文件，要求：

```text
scanned_count=expected_count
hits=0
leak_scan_is_last=True
```

---

## 14. `HERMES_DIAGNOSIS_21.md` 必须包含

- 唯一 primary + subcase；
- RUN_ID、evidence 绝对路径、是否仍存在；
- server/host/C 均 1_of_1；
- HEAD、branch、十二 blob start=end；
- native path/version/size/SHA start=end；
- TUN start/end 只观察；
- `HARNESS_CODEX_PATH` 设置时序；
- agent source/precomputed/session contents/runner load 对照；
- server 逐秒 sample 数、host sample 数、D2 sample 数和 ordinal；
- C 真实 PID/exit/timeout/duration；
- runner/native spawn UTC、identity 和事件边界；
- assistant sentinel 来源；
- 若失败，首个失败产品边界与 evidence 指针；
- required-check、cleanup、manifest、leak-scan；
- 明确未执行 D0/D1/后五轮/完整 Gate 2；
- 下一步：
  - 明确产品边界失败：建议 Codex 另发 **Grok 窄修复卡**；
  - `DIAG_D2_SINGLE_PASS`：建议 Codex 决定是否进入完整 Gate 2 重验；
  - `DIAG_INCONCLUSIVE`：不得建议源码修复。
- Gate 边界：非 Gate 2 PASS、不可 merge。

## 15. 停止条件

仓库内只允许新增：

```text
docs/fixes/handoffs/HERMES_DIAGNOSIS_21.md
```

完成一次 C 或在前置条件失败后，保留 evidence，立即停止并交回 Codex。禁止自行修复、重试、继续其余 Gate 2 轮次、commit/push/merge/tag。
