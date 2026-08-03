# CODEX TASK 17 — Codex CLI 0.146.0 的 D0/D1 重新基线

> **For agentic workers:** 本卡是 Grok 只读诊断计划。必须按顺序执行；只允许一次 D0 和一次 D1，不得执行 D2，不得修改源码。

**Goal:** 在 Windows、TUN 保持用户当前开启状态的前提下，固定新安装的 native Codex CLI `0.146.0`，重新验证 D0 one-shot 与 D1 app-server 是否都能产生可信 assistant 输出，为另开一张新 CLI D2 卡建立可审计基线。

**Architecture:** 使用一个全新的 RUN_ID、持久 evidence 根和独立临时 runtime。先冻结仓库与 native 身份，再依次执行一次 D0、一次 D1；每一层只在上一层通过后启动。所有正文和凭据留在临时 runtime，evidence 只保存脱敏元数据、时间线和布尔判定。

**Tech Stack:** Windows PowerShell、native `codex.exe`、Codex CLI `exec --json`、Codex `app-server` JSON-RPC、SHA-256、脱敏 evidence。

## Global Constraints

- **执行者：** Grok（只读诊断，不是开发者，不是 Gate 审查者）。
- **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`
- **唯一仓库交付：** `docs/fixes/handoffs/GROK_DIAGNOSIS_17.md`
- **模型：** `gpt-5.6-sol`
- **固定 native：** `C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`
- **固定版本：** `codex-cli 0.146.0`
- **固定大小：** `358650672` bytes
- **固定 SHA-256：** `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb`
- **平台：** 原生 Windows PowerShell；禁止 WSL、tmux、容器或远程 Linux 代跑。
- **TUN：** 只观察 start/end；禁止开关、重启、重配或调用控制 API。
- **次数：** D0 最多一次；仅 D0 PASS 后 D1 最多一次；禁止重试。
- **禁止执行：** D2、完整 Gate 2 六轮、pytest、Ruff、Gate 1。
- **禁止修改：** `omnigent/`、`tests/`、政策、`STATUS.md`、旧 handoff、用户 Codex/代理/认证/TUN 配置。
- **禁止：** commit、push、merge、tag、PR/Issue 修改。
- **Evidence 必须持久保留，不得删除。**
- Gate 1 仍是 `PASS（相对 main）`、不是全仓 GREEN；Gate 2 r4 仍是 `FAIL`；不可 merge。

---

## 1. 卡片替代关系与必读

### Files

- Read: `docs/fixes/handoffs/CODEX_REVIEW_15.md`
- Read: `docs/fixes/handoffs/GROK_DIAGNOSIS_15.md`
- Read: `docs/fixes/handoffs/CODEX_TASK_15.md`
- Read: `docs/fixes/handoffs/CODEX_TASK_16.md`
- Read: `docs/fixes/PRE_MERGE_GATES.md`

- [ ] **Step 1: 明确旧卡失效**

`CODEX_TASK_16.md` 固定的是旧 CLI `0.144.0-alpha.4`，已被本卡取代，**不得执行**。它只作为历史计划保留，不得修改。

- [ ] **Step 2: 明确旧证据边界**

阶段 15 证明的 D0/D1 PASS 只适用于旧 native：

```text
C:\Users\Administrator\.codex\.sandbox-bin\codex.exe
codex-cli 0.144.0-alpha.4
SHA256=b88f944ef63556527caae2ad43f80b88b8be174dc09b09d9b037fc94240a0e91
```

本卡不得把阶段 15、阶段 14 或 r4 的 PID、事件、退出码、sentinel、证据文件复制或拼接成本 RUN 结果。

- [ ] **Step 3: 明确本轮停止点**

```text
identity / precheck
  → D0（新 CLI one-shot，一次）
  → 仅 D0 PASS 后执行 D1（新 CLI app-server，一次）
  → finally / cleanup
  → manifest / leak-scan
  → GROK_DIAGNOSIS_17.md
  → STOP
```

即使 D0/D1 都 PASS，本轮仍不得执行 D2。D2 必须由 Codex 验收后另发新卡。

---

## 2. 新 RUN、路径和唯一交付

### Files

- Create outside repo: `C:\Users\Administrator\omnigent-diagnostics\$RUN_ID\`
- Create outside repo: `%TEMP%\omnigent-cli0146-d0d1-$RUN_ID\`
- Create: `docs/fixes/handoffs/GROK_DIAGNOSIS_17.md`

- [ ] **Step 1: 一次性生成并冻结变量**

```powershell
$ErrorActionPreference = 'Stop'
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-dc83140-grok-cli0146-d0d1-r1'
$EVIDENCE_ROOT = "C:\Users\Administrator\omnigent-diagnostics\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-cli0146-d0d1-$RUN_ID"
$CODEX_TMP = Join-Path $WORKTREE '.codex-tmp'
$NATIVE = 'C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe'
$EXPECTED_VERSION = 'codex-cli 0.146.0'
$EXPECTED_SIZE = 358650672
$EXPECTED_SHA256 = 'bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb'
$MODEL = 'gpt-5.6-sol'
```

`EVIDENCE_ROOT` 和 `RUNTIME_ROOT` 开始时必须不存在。若已存在，分类 `DIAG_INCONCLUSIVE` 并停止，不得续写、删后重建或换后缀继续。

- [ ] **Step 2: 保留 evidence、清理 runtime**

`EVIDENCE_ROOT` 完成后必须永久保留。`RUNTIME_ROOT` 只保存本轮敏感正文和临时驱动，finally 精确删除。

- [ ] **Step 3: 限定仓库写入**

仓库中只允许新增：

```text
docs/fixes/handoffs/GROK_DIAGNOSIS_17.md
```

不得修改任何现有文件。若工作树在开始时已有其他脏文件，只记录状态，不得清理、恢复、格式化或纳入本轮修改。

---

## 3. 仓库 identity 与八个冻结 blob

### Files

- Evidence: `identity-start.txt`
- Evidence: `identity-end.txt`
- Evidence: `candidate-source-blobs-start.txt`
- Evidence: `candidate-source-blobs-end.txt`
- Evidence: `git-status-start.txt`
- Evidence: `git-status-end.txt`

- [ ] **Step 1: 冻结 start identity**

必须记录：

```text
HEAD=dc83140c73ceb12fa165753c1880c19f68da86f4
branch=docs/fix-plans-core-secondary
worktree=F:\codex-ai\git项目部署\tmp\omnigent-review
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

任一 HEAD/blob 不匹配：分类 `DIAG_INCONCLUSIVE`，进入 finally，不执行未开始的层。

- [ ] **Step 3: 冻结 end identity**

用与 start 完全相同的方法重新计算。HEAD、八个 blob 和本轮不允许修改的路径必须 start=end；否则最终覆盖为 `DIAG_INCONCLUSIVE`。

`git-status-*.txt` 只保存相对路径、状态和文件大小，不保存 diff 或正文。

---

## 4. 预检与隔离

### Files

- Evidence: `precheck-processes.txt`
- Evidence: `precheck-paths.txt`
- Evidence: `codex-tmp-start.txt`
- Evidence: `codex-tmp-end.txt`

- [ ] **Step 1: 冻结诊断驱动 self/ancestor**

记录诊断驱动及 ancestor 的 PID、PPID、进程名、创建 UTC 和排除理由：

```text
DIAG_DRIVER_SELF_OR_ANCESTOR
```

不保存完整命令行。

- [ ] **Step 2: 搜索残留**

只读搜索旧 r4、阶段 14/15/16、本 RUN 字符串、`RUNTIME_ROOT`、本 RUN private home 叶名相关的残留进程和路径。

排除已冻结的 self/ancestor 后必须是：

```text
count=0
pass=True
```

非零时只记录、不 kill，分类 `DIAG_INCONCLUSIVE`，进入 finally。

- [ ] **Step 3: 冻结 `.codex-tmp`**

开始时 `.codex-tmp` 直接子项集合必须为空。非空时不得删除，分类 `DIAG_INCONCLUSIVE` 并停止。

结束时直接子项集合必须与 start 相等。

---

## 5. 新 native 身份固定

### Files

- Evidence: `native-discovery.txt`
- Evidence: `native-codex-identity-start.txt`
- Evidence: `native-codex-identity-end.txt`
- Evidence: `d0-codex-identity.txt`
- Evidence: `d1-codex-identity.txt`

- [ ] **Step 1: 只读记录候选入口**

允许执行：

```powershell
Get-Command codex -All
where.exe codex
```

并记录 Python `shutil.which("codex")` 的脱敏结果。只保存入口类型、绝对路径、是否存在、是否为 shim、版本和 SHA；不得保存完整 PATH 或环境变量值。

- [ ] **Step 2: 只允许固定的新 native**

本轮 D0/D1 只能直接调用 `$NATIVE`，禁止调用：

- `codex.ps1`
- `codex.cmd`
- `C:\Users\Administrator\.codex\.sandbox-bin\codex.exe`
- WindowsApps 内的 Codex Desktop 资源 binary
- PATH/`which` 动态选中的其他 binary

- [ ] **Step 3: 开始前核对四项**

```text
version=codex-cli 0.146.0
size=358650672
sha256=bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb
is_cmd_bat_ps1_shim=False
```

任一不匹配：分类 `DIAG_INCONCLUSIVE`，禁止自动更新、降级、复制或替换 CLI。

- [ ] **Step 4: 结束后重新核对**

start/end 的路径、版本、大小、SHA 必须一致；D0/D1 必须记录同一路径与同一 SHA。漂移时最终覆盖为 `DIAG_INCONCLUSIVE`。

---

## 6. TUN、代理存在性与 10100 基线

### Files

- Evidence: `tun-status-start.txt`
- Evidence: `tun-status-end.txt`
- Evidence: `environment-presence.txt`
- Evidence: `loopback-10100-start.txt`
- Evidence: `loopback-10100-end.txt`

- [ ] **Step 1: 强制数组化读取 TUN start**

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
$metaUp = [bool](
  @($tunLike | Where-Object {
    $_.Name -eq 'Meta' -and $_.Status -eq 'Up'
  }).Count -gt 0
)
```

记录 UTC、adapter name/status/ifIndex、脱敏 description、默认路由 ifIndex/metric、`up_tun_like_adapter_count` 和 `meta_up`。start 必须明确 `Meta=Up`；否则分类 `DIAG_INCONCLUSIVE`，不得替用户开启 TUN。

- [ ] **Step 2: 只记录代理环境“是否存在”**

只记录以下变量是否 present，不记录值：

- `HTTP_PROXY`
- `HTTPS_PROXY`
- `ALL_PROXY`
- `NO_PROXY`
- `CODEX_HOME`
- `HARNESS_CODEX_PATH`

允许额外记录：

```text
NO_PROXY_HAS_127_0_0_1=True|False
NO_PROXY_HAS_LOCALHOST=True|False
```

- [ ] **Step 3: 只读记录 10100**

记录 `127.0.0.1:10100` start/end 是否 LISTEN；若 LISTEN，记录 owning PID、进程名、binary SHA/版本（可读时）。不保存完整命令行，不向 `/v1/responses` 主动发送 HTTP/WebSocket 请求，不启动或停止该服务。

- [ ] **Step 4: 用相同代码读取 TUN end**

必须得到一致的原始行和派生布尔：

```text
meta_up_at_start=True
meta_up_at_end=True
tun_state_changed=False
```

禁止再次出现阶段 15 的“原始 adapter=Up、派生布尔=False”矛盾。TUN 状态变化或记录矛盾时最终覆盖为 `DIAG_INCONCLUSIVE`。

---

## 7. Private CODEX_HOME 与脱敏

### Files

- Runtime: `.codex-tmp\omnigent-codex-home-d0-<8hex>`
- Runtime: `.codex-tmp\omnigent-codex-home-d1-<8hex>`
- Evidence: `d0-private-home.txt`
- Evidence: `d1-private-home.txt`
- Evidence: `prompt-summaries.txt`

- [ ] **Step 1: 为 D0/D1 创建不同 private home**

两个 home 的叶名必须全新，创建时间属于本 RUN；配置来源策略保持一致。按现有产品策略处理 `auth.json` 和 `config.toml`，但不得读取、打印或保存凭据正文、配置正文或 symlink Target。

- [ ] **Step 2: 只保存安全摘要**

Evidence 只记录 home 叶名、创建 UTC、直接文件名、文件类型、存在性、prompt chars/SHA-256 和 sentinel 命中布尔。

prompt、userMessage、assistant 正文、token、cookie、header 值、认证/config 正文只能位于临时 runtime，并在 finally 删除。

---

## 8. D0 — 新 CLI one-shot

### Files

- Evidence: `d0-command-contract.txt`
- Evidence: `d0-timeline.txt`
- Evidence: `d0-events-sanitized.txt`
- Evidence: `d0-error-sanitized.txt`
- Evidence: `d0-meta.txt`

- [ ] **Step 1: 冻结 D0 合同**

只执行一次：

```text
executable=$NATIVE
mode=exec --json
model=gpt-5.6-sol
CODEX_HOME=D0 private home
cwd=$WORKTREE
budget=120s
prompt=仅要求返回本 RUN 唯一 sentinel
```

- [ ] **Step 2: 执行并记录真实结果**

`d0-meta.txt` 至少记录：

- executable path/version/SHA
- model
- TUN start 状态
- exit
- timeout
- duration
- 首 stdout、首 JSON、首可信业务事件 UTC
- 可信 final/assistant item 是否存在
- assistant/final sentinel 是否命中
- 10100/426 或 provider error 是否出现

- [ ] **Step 3: 严格判定**

```text
D0_PASS=True
```

必须同时满足：

```text
exit=0
timeout=False
可信 JSON/事件或 final assistant 结果存在
sentinel=True
```

若不满足，分类 `DIAG_ENVIRONMENT_OR_MODEL`，进入 finally，**不得执行 D1**。

---

## 9. D1 — 新 CLI app-server

### Files

- Evidence: `d1-app-server-help-sanitized.txt`
- Evidence: `d1-protocol-steps.txt`
- Evidence: `d1-process-tree.txt`
- Evidence: `d1-timeline.txt`
- Evidence: `d1-frames-sanitized.txt`
- Evidence: `d1-stderr-sanitized.txt`
- Evidence: `d1-meta.txt`
- Evidence: `d1-10100-426-analysis.txt`

- [ ] **Step 1: 读取当前协议入口**

允许在不发起模型 turn 的前提下，对固定 `$NATIVE` 读取 `app-server --help` 和当前 CLI 提供的只读协议/schema 信息。只把脱敏后的 method、参数形状、版本和错误码写入 evidence。

不得为了适配协议而修改 Omnigent 源码、tests、用户 config 或旧诊断脚本。

- [ ] **Step 2: 冻结 D1 合同**

仅在 D0 PASS 后执行一次业务 turn：

```text
executable=与 D0 完全相同的 $NATIVE
model=gpt-5.6-sol
CODEX_HOME=D1 private home
workspace=$WORKTREE
sandbox=read-only
budget=120s
dynamic_tools=none
```

- [ ] **Step 3: 执行当前 0.146.0 协议**

必须映射并记录：

1. `initialize`
2. 当前协议要求的 initialized/ready 状态（若存在）
3. `thread/start`
4. `turn/start`
5. 属于该 turn 的 item 与 terminal frame

只保存脱敏 frame 元数据：

- UTC
- method
- response id 是否存在
- thread/turn id 的 hash
- item type/phase
- error code
- HTTP/WS 状态码
- endpoint scheme/host/port/path
- stdout/stderr 累计 bytes

- [ ] **Step 4: 严格区分 user 与 assistant**

以下永远不能计入 PASS：

- `userMessage item/completed`
- 输入 sentinel 的回显
- 只有 `turn/completed` 但没有 assistant/model item

只有真实 assistant/model item 中命中 sentinel，才允许：

```text
assistant_sentinel=True
```

- [ ] **Step 5: 分开记录业务终态和进程终态**

必须分别记录：

- `turn/completed`、`turn/failed` 或可信 provider terminal
- assistant/model item 是否存在
- assistant sentinel
- app-server 业务终态时间
- app-server 进程 exit/被诊断驱动停止/timeout

不得把 cleanup 主动停止产生的 `-1` 或其他 exit 冒充业务失败，也不得用业务 PASS 掩盖异常进程退出。

- [ ] **Step 6: 记录 10100/426**

`d1-10100-426-analysis.txt` 至少包含：

- 是否出现 `responses_websocket`
- endpoint 是否为 `ws://127.0.0.1:10100/v1/responses`
- 是否出现 HTTP/WS 426
- 是否出现 app-server `error` method
- error 与 terminal frame 的先后
- 是否存在真实 assistant/model item
- D0 是否出现相同现象
- 10100 listener 是否变化
- TUN start/end 是否一致

只写证据支持的事实，不宣称 TUN 是唯一根因。

- [ ] **Step 7: 严格判定**

`D1_PASS=True` 必须同时满足：

```text
initialize/thread/start/turn/start 可映射
收到属于该 turn 的可信 terminal
存在真实 assistant/model item
assistant_sentinel=True
无未解释 provider/protocol error
```

否则 `D1_PASS=False`。

无论 PASS/FAIL，**都不得执行 D2**。

---

## 10. 唯一诊断分类

### Files

- Evidence: `DIAGNOSIS.txt`
- Evidence: `run-summary.txt`

- [ ] **Step 1: 只选一个主分类**

| 分类 | 必要条件 |
|---|---|
| `DIAG_ENVIRONMENT_OR_MODEL` | 固定 native 不可执行，或 D0 timeout/非零/无可信结果/sentinel 未命中 |
| `DIAG_APP_SERVER_PROTOCOL` | D0 PASS，但 D1 initialize/thread/turn、事件通道、terminal 或真实 assistant 输出失败 |
| `DIAG_D1_READY_FOR_D2` | D0 PASS，且 D1 有真实 assistant/model item、assistant sentinel、可信 terminal，无未解释协议错误 |
| `DIAG_INCONCLUSIVE` | identity、native、TUN、顺序、exit、cleanup、leak-scan 或 evidence 任一不可审计 |

- [ ] **Step 2: 保持结论边界**

- `DIAG_D1_READY_FOR_D2` 只表示“新 CLI 0.146.0 在本 RUN 的 D0/D1 可用”。
- 它不表示 D2、产品路径或 Gate 2 已通过。
- 它不证明 TUN 是根因或唯一修复。
- 若 D1 失败，只报告断点，不现场修改代码或网络重试。
- 若 evidence 丢失或被污染，最终必须是 `DIAG_INCONCLUSIVE`。

---

## 11. Finally、精确清理与持久 evidence

### Files

- Evidence: `run-pids.txt`
- Evidence: `codex-tmp-before-cleanup.txt`
- Evidence: `codex-tmp-delete-actions.txt`
- Evidence: `cleanup.txt`

- [ ] **Step 1: 冻结并停止本 RUN PID tree**

记录本 RUN 创建的 D0/D1 驱动、Codex 及子进程 PID/PPID/创建 UTC。先正常停止，再只对冻结 PID tree 做必要终止。

禁止 blanket kill、按进程名批量 kill、`taskkill /IM` 或终止 Codex Desktop。

- [ ] **Step 2: 精确删除 runtime 和 private home**

只允许删除：

- 绝对路径包含完整 RUN_ID 的 `RUNTIME_ROOT`
- start 快照后新增、创建时间属于本 RUN、叶名精确属于本 RUN 的两个 private home

每个目标删除前记录：

```text
target_abs=<规范化绝对路径>
leaf=<单个叶名>
under_expected_parent=True
ownership=this_RUN
target_is_reparse=True|False
action=<逐项结果>
```

后代 reparse 只删除链接本身，不读取或跟随 Target。禁止通配符、`git clean`，不得删除 `.codex-tmp` 父目录。

- [ ] **Step 3: 核验 cleanup**

必须同时满足：

- 本 RUN PID 全部 dead
- runtime 不存在
- `.codex-tmp` end=start
- 外部 leftover=0
- TUN/10100 只观察、未操作
- evidence 根仍存在

任一不可审计，最终覆盖为 `DIAG_INCONCLUSIVE`。

---

## 12. Manifest、leak-scan 与报告顺序

### Files

- Evidence: `evidence-manifest.txt`
- Evidence: `leak-scan.txt`
- Create: `docs/fixes/handoffs/GROK_DIAGNOSIS_17.md`

- [ ] **Step 1: 生成 manifest**

对当时所有 evidence 文件记录相对路径、大小、SHA-256、LastWriteTimeUtc。manifest 不包含自身和尚未创建的 leak-scan。

- [ ] **Step 2: 最后创建 leak-scan**

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

`leak-scan.txt` 必须是 evidence 最后创建、最后修改的文件。之后不得再改写 evidence。

- [ ] **Step 3: scan 后写唯一仓库报告**

`GROK_DIAGNOSIS_17.md` 至少包含：

- RUN_ID、持久 evidence 路径、已删除 runtime、时间窗
- 唯一诊断分类
- HEAD/八 blob/native path/version/size/SHA start=end
- 预检 `count=0/pass=True`
- TUN 原始与派生 start/end 一致、全程只观察
- D0 真实 exit/timeout/assistant sentinel/结果
- D1 协议映射、真实 assistant item、assistant sentinel、terminal、进程终态
- 10100/426/error method 观测
- D2=`NOT_EXECUTED_BY_TASK_DESIGN`
- cleanup、manifest、leak-scan
- 未修改源码/tests/政策/STATUS/配置，未重试
- Gate 1 相对 PASS、Gate 2 r4 FAIL、不可 merge

报告写完后只读确认 evidence 根仍存在，然后停止。

---

## 13. 完成标准

- [ ] 使用全新 RUN_ID/evidence/runtime，未拼接旧 RUN。
- [ ] 旧 `CODEX_TASK_16.md` 未执行。
- [ ] HEAD 和八个 blob start=end。
- [ ] 预检排除 self/ancestor 后 `count=0/pass=True`。
- [ ] 固定 native 是精确的 `0.146.0` 路径、大小和 SHA，不是 shim、旧 sandbox 或 Desktop binary。
- [ ] TUN start/end 用强制数组代码记录，原始与派生字段一致；未操作 TUN。
- [ ] D0 只执行一次。
- [ ] 仅 D0 PASS 后 D1 执行一次。
- [ ] userMessage 回显未计 PASS；D1 必须有真实 assistant/model item 和 sentinel。
- [ ] D2 和完整 Gate 2 均未执行。
- [ ] 本 RUN PID dead，runtime 删除，`.codex-tmp` start=end。
- [ ] evidence 持久保留，manifest 完整，leak-scan 最后且 hits=0。
- [ ] 仓库只新增 `GROK_DIAGNOSIS_17.md`。
- [ ] 未修改源码/tests/政策/STATUS/配置；未 commit/push/merge/tag。
- [ ] 最终分类未冒充 Gate 2 verdict。

完成后停止，交回 Codex 只读验收。
