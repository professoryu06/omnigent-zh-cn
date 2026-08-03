# CODEX TASK 12 — 阶段 10后全新 Gate 2 六轮实机 RUN

> **执行者：** Grok（Gate 2执行者；不自签merge许可）  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **唯一仓库交付：** `docs/fixes/handoffs/GROK_COMPLETION_12.md`

**目标：** 在包含阶段 10 Windows workspace契约修复的当前工作树上，以全新RUN_ID和单一前台拓扑重新执行完整Gate 2六轮实机smoke，验证0202的Windows absolute workspace 400是否消失，并依据唯一证据根给出PASS/FAIL/INVALID/NOT_EXECUTED之一。

**当前状态：** HEAD=`dc83140c73ceb12fa165753c1880c19f68da86f4`；Gate 1=`PASS（相对 main）`、非全仓GREEN；Gate 2=`FAIL`，唯一正式旧结论仍来自`20260730-0202-dc83140-grok-gate2-r2`；不可merge。

---

## 1. 前置批准与不可改写事实

阶段 11 Grok静态审查结论为`approve`，Codex只读验收为`ACCEPT_APPROVE`。其含义仅为允许本卡执行全新Gate 2 RUN：

- 不表示Gate 2已经PASS；
- 不表示全仓GREEN；
- 不批准merge；
- 不消除阶段 10的证据债务。

必须保留的P2：

1. 阶段 10原始RED没有可信真实退出码。
2. Hermes的`9/43/29/17 passed`与Ruff结果不是Grok独立运行。
3. `tests/host/test_connect.py -k "stat"`仍有既有Windows tilde失败，且Hermes写出的exit 0不可信；不得称该套件GREEN。
4. route测试使用双反斜杠字面量是非阻断P2；本卡不得顺手改测试。

## 2. 必读材料

执行前完整读取：

1. `docs/fixes/handoffs/CODEX_TASK_12.md`
2. `docs/fixes/handoffs/GROK_REVIEW_11.md`
3. `docs/fixes/handoffs/CODEX_TASK_10.md`
4. `docs/fixes/handoffs/HERMES_COMPLETION_10.md`，特别是返工轮次
5. `docs/fixes/handoffs/CODEX_TASK_9_REWORK_2.md`
6. `docs/fixes/handoffs/GROK_COMPLETION_9_REWORK_2.md`
7. `docs/fixes/PRE_MERGE_GATES.md` §2
8. `omnigent/cli.py`中Gate 2所用`run/server/host status`入口（只读）
9. `omnigent/inner/native_prompt_delivery.py`能力矩阵（只读）

不得修改上述任何文件。

## 3. 固定候选身份

开始和结束均冻结：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- 阶段 10 `_workspace_validation.py` blob：`5bf5e587b9177a9ecbce572b11656edac31ea7fe`
- 阶段 10 `sessions.py` blob：`0375e5f951d82c01c9f67e8cf7b41a90aff10330`
- 阶段 10 validator测试 blob：`63291bfa4bc47c196e04a218c82b782ecb613786`
- 阶段 10 helper测试 blob：`4cae0f53cb724c991a1c502c2919e37da7b7737a`
- workspace保护 blob：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model保护 blob：`be43ec45816e8ece4192822506df8072580910e0`
- idle保护 blob：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve保护 blob：`6116218097f2352c467524fd0ddf0838315aa524`

生成：

- `identity-start.txt` / `identity-end.txt`
- `git-status-start.txt` / `git-status-end.txt`
- `candidate-source-blobs-start.txt` / `candidate-source-blobs-end.txt`
- 当前tracked diff的文件清单、patch字节数与SHA-256摘要；不得把patch正文写进evidence。

任一固定值不匹配，或开始/结束身份漂移，最终=`INVALID`；不得修树、checkout或回滚。

## 4. 全新RUN与绝对隔离

使用新RUN_ID：

```powershell
$ErrorActionPreference = 'Stop'
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$CLI = Join-Path $WORKTREE '.venv\Scripts\omnigent-zh.exe'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmm') + '-dc83140-grok-gate2-r3'
$EVIDENCE_ROOT = "C:\Users\Administrator\gate2-evidence\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-gate2-runtime-$RUN_ID"
$AGENT_ROOT = Join-Path $RUNTIME_ROOT 'agents'
$DATA_ROOT = Join-Path $RUNTIME_ROOT 'omnigent-data'
$WS_ROOT = Join-Path $RUNTIME_ROOT 'workspaces'
```

规则：

- `EVIDENCE_ROOT`、`RUNTIME_ROOT`和端口必须全新且启动前不存在/未占用。
- 新端口不得使用旧0202端口`54040`或旧0136端口`65525`。
- 禁止读取并复制0130/0134/0136/0159/0202的session、PID、端口、日志、退出码或AC文件。
- 禁止把任何旧RUN文件拼入本RUN；旧evidence只允许保持原样并作为历史对照路径写在报告中。
- raw YAML、role prompt、DB、private config、sentinel正文和原始未脱敏日志只放`RUNTIME_ROOT`。
- evidence只存脱敏日志、真实exit、生命周期、SHA-256、chars、session映射和AC判定。

启动新RUN前只读枚举命令行包含旧RUN_ID、`54040`、`65525`或对应旧runtime的非shell进程。若存在疑似旧残留，停止并判`INVALID_PRECHECK`；本卡不得清理旧RUN、批量kill或借清理后继续。

## 5. Preflight与固定pin

重新确认，不得直接继承0202结论：

| 用途 | harness | model | auth |
|---|---|---|---|
| C/R | `codex`（非native） | `gpt-5.6-sol` | Codex subscription present |
| E-pos/E-pos-strict | `codex-native` | `gpt-5.6-sol` | Codex subscription present |
| E-neg-warn/E-neg-strict | `claude-native`（cap=`warn`） | `claude-opus-4-8` | Claude OAuth `loggedIn=true` |

同时确认：

- CLI必须是`$WORKTREE\.venv\Scripts\omnigent-zh.exe`，并加载当前工作树源码。
- `_workspace_validation.py`与`sessions.py`运行时来源必须指向当前工作树；记录路径和上述blob，不复制源码。
- C/R的`codex`必须确认为非native。
- E-neg必须确认为能力矩阵`warn`的非codex native。
- credential只记录存在性布尔值；不得读取、打印或保存credential值。
- 固定model不可临时替换。

若CLI/auth/model/第二个warn-only native缺失且尚未执行产品，最终=`NOT_EXECUTED`。不得降级为receipt-mismatch、resume、fork或单元测试。

所有子进程在启动前继承：

```powershell
$COMMON_ENV = @{
  'OMNIGENT_DATA_DIR' = $DATA_ROOT
  'NO_PROXY' = '127.0.0.1,localhost'
  'no_proxy' = '127.0.0.1,localhost'
  'PYTHONUTF8' = '1'
  'PYTHONIOENCODING' = 'utf-8'
}
```

evidence只记录变量名及`present=true`。

## 6. 单一前台驱动与进程所有权

Server、foreground host、六轮role与finally清理必须在**同一次PowerShell前台脚本/同一工具调用**内完成。

每个进程均以`System.Diagnostics.Process`管理并冻结：

- Process对象、PID、start time；
- PPID/子进程快照；
- 异步stdout/stderr采集；
- 真实exit code与timeout；
- 环境变量名称清单。

禁止：

- 跨工具调用遗留后台server/host；
- server或host重启；
- 换端口续跑；
- 跨RUN续session；
- detached无人管理daemon代替foreground host。

本RUN任一步失败后不得在同一证据根内“修脚本再续跑”。需要重试时停止并交回Codex另发新卡、新RUN_ID。

## 7. Server READY与10秒观察

启动：

```text
<CLI> server --host 127.0.0.1 --port <NEW_PORT> --no-open
```

使用`HttpWebRequest`且`Proxy=$null`探测`/health`。READY必须同时满足：

- server Process未退出；
- 新端口listen；
- `/health`=200；
- READY后连续`observe_1..10`每秒均为listen=true、health=200。

写`server-ready.txt`与`server-lifecycle.txt`。失败=`INVALID`，不得启动host。

## 8. Foreground host online

在同一驱动中启动：

```text
<CLI> host --server http://127.0.0.1:<NEW_PORT> --non-interactive
```

最多30秒轮询：

```text
<CLI> host status --server http://127.0.0.1:<NEW_PORT> --json
```

只有以下同时满足才允许执行C：

- foreground host Process未退出；
- server health=200；
- status JSON目标daemon `process=online`；
- server侧`host_status=online`；
- host stdout/stderr没有GBK/codec/encode错误。

写`host-start.txt`、`host-online.txt`、`host-status-online.txt`与脱敏host日志。

host未online且生命周期/exit/log可信=`FAIL`；生命周期、status JSON或exit不可信=`INVALID`。不得重启host。

## 9. 六个隔离workspace与配置

必须建立六个不同的绝对Windows workspace，每个具有唯一sentinel：

1. C
2. E-pos
3. E-pos-strict
4. E-neg-warn
5. E-neg-strict
6. R

Agent YAML和prompt只存在runtime。写`agents-sanitized.txt`，每个角色只记录：

- name
- harness
- model
- prompt chars
- prompt SHA-256
- workspace脱敏形状/摘要

不得写prompt正文。六个workspace均须是本RUN实际Windows drive-absolute路径，不能改成WSL `/mnt/...`或POSIX伪路径。

## 10. C必须先证明0202根因已跨过

执行：

```text
<CLI> run <RUNTIME>/agents/controller.yaml -p <SHORT_USER_MESSAGE> --server http://127.0.0.1:<NEW_PORT>
cwd=<RUNTIME>/workspaces/controller
STRICT=unset
timeout=180s
```

C前后均记录server health、server/host Process状态与host online。

C成功要求：

- CLI真实exit=0、timeout=false；
- 返回`CONTROLLER_OK`；
- session_id可确定；
- server与foreground host前后健康；
- runner实际启动；
- stderr/error体中**不存在**：

```text
workspace must be an absolute path starting with /
```

同时生成`c-workspace-contract.txt`：仅记录workspace为Windows drive-absolute、是否单分隔符形状、路径chars/SHA-256及旧0202错误命中数；不得把prompt正文放入。

判定：

- 若生命周期和exit可信，但仍出现旧400或任何新的runner launch 400：记录完整脱敏错误体与新错误分类，最终=`FAIL`并停止余下五轮。
- 若C为其它业务断言失败且生命周期/exit可信：`FAIL`并停止。
- 若server/host死亡、exit不可信、错误体截断或session映射不可信：`INVALID`。
- 只有C全部成功才可继续E-pos。

不得因阶段 10静态approve预设C会通过。

## 11. 后续五轮顺序与断言

每轮使用新workspace、新session；每轮前后均冻结server health、foreground host online和Process状态。生命周期异常=`INVALID`；生命周期健康但业务断言失败=`FAIL`并停止。

### 11.1 E-pos

- `codex-native`
- fresh、非fork
- STRICT未设置
- timeout=300s
- receipt四项匹配：harness/channel/chars/SHA-256
- private config摘要存在`developer_instructions`键、model匹配
- 真实回复`E_POS_OK`
- 无`not applying` warning

### 11.2 E-pos-strict

- 新fresh、非fork session/runner
- 进程启动前`OMNIGENT_STRICT_PROMPT=1`
- timeout=300s
- receipt匹配且真实回复`E_POS_STRICT_OK`
- 不得复用E-pos runner后再设置STRICT

### 11.3 E-neg-warn

- 新`claude-native` session
- 启动前STRICT未设置
- timeout=300s
- warning包含`chars=N`且不含prompt正文
- 原用户消息没有拼接role prompt
- 真实回复`E_NEG_USER_OK`

### 11.4 E-neg-strict

- 新`claude-native` session/runner
- 启动前`OMNIGENT_STRICT_PROMPT=1`
- timeout=180s
- 在任何用户消息RPC/注入前返回sole error
- 无成功模型回复

### 11.5 R

- `codex`非native
- 新workspace/session
- STRICT未设置
- timeout=180s
- exit=0、timeout=false、真实回复`REVIEWER_OK`

禁止用receipt-mismatch、resume、fork、单测或旧RUN证据替代E-neg或任何轮次。

## 12. Session映射与AC判定

生成`sessions.txt`，每轮必须记录：

- role与session_id
- workspace绝对路径或可复核的脱敏映射
- sentinel SHA-256
- YAML harness/model与实际harness/model
- strict启动前状态
- CLI PID、真实exit、timeout
- server health与host online前后状态
- stdout/stderr证据文件名

生成`ac-verdicts.txt`并逐项判断：

- AC-1
- AC-2
- AC-3
- AC-4-pos
- AC-4-neg
- AC-5-pos
- AC-5-neg
- AC-6

只有六轮全部执行并满足`PRE_MERGE_GATES.md` §2，AC全部PASS，才能写Gate 2 PASS。任何未执行轮不得标PASS。

## 13. finally清理

同一前台驱动的`finally`中严格执行：

1. 停止本RUN记录的sessions/runners。
2. 正常停止foreground host；必要时只处理已核对的本RUN PID tree。
3. 正常停止server；必要时只处理已核对的本RUN PID tree。
4. 枚举命令行包含本RUN端口、RUN_ID、RUNTIME_ROOT或本RUN host id的非shell进程。
5. 确认server/host/role PID tree全部dead。
6. 确认新端口free。
7. 生成runtime相对路径、bytes、SHA-256 manifest。
8. 验证删除目标的绝对路径包含完整新RUN_ID后删除`RUNTIME_ROOT`。
9. 再次确认runtime不存在、leftover=0。

禁止blanket kill、`taskkill /IM`、按进程名批量kill、`tmux kill-server`或触碰其它URL/PID。

清理不完整将最终结论覆盖为`INVALID`，即使此前六轮或业务断言已得到其它结果。

## 14. 最终证据顺序与leak-scan

先写完：

- `identity-end.txt`
- `git-status-end.txt`
- `candidate-source-blobs-end.txt`
- `sessions.txt`
- `ac-verdicts.txt`
- `cleanup.txt`
- `runtime-sha256-manifest.txt`
- `FINAL.txt`

确认不会再修改evidence后，对当时全部文件递归扫描：

- role prompt正文与negative sentinel正文
- API key格式
- JWT/Bearer
- OAuth/access/refresh/id token值
- cookie与credential值

`leak-scan.txt`必须最后创建，并写：

```text
files_present_before_scan=N
files_scanned=N
prompt_body_hits=0
secret_pattern_hits=0
```

要求`files_present_before_scan == files_scanned`。创建`leak-scan.txt`后不得新增或修改任何evidence文件。任一命中、数量不等或顺序不可信=`INVALID`。

完成报告草稿须在写入仓库前单独扫描；只允许credential存在性布尔值、prompt chars与SHA-256。

## 15. 唯一四态

- **PASS：** preflight合格；六轮全部执行；AC-1～AC-6全部PASS；身份、生命周期、exit、session映射、清理和leak-scan完整可信。
- **FAIL：** preflight合格且产品实际执行；生命周期、exit、证据与清理可信，但host上线或任一业务/契约断言失败。
- **INVALID：** 身份漂移、拓扑/生命周期/exit/session映射不可信、跨RUN拼接、证据不完整、清理失败或leak-scan失败。
- **NOT_EXECUTED：** 必要CLI/auth/model/warn-only native在产品执行前缺失。

优先级：清理/证据不完整会把此前PASS或FAIL覆盖为INVALID。不得创造第五种模糊状态。

## 16. 完成报告

只新建：

`docs/fixes/handoffs/GROK_COMPLETION_12.md`

必须包含：

1. 唯一RUN_ID与唯一evidence根。
2. preflight、固定pin、CLI/源码身份与环境变量名称。
3. server READY+10s、foreground host双online与完整生命周期。
4. C是否消除0202旧400；若失败，记录脱敏的新错误体和四态依据。
5. 六轮session/workspace/harness/model/strict/exit/timeout与结果表。
6. AC逐项判定。
7. cleanup、runtime删除、端口释放、leftover与leak-scan数量/顺序。
8. HEAD、阶段 10四blob、四保护blob与git status前后核对。
9. 阶段 10证据债务和host tilde非GREEN风险仍被保留。
10. 唯一结论：PASS/FAIL/INVALID/NOT_EXECUTED。
11. 明确：Gate 1仍为相对main PASS、非全仓GREEN；即使本RUN Gate 2 PASS，也不得自行批准merge。

## 17. 禁止项

- 不得修改源码、tests、fixture、依赖、lockfile、CI、policy、STATUS、POST_FIX、旧handoff或旧evidence。
- 不得运行pytest、Ruff、Gate 1、全仓测试或浏览器E2E。
- 不得拼接0130/0134/0136/0159/0202或任何其它RUN。
- 不得重启server/host、换端口续跑或在同一evidence根修脚本续跑。
- 不得用单测、receipt-mismatch、resume、fork或旧evidence替代真实六轮。
- 不得保存prompt正文或credential值。
- 不得批量kill或触碰非本RUN进程。
- 不得修复审查P2、host tilde失败或本RUN发现的源码问题；只报告并停止。
- 不得checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 不得commit/push/merge/tag、发版或编辑PR/Issue。
- 不得把阶段 11 `approve`写成Gate 2 PASS或可merge。

## 18. 完成标准

本卡只有在以下全部满足时完成：

1. 使用全新RUN_ID、全新evidence/runtime/端口，未拼接任何旧RUN。
2. 当前工作树CLI与阶段 10四blob身份在开始/结束一致。
3. 单一前台驱动管理server、foreground host、六轮与finally清理。
4. server READY+10s、host process/status双online后才执行C。
5. C明确验证0202旧Windows absolute-path 400是否消失；失败时没有伪装成INVALID或PASS。
6. 只有C通过才继续并按顺序执行其余五轮；未执行轮绝不标PASS。
7. sessions与AC映射完整；真实exit和timeout独立冻结。
8. 本RUN PID dead、runtime删除、端口free、leftover=0。
9. leak-scan最后创建、计数相等、hits=0，之后未再写evidence。
10. 只新建`GROK_COMPLETION_12.md`；HEAD/保护项/旧文件未变。
11. 无commit/push/merge/tag；没有自行批准merge。

完成后停止，交回Codex只读验收。无论四态为何，不得自行重跑第二个RUN。
