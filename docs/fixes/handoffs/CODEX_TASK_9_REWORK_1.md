# CODEX TASK 9 REWORK 1 — 单进程保活拓扑下重跑 Gate 2

**执行者：** Grok（Gate 2执行者；不自签merge许可）  
**日期：** 2026-07-30  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** Gate 1=`PASS（相对 main）`、非全仓GREEN；Gate 2=`INVALID`；不可merge。  
**严格度：** 相对严格。保留真实六轮、AC-1～AC-6、证据隔离和四态判定；允许在同一新RUN中先跑server+C，只要C成功且server持续存活，就立即完成余下五轮。  
**阶段边界：** 只执行Gate 2实机smoke；不得改源码、测试、政策或STATUS。

## 1. 上轮INVALID与本轮目标

上轮证据根：

`C:\Users\Administrator\gate2-evidence\20260729-2343-dc83140-grok-gate2\`

上轮已被Codex只读接受为`INVALID`：

- preflight `ELIGIBLE=true`；
- server曾READY，但server日志停止时间早于C命令启动；
- C在`sdk.sessions.create()`得到`ServerError`，但CLI exit为空；
- server没有对应create请求日志，无法区分进程被执行器回收、localhost代理/host拓扑问题或服务端缺陷；
- 其余五轮未运行，AC全部NOT_EXECUTED。

本轮必须解决证据拓扑，不预设源码有bug：server和六轮必须由**同一个持续存活的PowerShell驱动进程**管理，禁止把后台server跨工具调用遗留给外部执行器回收。

## 2. 必读与唯一交付

必须完整读取：

1. `docs/fixes/handoffs/GROK_COMPLETION_9.md`
2. `docs/fixes/handoffs/CODEX_TASK_9.md`
3. `docs/fixes/PRE_MERGE_GATES.md` §2
4. `docs/fixes/handoffs/HERMES_COMPLETION_8_POLICY_AMENDMENT.md`
5. `omnigent/cli.py` 的`server`/`run`路径（只读）
6. `omnigent/inner/codex_harness.py`（C/R subscription路径，只读）
7. `omnigent/inner/native_prompt_delivery.py`（能力矩阵，只读）

仓库内只允许新建：

`docs/fixes/handoffs/GROK_COMPLETION_9_REWORK_1.md`

不得修改或覆盖旧报告、旧evidence或任何其他仓库文件。

## 3. 固定身份与预期环境

开始和结束都要冻结：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- workspace blob：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model blob：`be43ec45816e8ece4192822506df8072580910e0`
- idle blob：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve blob：`6116218097f2352c467524fd0ddf0838315aa524`

预期入口和pin必须重新只读确认：

| 用途 | 固定候选 |
|---|---|
| Omnigent | `F:\codex-ai\git项目部署\tmp\omnigent-review\.venv\Scripts\omnigent-zh.exe` |
| C/R | `codex`，model=`gpt-5.6-sol`，Codex subscription auth |
| E-positive | `codex-native`，model=`gpt-5.6-sol` |
| E-negative | `claude-native`，model=`claude-opus-4-8`，Claude OAuth |

若任一CLI、认证或固定model不再可用，判`NOT_EXECUTED`并停止；不得临时换模型/harness后仍沿用同一RUN。

## 4. 全新RUN与目录隔离

在Windows PowerShell中建立：

```powershell
$ErrorActionPreference = 'Stop'
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$CLI = Join-Path $WORKTREE '.venv\Scripts\omnigent-zh.exe'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmm') + '-dc83140-grok-gate2-r1'
$EVIDENCE_ROOT = "C:\Users\Administrator\gate2-evidence\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-gate2-runtime-$RUN_ID"
$AGENT_ROOT = Join-Path $RUNTIME_ROOT 'agents'
$DATA_ROOT = Join-Path $RUNTIME_ROOT 'omnigent-data'
$WS_ROOT = Join-Path $RUNTIME_ROOT 'workspaces'

if (Test-Path -LiteralPath $EVIDENCE_ROOT) { throw 'evidence root exists' }
if (Test-Path -LiteralPath $RUNTIME_ROOT) { throw 'runtime root exists' }
New-Item -ItemType Directory -Path $EVIDENCE_ROOT,$RUNTIME_ROOT,$AGENT_ROOT,$DATA_ROOT,$WS_ROOT | Out-Null
```

`RUNTIME_ROOT`含原始YAML、数据库、artifact和可能含prompt的原始日志，**不得**放在evidence内。结束时只保留脱敏摘要和原始文件SHA-256清单，然后删除整个`RUNTIME_ROOT`。

Evidence只允许保存：

- 脱敏stdout/stderr和server/runner日志摘录；
- exit、PID、端口、session/workspace、harness/model、chars、SHA-256；
- AC判定、清理和泄漏扫描；
- 不含prompt正文或credential值的报告。

## 5. Preflight

重新执行并冻结以下只读结果：

1. `$CLI --version`，以及当前工作树`omnigent.__file__`。
2. `codex --version`、认证存在性、当前model=`gpt-5.6-sol`。
3. `claude --version`、`loggedIn=true`、当前model支持`claude-opus-4-8`。
4. 静态确认`codex`为非native subscription harness，`claude-native`能力矩阵=`warn`。
5. credential只记录`present=true/false`，不记录值。
6. 选择空闲loopback高位端口：

```powershell
$probe = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,0)
$probe.Start()
$PORT = ([Net.IPEndPoint]$probe.LocalEndpoint).Port
$probe.Stop()
```

7. 在启动任何产品进程前确认端口无监听。

设置本轮子进程的localhost直连规则：

```powershell
$env:NO_PROXY = '127.0.0.1,localhost'
$env:no_proxy = '127.0.0.1,localhost'
$env:OMNIGENT_DATA_DIR = $DATA_ROOT
```

只记录`NO_PROXY_includes_loopback=true`，不得记录其它proxy URL或credential。

Preflight任一必要项缺失 → `NOT_EXECUTED`。保护值错误、目录冲突或端口已有绑定 → `INVALID`。

## 6. 单一持久驱动进程

整个§6～§11必须在**同一次PowerShell工具调用/同一个前台脚本**中完成。禁止：

- 启动server后结束当前shell，再在另一次工具调用跑C；
- 使用会被宿主工具在调用结束时回收的跨调用后台进程；
- 重启server、换端口、另起RUN_ID后拼接。

使用`System.Diagnostics.Process`保留server对象和真实退出状态：

```powershell
$serverPsi = [Diagnostics.ProcessStartInfo]::new()
$serverPsi.FileName = $CLI
$serverPsi.WorkingDirectory = $WORKTREE
$serverPsi.UseShellExecute = $false
$serverPsi.RedirectStandardOutput = $true
$serverPsi.RedirectStandardError = $true
foreach($a in @('server','--host','127.0.0.1','--port',"$PORT",'--no-open')) {
  [void]$serverPsi.ArgumentList.Add($a)
}
$serverPsi.Environment['OMNIGENT_DATA_DIR'] = $DATA_ROOT
$serverPsi.Environment['NO_PROXY'] = '127.0.0.1,localhost'
$serverPsi.Environment['no_proxy'] = '127.0.0.1,localhost'
$server = [Diagnostics.Process]::new()
$server.StartInfo = $serverPsi
[void]$server.Start()
$serverOutTask = $server.StandardOutput.ReadToEndAsync()
$serverErrTask = $server.StandardError.ReadToEndAsync()
```

不得把raw stream直接写入evidence。先保存在内存，结束后按§12脱敏。

## 7. READY与生命周期探针

最多60秒轮询，每秒同时记录：

- `$server.HasExited`
- server PID
- loopback端口是否监听
- 无代理`GET http://127.0.0.1:$PORT/health`的HTTP状态

HTTP探针必须使用`HttpClientHandler.UseProxy=$false`，不得经过环境代理。READY要求：server未退出、端口监听、`/health`返回2xx。

READY后再连续观察10秒；每秒三项仍成立才允许C。把时间序写入`server-lifecycle.txt`。

若READY前/观察期server退出，保存真实`ExitCode`和脱敏日志，判`INVALID`并停止；不得启动C。

## 8. 可信角色进程执行器

用一个PowerShell函数运行每轮，必须使用`Diagnostics.Process`：

- 参数：role、YAML路径、workspace、用户消息、strict布尔、timeout秒。
- `UseShellExecute=false`，stdout/stderr异步读取。
- 每轮进程启动前按strict设置或删除`OMNIGENT_STRICT_PROMPT`。
- 环境固定`OMNIGENT_DATA_DIR`和NO_PROXY loopback。
- 参数固定为：`run <yaml> -p <user-message> --server http://127.0.0.1:<PORT>`。
- `WaitForExit(timeout*1000)`；正常结束后读取真实`.ExitCode`。
- 超时只kill该轮已核对的process tree并判该轮FAIL；不得批量杀进程。
- raw stdout/stderr只保存在内存；保存前按§12脱敏。

每轮开始前和结束后必须追加生命周期探针。任何时点server退出或health非2xx → 整体`INVALID`并停止，不把该轮判业务FAIL。

## 9. 临时agent与六轮

创建六个不同workspace和唯一sentinel；创建四类YAML（C、E-pos/E-pos-strict、E-neg、R）。所有YAML只放`RUNTIME_ROOT`。

配置：

- C/R：`harness=codex`、`model=gpt-5.6-sol`。
- E-pos/E-pos-strict：`type=omnigent`、`config.harness=codex-native`、`model=gpt-5.6-sol`。
- E-neg：`type=omnigent`、`config.harness=claude-native`、`model=claude-opus-4-8`。
- E-negative role prompt使用随机sentinel；用户消息为`Reply with the single token E_NEG_USER_OK`。
- 其他用户消息为`ping`，role prompt分别要求`CONTROLLER_OK`、`E_POS_OK`、`E_POS_STRICT_OK`、`REVIEWER_OK`。

顺序和条件：

1. **C**：STRICT未设置，180秒。必须exit 0、回复`CONTROLLER_OK`、session/workspace/harness/model可追溯。
2. C后server仍健康才继续。
3. **E-pos**：STRICT未设置，300秒；fresh非fork；exit 0、`E_POS_OK`、receipt四项匹配、private config含键、无warning。
4. **E-pos-strict**：新session/runner，启动前STRICT=1，300秒；exit 0、`E_POS_STRICT_OK`、receipt匹配、无warning。
5. **E-neg-warn**：新claude-native session，STRICT未设置，300秒；warning含`chars=N`、无role prompt正文、用户消息未拼接，继续时回复`E_NEG_USER_OK`。
6. **E-neg-strict**：新session/runner，启动前STRICT=1，180秒；在任何用户消息RPC/注入前sole error，无成功回复。
7. **R**：STRICT未设置，180秒；exit 0、回复`REVIEWER_OK`。

C若失败时：

- server仍健康、C exit可信、精确HTTP状态/错误体和server请求日志完整 → Gate 2=`FAIL`；
- server不健康、请求未到达、exit不可信或时序不完整 → `INVALID`。

C通过后任一业务断言失败且server健康、证据可信 → `FAIL`并停止。不得为了收集更多结果继续跑后续轮次。

## 10. Session与AC证据

每轮必须记录：

```text
role=... session_id=... workspace_abs=... harness=... yaml_model=...
actual_model=... strict=0|1 cli_exit=... timeout=false log=...
server_alive_before=true server_alive_after=true health_before=2xx health_after=2xx
```

生成`ac-verdicts.txt`，逐项判定：AC-1、AC-2、AC-3、AC-4-pos、AC-4-neg、AC-5-pos、AC-5-neg、AC-6。

不得用单元测试、resume、fork、receipt-mismatch或旧RUN证据替代任何AC。

## 11. 原始数据摘要与脱敏

在删除`RUNTIME_ROOT`前：

1. 对原始YAML、DB、artifact、server/runner日志生成`runtime-sha256-manifest.txt`（相对路径、字节数、SHA-256）。
2. 用全部五份role prompt正文和negative sentinel扫描待保存日志；记录每个raw stream的命中数。
3. 保存日志时把任何prompt正文替换为`<REDACTED_PROMPT chars=N sha256=...>`。
4. credential扫描至少覆盖：OpenAI/Anthropic key格式、JWT、Bearer、OAuth/access/refresh/id token赋值、cookie。
5. Evidence根递归扫描必须覆盖所有保存文件，而非仅顶层。
6. 任一保存文件仍含prompt正文或credential值 → `INVALID`。
7. 报告只写credential存在性布尔值。

不得把raw YAML、private config、DB、artifact、auth文件或未脱敏日志复制进evidence。

## 12. 清理

无论结论为何，都在同一驱动脚本的`finally`中：

1. 只停止本轮已记录的session/runner。
2. 若server仍活，先请求正常停止；再只针对`$server.Id`及已核对子进程处理。
3. 禁止`taskkill /IM`、blanket `pkill`、`tmux kill-server`、无差别TERM/KILL。
4. 记录所有本轮PID的start time、命令摘要、最终状态及端口状态。
5. 确认`RUNTIME_ROOT`绝对路径含本RUN_ID后递归删除；不得删除evidence或旧RUN。
6. 端口必须free，所有本轮PID必须dead；否则`INVALID`。

## 13. 四态判定

- `PASS`：六轮完成、AC-1～AC-6全部PASS、server全程健康、退出码可信、脱敏/清理完整。
- `FAIL`：环境和server健康、证据可信，但C或任一AC业务断言失败。
- `INVALID`：server生命周期、代理路由、退出码、时序、证据或清理不可信/不完整。
- `NOT_EXECUTED`：preflight时CLI、认证或固定model缺失，产品执行尚未开始。

Preflight `ELIGIBLE=true`不保证PASS；进入产品执行后出现证据/拓扑问题应判INVALID。

## 14. 完成报告

写：

`docs/fixes/handoffs/GROK_COMPLETION_9_REWORK_1.md`

必须包含：

1. 唯一结论和四态依据。
2. RUN_ID、evidence绝对路径。
3. preflight布尔结果与固定model/harness。
4. server READY观察期和每轮前后生命周期时间序。
5. 六轮命令摘要、真实exit、session/workspace/harness/model。
6. C若失败，必须给出“server健康+可信FAIL”或“拓扑/证据INVALID”的明确分界证据。
7. AC逐项判定、receipt/config摘要、warning/strict时序。
8. runtime manifest、递归泄漏扫描、清理结果。
9. HEAD/四blob、开始/结束git status。
10. Gate 1仍为相对PASS、非全仓GREEN；不得声称可merge。

## 15. 禁止项

- 不得修改`omnigent/`、`tests/`、`PRE_MERGE_GATES.md`、`STATUS.md`、`POST_FIX`、配置、依赖、CI、旧handoff或旧evidence。
- 不得运行pytest、Ruff、Gate 1或浏览器E2E。
- 不得重启server、换端口、另起RUN_ID后拼接。
- 不得使用旧日志、单元测试、receipt-mismatch、resume或fork替代真实轮次。
- 不得读取/打印credential值；不得在evidence/报告保存prompt正文。
- 不得触碰非本RUN_ID进程。
- 不得stage/commit/push/merge/tag、发版或编辑PR/Issue。
- 即使报告PASS，也不得自行批准merge；必须交回Codex只读验收。

完成后停止。任何源码问题只报告，不在本卡内修复。
