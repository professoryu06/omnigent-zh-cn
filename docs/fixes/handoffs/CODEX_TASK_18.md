# CODEX TASK 18 — CLI 0.146.0 单次 Omnigent C / D2 断点诊断计划

> **For agentic workers:** 本卡是 Grok 只读诊断计划。只允许一次 Omnigent Controller C/D2；禁止完整 Gate 2、禁止修改源码。所有业务证据必须实时落盘并在独立 outcome 文件创建前完成 required-check。

**Goal:** 在全新、持久 evidence RUN 中，固定已验收的 native Codex CLI `0.146.0`，只执行一次 Omnigent Controller C/D2，判断产品链路是未 spawn、native 早退、native 存活无事件、已有事件但 relay 丢失，还是可信成功。

**Architecture:** 一个原生 Windows PowerShell 编排器启动独立 Omnigent server、foreground host 和单次 C；一个在运行前通过 `node --check` 的 Node observer 以约 1 秒粒度实时记录进程树、服务健康度、session/runner/App Server 状态和可观察事件边界。`HARNESS_CODEX_PATH` 在所有产品进程启动前固定并继承；原始正文仅存在于临时 runtime，evidence 只保存脱敏元数据、时间线、哈希和结果。

**Tech Stack:** Windows PowerShell、Node.js、Omnigent `.venv\Scripts\omnigent-zh.exe`、native Codex CLI `0.146.0`、JSON/JSONL、SHA-256。

## Global Constraints

- **执行者：** Grok（只读诊断，不是开发者，不是 Gate 审查者）。
- **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`
- **唯一仓库交付：** `docs/fixes/handoffs/GROK_DIAGNOSIS_18.md`
- **Omnigent CLI：** `F:\codex-ai\git项目部署\tmp\omnigent-review\.venv\Scripts\omnigent-zh.exe`
- **模型：** `gpt-5.6-sol`
- **固定 native：** `C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`
- **native 版本：** `codex-cli 0.146.0`
- **native 大小：** `358650672` bytes
- **native SHA-256：** `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb`
- **产品 idle watchdog：** 保持 `240s`，禁止调高、关闭、绕过或 monkey-patch。
- **D2 次数：** 只允许一次 Controller C；禁止重试、换端口续跑、换模型续跑。
- **TUN：** 只观察 start/end；禁止开关、重启、重配或调用控制 API。
- **平台：** 原生 Windows PowerShell；禁止 WSL、tmux、容器或远程 Linux。
- **禁止执行：** D0、D1、E-pos、E-pos-strict、E-neg-warn、E-neg-strict、R、完整 Gate 2 六轮、pytest、Ruff、Gate 1。
- **禁止修改：** `omnigent/`、`tests/`、政策、`STATUS.md`、旧 handoff、用户 Codex/代理/认证/TUN 配置。
- **禁止：** commit、push、merge、tag、PR/Issue 修改。
- **Evidence 必须持久保留，不得删除。**
- Gate 1=`PASS（相对 main）`、非全仓 GREEN；Gate 2 r4=`FAIL`；不可 merge。

---

## 1. 必读、替代关系和执行边界

### Files

- Read: `docs/fixes/handoffs/CODEX_REVIEW_17_REWORK.md`
- Read: `docs/fixes/handoffs/GROK_DIAGNOSIS_17_REWORK.md`
- Read: `docs/fixes/handoffs/CODEX_TASK_17_REWORK.md`
- Read: `docs/fixes/handoffs/GROK_COMPLETION_13.md`
- Read: `docs/fixes/PRE_MERGE_GATES.md`
- Read: `omnigent/inner/codex_executor.py`
- Read: `omnigent/runtime/harnesses/_scaffold.py`

- [ ] **Step 1: 明确旧 D2 卡失效**

`CODEX_TASK_16.md` 固定旧 CLI `0.144.0-alpha.4`，已经失效，**不得执行**。

本卡 `CODEX_TASK_18.md` 是唯一允许执行的新 CLI D2 卡。

- [ ] **Step 2: 只使用阶段 17 REWORK 作为准入事实**

允许沿用的只有已验收事实：

```text
CLI 0.146.0 native 身份已固定
D0_PASS=True
D1_PASS=True
DIAG_D1_READY_FOR_D2
```

不得复制阶段 17 REWORK 的 PID、thread、turn、stdout、exit、sentinel 或 evidence 文件作为本 RUN 结果。

- [ ] **Step 3: 冻结执行流程**

```text
identity / precheck
  → native / TUN / environment
  → observer node --check
  → server READY + 10s health
  → foreground host online
  → 只执行一次 Controller C
  → 约 1s live spawn/event observation
  → 冻结业务结果
  → d2-required-files-check
  → finally / cleanup
  → final diagnosis / summary / outcome
  → required-evidence-final-check
  → manifest
  → leak-scan
  → GROK_DIAGNOSIS_18.md
  → STOP
```

本卡无论 D2 成功或失败，都不得继续执行其余五轮 Gate 2。

---

## 2. 全新 RUN、路径和端口

### Files

- Create outside repo: `C:\Users\Administrator\omnigent-diagnostics\$RUN_ID\`
- Create outside repo: `%TEMP%\omnigent-d2-c-cli0146-$RUN_ID\`
- Create: `docs/fixes/handoffs/GROK_DIAGNOSIS_18.md`

- [ ] **Step 1: 一次性生成并冻结变量**

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$OMNIGENT_CLI = Join-Path $WORKTREE '.venv\Scripts\omnigent-zh.exe'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-dc83140-grok-d2-c-cli0146-r1'
$EVIDENCE_ROOT = "C:\Users\Administrator\omnigent-diagnostics\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-d2-c-cli0146-$RUN_ID"
$DATA_ROOT = Join-Path $RUNTIME_ROOT 'data'
$CODEX_TMP = Join-Path $WORKTREE '.codex-tmp'
$NATIVE_CODEX_EXE = 'C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe'
$EXPECTED_NATIVE_VERSION = 'codex-cli 0.146.0'
$EXPECTED_NATIVE_SIZE = 358650672
$EXPECTED_NATIVE_SHA256 = 'bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb'
$CODEX_MODEL = 'gpt-5.6-sol'
$AGENT_PATH = Join-Path $RUNTIME_ROOT 'agents\controller.yaml'
$WORKSPACE_C = Join-Path $RUNTIME_ROOT 'workspaces\controller'
$OBSERVER_PATH = Join-Path $RUNTIME_ROOT 'd2-observer.mjs'
$SHORT_USER_MESSAGE = 'Reply with CONTROLLER_OK and stop.'
```

禁止只靠大小写区分变量。

- [ ] **Step 2: 路径必须全新**

`EVIDENCE_ROOT` 和 `RUNTIME_ROOT` 开始时必须不存在。若已存在：

```text
DIAG_INCONCLUSIVE
```

不得删除后复用、换后缀续跑或拼接内容。

- [ ] **Step 3: 分配单个动态端口**

```powershell
$PORT_PROBE = [System.Net.Sockets.TcpListener]::new(
  [System.Net.IPAddress]::Loopback,
  0
)
$PORT_PROBE.Start()
$SERVER_PORT = ([System.Net.IPEndPoint]$PORT_PROBE.LocalEndpoint).Port
$PORT_PROBE.Stop()
$SERVER_URL = "http://127.0.0.1:$SERVER_PORT"
```

端口取得后立即写入 identity。正式启动 server 前再次确认未被占用；若已占用，停止为 `DIAG_INCONCLUSIVE`，不得同 RUN 换端口续跑。

- [ ] **Step 4: 限定仓库写入**

仓库内只允许新增：

```text
docs/fixes/handoffs/GROK_DIAGNOSIS_18.md
```

不得修改现有文件。

---

## 3. Identity、八个 blob 与预检

### Files

- Evidence: `identity-start.txt`
- Evidence: `identity-end.txt`
- Evidence: `candidate-source-blobs-start.txt`
- Evidence: `candidate-source-blobs-end.txt`
- Evidence: `git-status-start.txt`
- Evidence: `git-status-end.txt`
- Evidence: `precheck-processes.txt`
- Evidence: `precheck-paths.txt`
- Evidence: `codex-tmp-start.txt`

- [ ] **Step 1: 冻结 start identity**

必须记录：

```text
HEAD=dc83140c73ceb12fa165753c1880c19f68da86f4
branch=docs/fix-plans-core-secondary
worktree=F:\codex-ai\git项目部署\tmp\omnigent-review
RUN_ID=<本 RUN>
SERVER_PORT=<本 RUN 唯一端口>
```

- [ ] **Step 2: 核对八个 blob**

| 文件 | 期望 blob |
|---|---|
| `omnigent/server/routes/_workspace_validation.py` | `5bf5e587b9177a9ecbce572b11656edac31ea7fe` |
| `omnigent/server/routes/sessions.py` | `0375e5f951d82c01c9f67e8cf7b41a90aff10330` |
| `tests/server/routes/test_workspace_validation.py` | `63291bfa4bc47c196e04a218c82b782ecb613786` |
| `tests/server/routes/test_workspace_validation_helpers.py` | `4cae0f53cb724c991a1c502c2919e37da7b7737a` |
| `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` |
| `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` |
| `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` |
| `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` |

任一不匹配时停止为 `DIAG_INCONCLUSIVE`。

- [ ] **Step 3: 预检 self/ancestor 和残留**

记录编排器 self/ancestor PID、PPID、进程名、创建 UTC，并标记：

```text
DIAG_DRIVER_SELF_OR_ANCESTOR
```

搜索旧 r4、阶段 14–17、失效 Task 16、本 RUN 字符串、runtime、拟用端口相关外部残留。排除 self/ancestor 后必须：

```text
count=0
pass=True
```

非零只记录、不 kill，进入 finally。

- [ ] **Step 4: 冻结 `.codex-tmp`**

start 直接子项必须为空。非空不得删除，停止为 `DIAG_INCONCLUSIVE`。

- [ ] **Step 5: end 复核**

HEAD、branch、八 blob、非本卡允许范围的 git status/size 必须 start=end。

---

## 4. Native、TUN 与产品环境继承

### Files

- Evidence: `native-discovery.txt`
- Evidence: `native-codex-identity-start.txt`
- Evidence: `native-codex-identity-end.txt`
- Evidence: `tun-status-start.txt`
- Evidence: `tun-status-end.txt`
- Evidence: `environment-presence.txt`
- Evidence: `child-environment-contract.txt`
- Evidence: `loopback-10100-start.txt`
- Evidence: `loopback-10100-end.txt`

- [ ] **Step 1: 固定 native**

开始和结束必须满足：

```text
path=C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe
version=codex-cli 0.146.0
size=358650672
sha256=bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb
shim=False
```

禁止 wrapper、旧 sandbox binary、Desktop binary 或 PATH 动态入口。

- [ ] **Step 2: 强制数组读取 TUN**

```powershell
$TUN_LIKE_ADAPTERS = @(
  Get-NetAdapter -IncludeHidden -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Status -eq 'Up' -and (
        $_.Name -eq 'Meta' -or
        $_.InterfaceDescription -match 'TUN|Wintun|Meta'
      )
    }
)
$META_TUN_IS_UP = [bool](
  @($TUN_LIKE_ADAPTERS | Where-Object {
    $_.Name -eq 'Meta' -and $_.Status -eq 'Up'
  }).Count -gt 0
)
```

start 必须 `Meta=Up`。end 必须：

```text
meta_up_at_start=True
meta_up_at_end=True
tun_state_changed=False
```

不得为满足条件而操作 TUN。

- [ ] **Step 3: 只记录环境变量存在性**

只记录以下名称是否 present，不记录值：

- `HTTP_PROXY`
- `HTTPS_PROXY`
- `ALL_PROXY`
- `NO_PROXY`
- `CODEX_HOME`
- `HARNESS_CODEX_PATH`
- `OMNIGENT_DATA_DIR`

允许记录：

```text
NO_PROXY_HAS_127_0_0_1=True|False
NO_PROXY_HAS_LOCALHOST=True|False
```

- [ ] **Step 4: 在产品进程启动前构造共同环境**

```powershell
$COMMON_CHILD_ENV = @{
  'OMNIGENT_DATA_DIR' = $DATA_ROOT
  'NO_PROXY' = '127.0.0.1,localhost'
  'no_proxy' = '127.0.0.1,localhost'
  'PYTHONUTF8' = '1'
  'PYTHONIOENCODING' = 'utf-8'
  'HARNESS_CODEX_PATH' = $NATIVE_CODEX_EXE
}
```

server、foreground host、C 以及后续 runner 必须继承该环境。不得在 server/host 启动后才设置 `HARNESS_CODEX_PATH`。

`child-environment-contract.txt` 记录：

- 每个产品进程启动前变量存在性；
- 允许记录的 native 绝对路径和 SHA；
- `HARNESS_CODEX_PATH_set_before_server=True`
- `HARNESS_CODEX_PATH_set_before_host=True`
- `HARNESS_CODEX_PATH_set_before_C=True`

不得输出完整环境或代理凭据。

- [ ] **Step 5: 只读记录 10100**

记录 start/end 是否 LISTEN；若监听，记录 owning PID、进程名、binary SHA/version。不得向 `/v1/responses` 主动发送请求，不启动或停止服务。

---

## 5. Observer 语法预检和实时落盘纪律

### Files

- Runtime: `d2-observer.mjs`
- Evidence: `observer-identity.txt`
- Evidence: `observer-syntax-check.txt`

- [ ] **Step 1: 创建外部 observer**

Observer 只允许：

- 每约 1 秒读取进程/服务/API/日志的只读状态；
- 读取本 RUN 产品 stdout/stderr；
- 把原始正文写到 runtime；
- 把脱敏元数据增量 append 到 evidence；
- 不修改 Omnigent 源码、数据库业务数据、TUN 或系统代理。

- [ ] **Step 2: 在启动任何产品进程前运行语法检查**

```text
node --check <absolute d2-observer.mjs>
```

必须：

```text
exit=0
syntax_ok=True
```

同时记录 observer path、size、SHA、Node version。

语法失败时允许只修改 runtime observer；但修改后必须重新记录新 SHA 并重新 `node --check`。在 syntax_ok 前禁止启动 server/host/C。

- [ ] **Step 3: 禁止业务中途改 observer**

server 启动后，observer path/size/SHA 必须冻结；后续变化为 `DIAG_INCONCLUSIVE`，不得换 observer 后继续业务。

- [ ] **Step 4: Evidence 写入失败立即降级**

任一 live evidence append 失败：

- 不重试 C；
- 不补写伪 live 数据；
- 冻结已取得事实；
- finally 后分类 `DIAG_INCONCLUSIVE`。

---

## 6. 单一 Controller agent 与 workspace

### Files

- Runtime: `agents\controller.yaml`
- Runtime: `workspaces\controller\`
- Evidence: `agents-sanitized.txt`
- Evidence: `d2-workspace-contract.txt`

- [ ] **Step 1: 创建唯一 agent**

```yaml
name: controller-d2-cli0146
prompt: "You are Controller. Reply with the single token CONTROLLER_OK and stop."
executor:
  harness: codex
  model: gpt-5.6-sol
```

Evidence 只记录 name、harness、model、prompt chars/SHA 和 sentinel token；不保存 prompt 正文。

- [ ] **Step 2: 创建 Windows drive-absolute workspace**

必须证明：

```text
drive_absolute=True
single_separator_shape=True
contains_RUN_ID=True
```

禁止 WSL/POSIX 伪路径。

---

## 7. 启动 server 和 foreground host

### Files

- Evidence: `server-lifecycle-live.jsonl`
- Evidence: `server-ready.txt`
- Evidence: `host-lifecycle-live.jsonl`
- Evidence: `host-online.txt`

- [ ] **Step 1: 启动 server**

使用共同环境，等价执行：

```text
omnigent-zh.exe server --host 127.0.0.1 --port <SERVER_PORT> --no-open
```

READY 必须同时满足：

- server process alive；
- 端口 LISTEN；
- `/health` 通过显式 no-proxy 请求返回 200；
- 连续 10 秒、每秒一次 health=200。

server stdout/stderr 原文只写 runtime，evidence 实时记录 UTC、PID、alive、累计 bytes、health status 和端口状态。

- [ ] **Step 2: 启动 foreground host**

使用共同环境，等价执行：

```text
omnigent-zh.exe host --server <SERVER_URL> --non-interactive
omnigent-zh.exe host status --server <SERVER_URL> --json
```

最多 30 秒等待。只有以下全部成立才允许 C：

```text
host_process_alive=True
process=online
host_status=online
```

- [ ] **Step 3: 前置失败停止**

server/host 身份、环境、健康或 online 不可信时：

```text
DIAG_INCONCLUSIVE
```

不得执行 C，不得重启 server/host、换端口或同 RUN 续跑。

---

## 8. 单次 C 与约 1 秒 spawn 观测

### Files

- Evidence: `d2-samples-live-sanitized.jsonl`
- Evidence: `d2-events-live-sanitized.jsonl`
- Evidence: `d2-c-timeline.txt`
- Evidence: `d2-process-tree.txt`
- Evidence: `d2-business-result.txt`
- Evidence: `d2-spawn-window.txt`
- Evidence: `d2-event-relay.txt`
- Evidence: `d2-error-sanitized.txt`
- Evidence: `d2-stream-hashes.txt`

- [ ] **Step 1: 在 C 前启动 live observer**

从 C 启动前至少 1 秒开始，以单调时间和 UTC 约每 1 秒 append 一条 sample，直到：

- C 可信业务终态；
- 或外层 300 秒预算；
- 或不可恢复前置失败。

每条 sample 至少记录：

- ordinal、UTC、monotonic elapsed；
- server PID/alive/health/累计 stdout/stderr bytes；
- host PID/alive/process status/host status；
- C PID/alive/累计 stdout/stderr bytes；
- session id hash/status；
- runner PID/PPID/create UTC/alive/exit/可读 CPU/IO；
- native Codex PID/PPID/create UTC/alive/exit/可执行路径/version/SHA；
- runner/App Server 可观察事件类别和累计数；
- Omnigent relay 可观察事件类别和累计数；
- CLI 可见事件类别和累计数；
- `.codex-tmp` 新 home 的创建 UTC 和文件/目录计数变化。

不可读取的字段写：

```text
NOT_OBSERVABLE
```

禁止伪造为 0 或 False。

- [ ] **Step 2: 只执行一次 C**

使用共同环境，等价执行：

```text
cwd=<WORKSPACE_C>
OMNIGENT_STRICT_PROMPT=unset
omnigent-zh.exe run <AGENT_PATH> -p "Reply with CONTROLLER_OK and stop." --server <SERVER_URL>
outer_budget=300s
product_idle_watchdog=240s_UNCHANGED
attempt=1_of_1
```

不得运行 D0/D1 或后五轮。不得在 240 秒 idle 后拉长 timeout 重试。

- [ ] **Step 3: 实时记录事件边界**

`d2-events-live-sanitized.jsonl` 对每个可观察事件增量记录：

```text
ordinal
observed_utc
source=server|host|runner|app_server|relay|cli
event_type
session_hash
turn_hash
item_type
phase
is_user_message
is_assistant_or_final
sentinel_match
error_code
http_ws_status
raw_line_bytes
```

正文只写 runtime。

- [ ] **Step 4: 冻结真实业务结果**

在 cleanup 前创建 `d2-business-result.txt`，记录：

- C 真实 exit/timeout/duration；
- C 是否由产品 240 秒 idle watchdog 终止；
- server/host 在业务终态时是否健康；
- session/runner/App Server 是否产生；
- 首次 runner spawn UTC；
- 首次 native spawn UTC；
- 首次 native 事件 UTC；
- 首次 Omnigent relay 事件 UTC；
- 首次 CLI 可见事件 UTC；
- assistant sentinel 是否来自真实 assistant/model 输出；
- 0202 workspace 400 是否命中；
- 10100/426/provider/protocol error 是否命中。

不得把 cleanup 主动停止产生的 exit 冒充业务 exit。

- [ ] **Step 5: 验证实际 child binary**

若出现 native child，必须记录：

```text
actual_child_path
actual_child_version
actual_child_size
actual_child_sha256
matches_HARNESS_CODEX_PATH=True
```

若实际使用其他 binary，最终为 `DIAG_INCONCLUSIVE`；完成观察和 finally，但不得重试。

- [ ] **Step 6: 写互斥断点布尔**

`d2-spawn-window.txt`：

```text
runner_spawned=True|False
codex_child_spawned=True|False
codex_child_early_exit=True|False
codex_child_alive_without_events=True|False
codex_events_seen_by_runner=True|False|NOT_OBSERVABLE
events_seen_by_omnigent_relay=True|False|NOT_OBSERVABLE
events_seen_by_cli=True|False
business_success=True|False
```

必须用约 1 秒 sample 的 ordinal/UTC 支撑每个布尔。

- [ ] **Step 7: 冻结 raw stream size/SHA**

在删除 runtime 前，对 server、host、C、observer 的 raw stdout/stderr 记录相对文件名、size、SHA；不复制正文到 evidence。

---

## 9. D2 required-check

### Files

- Evidence: `d2-required-files-check.txt`

- [ ] **Step 1: 在 cleanup 前检查业务证据**

逐项记录存在性、非空、size、SHA：

```text
server-lifecycle-live.jsonl
server-ready.txt
host-lifecycle-live.jsonl
host-online.txt
d2-samples-live-sanitized.jsonl
d2-events-live-sanitized.jsonl
d2-c-timeline.txt
d2-process-tree.txt
d2-business-result.txt
d2-spawn-window.txt
d2-event-relay.txt
d2-error-sanitized.txt
d2-stream-hashes.txt
child-environment-contract.txt
```

同时检查：

- sample ordinals 连续；
- event ordinals 连续；
- C attempt=`1_of_1`；
- business exit 与 cleanup exit 分离；
- observer SHA 未漂移；
- 1 秒采样覆盖整个 C 时间窗；
- 所有不可观察字段明确为 `NOT_OBSERVABLE`；
- 没有 prompt/assistant 正文进入 evidence。

- [ ] **Step 2: required-check 失败不得补写**

失败时：

```text
DIAG_INCONCLUSIVE
```

不得补造 live sample、重试 C 或从控制台回忆重建。

---

## 10. 断点分类矩阵

### Files

- Evidence: `DIAGNOSIS.txt`
- Evidence: `d2-outcome.txt`
- Evidence: `run-summary.txt`

- [ ] **Step 1: 只选一个主分类**

| 分类 | 必要证据 |
|---|---|
| `DIAG_RUNNER_SPAWN` | C 已可信启动，但 runner 未产生，或 runner 产生而固定 native child 从未产生 |
| `DIAG_CODEX_CHILD_EARLY_EXIT` | 固定 native child 已产生，但在首个可信业务事件前退出；exit/error 时间线可信 |
| `DIAG_CODEX_CHILD_STALL` | 固定 native child 持续存活，但没有可信业务事件，最终命中未改动的 240 秒 idle watchdog |
| `DIAG_EVENT_RELAY` | runner/App Server 已有属于该 turn 的事件，但 Omnigent relay/CLI 没有对应事件 |
| `DIAG_TRANSIENT_R4` | 单次 C 在 300 秒内 exit=0、timeout=False、真实 assistant sentinel=`CONTROLLER_OK`，产品链路前后健康 |
| `DIAG_INCONCLUSIVE` | identity、环境继承、binary、observer、exit、时间线、cleanup、required-check、manifest 或 leak-scan任一不可审计 |

- [ ] **Step 2: 写细分 subcase**

主分类之外允许记录一个不替代主分类的 subcase：

```text
RUNNER_NOT_SPAWNED
RUNNER_SPAWNED_CODEX_NOT_SPAWNED
CODEX_EARLY_EXIT
CODEX_ALIVE_NO_EVENTS
RUNNER_EVENTS_RELAY_MISSING
PRODUCT_C_SUCCESS
NOT_DETERMINABLE
```

- [ ] **Step 3: outcome 必须在 d2 required-check 之后首次创建**

`d2-outcome.txt` 至少包含：

```text
attempt=1_of_1
d2_required_files_pass=True|False
business_success=True|False
primary_classification=<唯一分类>
subcase=<细分>
product_idle_watchdog_s=240
full_gate2_executed=False
```

- [ ] **Step 4: 保持 Gate 边界**

- `DIAG_TRANSIENT_R4` 也不是 Gate 2 PASS。
- 本卡没有执行六轮，不能生成 Gate 2 verdict。
- TUN 开启仅是本 RUN 环境事实，不是根因证明。
- 任何需要改代码的结论只交回 Codex，由 Codex 另发 Hermes 卡。

---

## 11. Finally 与精确 cleanup

### Files

- Evidence: `run-pids.txt`
- Evidence: `codex-tmp-before-cleanup.txt`
- Evidence: `codex-tmp-delete-actions.txt`
- Evidence: `codex-tmp-end.txt`
- Evidence: `cleanup.txt`

- [ ] **Step 1: 冻结本 RUN PID tree**

包含：

- observer；
- server；
- foreground host；
- C；
- runner；
- native App Server；
- 本 RUN 明确创建的其他子进程。

先正常停止，再只对冻结 PID tree 做必要终止。禁止 blanket kill、按名称批量 kill、`taskkill /IM`、终止 Codex Desktop 或 TUN。

- [ ] **Step 2: 精确清理 runtime 和 private home**

只允许删除：

- 绝对路径包含完整 RUN_ID 的 `RUNTIME_ROOT`；
- start 后新增、创建时间属于本 RUN、叶名归属于本 RUN 的 `.codex-tmp\omnigent-codex-home-*`。

每个目标删除前记录：

```text
target_abs=<规范化绝对路径>
leaf=<单个叶名>
under_expected_parent=True
ownership=this_RUN
target_is_reparse=True|False
action=<逐项结果>
```

后代 reparse 只删除链接，不读取或跟随 Target。禁止通配符、`git clean`，不得删除 `.codex-tmp` 父目录。

- [ ] **Step 3: cleanup 验证**

必须满足：

- 本 RUN PID 全部 dead；
- SERVER_PORT free；
- runtime 不存在；
- `.codex-tmp` end=start；
- 命令行匹配本 RUN/端口/runtime 的外部 leftover=0；
- TUN/10100 只观察；
- evidence 根仍存在。

任一不可审计，最终分类覆盖为 `DIAG_INCONCLUSIVE`。

---

## 12. 最终 evidence 顺序

### Files

- Evidence: `required-evidence-final-check.txt`
- Evidence: `evidence-manifest.txt`
- Evidence: `leak-scan.txt`

- [ ] **Step 1: 一次性写最终 diagnosis/outcome/summary**

在 cleanup 结果已知后，首次创建并冻结：

- `DIAGNOSIS.txt`
- `d2-outcome.txt`
- `run-summary.txt`

写完后不得再修改。

- [ ] **Step 2: 生成 final required-check**

检查任务要求的全部 evidence，包括最终 diagnosis/outcome/summary：

- exists；
- non-empty；
- size；
- SHA-256。

该文件不检查自身、manifest 或尚未创建的 leak-scan。

**final required-check 之后禁止修改任何被检查文件。**

- [ ] **Step 3: 生成 manifest**

对当时全部 evidence（排除 manifest 自身和尚未创建的 leak-scan）记录：

- relative path；
- size；
- SHA-256；
- LastWriteTimeUtc。

- [ ] **Step 4: 最后生成 leak-scan**

必须：

```text
files_present_before_scan == files_scanned
prompt_body_hits=0
credential_token_cookie_header_value_hits=0
auth_config_body_hits=0
symlink_target_hits=0
evidence_root_exists=True
pass=True
```

`leak-scan.txt` 必须是 evidence 最后创建、最后修改文件。之后不得改写 evidence。

---

## 13. 唯一仓库报告

### Files

- Create: `docs/fixes/handoffs/GROK_DIAGNOSIS_18.md`

- [ ] **Step 1: leak-scan 后写报告**

至少包含：

- RUN_ID、持久 evidence、已删除 runtime、端口和时间窗；
- 唯一分类和 subcase；
- HEAD/八 blob/native start=end；
- `HARNESS_CODEX_PATH` 注入和实际 child binary；
- TUN start/end 只观察；
- server READY+10s、foreground host online；
- 单次 C 的真实 exit/timeout/sentinel/240 秒 watchdog；
- 约 1 秒 live sample 数、ordinal、时间覆盖；
- runner/App Server spawn、early exit/alive/no event、relay/CLI 事件边界；
- business exit 与 cleanup exit 分离；
- d2 required-check、outcome 创建顺序；
- cleanup、final required-check、manifest、leak-scan；
- 没有执行完整 Gate 2；
- 没有修改源码/tests/政策/STATUS/配置；
- Gate 1 相对 PASS、Gate 2 r4 FAIL、不可 merge；
- 若需源码修复，明确请求 Codex 另发 Hermes 卡。

报告完成后只读确认 evidence 根仍存在，然后停止。

---

## 14. 完成标准

- [ ] 全新 RUN_ID/evidence/runtime/端口，未拼接旧 RUN。
- [ ] 固定 CLI 0.146.0 native path/size/SHA。
- [ ] `HARNESS_CODEX_PATH` 在 server/host/C 前设置并继承。
- [ ] TUN start/end 一致且只观察。
- [ ] observer 在业务启动前 `node --check` PASS，业务中 SHA 不变。
- [ ] server READY+10s、foreground host online 后才执行 C。
- [ ] 只执行一次 C；未执行 D0/D1/后五轮。
- [ ] 产品 240 秒 idle watchdog 未修改。
- [ ] 约 1 秒 sample 覆盖 C 时间窗，ordinal 连续。
- [ ] 区分未 spawn、早退、存活无事件、relay 丢失或可信成功。
- [ ] 实际 native child identity 与固定 SHA 一致，或明确未 spawn。
- [ ] business exit 与 cleanup exit 分开。
- [ ] d2 live evidence 和 required-check 在 outcome 前完成。
- [ ] 没有重试、没有事后重建 live evidence。
- [ ] 本 RUN PID dead、端口 free、runtime 删除、`.codex-tmp` start=end、leftover=0。
- [ ] diagnosis/outcome/summary 在 final required-check 前冻结，check 后不再修改。
- [ ] manifest 重新覆盖最终文件，leak-scan 最后且 hits=0。
- [ ] evidence 持久保留。
- [ ] 仓库只新增 `GROK_DIAGNOSIS_18.md`。
- [ ] 未修改源码/tests/政策/STATUS/配置；未 commit/push/merge/tag。
- [ ] 唯一分类未冒充 Gate 2 verdict。

完成后停止，交回 Codex 只读验收。
