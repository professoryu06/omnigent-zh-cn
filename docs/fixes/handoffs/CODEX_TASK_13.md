# CODEX TASK 13 — Gate 2 r4全新六轮RUN（C可观测性与Codex home闭环）

> **执行者：** Grok（Gate 2执行者；不自签merge许可）  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **唯一仓库交付：** `docs/fixes/handoffs/GROK_COMPLETION_13.md`

**目标：** 使用全新RUN_ID重新执行完整Gate 2六轮实机smoke；在C启动前固定Windows workspace契约证据，在有界360秒内持续记录runner启动时间线，并在finally精确清理本RUN创建的runtime、进程、端口和`.codex-tmp\omnigent-codex-home-*`。

**当前状态：** Gate 1=`PASS（相对 main）`、非全仓GREEN；r3永久=`INVALID`；历史正式业务FAIL仍为0202 Windows workspace 400；Gate 2非PASS；不可merge。

---

## 1. 不可改写的历史

- 0202：生命周期与exit可信，C因`workspace must be an absolute path starting with /`判FAIL。
- r3：C在约180秒timeout，`cli_exit=-1`、session未知，判INVALID；未证明旧400消失。
- r3事后清理已验收为`ACCEPT_REWORK_CLEANUP_OK`，但不能提升r3状态。
- 阶段10/11静态approve只允许实机重跑，不代表Gate 2 PASS。

禁止读取或拼接0130/0134/0136/0159/0202/r3的任何session、PID、日志、退出码、AC或evidence文件。旧RUN只能在报告中作为历史路径和结论引用。

## 2. 必读

1. `docs/fixes/handoffs/CODEX_TASK_13.md`
2. `docs/fixes/handoffs/CODEX_TASK_12.md`
3. `docs/fixes/handoffs/GROK_COMPLETION_12.md`
4. `docs/fixes/handoffs/CODEX_TASK_12_REWORK.md`
5. `docs/fixes/handoffs/GROK_COMPLETION_12_REWORK.md`
6. `docs/fixes/handoffs/GROK_REVIEW_11.md`
7. `docs/fixes/PRE_MERGE_GATES.md` §2
8. `omnigent/inner/codex_executor.py`临时Codex home创建/清理逻辑（只读）
9. `omnigent/inner/native_prompt_delivery.py`能力矩阵（只读）

不得修改上述文件。

## 3. 固定候选身份

开始和结束冻结：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- `_workspace_validation.py`：`5bf5e587b9177a9ecbce572b11656edac31ea7fe`
- `sessions.py`：`0375e5f951d82c01c9f67e8cf7b41a90aff10330`
- validator测试：`63291bfa4bc47c196e04a218c82b782ecb613786`
- helper测试：`4cae0f53cb724c991a1c502c2919e37da7b7737a`
- workspace保护：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model保护：`be43ec45816e8ece4192822506df8072580910e0`
- idle保护：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve保护：`6116218097f2352c467524fd0ddf0838315aa524`

生成identity、git-status、candidate-source-blobs start/end。当前tracked diff只保存文件清单、bytes与SHA-256，不保存patch正文。

任一不匹配或开始/结束漂移=`INVALID`；不得修树、checkout或回滚。

## 4. 全新RUN隔离

```powershell
$ErrorActionPreference = 'Stop'
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$CLI = Join-Path $WORKTREE '.venv\Scripts\omnigent-zh.exe'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmm') + '-dc83140-grok-gate2-r4'
$EVIDENCE_ROOT = "C:\Users\Administrator\gate2-evidence\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-gate2-runtime-$RUN_ID"
$AGENT_ROOT = Join-Path $RUNTIME_ROOT 'agents'
$DATA_ROOT = Join-Path $RUNTIME_ROOT 'omnigent-data'
$WS_ROOT = Join-Path $RUNTIME_ROOT 'workspaces'
$CODEX_TMP = Join-Path $WORKTREE '.codex-tmp'
```

要求：

- RUN_ID、evidence、runtime和高位端口全新；端口不得为54040、64774或65525。
- 正式RUN开始后不得换端口、重启server/host、修脚本续跑或启动第二RUN。
- raw YAML、prompt、DB、private config、sentinel正文和未脱敏日志仅放runtime。
- evidence仅存脱敏日志、exit、生命周期、session映射、chars和SHA-256。

启动前枚举旧RUN相关非shell进程；任一命中=`INVALID_PRECHECK`，不得清理旧RUN后继续。

## 5. `.codex-tmp`开始快照

在启动任何子进程前生成`codex-tmp-start.txt`：

- `$CODEX_TMP`绝对路径及其父级归属；
- 是否存在；
- 直接子项叶名、类型、reparse布尔值、创建时间、mtime；
- 直接子项名称集合的SHA-256；
- 不读取文件内容、链接Target或credential值。

当前预期`.codex-tmp`存在且为空。若不为空，不得删除；记录现状并停止为`INVALID_PRECHECK`，由Codex判断归属。

## 6. Preflight与固定pin

重新实测：

| 用途 | harness | model | auth |
|---|---|---|---|
| C/R | `codex`非native | `gpt-5.6-sol` | Codex subscription present |
| E-pos/E-pos-strict | `codex-native` | `gpt-5.6-sol` | Codex subscription present |
| E-neg-warn/E-neg-strict | `claude-native`，cap=`warn` | `claude-opus-4-8` | Claude OAuth loggedIn |

CLI必须为工作树`.venv\Scripts\omnigent-zh.exe`并加载当前工作树源码。credential只记录存在性布尔值，model不可替换。

必要CLI/auth/model/warn-only native缺失且尚未执行产品=`NOT_EXECUTED`。

所有子进程启动前继承：

```powershell
$COMMON_ENV = @{
  'OMNIGENT_DATA_DIR' = $DATA_ROOT
  'NO_PROXY' = '127.0.0.1,localhost'
  'no_proxy' = '127.0.0.1,localhost'
  'PYTHONUTF8' = '1'
  'PYTHONIOENCODING' = 'utf-8'
}
```

只记录变量名与`present=true`。

## 7. 单一前台驱动

Server、foreground host、六轮、C观察器和finally清理必须在同一个PowerShell前台脚本/工具调用内完成。

所有长期/短期进程均用`System.Diagnostics.Process`管理，保存Process对象、PID/start time、受控stdout/stderr、真实exit/timeout和子进程快照。

禁止detached无人管理daemon、跨工具调用后台进程、blanket kill和不同RUN拼接。

## 8. Server与foreground host

Server：

```text
<CLI> server --host 127.0.0.1 --port <NEW_PORT> --no-open
```

使用`HttpWebRequest`且`Proxy=$null`。READY后连续`observe_1..10`每秒必须server未退出、port listen、health=200；否则=`INVALID`。

Host：

```text
<CLI> host --server http://127.0.0.1:<NEW_PORT> --non-interactive
```

最多30秒轮询`host status --json`。只有foreground Process未退出、server health=200、daemon `process=online`、server `host_status=online`且无codec错误，才能执行C。

host未online且exit/log可信=`FAIL`；生命周期或证据不可信=`INVALID`。不得重启。

## 9. 六个workspace与脱敏配置

建立C、E-pos、E-pos-strict、E-neg-warn、E-neg-strict、R六个不同Windows drive-absolute workspace及唯一sentinel。

`agents-sanitized.txt`只记录name、harness、model、prompt chars/SHA-256与workspace chars/SHA-256。不得保存prompt正文或credential。

## 10. C启动前强制写workspace契约

**必须在启动C进程前**生成`c-workspace-contract.txt`，不能放在exit可信检查之后。记录：

- C workspace为Windows drive-absolute：true/false；
- 使用实际单分隔符`C:\...`形状：true/false；
- drive、路径chars、SHA-256；
- runtime和workspace存在性；
- YAML/workspace路径chars与SHA-256；
- 旧0202错误预期命中数初值=0。

不得记录prompt正文；workspace可使用脱敏路径或明确受控的本RUN runtime路径。

任一workspace契约为false，不启动C，最终=`FAIL`（证据可信）或`INVALID`（证据不可信）。

## 11. C执行与360秒可观测时间线

```text
<CLI> run <RUNTIME>/agents/controller.yaml -p <SHORT_USER_MESSAGE> --server http://127.0.0.1:<NEW_PORT>
cwd=<RUNTIME>/workspaces/controller
STRICT=unset
timeout=360s
```

启动C后每10秒向`c-progress-timeline.txt`追加：

- 时间戳与elapsed；
- C Process是否退出；
- server Process/port/health；
- foreground host Process状态；
- 每30秒执行一次有界`host status --json`，记录其exit、process、host_status与sessions数量；
- C PID tree的PID/PPID/进程名和创建时间，不记录完整command line；
- server/host/C stdout/stderr累计bytes与新增脱敏进度行；
- 新发现session/runner id的脱敏值或SHA-256映射。

观察器本身不得阻塞主timeout；单次`host status`必须有短timeout，失败只记录，不重启任何进程。

C成功必须全部满足：

- exit=0、timeout=false、`CONTROLLER_OK`；
- session_id与runner映射可确定；
- server/host前后健康；
- 旧错误`workspace must be an absolute path starting with /`命中=0；
- 无其它runner launch 400。

若360秒timeout：终止并回收C的精确PID tree，保留server/host到after_c证据完成；`cli_exit=-1`、session不可信时=`INVALID`。不得仅因旧400未见而宣称修复已实机证明。

若exit/生命周期可信但出现旧400、新400或其它业务断言失败=`FAIL`并停止后五轮。只有C成功才继续。

## 12. 后五轮

每轮使用新workspace/session；每轮前后server/host必须健康。

1. E-pos：fresh非fork `codex-native`，STRICT unset，300秒；receipt四项匹配、private config摘要、`E_POS_OK`、无not-applying warning。
2. E-pos-strict：新fresh runner，启动前STRICT=1，300秒；receipt匹配并回复`E_POS_STRICT_OK`。
3. E-neg-warn：新`claude-native`，STRICT unset，300秒；warning含chars、不含正文，回复`E_NEG_USER_OK`。
4. E-neg-strict：新runner，启动前STRICT=1，180秒；任何用户消息RPC前sole error，无成功回复。
5. R：`codex`非native，新workspace/session，180秒；exit0、`REVIEWER_OK`。

生命周期/exit不可信=`INVALID`；可信业务断言失败=`FAIL`并停止。禁止receipt-mismatch、resume、fork、单测或旧RUN代替任何轮次。

## 13. Session与AC

`sessions.txt`逐轮记录role/session/workspace映射、sentinel SHA-256、YAML与实际harness/model、strict启动前状态、PID、真实exit/timeout、前后health/host online和证据文件名。

`ac-verdicts.txt`逐项记录AC-1、AC-2、AC-3、AC-4-pos、AC-4-neg、AC-5-pos、AC-5-neg、AC-6。

只有六轮全部执行且所有AC通过，才允许Gate 2 PASS。

## 14. finally：进程/runtime/端口清理

同一驱动中：

1. 停止本RUN sessions/runners。
2. 正常停止foreground host和server；必要时仅处理已冻结的本RUN PID tree。
3. 确认本RUN全部PID dead、端口free、进程命令行匹配RUN_ID/端口/runtime/host id为0。
4. 生成runtime相对路径/bytes/SHA-256 manifest。
5. 校验删除目标绝对路径包含完整RUN_ID后删除runtime。
6. 再确认runtime不存在。

清理不完整覆盖最终状态为`INVALID`。

## 15. finally：`.codex-tmp`精确闭环

停止所有本RUN进程后生成`codex-tmp-before-cleanup.txt`，与start快照比较：

- 新增直接子项必须全部匹配`omnigent-codex-home-*`；
- 每个新增项父级精确为`$CODEX_TMP`；
- 自身必须为普通目录、非reparse；
- 创建时间必须不早于本RUN开始且不晚于当前时间；
- 当前无进程引用其绝对路径或叶名。

若存在不匹配新增项，停止清理并判`INVALID`；不得扩大删除范围。

对每个已验证的本RUN Codex home：

1. 枚举所有后代但不得跟随reparse point。
2. 验证每个后代的词法绝对路径位于该精确目录下。
3. 先逐个删除reparse point本身，不记录Target。
4. 再逐个删除普通文件，不读取、hash或打印内容。
5. 再按深度从深到浅非递归删除已空普通目录。
6. 最后非递归删除该精确Codex home。

禁止删除`.codex-tmp`父目录、使用通配符删除、跟随链接Target、读取auth/config内容或使用`git clean`。

生成`codex-tmp-end.txt`：父目录仍存在，直接子项集合必须与start快照完全相同。否则最终=`INVALID`。

## 16. 最终证据与leak-scan

先完成identity/git-status/source blobs、sessions、AC、process cleanup、runtime manifest、`.codex-tmp` start/end/删除动作、`FINAL.txt`。

然后递归扫描当时evidence全部文件中的prompt正文与secret格式。`leak-scan.txt`最后创建：

```text
files_present_before_scan=N
files_scanned=N
prompt_body_hits=0
secret_pattern_hits=0
```

要求计数相等、hits=0，之后不得再写evidence。失败=`INVALID`。

## 17. 四态

- PASS：六轮与AC全部通过，身份/exit/session/清理/leak证据完整。
- FAIL：preflight合格并实际执行，生命周期/exit/证据/清理可信，但host或业务断言失败。
- INVALID：身份、timeout/exit、session映射、拓扑、证据、runtime、`.codex-tmp`闭环或leak-scan不可信/不完整。
- NOT_EXECUTED：执行产品前缺必要CLI/auth/model/warn-only native。

清理或证据失败优先覆盖为INVALID。不得创造第五种状态。

## 18. 唯一报告

只新建`docs/fixes/handoffs/GROK_COMPLETION_13.md`，必须包含：

1. RUN_ID、端口、唯一evidence根。
2. preflight与固定pin。
3. server READY+10s、host双online。
4. C启动前workspace契约和360秒时间线摘要。
5. 0202旧400是否被完整实机证据消除；“未见”不得冒充证明。
6. 六轮exit/session/workspace/harness/model/strict和AC。
7. PID/runtime/端口及`.codex-tmp`开始/结束集合、精确删除结果。
8. leak-scan顺序/计数/hits。
9. HEAD、阶段10四blob、四保护blob和git-status前后。
10. 唯一四态结论。
11. Gate 1仍为相对main PASS、非全仓GREEN；即使Gate 2 PASS也不得自行merge。

## 19. 禁止项

- 不得修改源码/tests/fixture/依赖/CI/policy/STATUS/POST_FIX/旧handoff/旧evidence。
- 不得运行pytest、Ruff、Gate 1、全仓测试或浏览器E2E。
- 不得拼接旧RUN、同根续跑、重启/换端口或启动第二RUN。
- 不得保存prompt正文、credential值、auth/config正文或reparse Target。
- 不得批量kill、删除`.codex-tmp`父目录或非本RUN文件。
- 不得commit/push/merge/tag、发版或编辑PR/Issue。

## 20. 完成标准

1. 全新RUN/evidence/runtime/端口，无旧证据拼接。
2. 身份与固定blob开始/结束匹配。
3. 单前台驱动，READY+10s、host双online后执行C。
4. `c-workspace-contract.txt`在C启动前生成。
5. C在360秒内有完整10秒时间线；timeout时正确判INVALID。
6. 只有C成功才完成后五轮；所有AC通过才PASS。
7. PID dead、runtime删除、端口free、进程匹配0。
8. `.codex-tmp`结束集合与开始集合完全一致；只精确清理本RUN新home。
9. leak-scan最后创建、计数相等、hits=0。
10. 只新建`GROK_COMPLETION_13.md`；旧文件未改。
11. 无commit/push/merge/tag，未自行批准merge。

完成后停止，交回Codex只读验收；不得自行启动第二RUN。
