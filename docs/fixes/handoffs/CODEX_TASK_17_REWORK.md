# CODEX TASK 17 REWORK — CLI 0.146.0 D0/D1 可审计重跑

> **For agentic workers:** 本卡是 Grok 只读诊断计划。必须使用全新 RUN；只允许一次 D0 和一次 D1；任何直播证据写入失败都必须停止为 `DIAG_INCONCLUSIVE`，禁止事后重建 PASS。

**Goal:** 使用同一 native Codex CLI `0.146.0`，在一个全新 RUN 中重新取得可独立审计的 D0/D1 基线，关闭阶段 17 因 D0 流证据丢失产生的审计缺口。

**Architecture:** Windows PowerShell 只负责编排、identity、TUN 和 cleanup；D0/D1 的 stdout/stderr/JSON 流由大小写敏感的 Node 驱动实时读取。原始正文只写临时 runtime，evidence 在事件到达时增量写入脱敏元数据；只有 required-file 和 SHA 自检通过后才能写 PASS 文件。

**Tech Stack:** Windows PowerShell、Node.js `child_process.spawn(shell:false)`、native `codex.exe`、JSON/JSONL、SHA-256、持久脱敏 evidence。

## Global Constraints

- **执行者：** Grok（只读诊断，不是开发者，不是 Gate 审查者）。
- **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
- **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`
- **唯一仓库交付：** `docs/fixes/handoffs/GROK_DIAGNOSIS_17_REWORK.md`
- **模型：** `gpt-5.6-sol`
- **固定 native：** `C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`
- **固定版本：** `codex-cli 0.146.0`
- **固定大小：** `358650672` bytes
- **固定 SHA-256：** `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb`
- **平台：** 原生 Windows PowerShell + 本机 Node；禁止 WSL、tmux、容器或远程 Linux。
- **TUN：** 只观察 start/end；禁止开关、重启、重配或调用控制 API。
- **次数：** D0 最多一次；仅 D0 可审计 PASS 后 D1 最多一次；禁止重试。
- **禁止执行：** D2、完整 Gate 2、pytest、Ruff、Gate 1。
- **禁止修改：** `omnigent/`、`tests/`、政策、`STATUS.md`、旧 handoff、用户 Codex/代理/认证/TUN 配置。
- **禁止：** commit、push、merge、tag、PR/Issue 修改。
- **Evidence 必须持久保留，不得删除或事后改写。**
- Gate 1=`PASS（相对 main）`、非全仓 GREEN；Gate 2 r4=`FAIL`；不可 merge。

---

## 1. 必读、旧 RUN 边界与停止条件

### Files

- Read: `docs/fixes/handoffs/CODEX_TASK_17.md`
- Read: `docs/fixes/handoffs/GROK_DIAGNOSIS_17.md`
- Read: `docs/fixes/handoffs/CODEX_REVIEW_17.md`
- Read: `docs/fixes/handoffs/CODEX_REVIEW_15.md`

- [ ] **Step 1: 接受阶段 17 改判**

阶段 17 正式分类为：

```text
DIAG_INCONCLUSIVE
```

原因是 D0 直播结果和被引用的 `d0-pass.txt` 没有持久保留，事后重建的 meta/events/timeline 不能独立证明 D0 PASS。

- [ ] **Step 2: 禁止拼接**

不得复制、恢复、续写或引用阶段 14/15/16/17/r4 的 PID、事件、exit、sentinel 或 evidence 文件作为本 RUN 结果。

阶段 17 的 D1 虽然可信，本卡仍必须在同一个新 RUN 中重新执行 D0 和 D1；禁止“新 D0 + 旧 D1”拼接。

- [ ] **Step 3: 冻结停止条件**

```text
identity / precheck
  → D0 一次
  → D0 required evidence 自检
  → 仅可审计 D0 PASS 后 D1 一次
  → D1 required evidence 自检
  → finally / cleanup
  → manifest / leak-scan
  → GROK_DIAGNOSIS_17_REWORK.md
  → STOP
```

以下任一发生，必须停止为 `DIAG_INCONCLUSIVE`，不得补写 PASS、不得重试：

- evidence 文件首次写入失败；
- required evidence 缺失或为空；
- raw runtime 在生成脱敏 evidence 前丢失；
- Node driver 异常退出且无法冻结真实 child exit；
- identity/native/TUN 漂移；
- cleanup、manifest 或 leak-scan 不可审计。

---

## 2. 全新 RUN 和路径

### Files

- Create outside repo: `C:\Users\Administrator\omnigent-diagnostics\$RUN_ID\`
- Create outside repo: `%TEMP%\omnigent-cli0146-d0d1-rework-$RUN_ID\`
- Create: `docs/fixes/handoffs/GROK_DIAGNOSIS_17_REWORK.md`

- [ ] **Step 1: 一次性生成变量**

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-dc83140-grok-cli0146-d0d1-r2'
$EVIDENCE_ROOT = "C:\Users\Administrator\omnigent-diagnostics\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-cli0146-d0d1-rework-$RUN_ID"
$CODEX_TMP = Join-Path $WORKTREE '.codex-tmp'
$NATIVE_CODEX_EXE = 'C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe'
$EXPECTED_NATIVE_VERSION = 'codex-cli 0.146.0'
$EXPECTED_NATIVE_SIZE = 358650672
$EXPECTED_NATIVE_SHA256 = 'bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb'
$CODEX_MODEL = 'gpt-5.6-sol'
```

禁止定义只靠大小写区分的变量。特别禁止再次出现：

```text
$ev / $EV
```

本卡变量必须使用完整语义名，例如：

```text
$EVIDENCE_ROOT
$D0_EVENT_RECORDS
$D0_PROCESS_RESULT
```

- [ ] **Step 2: 确认路径全新**

`EVIDENCE_ROOT` 和 `RUNTIME_ROOT` 必须开始时不存在。若存在，停止为 `DIAG_INCONCLUSIVE`，不得删除后复用、换后缀续跑或拼接旧内容。

- [ ] **Step 3: 限定仓库写入**

仓库内只允许新增：

```text
docs/fixes/handoffs/GROK_DIAGNOSIS_17_REWORK.md
```

不得修改任何现有文件。

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

- [ ] **Step 1: 冻结仓库身份**

必须满足：

```text
HEAD=dc83140c73ceb12fa165753c1880c19f68da86f4
branch=docs/fix-plans-core-secondary
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

- [ ] **Step 3: 预检残留**

登记诊断 self/ancestor PID，并以 `DIAG_DRIVER_SELF_OR_ANCESTOR` 排除。搜索旧 RUN、本 RUN/runtime/private home 相关外部残留；排除后必须：

```text
count=0
pass=True
```

非零只记录、不 kill，进入 finally。

- [ ] **Step 4: 冻结 `.codex-tmp`**

start 直接子项集合必须为空。非空时不得删除，停止为 `DIAG_INCONCLUSIVE`。

- [ ] **Step 5: 结束复核**

HEAD、branch、八 blob、非本卡允许范围的 git status/size 必须 start=end。

---

## 4. Native、TUN 和 10100

### Files

- Evidence: `native-discovery.txt`
- Evidence: `native-codex-identity-start.txt`
- Evidence: `native-codex-identity-end.txt`
- Evidence: `tun-status-start.txt`
- Evidence: `tun-status-end.txt`
- Evidence: `environment-presence.txt`
- Evidence: `loopback-10100-start.txt`
- Evidence: `loopback-10100-end.txt`

- [ ] **Step 1: 固定 native**

开始和结束均核对：

```text
path=C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe
version=codex-cli 0.146.0
size=358650672
sha256=bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb
shim=False
```

D0/D1 只能直接调用该 exe。禁止 wrapper、旧 sandbox binary、Desktop binary 和 PATH 动态入口。任一不匹配时不得更新或替换 CLI。

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

start 必须 `Meta=Up`。end 使用同一代码，并得到：

```text
meta_up_at_start=True
meta_up_at_end=True
tun_state_changed=False
```

只观察，不得开关或重配。

- [ ] **Step 3: 记录环境存在性和 10100**

代理相关环境只记录 present 布尔，不记录值。10100 只记录 LISTEN/PID/binary 脱敏身份，不主动发送 HTTP/WS 请求，不启动或停止服务。

---

## 5. Private CODEX_HOME 与 Node 驱动

### Files

- Runtime: `d0-driver.mjs`
- Runtime: `d1-driver.mjs`
- Runtime: `d0-stdout-raw.jsonl`
- Runtime: `d0-stderr-raw.log`
- Runtime: `d1-stdout-raw.jsonl`
- Runtime: `d1-stderr-raw.log`
- Evidence: `driver-identities.txt`
- Evidence: `d0-private-home.txt`
- Evidence: `d1-private-home.txt`
- Evidence: `prompt-summaries.txt`

- [ ] **Step 1: 创建两个全新 private home**

```text
.codex-tmp\omnigent-codex-home-d0-<8hex>
.codex-tmp\omnigent-codex-home-d1-<8hex>
```

按现有产品策略处理 `auth.json` 和 `config.toml`。不得保存凭据/config 正文或 symlink Target。

- [ ] **Step 2: 使用 Node 直接 spawn**

D0/D1 驱动必须满足：

```javascript
spawn(nativePath, args, {
  shell: false,
  windowsHide: true,
  cwd: worktree,
  env: childEnvironment,
  stdio: ["pipe", "pipe", "pipe"]
})
```

禁止通过 PowerShell wrapper、`.cmd`、`.ps1` 或拼接 shell 字符串执行 native。

- [ ] **Step 3: 冻结驱动身份**

执行前记录两个 runtime driver 的：

- 绝对路径
- size
- SHA-256
- Node version
- `shell=false`
- `windowsHide=true`

不把 driver 正文复制到 evidence。

- [ ] **Step 4: 正文隔离**

raw stdout/stderr、prompt 和 assistant 正文只允许写到 `RUNTIME_ROOT`。Evidence 只保存脱敏事件类型、角色、phase、UTC、bytes、hash、exit 和 sentinel 布尔。

---

## 6. D0 — 实时持久化、禁止重建

### Files

- Evidence: `d0-codex-identity.txt`
- Evidence: `d0-command-contract.txt`
- Evidence: `d0-events-live-sanitized.jsonl`
- Evidence: `d0-process-result.txt`
- Evidence: `d0-stream-hashes.txt`
- Evidence: `d0-timeline.txt`
- Evidence: `d0-error-sanitized.txt`
- Evidence: `d0-required-files-check.txt`
- Evidence: `d0-pass.txt`

- [ ] **Step 1: 冻结 D0 合同**

```text
executable=固定 native
mode=exec --json
model=gpt-5.6-sol
CODEX_HOME=D0 private home
cwd=工作树
sandbox=read-only
budget=120s
attempt=1_of_1
```

- [ ] **Step 2: 实时捕获 stdout**

Node driver 对每一条 stdout JSONL：

1. 立即把原始行写入 runtime 的 `d0-stdout-raw.jsonl`；
2. 立即解析 JSON；
3. 立即向 evidence 的 `d0-events-live-sanitized.jsonl` append 一条脱敏记录；
4. 每条脱敏记录至少包含：

```text
ordinal
observed_utc
event_type
item_type
item_role_or_source
phase
is_user_message
is_assistant_or_final
sentinel_match
json_parse_ok
raw_line_bytes
```

不得保存 message 正文。

只有 `is_assistant_or_final=True` 的事件才允许贡献 sentinel；输入/userMessage 回显不得计入。

- [ ] **Step 3: 实时捕获 stderr**

原始 stderr 只写 runtime。Evidence 的 `d0-error-sanitized.txt` 只保存 UTC、line count、bytes、错误类别、10100/426/provider error 布尔和脱敏错误码。

- [ ] **Step 4: 冻结真实进程结果**

child `close` 后立即创建 `d0-process-result.txt`：

```text
pid
spawn_utc
close_utc
exit_code
signal
timeout
duration_ms
stdout_bytes
stderr_bytes
json_line_count
json_parse_fail_count
```

此文件必须在任何 D0 PASS 判定前存在。

- [ ] **Step 5: 冻结 raw stream hash**

在删除 runtime 前，对 raw stdout/stderr 记录：

```text
relative_runtime_name
size
sha256
```

只保存 hash/size，不保存 raw 正文到 evidence。

- [ ] **Step 6: required-file 自检**

`d0-required-files-check.txt` 必须逐项记录存在性、非空、size、SHA：

```text
d0-codex-identity.txt
d0-command-contract.txt
d0-events-live-sanitized.jsonl
d0-process-result.txt
d0-stream-hashes.txt
d0-timeline.txt
d0-error-sanitized.txt
```

同时核对：

- event ordinals 连续；
- json line count 与 process result 一致；
- 至少一个可信 final/assistant event；
- sentinel 来自该 event；
- exit=0；
- timeout=False；
- parse failures=0。

- [ ] **Step 7: 最后写 D0 判定**

只有 required-file 自检全部通过，才允许首次创建：

```text
d0-pass.txt
```

内容至少包含：

```text
D0_PASS=True
attempt=1_of_1
exit=0
timeout=False
assistant_or_final_event=True
assistant_or_final_sentinel=True
required_files_pass=True
```

`d0-pass.txt` 不得由事后回忆或控制台直播行补写。

若业务真实失败且证据完整，分类 `DIAG_ENVIRONMENT_OR_MODEL`；若 evidence 写入/自检失败，分类 `DIAG_INCONCLUSIVE`。两者都不得执行 D1。

---

## 7. D1 — 同一新 RUN 的 app-server

### Files

- Evidence: `d1-codex-identity.txt`
- Evidence: `d1-protocol-steps.txt`
- Evidence: `d1-process-tree.txt`
- Evidence: `d1-frames-live-sanitized.jsonl`
- Evidence: `d1-timeline.txt`
- Evidence: `d1-stderr-sanitized.txt`
- Evidence: `d1-process-result.txt`
- Evidence: `d1-10100-426-analysis.txt`
- Evidence: `d1-required-files-check.txt`
- Evidence: `d1-pass.txt`

- [ ] **Step 1: 只在 D0 可审计 PASS 后启动**

必须先读取并验证本 RUN 的 `d0-pass.txt` 和其引用文件 SHA。缺失或不一致时不得启动 D1。

- [ ] **Step 2: 冻结 D1 合同**

```text
executable=与 D0 相同路径/版本/SHA
model=gpt-5.6-sol
CODEX_HOME=D1 private home
workspace=工作树
sandbox=read-only
budget=120s
dynamic_tools=none
attempt=1_of_1
```

- [ ] **Step 3: 实时映射协议**

按当前 `0.146.0` 协议依次映射：

1. `initialize`
2. 当前协议要求的 initialized/ready（若存在）
3. `thread/start`
4. `turn/start`
5. 同 turn item
6. `turn/completed`、`turn/failed` 或可信 provider terminal

每个 frame 到达时立即 append 脱敏记录：

```text
ordinal
observed_utc
kind
method
response_id_present
thread_hash
turn_hash
item_type
phase
is_user_message
is_assistant_or_final
sentinel_match
error_code
http_ws_status
endpoint_scheme_host_port_path
raw_line_bytes
```

- [ ] **Step 4: 严格业务判定**

以下不能计 PASS：

- userMessage item；
- 输入 sentinel 回显；
- 只有 terminal、没有 assistant/model item；
- assistant sentinel=False；
- 未解释 provider/protocol error。

`D1_PASS=True` 必须同时满足：

```text
initialize/thread/start/turn/start 可映射
可信同 turn terminal
真实 assistant/model item
assistant_sentinel=True
无未解释 provider/protocol error
required_files_pass=True
```

- [ ] **Step 5: 分离业务和进程终态**

记录真实业务 terminal UTC，再记录进程自然 exit 或由诊断驱动停止的 exit。禁止把 cleanup 停止码冒充业务结果。

- [ ] **Step 6: required-file 自检和 D1 判定**

逐项核对 required files 的存在性、非空、size、SHA、ordinal 连续性和 frame count。

只有全部通过才允许创建 `d1-pass.txt`。任何 evidence 写入失败均为 `DIAG_INCONCLUSIVE`，禁止重建。

- [ ] **Step 7: 明确不执行 D2**

无论 D1 PASS/FAIL：

```text
D2=NOT_EXECUTED_BY_TASK_DESIGN
```

然后进入 finally。

---

## 8. 唯一分类

### Files

- Evidence: `DIAGNOSIS.txt`
- Evidence: `run-summary.txt`

- [ ] **Step 1: 只选一个**

| 分类 | 必要证据 |
|---|---|
| `DIAG_ENVIRONMENT_OR_MODEL` | D0 业务失败，且 D0 required evidence 完整可审计 |
| `DIAG_APP_SERVER_PROTOCOL` | D0 可审计 PASS，但 D1 协议/assistant/terminal 业务失败，且 D1 evidence 完整 |
| `DIAG_D1_READY_FOR_D2` | D0/D1 均有独立 pass 文件、required-file 自检和真实 assistant sentinel/terminal |
| `DIAG_INCONCLUSIVE` | 任一 evidence 写入、identity、native、TUN、exit、cleanup、manifest 或 leak-scan 不可审计 |

- [ ] **Step 2: 禁止过度结论**

- `DIAG_D1_READY_FOR_D2` 不是 Gate 2 PASS。
- 本轮没有证明 D2/r4 已修复。
- TUN 只是在本 RUN 保持开启，不能宣称唯一根因。
- 需要源码修复时只报告，交回 Codex 另发 Hermes 卡。

---

## 9. Finally、cleanup 与 evidence 顺序

### Files

- Evidence: `run-pids.txt`
- Evidence: `codex-tmp-before-cleanup.txt`
- Evidence: `codex-tmp-delete-actions.txt`
- Evidence: `codex-tmp-end.txt`
- Evidence: `cleanup.txt`
- Evidence: `evidence-manifest.txt`
- Evidence: `leak-scan.txt`

- [ ] **Step 1: 精确停止 PID**

冻结本 RUN 的 PowerShell/Node/D0/D1 子进程树。先正常停止，再只对冻结 PID tree 做必要终止。禁止按名称批量 kill 或终止 Codex Desktop。

- [ ] **Step 2: 在删除 runtime 前完成 evidence**

必须先完成：

- D0/D1 process result；
- D0/D1 raw stream size/SHA；
- required-file checks；
- 业务分类。

然后才允许精确删除 `RUNTIME_ROOT`。

- [ ] **Step 3: 精确删除 private home**

每个目标记录规范化绝对路径、单个叶名、父路径验证、this_RUN 归属、reparse 判断和逐项结果。后代 reparse 只删链接，不读取或跟随 Target。

- [ ] **Step 4: cleanup 验证**

必须满足：

- 本 RUN PID 全部 dead；
- runtime 不存在；
- `.codex-tmp` end=start；
- leftover=0；
- TUN/10100 只观察；
- evidence 根仍存在。

- [ ] **Step 5: required evidence 总检查**

在 manifest 前生成 `required-evidence-final-check.txt`，逐项列出所有任务要求的 evidence 文件存在性、非空、size 和 SHA。

任何缺失都必须把最终分类覆盖为 `DIAG_INCONCLUSIVE`；禁止补造业务 PASS 文件。

- [ ] **Step 6: manifest 和最后的 leak-scan**

Manifest 记录当时全部 evidence 的相对路径、size、SHA、mtime。

`leak-scan.txt` 必须是 evidence 最后创建、最后修改文件，并满足：

```text
files_present_before_scan == files_scanned
prompt_body_hits=0
credential_token_cookie_header_value_hits=0
auth_config_body_hits=0
symlink_target_hits=0
evidence_root_exists=True
pass=True
```

之后不得改写 evidence。

---

## 10. 唯一仓库报告

### Files

- Create: `docs/fixes/handoffs/GROK_DIAGNOSIS_17_REWORK.md`

- [ ] **Step 1: leak-scan 后写报告**

报告至少包含：

- RUN_ID、持久 evidence、已删除 runtime、时间窗；
- 唯一分类；
- HEAD/八 blob/native path/version/size/SHA start=end；
- 预检 `count=0/pass=True`；
- TUN start/end 一致且只观察；
- D0 实时事件文件、process result、stream hashes、required check、独立 pass 文件；
- D1 实时 frame、assistant item/sentinel、terminal、required check、独立 pass 文件；
- userMessage 未计 PASS；
- 10100/426/error method；
- D2 未执行；
- cleanup、manifest、leak-scan；
- 没有重建丢失的 PASS 证据；
- 未修改源码/tests/政策/STATUS/配置；
- Gate 1 相对 PASS、Gate 2 r4 FAIL、不可 merge。

写完后只读确认 evidence 根仍存在，然后停止。

---

## 11. 完成标准

- [ ] 全新 RUN_ID/evidence/runtime，未拼接旧 RUN。
- [ ] 固定同一 CLI 0.146.0 native path/size/SHA。
- [ ] HEAD、八 blob、非允许范围状态 start=end。
- [ ] 预检 `count=0/pass=True`。
- [ ] TUN start/end 原始和派生字段一致，未操作 TUN。
- [ ] D0 只执行一次，事件实时脱敏落盘。
- [ ] D0 process result、stream hash、required check 在 pass 文件之前存在。
- [ ] D0 assistant/final sentinel 来源可审计。
- [ ] 仅 D0 可审计 PASS 后 D1 执行一次。
- [ ] D1 frame 实时脱敏落盘，assistant item/sentinel/terminal 可审计。
- [ ] userMessage/输入回显未计 PASS。
- [ ] 没有事后重建 PASS，没有重试。
- [ ] D2 和完整 Gate 2 未执行。
- [ ] PID dead、runtime 删除、`.codex-tmp` start=end、leftover=0。
- [ ] required evidence final check 通过。
- [ ] evidence 持久保留，manifest 完整，leak-scan 最后且 hits=0。
- [ ] 仓库只新增 `GROK_DIAGNOSIS_17_REWORK.md`。
- [ ] 未修改源码/tests/政策/STATUS/配置；未 commit/push/merge/tag。
- [ ] 唯一分类未冒充 Gate 2 verdict。

完成后停止，交回 Codex 只读验收。
