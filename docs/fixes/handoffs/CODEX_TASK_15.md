# CODEX TASK 15 — native App Server 10100/426 可审计复诊

> **执行者：** Grok（只读诊断执行者，不是 Gate 审查者）
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
> **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`
> **唯一仓库交付：** `docs/fixes/handoffs/GROK_DIAGNOSIS_15.md`

**目标：** 在用户已开启并保持不变的 TUN 模式下，使用全新 RUN_ID 和持久保留的 evidence，重新验证同一 native Codex 的 D0 one-shot 与 D1 app-server；在 D1 中精确记录 `error + turn/completed`、无 assistant item 及 `127.0.0.1:10100/v1/responses` `426 Upgrade Required` 是否真实出现。不得执行 D2，不得修改 Omnigent 源码、用户配置或 TUN/代理状态。

**当前状态：**

- Gate 1=`PASS（相对 main）`，不是全仓 GREEN。
- Gate 2 r4=`FAIL`，仍在诊断/修复。
- `CODEX_REVIEW_14_REWORK.md`=`REJECT`：上一轮报告的 evidence 根不存在，正式分类保持 `DIAG_INCONCLUSIVE`。
- 用户已在本轮开始前手动开启 TUN；Grok 只观察，不开关、不重启、不重配 TUN。
- 本任务不是 Gate 2 verdict；不可 merge。

---

## 1. 必读

开始前完整读取：

1. `docs/fixes/handoffs/CODEX_TASK_14.md`
2. `docs/fixes/handoffs/CODEX_REVIEW_14.md`
3. `docs/fixes/handoffs/GROK_DIAGNOSIS_14_REWORK.md`
4. `docs/fixes/handoffs/CODEX_REVIEW_14_REWORK.md`
5. `docs/fixes/handoffs/GROK_COMPLETION_13.md`
6. `docs/fixes/PRE_MERGE_GATES.md` §2
7. `omnigent/inner/codex_executor.py`
   - `_find_codex_cli()`
   - `CodexExecutor.__init__()`
   - `_CodexAppServerSession.start()`
   - `_reader_loop()` / `_stderr_loop()`
   - `_CodexAppServerSession.run_turn()`

不可改写的历史：

- Gate 1 仍为相对 PASS、非全仓 GREEN。
- Gate 2 r4 永久为 FAIL。
- 阶段 14 原报告被 `CODEX_REVIEW_14.md` REJECT。
- 阶段 14 REWORK 因 evidence 丢失被 `CODEX_REVIEW_14_REWORK.md` REJECT；不能把报告文字当已验收证据。

---

## 2. 方案与停止边界

本轮只执行：

```text
身份/隔离预检
  → D0：同一 native Codex one-shot
  → 仅 D0 PASS 后执行 D1：同一 native Codex app-server
  → cleanup
  → leak-scan
  → GROK_DIAGNOSIS_15.md
```

本轮明确禁止：

- D2 Omnigent C 对照。
- 完整 Gate 2 六轮。
- pytest、Ruff、Gate 1。
- 修改源码、tests、政策、`STATUS.md` 或旧 handoff。
- 修复 `10100/426`、开关/重启/重配 TUN、修改系统代理、修改环境代理、修改认证、修改 Codex/Omnigent 配置。
- 重试 D0/D1；需要重试时停止并交回 Codex。

即使 D1 获得真实 assistant sentinel，本轮也必须停止并交回 Codex，由下一张独立任务卡决定是否运行 D2。

---

## 3. 仓库范围

不得修改：

- `omnigent/`
- `tests/`
- `docs/fixes/PRE_MERGE_GATES.md`
- `docs/fixes/STATUS.md`
- `docs/fixes/POST_FIX_HANDOFF_PROMPT.md`
- 任一旧 task、completion、review、diagnosis
- 用户 Codex/Claude 配置、认证文件或代理配置

允许在仓库外创建本 RUN 的 evidence/runtime。仓库中只允许新增：

```text
docs/fixes/handoffs/GROK_DIAGNOSIS_15.md
```

不得 commit、push、merge、tag，不得修改 PR/Issue。

---

## 4. 全新 RUN 与 evidence 保留

使用：

```powershell
$ErrorActionPreference = 'Stop'
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-dc83140-grok-appserver-426-r1'
$EVIDENCE_ROOT = "C:\Users\Administrator\omnigent-diagnostics\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-appserver-426-$RUN_ID"
$CODEX_TMP = Join-Path $WORKTREE '.codex-tmp'
$MODEL = 'gpt-5.6-sol'
```

硬约束：

1. `EVIDENCE_ROOT` 与 `RUNTIME_ROOT` 开始时必须不存在。
2. 创建后立即记录绝对路径、RUN_ID、创建 UTC。
3. 不得复制、恢复、续写或引用 `20260730-1415-...-diag`、`20260730-1452-...-diag-r2` 或 r4 evidence 内容。
4. 本轮最多一次 D0、一次 D1。
5. cleanup 只能删除 `RUNTIME_ROOT` 和本 RUN 新建的 `.codex-tmp\omnigent-codex-home-*`。
6. **不得删除 `EVIDENCE_ROOT`。** 完成报告写入后再次只读确认该目录存在；不得再修改其内容。
7. evidence 中不保存 prompt、模型回复、token、cookie、header 值、认证/config 正文或 symlink Target。

---

## 5. Identity 与八个冻结 blob

开始和结束均记录：

```text
HEAD=dc83140c73ceb12fa165753c1880c19f68da86f4
branch=docs/fix-plans-core-secondary
```

冻结文件：

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

生成：

- `identity-start.txt`
- `identity-end.txt`
- `candidate-source-blobs-start.txt`
- `candidate-source-blobs-end.txt`
- `git-status-start.txt`
- `git-status-end.txt`

`git-status-*.txt` 只记录相对路径、状态和文件大小，不保存 diff。任一 HEAD/blob/status 漂移时：

```text
DIAG_INCONCLUSIVE
```

并停止未执行层。

---

## 6. 开始预检

生成：

- `precheck-processes.txt`
- `precheck-codex-tmp.txt`
- `precheck-paths.txt`

要求：

1. 记录诊断驱动 self/ancestor PID 集合。
2. 搜索旧 r4、旧阶段 14、当前 RUN_ID、旧 runtime/端口相关进程。
3. self/ancestor 可以标为 `DIAG_DRIVER_SELF_OR_ANCESTOR` 并从残留计数排除；必须记录 PID、PPID、进程名、创建 UTC 和排除理由，不保存完整命令行。
4. 排除 self/ancestor 后必须：

```text
count=0
pass=True
```

5. 非零时只记录、不 kill，分类 `DIAG_INCONCLUSIVE`，执行 finally 后停止。
6. `.codex-tmp` 开始直接子项集合必须为空；非空时不得删除，分类 `DIAG_INCONCLUSIVE` 并停止。
7. `EVIDENCE_ROOT`、`RUNTIME_ROOT`、本 RUN private home 叶名必须是全新值。
8. 开始时记录 `TUN_USER_ENABLED=True`；若无法确认 TUN 处于用户声明的开启状态，分类 `DIAG_INCONCLUSIVE` 并停止。
9. 本 RUN 期间 TUN 状态、代理环境和系统代理必须保持不变；发现变化时分类 `DIAG_INCONCLUSIVE`。

---

## 7. Native Codex 固定

### 7.1 发现候选

只读记录以下入口，不执行模型 turn：

```powershell
Get-Command codex -All
where.exe codex
```

同时使用 Python `shutil.which("codex")` 记录默认入口。只保存：

- 入口类型
- 绝对路径
- 是否存在
- 是否可执行
- 文件 SHA-256
- `--version` 的单行脱敏结果

不保存 PATH 全量或环境变量值。

### 7.2 固定唯一 native

选择一个**实际可执行的 native `codex.exe`**，写入：

```text
native-codex-identity.txt
```

必须包含：

- `NATIVE_CODEX_PATH`
- 文件大小
- SHA-256
- 版本
- 是否为 `.cmd/.bat` shim：必须 False
- D0/D1 是否使用同一路径：必须 True

D0 和 D1 必须引用同一个绝对路径变量，不得重新 `which`、不得静默切换。开始和结束分别重新计算该文件 SHA-256；发生变化时分类 `DIAG_INCONCLUSIVE`。

若没有可执行 native，或版本/帮助命令无法执行：

```text
DIAG_ENVIRONMENT_OR_MODEL
```

完成 finally 后停止，不执行 D0/D1。

---

## 8. 环境与 10100 观察基线

生成：

- `environment-presence.txt`
- `tun-state-start.txt`
- `loopback-10100-start.txt`

只记录以下环境变量是否 present，不记录值：

- `HTTP_PROXY`
- `HTTPS_PROXY`
- `ALL_PROXY`
- `NO_PROXY`
- `CODEX_HOME`
- `HARNESS_CODEX_PATH`

额外允许记录：

- `NO_PROXY_HAS_127_0_0_1=True|False`
- `NO_PROXY_HAS_LOCALHOST=True|False`

TUN 只读快照记录：

- `TUN_USER_ENABLED=True`
- 当前 Up 状态的网络适配器名称、InterfaceIndex、InterfaceDescription
- IPv4/IPv6 默认路由的 InterfaceIndex、RouteMetric
- WinHTTP/system proxy 是否 configured；不记录代理凭据
- 不保存非 loopback 的完整本机 IP、DNS 查询内容或流量正文

Grok 不得调用任何 TUN 客户端控制 API，不得点击界面，不得执行 enable/disable/restart/reload，不得修改路由、DNS、WinHTTP 或系统代理。结束时以相同字段生成 `tun-state-end.txt`；start/end 的 TUN 开启状态和相关适配器必须一致。

对 `127.0.0.1:10100` 只读记录：

- 开始时是否 LISTEN
- owning PID、进程名、进程文件 SHA-256/版本（若可读）
- 不记录完整命令行
- 不主动向 `/v1/responses` 发 HTTP/WebSocket 请求

本轮不得启动、停止或修改 10100 的服务。

---

## 9. Private CODEX_HOME

D0 和 D1 使用两个不同的 private home，但创建策略一致：

```text
.codex-tmp\omnigent-codex-home-d0-<8hex>
.codex-tmp\omnigent-codex-home-d1-<8hex>
```

要求：

1. `auth.json` 只按产品策略创建链接，不读取/输出正文或 Target。
2. `config.toml` 只按产品策略复制，不读取/输出正文。
3. evidence 仅记录 home 叶名、创建 UTC、直接文件名集合、文件类型与存在性。
4. D0 与 D1 分别记录 private home 策略摘要，证明配置来源策略一致。
5. prompt 存在 runtime 中，evidence 只记录 chars、SHA-256 与 sentinel 命中布尔值。

---

## 10. D0 — 同一 native one-shot

只执行一次，固定：

- native executable：第 7 节冻结的绝对路径
- model：`gpt-5.6-sol`
- private home：D0 home
- 总预算：120 秒
- prompt：只要求返回固定 sentinel

生成：

- `d0-codex-identity.txt`
- `d0-exec-help-sanitized.txt`
- `d0-private-home.txt`
- `d0-prompt-summary.txt`
- `d0-timeline.txt`
- `d0-events-sanitized.txt`
- `d0-error-sanitized.txt`
- `d0-meta.txt`

`d0-meta.txt` 必须包含：

- executable SHA-256
- model
- `TUN_USER_ENABLED=True`
- exit
- timeout
- duration
- 首 stdout/首 JSON/首有效事件时间
- 可信最终结果存在性
- assistant/final-message sentinel 命中

D0 PASS：

```text
exit=0
timeout=False
可信 JSON/事件或最终结果存在
sentinel=True
```

若 D0 不满足，分类 `DIAG_ENVIRONMENT_OR_MODEL`，执行 finally 后停止，不执行 D1。

---

## 11. D1 — 同一 native app-server

仅 D0 PASS 后执行一次。

固定：

- 与 D0 完全相同的 native executable 路径和 SHA-256
- model：`gpt-5.6-sol`
- 新的 D1 private home
- workspace：工作树绝对路径
- sandbox：`read-only`
- 总预算：120 秒
- 不注册 dynamic tools

协议驱动必须：

1. 发送 `initialize` 并映射响应。
2. 发送 `thread/start` 并映射响应。
3. 发送 `turn/start` 并映射响应。
4. 只保存脱敏 frame 元数据：
   - UTC
   - method
   - response id 是否存在
   - turn id 哈希
   - item type/phase
   - error code
   - HTTP/WS 状态码
   - endpoint scheme/host/port/path
   - stderr/stdout 累计 bytes
5. 禁止保存 prompt、userMessage、assistant/model content 正文。
6. `userMessage item/completed` 和输入 sentinel 回显永远不得计入 PASS。
7. 等待属于该 turn 的 `turn/completed`、`turn/failed` 或可信 provider terminal。
8. 只有 assistant/model item 中命中 sentinel 才能标 `assistant_sentinel=True`。

生成：

- `d1-codex-identity.txt`
- `d1-private-home.txt`
- `d1-protocol-steps.txt`
- `d1-process-tree.txt`
- `d1-timeline.txt`
- `d1-frames-sanitized.txt`
- `d1-stderr-sanitized.txt`
- `d1-meta.txt`
- `d1-10100-426-analysis.txt`

### 11.1 `10100/426` 必须回答

`d1-10100-426-analysis.txt` 只记录布尔值和脱敏元数据：

- D1 是否出现 `responses_websocket`
- endpoint 是否为 `ws://127.0.0.1:10100/v1/responses`
- 是否出现 HTTP/WS 426
- 426 首次出现 UTC
- 426 在 initialize/thread/start/turn/start 的哪个阶段之后出现
- 同 turn 是否出现 `error`
- error 与 `turn/completed` 的时间顺序
- 是否存在 assistant/model item
- assistant sentinel 是否命中
- 10100 监听 PID 是否在 D1 时间窗变化
- D0 是否出现同类 426
- TUN start/end 是否保持开启且未变化

不得猜测 426 根因；只给证据支持的边界结论。

### 11.2 D1 结果

`D1_PASS=True` 必须同时满足：

```text
initialize/thread/start/turn/start 均可映射
收到可信 turn 终态
存在 assistant/model item
assistant_sentinel=True
无未解释 provider/protocol error
```

以下情况均为 `D1_PASS=False`：

- 只有 userMessage 回显。
- 有 `turn/completed` 但无 assistant/model item。
- `assistant_sentinel=False`。
- 有 `error + turn/completed` 且没有可信模型输出。
- timeout、进程早退、JSON 不可解析或 turn 无 frame。

**本轮无论 D1 PASS/FAIL 都不得执行 D2。**

---

## 12. 唯一诊断分类

`DIAGNOSIS.txt` 只能写一个：

| 分类 | 条件 |
|---|---|
| `DIAG_ENVIRONMENT_OR_MODEL` | 无可执行 native，或 D0 timeout/非零/无可信结果/sentinel 未命中 |
| `DIAG_APP_SERVER_PROTOCOL` | D0 PASS，但 D1 initialize/thread/turn、事件通道或真实 assistant 输出失败 |
| `DIAG_D1_READY_FOR_D2` | D0 PASS，且 D1 获得真实 assistant/model item、assistant sentinel 与可信 turn 终态 |
| `DIAG_INCONCLUSIVE` | identity、顺序、exit、时间线、cleanup、leak-scan 或 evidence 保留任一不可信 |

约束：

- `DIAG_D1_READY_FOR_D2` 不是 Gate 2 PASS，也不授权本轮执行 D2。
- `DIAG_D1_READY_FOR_D2` 只能说明“在本次 TUN 开启状态下 D1 可用”；由于上一轮 evidence 已丢失，本 RUN 不是可审计的 TUN OFF/ON A/B，不得宣称 TUN 已被证明为根因或唯一修复。
- 不得因看到 426 就直接写根因已确认。
- 不得切换模型、改变代理或拉长 timeout 后拼接证据。
- 任何 evidence 缺失或 evidence 根被删除，最终必须是 `DIAG_INCONCLUSIVE`。

---

## 13. Finally 与精确清理

无论在哪一步停止，finally 都必须执行：

1. 冻结本 RUN 创建的全部 PID。
2. 先正常停止，再只对冻结 PID tree 做必要 TERM/KILL。
3. 禁止 blanket kill、按进程名批量 kill、`taskkill /IM`、`pkill` 或 `tmux kill-server`。
4. 确认全部本 RUN PID dead。
5. 删除绝对路径且包含完整 RUN_ID 的 `RUNTIME_ROOT`。
6. 只删除 start 快照后新增、创建时间落在本 RUN 窗口、叶名精确匹配本 RUN D0/D1 home 的目录。
7. 删除前确认目标位于 `$WORKTREE\.codex-tmp` 且目标本身非 reparse。
8. 后代 reparse 只删除链接本身，不读取/跟随 Target。
9. 不删除 `.codex-tmp` 父目录。
10. 不删除或移动 `EVIDENCE_ROOT`。

生成：

- `run-pids.txt`
- `codex-tmp-start.txt`
- `codex-tmp-before-cleanup.txt`
- `codex-tmp-delete-actions.txt`
- `codex-tmp-end.txt`
- `tun-state-end.txt`
- `loopback-10100-end.txt`
- `cleanup.txt`

`cleanup.txt` 必须记录：

- 每个 PID 与 dead 结果
- runtime_deleted
- D2 port=`NOT_APPLICABLE`
- 10100 仅观察、未操作
- TUN start/end 保持开启且未操作
- leftover=0
- `.codex-tmp` start/end set_equal
- evidence_root_exists=True

清理任一项不可信时分类 `DIAG_INCONCLUSIVE`。

---

## 14. Evidence manifest 与最终 leak-scan

在 leak-scan 前生成：

```text
evidence-manifest.txt
```

包含当时除 `evidence-manifest.txt`、`leak-scan.txt` 外所有 evidence 文件的相对路径、大小、SHA-256 和 LastWriteTimeUtc。manifest 不得尝试记录自身哈希。

完成 identity end、blob end、git status end、诊断分类、cleanup 和 manifest 后，最后创建：

```text
leak-scan.txt
```

必须记录：

- `files_present_before_scan == files_scanned`
- prompt 正文 hits=0
- credential/token/cookie/header 值 hits=0
- auth/config 正文 hits=0
- symlink Target hits=0
- `evidence_root_exists=True`

`leak-scan.txt` 必须是 evidence 最后创建和最后修改的文件。创建后：

- 不得改写任何 evidence 文件。
- 不得删除或移动 evidence 根。
- 仓库报告只引用 evidence 绝对路径、RUN_ID 和摘要，不复制 evidence 正文。

计数不等、hits 非零、scan 不是最后文件或 evidence 根消失时，分类 `DIAG_INCONCLUSIVE`。

---

## 15. 完成报告

新增：

```text
docs/fixes/handoffs/GROK_DIAGNOSIS_15.md
```

至少包含：

1. 唯一 RUN_ID、evidence/runtime 和执行时间窗。
2. evidence 根在报告写入时存在的只读确认。
3. 唯一诊断分类；明确不是 Gate 2 verdict。
4. HEAD、八 blob、git status start/end。
5. 预检 self/ancestor 排除与 `count=0/pass=True`。
6. 默认 codex 入口与固定 native 的路径、版本、SHA-256；D0/D1 同一性。
7. D0 exit/timeout/final-result/sentinel。
8. D1 initialize/thread/turn、终态、assistant item、assistant sentinel、exit/timeout。
9. TUN start/end 状态一致；明确 Grok 未开关、重启或修改 TUN/代理。
10. `10100/426` 观察结果与阶段时序；不宣称未证实根因，不把“TUN 开启时恢复”写成已证明因果。
11. D2=`NOT_EXECUTED_BY_TASK_DESIGN`。
12. PID/runtime/`.codex-tmp` cleanup。
13. manifest、leak-scan 顺序、计数和 hits。
14. Gate 1 相对 PASS、非全仓 GREEN；Gate 2 r4 仍 FAIL；不可 merge。
15. 下一步只写一条：
    - `DIAG_APP_SERVER_PROTOCOL`：继续环境/CLI/代理/协议卡；
    - `DIAG_D1_READY_FOR_D2`：交回 Codex 编写独立单次 D2 + 1 秒 spawn 观测卡；
    - 其它分类：按矩阵停止并交回 Codex。

报告完成后停止。

---

## 16. 完成标准

- [ ] 只新增 `GROK_DIAGNOSIS_15.md`。
- [ ] 全新 RUN_ID/evidence/runtime；未拼接旧 RUN。
- [ ] evidence 根在最终报告完成后仍存在。
- [ ] HEAD 和八个 blob start=end。
- [ ] 预检排除 self/ancestor 后 count=0/pass=True。
- [ ] 用户已开启 TUN；Grok 全程未开关、重启或修改 TUN/代理，start/end 状态一致。
- [ ] D0/D1 使用同一 native 绝对路径和 SHA-256。
- [ ] D0 只执行一次；D0 PASS 后才执行 D1。
- [ ] D1 严格区分 userMessage 回显与 assistant/model 输出。
- [ ] 精确记录 `10100/426` 的出现、时序和边界，不猜根因。
- [ ] 若 TUN 开启状态下恢复，只陈述相关性，不宣称已证明因果。
- [ ] 本轮未执行 D2。
- [ ] 所有本 RUN PID dead，runtime 删除，`.codex-tmp` start=end。
- [ ] evidence manifest 完成。
- [ ] leak-scan 最后生成、计数相等、hits=0。
- [ ] 唯一分类符合矩阵。
- [ ] 报告明确 Gate 1 相对 PASS、Gate 2 r4 FAIL、不可 merge。
- [ ] 未 commit/push/merge/tag。

完成后停止，等待 Codex 只读验收。
