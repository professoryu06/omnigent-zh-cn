# CODEX TASK 9 REWORK 2 — UTF-8前台host拓扑下重新执行Gate 2

**执行者：** Grok（Gate 2执行者；不自签merge许可）  
**日期：** 2026-07-30  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** Gate 1=`PASS（相对 main）`、非全仓GREEN；Gate 2=`INVALID`；不可merge。  
**阶段边界：** 先精确清理0136遗留host daemon，再用全新RUN_ID在同一前台驱动中管理server、foreground host和六轮smoke。不得改源码/tests/政策/STATUS。

## 1. 已确认根因与本轮目标

0136报告的`FAIL`未被Codex接受，原因：

- runtime未删除，`cleanup-runtime-retry.txt`为`runtime_still_exists=True`；
- 验收时两个0136绑定daemon仍活：PID快照`6760`/`36016`，命令指向`http://127.0.0.1:65525`；
- 残留host日志显示tunnel反复失败：Windows GBK无法编码字符`✓`；
- leak scan只扫描20个文件，正式evidence最终为27个文件。

所以0136永久保持`INVALID`，不得通过事后清理改写成FAIL。本轮目标：

1. 精确清理旧daemon并记录，不触碰其它进程；
2. 新RUN的所有Python子进程启动前统一UTF-8；
3. 显式启动并管理foreground host，确认server侧host=`online`后才跑C；
4. C通过后直接完成余下五轮；
5. 先完成清理和所有最终文件，再执行最后一次递归泄漏扫描。

## 2. 必读与唯一仓库交付

必须完整读取：

1. `docs/fixes/handoffs/CODEX_TASK_9_REWORK_1.md`
2. `docs/fixes/handoffs/GROK_COMPLETION_9_REWORK_1.md`
3. `docs/fixes/handoffs/GROK_COMPLETION_9.md`
4. `docs/fixes/PRE_MERGE_GATES.md` §2
5. `omnigent/cli.py`第7036–7143、7882–8063行（只读）
6. `omnigent/host/connect.py`中console/online路径（只读）
7. `omnigent/inner/native_prompt_delivery.py`能力矩阵（只读）

仓库内只允许新建：

`docs/fixes/handoffs/GROK_COMPLETION_9_REWORK_2.md`

不得修改旧报告、旧evidence或任何其他仓库文件。

## 3. 固定身份与保护

开始和结束冻结：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- workspace blob：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model blob：`be43ec45816e8ece4192822506df8072580910e0`
- idle blob：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve blob：`6116218097f2352c467524fd0ddf0838315aa524`

任一不匹配即`INVALID`，不得修树或回滚。

## 4. 先精确清理0136遗留daemon

旧目标仅限：

`http://127.0.0.1:65525`

先创建新任务的外部清理记录目录：

`C:\Users\Administrator\gate2-evidence\cleanup-0136-before-rework2-<timestamp>\`

### 4.1 发现与匹配

只枚举满足全部条件的进程：

- executable为本工作树`.venv` Python或其uv Python子进程；
- command line精确包含`-m omnigent.host._daemon_entry`；
- command line精确包含`--server http://127.0.0.1:65525`。

记录PID、PPID、executable、start time和脱敏command line。不得以旧PID数字作为唯一依据；PID可能已经复用。

### 4.2 正常停止优先

先运行一次：

```powershell
& $CLI host stop --server 'http://127.0.0.1:65525' --daemon-only --force
```

记录真实exit/stdout/stderr。然后重新枚举精确匹配进程。

若仍有匹配进程，只允许对重新验证后的精确PID执行`Stop-Process -Id <exact-pid>`；等待5秒后再次检查。不得使用`taskkill /IM`、进程名批量kill或清理其它server URL。

清理完成标准：

- 精确匹配进程数=0；
- runtime残留目录可删除且已删除；
- 端口65525无监听。

任一不满足则停止，写`GROK_COMPLETION_9_REWORK_2.md`结论`INVALID_PRE_CLEANUP`；不得开始新Gate RUN。

## 5. 全新RUN与隔离目录

仅在旧daemon清理完成后创建：

```powershell
$ErrorActionPreference = 'Stop'
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$CLI = Join-Path $WORKTREE '.venv\Scripts\omnigent-zh.exe'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmm') + '-dc83140-grok-gate2-r2'
$EVIDENCE_ROOT = "C:\Users\Administrator\gate2-evidence\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-gate2-runtime-$RUN_ID"
$AGENT_ROOT = Join-Path $RUNTIME_ROOT 'agents'
$DATA_ROOT = Join-Path $RUNTIME_ROOT 'omnigent-data'
$WS_ROOT = Join-Path $RUNTIME_ROOT 'workspaces'
```

所有raw YAML、DB、artifact、private config和raw日志仅在`RUNTIME_ROOT`。Evidence只能保存脱敏摘要、退出码、PID/状态、SHA-256和AC证据。

不得复用0130/0134/0136任何文件、端口、PID、session或日志。

## 6. Preflight与固定配置

重新确认并固定：

| 用途 | harness | model | auth |
|---|---|---|---|
| C/R | `codex` | `gpt-5.6-sol` | Codex subscription |
| E-positive | `codex-native` | `gpt-5.6-sol` | Codex subscription |
| E-negative | `claude-native` | `claude-opus-4-8` | Claude OAuth |

确认工作树CLI、认证、model、能力矩阵和空闲新高位端口。任一缺失→`NOT_EXECUTED`；不得临时更换固定项。

新RUN所有子进程环境必须从启动前包含：

```powershell
$COMMON_ENV = @{
  'OMNIGENT_DATA_DIR' = $DATA_ROOT
  'NO_PROXY' = '127.0.0.1,localhost'
  'no_proxy' = '127.0.0.1,localhost'
  'PYTHONUTF8' = '1'
  'PYTHONIOENCODING' = 'utf-8'
}
```

Evidence只记录这些变量的名称及`present=true`，不得记录其它环境或credential值。

## 7. 单一前台驱动与进程所有权

Server、foreground host、六轮role和finally清理必须在**同一次PowerShell前台脚本/同一工具调用**内完成。

每个进程都用`System.Diagnostics.Process`启动，并保存：

- Process对象；
- PID、PPID/子进程快照、start time；
-异步stdout/stderr任务；
-真实exit code；
-启动环境名称清单。

禁止跨工具调用遗留后台进程，禁止server/host重启，禁止换端口后拼接。

## 8. Server READY

启动：

```text
<CLI> server --host 127.0.0.1 --port <NEW_PORT> --no-open
```

用`HttpWebRequest`且`Proxy=$null`探测`/health`。READY要求：

- server未退出；
- 端口监听；
- health=200；
- 连续观察10秒仍全部成立。

失败→`INVALID`，不得启动host。

## 9. Foreground host上线

使用第二个受驱动脚本管理的长期进程：

```text
<CLI> host --server http://127.0.0.1:<NEW_PORT> --non-interactive
```

该host进程必须继承§6全部UTF-8环境。不得依赖`run --server`临时生成无人管理的detached daemon。

最多30秒轮询：

```text
<CLI> host status --server http://127.0.0.1:<NEW_PORT> --json
```

只有同时满足才允许C：

- foreground host进程未退出；
- server health=200；
- status JSON中目标daemon process=`online`且server host status=`online`；
- host stdout/stderr不存在GBK/codec/encode错误。

host未online：

- host exit可信、UTF-8环境已确认、日志完整→`FAIL`；
- host/server生命周期、status JSON或退出码不可信→`INVALID`。

不得继续C，不得重启host。

## 10. Agent配置与六轮

使用六个独立workspace和唯一sentinel。YAML、prompt与negative sentinel只放runtime。

顺序：

1. C：`codex`，STRICT unset，180秒，要求exit0、`CONTROLLER_OK`。
2. E-pos：fresh非fork`codex-native`，STRICT unset，300秒；receipt/config/回复/无warning。
3. E-pos-strict：新session/runner，启动前STRICT=1，300秒；receipt匹配且继续成功。
4. E-neg-warn：新`claude-native`，STRICT unset，300秒；`chars=N` warning、无prompt正文、原用户消息回复`E_NEG_USER_OK`。
5. E-neg-strict：新session/runner，启动前STRICT=1，180秒；注入前sole error，无成功回复。
6. R：`codex`，STRICT unset，180秒，要求exit0、`REVIEWER_OK`。

每轮前后都要求：server health=200、foreground host online、server和host Process对象未退出。任一生命周期异常→`INVALID`。生命周期健康且业务断言失败→`FAIL`并停止。

不得用receipt-mismatch/resume/fork/单测或旧证据替代任何轮次。

## 11. AC与证据

生成`sessions.txt`，每轮记录：session id、workspace、harness、YAML/实际model、strict、真实exit、timeout、server health、host online。

生成`ac-verdicts.txt`，逐项判定AC-1、AC-2、AC-3、AC-4-pos、AC-4-neg、AC-5-pos、AC-5-neg、AC-6。

PASS只允许六轮和全部AC通过。任何未运行轮不得标PASS。

## 12. finally清理与最终四态

在同一脚本`finally`中：

1. 停止本RUN已记录sessions/runners。
2. 正常停止foreground host；若未退出，只对其已核对PID tree处理。
3. 正常停止server；若未退出，只对其已核对PID tree处理。
4. 重新枚举命令行包含新RUN端口、`RUNTIME_ROOT`或本RUN host id的进程。
5. 所有本RUN进程必须dead，新端口必须free。
6. 生成runtime相对路径/字节数/SHA-256 manifest。
7. 确认绝对路径含新RUN_ID后删除`RUNTIME_ROOT`。
8. 删除后再次验证`RUNTIME_ROOT`不存在。

若进程残留、端口占用或runtime仍存在，最终必须`INVALID`，即使此前业务断言失败。

四态：

- PASS：六轮/AC全通过且清理/证据完整。
- FAIL：生命周期和证据可信、清理完整，但host上线或业务断言失败。
- INVALID：生命周期、退出码、证据、泄漏扫描或清理不完整。
- NOT_EXECUTED：preflight缺必要CLI/auth/model且尚未执行产品。

## 13. 最终文件顺序与递归泄漏扫描

严格按以下顺序：

1. 写完identity-end、git-status-end、sessions、AC、cleanup、runtime manifest和`FINAL.txt`。
2. 确认不会再向evidence新增或修改除`leak-scan.txt`外的文件。
3. 对当前evidence全部文件递归扫描prompt正文、negative sentinel、API key/JWT/Bearer/OAuth/access/refresh/id token/cookie值。
4. `leak-scan.txt`最后创建，记录：
   - `files_present_before_scan=N`
   - `files_scanned=N`
   - `prompt_body_hits=0`
   - `secret_pattern_hits=0`
5. 创建`leak-scan.txt`后不得再写evidence文件。
6. 报告草稿在写入仓库前单独扫描；只允许credential存在性布尔值。

任一命中或数量不等→`INVALID`。

## 14. 完成报告

写`docs/fixes/handoffs/GROK_COMPLETION_9_REWORK_2.md`，包含：

- 旧0136精确清理报告路径和结果；
- 新RUN_ID和唯一evidence根；
- preflight、UTF-8环境名称、server/host生命周期；
- 六轮exit/session/workspace/harness/model；
- AC逐项判定；
- cleanup、runtime删除、最终递归泄漏扫描；
- HEAD/四blob和git status；
- 唯一四态结论。

Gate 1仍为相对PASS、非全仓GREEN。即使Gate 2 PASS也不得自行批准merge。

## 15. 禁止项

- 不得修改源码/tests/政策/STATUS/POST_FIX/依赖/CI/旧handoff/旧evidence。
- 不得运行pytest、Ruff、Gate 1或浏览器E2E。
- 不得跨RUN拼接、重启server/host或换端口续跑。
- 不得批量kill；只处理精确匹配的旧0136 daemon和新RUN自有PID tree。
- 不得读取/打印credential值或保存prompt正文。
- 不得commit/push/merge/tag、发版或编辑PR/Issue。
- 任何源码问题只报告，交Codex另卡；本卡不得修源码。

完成后停止，交回Codex只读验收。
