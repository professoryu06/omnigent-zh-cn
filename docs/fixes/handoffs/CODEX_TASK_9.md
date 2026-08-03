# CODEX TASK 9 — Gate 2 AgentCenter C/E/R 实机执行

**执行者：** Grok（Gate 2 执行者；不自签 merge 许可）  
**日期：** 2026-07-29  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** Gate 1=`PASS（相对 main）`，非全仓 GREEN；Gate 2=未执行、未判定；不可 merge。  
**阶段边界：** 按修订后的 `PRE_MERGE_GATES.md` §2 先做环境 preflight；条件完整才执行一个独立 RUN_ID 的 Gate 2。不得修改源码、测试或政策。

## 1. 必读与交付

必须完整读取：

1. `docs/fixes/PRE_MERGE_GATES.md` §2及“本环境执行记录”
2. `docs/fixes/handoffs/HERMES_COMPLETION_8_POLICY_AMENDMENT.md`
3. `docs/fixes/handoffs/CODEX_TASK_8_POLICY_AMENDMENT.md`
4. `docs/fixes/handoffs/GROK_GATE2_POLICY_REVIEW.md`
5. `docs/fixes/handoffs/HERMES_REVIEW_6.md`
6. `omnigent/inner/native_prompt_delivery.py`（只读能力矩阵）
7. `omnigent/cli.py` 中 `server`、`run` 与 native dispatch（只读）

只允许在仓库中新建：

`docs/fixes/handoffs/GROK_COMPLETION_9.md`

运行时临时文件和证据必须写到仓库外：

`C:\Users\Administrator\gate2-evidence\<RUN_ID>\`

不得复用或覆盖 Gate 1 evidence、任何旧 Gate 2 run 或旧 handoff。

## 2. 固定身份与保护

- 工作树 HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- workspace blob：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model blob：`be43ec45816e8ece4192822506df8072580910e0`
- idle blob：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve blob：`6116218097f2352c467524fd0ddf0838315aa524`

开始和结束时都要记录 HEAD、四 blob、`git status --short --branch`。任何保护值变化即 `INVALID`并停止；不得修复或回滚。

## 3. 新 RUN_ID 与证据目录

在 Windows PowerShell 中创建全新证据根；不得把 secret 或 prompt 正文写入证据：

```powershell
$ErrorActionPreference = 'Stop'
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmm') + '-dc83140-grok-gate2'
$EVIDENCE_ROOT = "C:\Users\Administrator\gate2-evidence\$RUN_ID"
$INPUT_ROOT = Join-Path $env:TEMP "omnigent-gate2-input-$RUN_ID"
$DATA_ROOT = Join-Path $EVIDENCE_ROOT 'omnigent-data'
$AGENT_ROOT = Join-Path $INPUT_ROOT 'agents'
$WS_ROOT = Join-Path $EVIDENCE_ROOT 'workspaces'

if (Test-Path -LiteralPath $EVIDENCE_ROOT) { throw 'evidence root already exists' }
if (Test-Path -LiteralPath $INPUT_ROOT) { throw 'input root already exists' }
New-Item -ItemType Directory -Path $EVIDENCE_ROOT,$INPUT_ROOT,$DATA_ROOT,$AGENT_ROOT,$WS_ROOT | Out-Null
```

角色 YAML 含非空 role prompt，只能放在 `$INPUT_ROOT`，不能原样复制进 evidence。证据中仅保存脱敏配置摘要：role、harness、model、prompt chars、prompt SHA-256，不保存 prompt 字符串。

为以下六个 session 创建六个不同 workspace：

- `controller`
- `e-pos`
- `e-pos-strict`
- `e-neg-warn`
- `e-neg-strict`
- `reviewer`

每个目录写一个只属于自己的随机 sentinel 文件名；`workspace-layout.txt` 记录路径和文件名，不记录 secret。

## 4. Preflight：必须先完成，缺项立即 NOT_EXECUTED

### 4.1 候选 Omnigent CLI

优先使用当前工作树 venv 的 console script：

```powershell
$CLI = Join-Path $WORKTREE '.venv\Scripts\omnigent-zh.exe'
if (-not (Test-Path -LiteralPath $CLI)) {
  'OMNIGENT_CLI_MISSING' | Set-Content "$EVIDENCE_ROOT\preflight-verdict.txt"
}
```

若该路径不存在，只能选择一个能证明加载当前工作树源码的等价入口；必须记录绝对路径、`--version` 输出、导入的 `omnigent.__file__` 和 HEAD。不得静默使用另一份全局安装。

### 4.2 CLI、认证和模型

只记录存在性和非敏感标识：

1. `codex` 必须在 PATH 且可查询版本。
2. 从 `NATIVE_PROMPT_CAPABILITY_MATRIX` 中选择一个值为 `warn` 的**非 codex** native harness；其真实 CLI 必须在 PATH、能查询版本且已有可用认证。优先 `claude-native`，否则可用 `hermes-native`、`cursor-native`、`pi-native` 等真实可用项。
3. C/R 必须有一个真实可用的非 native harness及认证。
4. 为 codex-native、warn-only native、C/R 分别得到当前真实可用 model id；最终 YAML 必须写具体值，不得保留占位符、不得猜测。
5. credential 只写名称与 `present=true/false`；不得打印值、token、cookie、认证文件正文或完整环境。

如果缺少下列任一项，立刻判 Gate 2=`NOT_EXECUTED/未完成`并跳到§10写报告：

- 当前工作树 Omnigent CLI
- codex CLI/认证/真实 model
- 第二个 warn-only native CLI/认证/真实 model
- C/R 非 native harness/认证/真实 model

禁止用 receipt-mismatch、resume、fork codex-native 或单元测试代替第二个 warn-only native。

### 4.3 端口与遗留进程

选择一个当前空闲的 loopback 高位端口并写入 `port.txt`。记录但不得清理非本 RUN_ID 进程。

若发现与计划端口、`$DATA_ROOT`、六个 workspace 或 `$INPUT_ROOT` 绑定的既有进程，判 `INVALID`并停止。禁止 blanket `pkill`、`taskkill /IM`、`tmux kill-server`或无差别 TERM/KILL。

Preflight 总结写入 `preflight-summary.txt`，必须包含：OS、CLI绝对路径/版本、三个 harness、三个 pinned model、CLI/credential存在性布尔值、端口、HEAD、保护值和最终 `ELIGIBLE=true/false`。

## 5. 服务器启动与环境继承

只有 `ELIGIBLE=true` 才允许继续。

使用独立数据目录和显式端口启动本轮 server；记录 PID、命令摘要、启动/错误日志：

```powershell
$env:OMNIGENT_DATA_DIR = $DATA_ROOT
$SERVER_OUT = Join-Path $EVIDENCE_ROOT 'server.stdout.log'
$SERVER_ERR = Join-Path $EVIDENCE_ROOT 'server.stderr.log'
$SERVER = Start-Process -FilePath $CLI `
  -ArgumentList @('server','--host','127.0.0.1','--port',"$PORT",'--no-open') `
  -WorkingDirectory $WORKTREE -WindowStyle Hidden -PassThru `
  -RedirectStandardOutput $SERVER_OUT -RedirectStandardError $SERVER_ERR
$SERVER.Id | Set-Content "$EVIDENCE_ROOT\server.pid"
```

最多等待60秒，以端口监听和 server 日志共同确认启动。未就绪、PID提前退出或证据日志不可写 → `INVALID`；不得盲目重启或换端口拼接证据。

所有 role 命令必须显式使用同一个 `--server http://127.0.0.1:$PORT`，使每次 `run <yaml> -p ...` 启动其自己的 local runner并继承该命令启动前的 STRICT 环境。不得复用旧 host/runner。

## 6. 临时 YAML 与脱敏快照

根据 preflight 真实选择生成四份 YAML：C、E-pos（E-pos-strict可复制后改名）、E-neg、R。

硬要求：

- E-pos/E-pos-strict：`executor.type=omnigent`、`executor.config.harness=codex-native`、具体 pinned model。
- E-neg：`executor.type=omnigent`、`executor.config.harness=<真实 warn-only 非 codex native>`、具体 pinned model。
- C/R：真实非 native harness与具体 pinned model。
- C/E-positive/R 的 role prompt 非空并分别要求短 token：`CONTROLLER_OK`、`E_POS_OK`、`E_POS_STRICT_OK`、`REVIEWER_OK`。
- E-negative 的 role prompt 使用本轮唯一、不会出现在用户消息中的随机 sentinel；用户消息本身要求回复 `E_NEG_USER_OK`。这样 warning 轮可证明原始用户消息继续执行，同时不会错误期待一个已被丢弃的 role prompt 控制回复。
- 各 YAML 名称唯一；不得带 resume/fork/external session id。

把每份 YAML 转换成脱敏摘要 `agents-sanitized.txt`：只保留 name、harness、model、prompt chars、prompt SHA-256。不得把原 YAML 或 prompt 正文复制进 evidence/报告。

## 7. 六轮执行

每轮都必须：

- `Push-Location` 到该轮独立 workspace后执行；结束后恢复目录。
- 用系统超时机制限制：C/R 180秒，E-positive/negative 300秒。
- stdout、stderr和**命令本体退出码**分别冻结；若使用管道，必须单独保存 CLI exit和tee exit。
- 从实际 CLI/server/session API或日志提取 session id、workspace、harness/model；不得猜测。
- 每轮结束确认没有串入其它 workspace sentinel。

### 7.1 C 与 R

STRICT 必须未设置。分别运行：

```text
<CLI> run <controller.yaml> -p ping --server http://127.0.0.1:<PORT>
<CLI> run <reviewer.yaml>   -p ping --server http://127.0.0.1:<PORT>
```

两轮要求 CLI exit 0、真实回复分别含 `CONTROLLER_OK`/`REVIEWER_OK`、session/workspace 可追溯。

### 7.2 E-pos

启动命令前移除 `OMNIGENT_STRICT_PROMPT`，使用新的 fresh、非 fork session：

```text
<CLI> run <e-pos.yaml> -p ping --server http://127.0.0.1:<PORT>
```

要求：exit 0、真实回复 `E_POS_OK`、实际 harness/model匹配；receipt四项匹配；private config存在顶层`developer_instructions`键；日志无`not applying`；所有公开证据无 prompt 正文。

### 7.3 E-pos-strict

不得复用 E-pos。必须在**启动 CLI/runner 前**设置 `OMNIGENT_STRICT_PROMPT=1`，运行新的 fresh、非 fork session：

```text
OMNIGENT_STRICT_PROMPT=1 <CLI> run <e-pos-strict.yaml> -p ping --server http://127.0.0.1:<PORT>
```

要求：exit 0、真实回复 `E_POS_STRICT_OK`、receipt匹配、实际 harness/model匹配、无 fail-loud warning。证据必须证明 STRICT 在 runner进程启动前存在，但不得记录完整环境。

### 7.4 E-neg-warn

启动前移除 STRICT，使用新 warn-only native session：

```text
<CLI> run <e-neg.yaml> -p "Reply with the single token E_NEG_USER_OK" --server http://127.0.0.1:<PORT>
```

要求：日志出现 `not applying` 和 `chars=N`，不出现 role prompt 正文；发送给模型的用户消息仍为原始 `Reply with the single token E_NEG_USER_OK`，未拼接 role prompt。若产品允许继续，应有真实 `E_NEG_USER_OK`；若 warning 路径本身返回非零，按真实产品行为记录并由 AC-4-neg 语义判定，不得改写退出码。

### 7.5 E-neg-strict

不得复用 E-neg-warn。启动新 session/runner前设置 STRICT=1：

```text
OMNIGENT_STRICT_PROMPT=1 <CLI> run <e-neg.yaml> -p "Reply with the single token E_NEG_USER_OK" --server http://127.0.0.1:<PORT>
```

要求：在任何用户消息 RPC/注入前产生 sole error/非零退出；不得出现成功模型回复；日志只含 `chars=N`，无 role prompt正文。必须用时间序或事件证据证明失败点早于注入。

## 8. AC 证据与泄漏扫描

生成 `sessions.txt`，每轮至少一条：

```text
role=... session_id=... workspace_abs=... harness=... yaml_model=...
actual_model=... strict=0|1 cli_exit=... capture_exit=... log=...
```

生成 `ac-verdicts.txt`，逐项给出 AC-1、AC-2、AC-3、AC-4-pos、AC-4-neg、AC-5-pos、AC-5-neg、AC-6 的 `PASS/FAIL/INVALID/NOT_EXECUTED` 和证据文件名。

泄漏扫描必须覆盖 server日志、六轮日志、sessions、receipt副本、config摘要和最终报告草稿：

- prompt 正文命中数必须为0。
- credential/token/cookie值命中数必须为0。
- 允许保留 prompt chars、SHA-256、harness、model、session id、workspace、退出码。

不得把真实 private `config.toml` 整份复制到 evidence。receipt只能复制固定四字段；任何额外字段先停止并判 `INVALID`，不得自行删除后冒充原始证据。

## 9. 清理

无论最终结果为何，只能清理由本 RUN_ID 精确记录的 PID/子进程：

1. 先正常请求停止/关闭本轮 sessions。
2. 再停止 `$SERVER.Id`；不得使用进程名批量清理。
3. 对每个待处理 PID核对 start time、命令、端口、工作目录或 `$DATA_ROOT`绑定；不完全匹配则不发送信号，只在 `cleanup.txt` 报告。
4. 不得触碰旧 Gate 1 tmux、其它 Codex/Grok/Hermes 会话或用户进程。
5. `$INPUT_ROOT` 含 role prompt；确认绝对路径带本 RUN_ID 后删除。不得删除 evidence。

清理后记录端口状态和所有本轮 PID状态。若本轮进程残留且无法安全清理，最终判 `INVALID`。

## 10. 判定与完成报告

严格四态：

- `PASS`：六轮全部按要求执行，AC-1～AC-6全部PASS，证据完整可解析、无泄漏、本轮进程清理完成。
- `FAIL`：环境和证据链有效，但任一实际断言失败。
- `INVALID`：证据缺失/串轮、退出码不可信、时序不可判、保护值变化、预检后使用了错误入口、进程污染或清理不完整。
- `NOT_EXECUTED/未完成`：preflight缺 CLI、credential、真实 model或第二个 warn-only native。

写 `docs/fixes/handoffs/GROK_COMPLETION_9.md`，必须包含：

1. RUN_ID和绝对 evidence root。
2. preflight结果；只记credential存在性，不记值。
3. 六轮命令的脱敏展开式、CLI/capture退出码、session/workspace/harness/model。
4. AC逐项判定及证据索引。
5. receipt/config摘要、warning/strict时序、泄漏扫描和清理结果。
6. HEAD/四blob和最终git status。
7. 唯一最终结论：`PASS`、`FAIL`、`INVALID`或`NOT_EXECUTED`。
8. 明确 Gate 1仅为相对PASS、非全仓GREEN；不得声称可merge。

## 11. 禁止项

- 不得修改 `omnigent/`、`tests/`、`PRE_MERGE_GATES.md`、`STATUS.md`、`POST_FIX_HANDOFF_PROMPT.md`、配置、依赖、lockfile、CI、旧 handoff或Gate 1 evidence。
- 不得运行 pytest、Ruff、Gate 1或浏览器E2E；本卡只运行Gate 2真实smoke。
- 不得用单元测试、旧日志或不同RUN_ID拼接Gate 2证据。
- 不得使用 codex receipt-mismatch/resume/fork 代替warn-only native。
- 不得读取/打印secret、token、cookie、credential值或在公开证据中保存role prompt正文。
- 不得 blanket清理进程、不得触碰非本RUN_ID进程。
- 不得stage/commit/push/merge/tag、发版或编辑PR/Issue。
- 不得自行批准merge；即使Gate 2报告PASS，仍须Codex只读验收。

完成后停止并交回 Codex。不得在同一轮自行返工或另起RUN_ID；任何重跑必须由Codex另发任务卡。
