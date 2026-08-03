# CODEX TASK 16 — 单次 Omnigent C / D2 与 1 秒 spawn 观测计划

> **For agentic workers:** 本卡是 Grok 只读诊断计划；按顺序逐项执行和记录。禁止调用开发/实现流程，禁止修改源码。

**Goal:** 在全新、持久 evidence RUN 中，仅执行一次 Omnigent Controller C/D2，确认阶段 15 已通过的同一 native Codex 在产品 runner 拓扑中是未 spawn、早退、存活无事件、已有事件但 relay 丢失，还是 C 可信成功。

**Architecture:** 使用一个 PowerShell 前台驱动管理 Omnigent server、foreground host、单次 C、约 1 秒粒度的进程/事件观察和 finally 清理。`HARNESS_CODEX_PATH`、模型、TUN 状态和 240 秒产品 watchdog 都固定；原始正文留在临时 runtime，evidence 只保存脱敏元数据。

**Tech Stack:** Windows PowerShell、工作树 `.venv\Scripts\omnigent-zh.exe`、Omnigent server/host/runner、native `codex.exe`、JSON/JSONL 脱敏摘要。

## Global Constraints

- **执行者：** Grok（只读诊断，不是 Gate 审查者，不是开发者）。
- **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`
- **唯一仓库交付：** `docs/fixes/handoffs/GROK_DIAGNOSIS_16.md`
- **模型：** `gpt-5.6-sol`，本 RUN 禁止换模型。
- **native：** `C:\Users\Administrator\.codex\.sandbox-bin\codex.exe`
- **native SHA-256：** `b88f944ef63556527caae2ad43f80b88b8be174dc09b09d9b037fc94240a0e91`
- **TUN：** 只观察 start/end；禁止开关、重启、重配或调用 TUN 控制 API。
- **产品 watchdog：** 保持 240 秒；禁止调高、关闭或 monkey-patch。
- **D2 次数：** 只允许一次 C；禁止重试、换端口续跑、换模型续跑。
- **禁止：** D0、D1、E-pos、E-pos-strict、E-neg-warn、E-neg-strict、R、完整 Gate 2 六轮、pytest、Ruff、Gate 1。
- **禁止修改：** `omnigent/`、`tests/`、政策、`STATUS.md`、旧 handoff、用户 Codex/代理/认证配置。
- **禁止：** commit、push、merge、tag、PR/Issue 修改。
- **Evidence 必须持久保留，不得删除。**
- Gate 1 仍为 `PASS（相对 main）`、非全仓 GREEN；Gate 2 r4 仍为 `FAIL`；不可 merge。

---

## 1. 必读与执行入口

开始前完整读取：

1. `docs/fixes/handoffs/CODEX_REVIEW_15.md`
2. `docs/fixes/handoffs/GROK_DIAGNOSIS_15.md`
3. `docs/fixes/handoffs/CODEX_TASK_14.md` 的 D2 与分类矩阵
4. `docs/fixes/handoffs/GROK_COMPLETION_13.md` 的 r4 C 失败事实
5. `docs/fixes/PRE_MERGE_GATES.md` §2 的 C 拓扑
6. `omnigent/inner/codex_executor.py`
7. `omnigent/runtime/harnesses/_scaffold.py::_guarded_run_turn()`

阶段 15 只作为“允许另开 D2 卡”的已验收前提。不得复制、续写或拼接阶段 15、阶段 14 或 r4 evidence，不能把旧 RUN 的 PID、session、stdout、exit 或事件当成本 RUN 结果。

## 2. 文件结构与唯一交付

**仓库内创建：**

- `docs/fixes/handoffs/GROK_DIAGNOSIS_16.md`：最终只读诊断报告。

**仓库外创建：**

- `C:\Users\Administrator\omnigent-diagnostics\$RUN_ID\`：持久 evidence；`$RUN_ID` 按 Task 1 的命令一次生成并冻结。
- `%TEMP%\omnigent-d2-c-$RUN_ID\`：本 RUN 临时 runtime，finally 删除。

**仓库内不得修改：**

- 任意现有 `.py`、tests、政策、状态或 handoff。

如果诊断指向代码修复，停止并在报告中请求 Codex 另发 Hermes 开发卡；不得由 Grok 当场实现。

## 3. Task 1 — 全新 RUN、identity 与预检

**Files:**

- Create outside repo: `C:\Users\Administrator\omnigent-diagnostics\$RUN_ID\`
- Create outside repo: `%TEMP%\omnigent-d2-c-$RUN_ID\`
- Evidence: `identity-start.txt`、`candidate-source-blobs-start.txt`、`git-status-start.txt`、`precheck-processes.txt`、`precheck-paths.txt`、`codex-tmp-start.txt`

- [ ] **Step 1: 生成一次性标识和路径**

```powershell
$ErrorActionPreference = 'Stop'
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$CLI = Join-Path $WORKTREE '.venv\Scripts\omnigent-zh.exe'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-dc83140-grok-d2-c-r1'
$EVIDENCE_ROOT = "C:\Users\Administrator\omnigent-diagnostics\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-d2-c-$RUN_ID"
$DATA_ROOT = Join-Path $RUNTIME_ROOT 'data'
$CODEX_TMP = Join-Path $WORKTREE '.codex-tmp'
$NATIVE = 'C:\Users\Administrator\.codex\.sandbox-bin\codex.exe'
$MODEL = 'gpt-5.6-sol'
$AGENT_PATH = Join-Path $RUNTIME_ROOT 'agents\controller.yaml'
$WORKSPACE_C = Join-Path $RUNTIME_ROOT 'workspaces\controller'
$SHORT_USER_MESSAGE = 'Reply with CONTROLLER_OK and stop.'

$portProbe = [System.Net.Sockets.TcpListener]::new(
  [System.Net.IPAddress]::Loopback,
  0
)
$portProbe.Start()
$PORT = ([System.Net.IPEndPoint]$portProbe.LocalEndpoint).Port
$portProbe.Stop()
$SERVER_URL = "http://127.0.0.1:$PORT"
```

`EVIDENCE_ROOT` 与 `RUNTIME_ROOT` 必须开始时不存在；若已存在，停止并分类 `DIAG_INCONCLUSIVE`，不得续写。
`$PORT` 取得后立即冻结到 identity；正式启动 server 前再次确认它未被其它进程占用。若已占用，停止为 `DIAG_INCONCLUSIVE`，不得在同一 RUN 换端口续跑。

- [ ] **Step 2: 冻结 identity**

记录 HEAD、branch、工作树绝对路径、CLI 绝对路径/版本/源码加载路径、RUN_ID、evidence/runtime、native 路径/版本/大小/SHA-256。HEAD 或 native SHA 不匹配即停止。

- [ ] **Step 3: 冻结八个 blob**

使用 `CODEX_REVIEW_15.md` 中八个文件及 blob；start 全部匹配才继续。结束时必须按同一方法生成 end。

- [ ] **Step 4: 精确预检**

记录 self/ancestor PID 并从残留计数中排除；搜索旧 r4/14/15、本 RUN 字符串、runtime、拟用端口相关外部进程。排除后必须：

```text
count=0
pass=True
```

发现非零只记录、不 kill，执行 finally 后分类 `DIAG_INCONCLUSIVE`。

- [ ] **Step 5: 冻结 `.codex-tmp` start 集合**

直接子项集合必须为空；非空时不删除，停止并分类 `DIAG_INCONCLUSIVE`。

## 4. Task 2 — TUN、代理存在性与 native 继承

**Files:**

- Evidence: `tun-status-start.txt`、`tun-status-end.txt`、`environment-presence.txt`、`native-codex-identity.txt`、`child-environment-contract.txt`

- [ ] **Step 1: 只读记录 TUN start**

必须强制数组化，避免阶段 15 的单对象 `.Count` 错误：

```powershell
$tunLike = @(
  Get-NetAdapter -IncludeHidden -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Status -eq 'Up' -and (
        $_.Name -eq 'Meta' -or
        $_.InterfaceDescription -match 'TUN|Wintun|Meta'
      )
    }
)
$metaUp = [bool](@($tunLike | Where-Object { $_.Name -eq 'Meta' -and $_.Status -eq 'Up' }).Count -gt 0)
```

记录 UTC、adapter name/status/ifIndex、脱敏 description、默认路由 ifIndex/metric、`up_tun_like_adapter_count` 和 `meta_up`。不记录非 loopback IP、DNS 正文、代理凭据或流量正文。

start 必须明确 `Meta=Up`；否则停止为 `DIAG_INCONCLUSIVE`。禁止为了满足条件而开启或修改 TUN。

- [ ] **Step 2: 记录环境变量存在性**

只记录以下名称是否 present，不记录值：

- `HTTP_PROXY`
- `HTTPS_PROXY`
- `ALL_PROXY`
- `NO_PROXY`
- `CODEX_HOME`
- `HARNESS_CODEX_PATH`

允许额外记录 `NO_PROXY_HAS_127_0_0_1` 与 `NO_PROXY_HAS_LOCALHOST` 布尔值。

- [ ] **Step 3: 固定所有产品子进程环境**

在启动 server、host 和 C 之前构造公共环境：

```powershell
$COMMON_ENV = @{
  'OMNIGENT_DATA_DIR' = $DATA_ROOT
  'NO_PROXY' = '127.0.0.1,localhost'
  'no_proxy' = '127.0.0.1,localhost'
  'PYTHONUTF8' = '1'
  'PYTHONIOENCODING' = 'utf-8'
  'HARNESS_CODEX_PATH' = $NATIVE
}
```

`HARNESS_CODEX_PATH` 必须在 server/host/C 及其后续 runner 启动前设置并继承。只记录变量存在、允许的 native 绝对路径和 SHA；不输出完整环境。

- [ ] **Step 4: 验证实际 App Server binary**

D2 若产生 `codex.exe` 子进程，记录 PID、PPID、创建 UTC、可执行文件绝对路径、版本与 SHA-256；必须等于固定 native。若产品实际使用了其它 binary，分类 `DIAG_INCONCLUSIVE`，但仍完成本次观察和 finally，不得现场重试。

## 5. Task 3 — 单一前台驱动与产品拓扑

**Files:**

- Runtime: `agents\controller.yaml`、`workspaces\controller\`
- Evidence: `server-lifecycle.txt`、`server-ready.txt`、`host-lifecycle.txt`、`host-online.txt`、`d2-workspace-contract.txt`、`agents-sanitized.txt`

- [ ] **Step 1: 只创建一个 C agent**

Runtime 中的 YAML 使用：

```yaml
name: controller-d2
prompt: "You are Controller. Reply with the single token CONTROLLER_OK and stop."
executor:
  harness: codex
  model: gpt-5.6-sol
```

Evidence 只记录 name、harness、model、prompt chars/SHA-256、workspace chars/SHA-256，不保存 prompt 正文。

- [ ] **Step 2: 创建一个 Windows drive-absolute workspace**

`d2-workspace-contract.txt` 必须证明：

```text
drive_absolute=True
single_separator_shape=True
contains_RUN_ID=True
```

禁止 WSL/POSIX 伪路径。记录旧 0202 `starting with /` 错误命中数，但不把它作为本卡主目标。

- [ ] **Step 3: 在同一个 PowerShell 前台驱动启动 server**

```text
& $CLI server --host 127.0.0.1 --port $PORT --no-open
```

使用 `HttpWebRequest` 且 `Proxy=$null` 检查 `/health`。READY 必须同时满足进程 alive、端口 LISTEN、health=200，并连续 10 秒每秒观察均为 health=200。

- [ ] **Step 4: 在同一驱动启动 foreground host**

```text
& $CLI host --server $SERVER_URL --non-interactive
& $CLI host status --server $SERVER_URL --json
```

最多 30 秒等待；只有 Process alive、`process=online`、`host_status=online` 同时成立才可启动 C。

- [ ] **Step 5: 任一拓扑前置失败即停止**

server/host 生命周期、身份或状态不可信时，分类 `DIAG_INCONCLUSIVE`，不执行 C，进入 finally。不得重启 server/host、换端口或在同一 evidence 根续跑。

## 6. Task 4 — 单次 C 与约 1 秒 spawn 观测

**Files:**

- Evidence: `d2-c-timeline.txt`、`d2-process-tree.txt`、`d2-spawn-window.txt`、`d2-event-relay.txt`、`d2-c-meta.txt`、`d2-c-error-sanitized.txt`、`d2-events-sanitized.txt`

- [ ] **Step 1: 启动约 1 秒采样器**

在 C 进程启动前开始，以单调时间/UTC 约每 1 秒记录一次，持续到 C 可信结束或外层 300 秒预算：

- server health；
- foreground host PID/alive、`process=online`、`host_status=online`；
- C PID/alive、stdout/stderr 累计 bytes；
- session id/hash与状态；
- runner PID/PPID、创建 UTC、alive、exit、可读 CPU/IO；
- runner 下 `codex.exe` PID/PPID、创建 UTC、binary/SHA、alive、exit、可读 CPU/IO；
- runner/App Server 脱敏事件类型、错误码、累计事件数；
- Omnigent `ctx.emit`/CLI 可见的脱敏事件类型与累计数；
- `.codex-tmp` 新 home 的创建时间和文件/目录计数变化，不读正文或 symlink Target。

无法读取的字段写 `NOT_OBSERVABLE`，禁止伪造为 0。

- [ ] **Step 2: 只执行一次 C**

```text
& $CLI run $AGENT_PATH -p $SHORT_USER_MESSAGE --server $SERVER_URL
cwd=$WORKSPACE_C
OMNIGENT_STRICT_PROMPT=unset
outer_budget=300s
product_idle_watchdog=240s_UNCHANGED
```

不得运行 D0/D1 或后五轮。不得在 240 秒到达后拉长 timeout 再试。

- [ ] **Step 3: 冻结真实业务和进程终态**

分别记录：

- C 的真实 exit/timeout/duration；
- session/runner/App Server 是否曾产生；
- App Server 的真实退出原因或 `NOT_OBSERVABLE`；
- 首次 runner spawn、首次 App Server spawn、首次 App Server 事件、首次 Omnigent relay 事件、首次 CLI 可见事件的 UTC；
- sentinel 是否来自真实 assistant/model 输出；
- 旧 0202 400 是否命中；
- 240 秒 idle watchdog 是否命中。

不能把清理阶段主动终止产生的 exit 值冒充业务 exit。

- [ ] **Step 4: 明确四个断点**

`d2-spawn-window.txt` 必须给出互斥布尔值和证据时间：

```text
runner_spawned=True|False
codex_child_spawned=True|False
codex_child_early_exit=True|False
codex_child_alive_without_events=True|False
codex_events_seen_by_runner=True|False
events_seen_by_omnigent_relay=True|False
events_seen_by_cli=True|False
```

四种重点现象：

1. **未 spawn：** runner 未产生，或 runner 产生但固定 native App Server 从未产生；
2. **早退：** native App Server 产生后在首个业务事件前退出，记录脱敏 exit/error；
3. **存活无事件：** App Server 持续 alive，但直到 240 秒 watchdog 无业务事件；
4. **有事件但 relay 丢：** runner/App Server 侧已有可映射 turn 事件，而 `ctx.emit`/CLI 侧未出现对应事件。

若真实 C 成功，也必须保留上述字段，不能只写 sentinel。

## 7. Task 5 — 唯一诊断分类

**Files:**

- Evidence: `DIAGNOSIS.txt`、`run-summary.txt`

- [ ] **Step 1: 只选一个主分类**

| 分类 | 必要证据 |
|---|---|
| `DIAG_RUNNER_SPAWN` | C 已可信启动，但 runner 未产生，或 runner 产生而固定 native App Server 从未产生 |
| `DIAG_CODEX_CHILD_EARLY_EXIT` | 固定 native App Server 已产生，但在首业务事件前退出；exit/错误时间线可信 |
| `DIAG_CODEX_CHILD_STALL` | 固定 native App Server 持续存活，但无业务事件，最终命中未改动的 240 秒 idle watchdog |
| `DIAG_EVENT_RELAY` | runner/App Server 已有属于该 turn 的事件，但 Omnigent `ctx.emit`/CLI 没有对应 relay |
| `DIAG_TRANSIENT_R4` | 单次 C 在 300 秒内 exit=0、timeout=False、真实 assistant sentinel=`CONTROLLER_OK`，产品链路前后健康 |
| `DIAG_INCONCLUSIVE` | identity、TUN、binary、拓扑、exit、时间线、cleanup、leak-scan 或 evidence 任一不可信 |

若早退有明确的 provider/auth/model/协议错误，只在 `DIAG_CODEX_CHILD_EARLY_EXIT` 下记录脱敏子原因；不得换模型或改网络后续跑。

- [ ] **Step 2: 保持 Gate 边界**

- `DIAG_TRANSIENT_R4` 也不等于 Gate 2 PASS；
- 本卡没有执行六轮，不能生成 Gate 2 四态 verdict；
- TUN 只是在本 RUN 中保持开启，不能宣称是唯一根因；
- 任一需改代码的分类只建议另发 Hermes 开发卡。

## 8. Task 6 — Finally、精确清理与持久 evidence

**Files:**

- Evidence: `run-pids.txt`、`codex-tmp-before-cleanup.txt`、`codex-tmp-delete-actions.txt`、`codex-tmp-end.txt`、`cleanup.txt`

- [ ] **Step 1: 冻结本 RUN PID tree**

包含 server、host、C、runner、App Server 及本 RUN 明确创建的子进程。先正常停止，再只对冻结 PID tree 做必要终止。禁止 blanket kill、`taskkill /IM`、按进程名批量 kill。

- [ ] **Step 2: 精确清理 runtime 与 private home**

只删除：

- 绝对路径包含完整 RUN_ID 的 `RUNTIME_ROOT`；
- start 快照后新增、创建时间在本 RUN 窗口、叶名属于本 RUN 的 `.codex-tmp\omnigent-codex-home-*`。

每个目标先记录：

```text
target_abs=经 Resolve-Path/GetFullPath 核验的单个绝对目标
leaf=该目标的单个目录叶名，必须精确属于本 RUN
under_codex_tmp=True
ownership=this_RUN
target_is_reparse=False
```

后代 reparse 只删除链接本身，不读取或跟随 Target。禁止通配符、`git clean`，不得删除 `.codex-tmp` 父目录。不要复用阶段 15 那条把两个叶名拼接到同一 `skip_missing` 的日志逻辑。

- [ ] **Step 3: 核验 cleanup**

必须同时满足：

- 全部本 RUN PID dead；
- 新端口 free；
- runtime 不存在；
- 命令行匹配 RUN_ID/端口/runtime 的外部 leftover=0；
- `.codex-tmp` end 直接子项集合等于 start；
- TUN/10100 仅观察、未操作；
- evidence 根仍存在。

任一不可信将主分类覆盖为 `DIAG_INCONCLUSIVE`。

## 9. Task 7 — End identity、manifest、leak-scan 与报告

**Files:**

- Evidence: `identity-end.txt`、`candidate-source-blobs-end.txt`、`git-status-end.txt`、`tun-status-end.txt`、`evidence-manifest.txt`、`leak-scan.txt`
- Create: `docs/fixes/handoffs/GROK_DIAGNOSIS_16.md`

- [ ] **Step 1: 只读记录 TUN end**

使用与 start 完全相同、强制数组化的代码和字段。必须原始 adapter 行与派生布尔一致：

```text
meta_up_at_start=True
meta_up_at_end=True
tun_state_changed=False
```

若不一致，主分类为 `DIAG_INCONCLUSIVE`；不得开关 TUN 修正结果。

- [ ] **Step 2: 冻结 end identity**

HEAD、branch、八 blob、git status 必须与 start 一致。允许的唯一仓库新增是 `GROK_DIAGNOSIS_16.md`，但该报告在 evidence 完成后写入，因此 end status 应明确其写入顺序和允许范围。

- [ ] **Step 3: 生成 manifest**

在 leak-scan 前，对当时所有 evidence 文件（排除 manifest 自身和尚未创建的 leak-scan）记录相对路径、大小、SHA-256、LastWriteTimeUtc。

- [ ] **Step 4: 最后创建 leak-scan**

必须记录：

```text
files_present_before_scan == files_scanned
prompt_body_hits=0
credential_token_cookie_header_value_hits=0
auth_config_body_hits=0
symlink_target_hits=0
evidence_root_exists=True
pass=True
```

`leak-scan.txt` 必须是 evidence 最后创建、最后修改的文件。其后不得改写任何 evidence。

- [ ] **Step 5: 写唯一仓库报告**

`GROK_DIAGNOSIS_16.md` 至少包含：

- RUN_ID、持久 evidence、已删除 runtime、时间窗；
- 唯一诊断分类及证据链；
- TUN start/end 一致且只观察；
- fixed native 路径/版本/SHA 与实际 child binary；
- server/foreground host/C/runner/App Server 时间线；
- 约 1 秒 spawn 窗口的四类断点结论；
- C 真实 exit/timeout/sentinel/240 秒 watchdog；
- cleanup、manifest、leak-scan；
- 没有修改源码、tests、政策、配置，没有重试；
- Gate 1 相对 PASS、Gate 2 r4 FAIL、不可 merge；
- 若需源码修复，明确请求 Codex 另发 Hermes 开发卡。

报告完成后只读确认 evidence 根仍存在，然后停止。

## 10. 完成标准

- [ ] 全新 RUN_ID/evidence/runtime/端口，未拼接旧 RUN。
- [ ] HEAD、八 blob、native path/SHA start=end。
- [ ] TUN start/end 原始与派生字段一致；全程只观察。
- [ ] `HARNESS_CODEX_PATH` 在产品进程启动前设置并由 runner 继承。
- [ ] 模型固定 `gpt-5.6-sol`。
- [ ] server READY+10 秒、foreground host 双 online 后才执行 C。
- [ ] 只执行一次 C；未执行 D0/D1/后五轮。
- [ ] 产品 240 秒 idle watchdog 未修改。
- [ ] 约 1 秒观察区分未 spawn、早退、存活无事件、事件 relay 丢失或可信成功。
- [ ] 业务 exit 与 cleanup 主动终止 exit 分开记录。
- [ ] 所有本 RUN PID dead、runtime 删除、端口 free、leftover=0。
- [ ] `.codex-tmp` start=end，删除动作逐目标可信。
- [ ] evidence 持久保留，manifest 校验完整，leak-scan 最后且 hits=0。
- [ ] 仓库只新增 `GROK_DIAGNOSIS_16.md`。
- [ ] 唯一分类不冒充 Gate 2 verdict。
- [ ] 未修改源码、tests、政策、STATUS、配置；未 commit/push/merge/tag。

完成后停止，交回 Codex 只读验收。
