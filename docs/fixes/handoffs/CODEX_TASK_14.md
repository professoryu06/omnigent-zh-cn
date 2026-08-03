# CODEX TASK 14 — Codex harness 240s idle 根因分层诊断

> **执行者：** Grok（诊断执行者，不是 Gate 审查者）
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
> **唯一仓库交付：** `docs/fixes/handoffs/GROK_DIAGNOSIS_14.md`

**目标：** 用一个全新、可清理的诊断 RUN 分层判断 Gate 2 r4 的 `codex` harness 为何在 `turn/start` 后 240 秒无事件。先验证同一 Codex CLI、同一认证和同一模型能否独立产生首响应，再验证 `codex app-server` 是否产生事件；仅在前两层可信通过时，执行一次 Omnigent C 诊断链路。不得盲目增加 watchdog，也不得把本诊断写成 Gate 2 PASS。

**当前状态：** Gate 1=`PASS（相对 main）`、非全仓 GREEN；Gate 2 r4=`FAIL`；0202 的 Windows workspace 400 在 r4 未再出现并已越过 runner launch，但 C 因 240 秒无事件失败；不可 merge。

---

## 1. 必读与不可改写历史

1. `docs/fixes/handoffs/CODEX_TASK_13.md`
2. `docs/fixes/handoffs/GROK_COMPLETION_13.md`
3. `docs/fixes/handoffs/CODEX_TASK_12.md`
4. `docs/fixes/handoffs/GROK_COMPLETION_12.md`
5. `docs/fixes/handoffs/GROK_COMPLETION_12_REWORK.md`
6. `docs/fixes/PRE_MERGE_GATES.md` §2
7. `omnigent/inner/codex_executor.py`，重点只读核对：
   - `_CodexAppServerSession.start()`：私有 `CODEX_HOME`、`codex app-server` 启动；
   - `_reader_loop()` / `_stderr_loop()`：JSONL 事件与 stderr；
   - `_CodexAppServerSession.run_turn()`：`thread/start`、`turn/start`、事件队列；
8. `omnigent/runtime/harnesses/_scaffold.py::_guarded_run_turn()`：240 秒 idle watchdog。

历史状态不得改写：

- 0202 永久是 Windows workspace 400 的历史正式 `FAIL`。
- r3 永久是 timeout/exit 不可信的 `INVALID`。
- r4 永久是 exit 可信、`run_turn` 240 秒无事件的 `FAIL`。
- r4 的 `old400=0` 只支持“旧路径误拒未复现且已越过 launch”，不等于 Gate 2 PASS。

禁止读取或拼接 0130/0134/0136/0159/0202/r3/r4 的 PID、session、stdout、退出码、AC 或 evidence 作为本诊断结果；旧报告只能作为文字对照。

---

## 2. 精确问题与诊断边界

源码静态关系已知：

- `codex` harness 不是一次性 `codex exec`，而是由 runner 启动长期 `codex app-server`。
- App Server stdout 由 `_reader_loop()` 按 JSONL 解析并进入 `_events` 队列。
- 外层 `_guarded_run_turn()` 只有收到非 heartbeat 的 `ctx.emit` 才重置 240 秒 idle deadline。
- r4 证明 server、foreground host、workspace 与 runner launch 已成立；未证明同一模型当时可达，也未证明 App Server 已产生但 Omnigent 丢失事件。

本卡只回答以下问题：

1. 同一机器、同一工作树 Codex CLI、同一认证、同一模型 `gpt-5.6-sol`，原生 one-shot 是否能在有界时间产生可信结果？
2. 同一私有 `CODEX_HOME` 策略下，原始 `codex app-server` 是否能完成 initialize/thread/turn，并产生首个 turn 事件？
3. 若前两层通过，Omnigent 单次 C 诊断是否仍出现无事件；若出现，进程树、日志与事件时间线把断点放在哪一层？

本卡不是完整 Gate 2，不执行 E-pos、E-pos-strict、E-neg-warn、E-neg-strict、R，不得生成 Gate 2 四态判定。

---

## 3. 禁止修改范围与唯一交付

不得修改：

- `omnigent/`、`tests/`；
- `docs/fixes/PRE_MERGE_GATES.md`、`STATUS.md`、`POST_FIX_HANDOFF_PROMPT.md`；
- 任一旧 task、completion、review、evidence；
- 用户 Codex/Claude 配置或认证文件。

允许在**本 RUN 外部 evidence/runtime 根**创建通用诊断脚本、日志和临时文件；不得把脚本写入仓库。仓库中只允许新增：

`docs/fixes/handoffs/GROK_DIAGNOSIS_14.md`

不得 commit/push/merge/tag，不得编辑 PR/Issue。

---

## 4. 身份冻结

开始和结束均记录并核对：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- `_workspace_validation.py`：`5bf5e587b9177a9ecbce572b11656edac31ea7fe`
- `sessions.py`：`0375e5f951d82c01c9f67e8cf7b41a90aff10330`
- validator 测试：`63291bfa4bc47c196e04a218c82b782ecb613786`
- helper 测试：`4cae0f53cb724c991a1c502c2919e37da7b7737a`
- workspace 保护：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model 保护：`be43ec45816e8ece4192822506df8072580910e0`
- idle 保护：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve 保护：`6116218097f2352c467524fd0ddf0838315aa524`

生成：

- `identity-start.txt` / `identity-end.txt`
- `git-status-start.txt` / `git-status-end.txt`
- `candidate-source-blobs-start.txt` / `candidate-source-blobs-end.txt`

git status 只记录文件名、状态和大小，不保存 patch 正文。任一身份漂移则诊断结论只能为 `DIAG_INCONCLUSIVE`，并停止后续层。

---

## 5. 全新诊断 RUN 与隔离

使用全新名称，不放入旧 Gate evidence 根：

```powershell
$ErrorActionPreference = 'Stop'
$WORKTREE = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$RUN_ID = (Get-Date -Format 'yyyyMMdd-HHmm') + '-dc83140-grok-codex-idle-diag'
$EVIDENCE_ROOT = "C:\Users\Administrator\omnigent-diagnostics\$RUN_ID"
$RUNTIME_ROOT = Join-Path $env:TEMP "omnigent-codex-idle-diag-$RUN_ID"
$CODEX_TMP = Join-Path $WORKTREE '.codex-tmp'
$MODEL = 'gpt-5.6-sol'
```

要求：

- RUN_ID、evidence、runtime、端口均全新；不得在同一 evidence 根续跑或替换结果。
- 本卡最多各执行一次 D0、D1、D2；任何重试都必须由 Codex 另发新任务卡和新 RUN_ID。
- 开始前精确检查旧 r4 PID/端口/RUN_ID 相关进程均为 0；只检查，不批量 kill。发现残留则 `DIAG_INCONCLUSIVE` 并停止。
- 子进程环境至少固定 `PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`、`NO_PROXY=127.0.0.1,localhost`；只记录变量名与是否 present，不记录敏感值。
- CLI 身份、版本、真实路径和源码加载路径必须记录；工作树 CLI 应为 `.venv\Scripts\omnigent-zh.exe`。

---

## 6. 凭据、prompt 与日志安全

1. credential 只记录存在性布尔值、登录态布尔值和认证类型；禁止打印 token、cookie、header、auth JSON、symlink Target。
2. 不得打开、解析或保存 `auth.json` 正文；只可按产品策略创建指向认证文件的链接本身。
3. `config.toml` 只可按产品策略复制到私有 home；不得把正文写入 evidence。
4. 诊断 prompt 放在 runtime 内，通过 stdin 或临时文件传入；evidence 只记录 chars、SHA-256 与固定 sentinel 命中布尔值，不保存 prompt 正文。
5. 模型输出不得原样落 evidence；只记录事件类型、时间、字节数、退出码、错误码、脱敏错误摘要和 sentinel 命中布尔值。
6. 进程证据只记录 PID、PPID、进程名、创建时间、退出状态和与本 RUN 的匹配布尔值；不得保存含 prompt/credential 的完整命令行。

---

## 7. `.codex-tmp` 开始快照

在启动任何诊断子进程前生成 `codex-tmp-start.txt`：

- `.codex-tmp` 父目录存在性；
- 直接子项的叶名、类型、创建 UTC 秒、是否 reparse；
- 不读取链接 Target；
- 不递归读取 auth/config 内容。

若开始集合非空，不得自行删除；记录并以 `DIAG_INCONCLUSIVE` 停止，交回 Codex 判定归属。

---

## 8. D0 — 原生 Codex one-shot 可达性

### 8.1 先固定 CLI 能力

只读执行 Codex CLI 的版本和帮助命令，生成：

- `d0-codex-identity.txt`
- `d0-exec-help-sanitized.txt`

帮助输出只保留可用 flag 名，不保存环境、配置或路径值。根据当前 CLI 实际帮助选择受支持的非交互 JSON/JSONL one-shot 语法；不得凭记忆使用不存在的 flag。

### 8.2 私有 home

在 `$CODEX_TMP` 下以 `omnigent-codex-home-` 加八位随机串创建唯一目录，模拟 `codex_executor.py`：

- `auth.json` 仅创建链接；
- `config.toml` 仅复制；
- 不读取或输出二者内容/Target；
- 记录 home 叶名、类型、创建时间和文件名集合，不记录正文。

### 8.3 一次有界调用

用 `gpt-5.6-sol`、当前 ChatGPT auth 和上述私有 `CODEX_HOME` 执行一次最小 one-shot：

- prompt 从 stdin/runtime 传入；要求只返回固定 sentinel；
- 总预算 120 秒；每 5 秒记录进程 alive、stdout/stderr 字节累计、CPU/IO 可读取计数；
- 保存 `d0-timeline.txt`、`d0-meta.txt`、`d0-events-sanitized.txt`、`d0-error-sanitized.txt`；
- `d0-meta.txt` 必须含真实 exit、timeout、首 stdout/首 JSON/首有效事件/完成时间、sentinel 命中布尔值；
- 原始输出只能在 runtime 暂存用于脱敏，随后删除，不进入 evidence。

D0 通过条件：在 120 秒内非 timeout、exit=0、至少一个可信 JSON/事件或可信最终结果、sentinel 命中。否则分类 `D0_FAIL`，完成 finally 后停止；不得继续 D1/D2。

---

## 9. D1 — 原始 `codex app-server` 协议探针

仅 D0 通过后执行。D1 使用**新的**私有 `CODEX_HOME`，仍在同一 RUN/evidence 内，但不得复用 D0 thread/session。

可在 runtime 创建一个通用协议驱动，不得写入仓库。驱动必须：

1. 以与 `codex_executor.py` 相同的基础 argv 启动 `codex app-server`；不替换模型、不修改 provider、不增加与产品不同的路由。
2. 通过 stdin 发送 `initialize`，再按当前源码/协议发送 `thread/start` 与 `turn/start`。
3. workspace/cwd 使用工作树绝对路径；sandbox 使用 `read-only`；不注册 dynamic tools。
4. prompt 从 runtime 读取，脚本/evidence 不含 prompt 正文。
5. 对每个 JSONL frame 只保存：接收 UTC、method、response id 是否存在、turn id 哈希、item type/phase、error code/脱敏摘要、累计 stdout/stderr bytes；禁止保存 message/prompt/content 正文。
6. 120 秒内持续记录 `d1-timeline.txt`；不得因为前 10 秒无输出提前推断失败。
7. 正常完成或超时后只终止 D1 冻结的精确 PID tree。

生成：

- `d1-protocol-steps.txt`
- `d1-process-tree.txt`
- `d1-timeline.txt`
- `d1-frames-sanitized.txt`
- `d1-stderr-sanitized.txt`
- `d1-meta.txt`

D1 通过条件：initialize、thread/start、turn/start 均有可映射响应，120 秒内收到属于该 turn 的至少一个业务事件，并最终收到 completed/failed 等可信终态；sentinel 成功时另记录，但“出现可信 provider 失败事件”也足以证明事件通道工作，不能冒充业务成功。

若 D1 timeout、进程意外死亡、JSON 不可解析或 turn 无任何 frame：完成 finally 后停止，不执行 D2。

---

## 10. D2 — 单次 Omnigent C 对照诊断

仅当 D0 通过且 D1 的事件通道可信时执行。D2 不是 Gate 2 六轮，仅执行一次 C；必须使用与 r4 相同的产品拓扑和固定模型，不得改源码/配置规避失败。

### 10.1 拓扑

- 一个 PowerShell 前台驱动内启动 server、foreground host、C 观察器和 finally 清理。
- server 新高位端口，READY 后连续观察 10 秒 health=200。
- foreground host 必须同时满足 Process alive、`process=online`、`host_status=online` 后才能启动 C。
- `OMNIGENT_DATA_DIR`、UTF-8 和 `NO_PROXY` 必须传入所有相关子进程。
- C 启动前生成 `d2-workspace-contract.txt`，证明 Windows drive absolute、单反斜杠形状、runtime 含 RUN_ID。
- agents 仅记录 name、harness=`codex`、model=`gpt-5.6-sol`、prompt/workspace chars 与 SHA-256；不保存正文。

### 10.2 有界可观测性

C 总预算 300 秒；不得调高或关闭产品 240 秒 idle watchdog。每 5 秒记录：

- server health；
- foreground host PID/alive 与双 online；
- C PID/alive、stdout/stderr bytes；
- server session 数与状态；
- runner PID/alive；
- runner 下名为 `codex`/`codex.exe` 的 App Server 子进程 PID、PPID、创建时间、alive、可读取的 CPU/IO 计数；
- `.codex-tmp` 新 home 的创建时间与文件/目录数量变化，禁止读文件正文或链接 Target；
- host/server/runner 日志新增字节数和最近一个**脱敏事件类型/错误码**，不得复制 prompt/模型正文。

若 Windows 无法只读取得某个 stdout pipe 或 IO 字段，记录 `NOT_OBSERVABLE`，不得伪造 0。不得 attach debugger、注入 DLL、修改 Python、修改日志级别配置或抓取 credential。

生成至少：

- `d2-server-lifecycle.txt`
- `d2-host-lifecycle.txt`
- `d2-process-tree-timeline.txt`
- `d2-session-timeline.txt`
- `d2-log-growth-timeline.txt`
- `d2-c.meta.txt`
- `d2-c-error-sanitized.txt`
- `d2-events-sanitized.txt`

D2 到达产品 idle watchdog 并以可信 exit=1 结束时，记录为诊断现象，不把它改写为 INVALID 或 Gate FAIL/PASS。本卡最终只输出下节诊断分类。

---

## 11. 唯一诊断分类矩阵

`DIAGNOSIS.txt` 只能写一个主分类：

| 分类 | 证据条件 | 下一步建议 |
|---|---|---|
| `DIAG_ENVIRONMENT_OR_MODEL` | D0 timeout/非零/无可信结果 | 先修 auth、网络、模型可用性或选择经单独批准且实际可用的模型；不改 Omnigent |
| `DIAG_APP_SERVER_PROTOCOL` | D0 通过，但 D1 initialize/thread/turn 或事件通道失败 | 聚焦 Codex CLI/App Server 版本、协议或私有 home 配置兼容性 |
| `DIAG_RUNNER_SPAWN` | D0/D1 通过，D2 未产生 runner 或未产生 App Server 子进程 | 交 Hermes 开发卡，修 runner/executor 启动链路 |
| `DIAG_CODEX_CHILD_STALL` | D0/D1 通过，D2 App Server 子进程存在，但无事件且无可解释退出/错误 | 交 Hermes 开发卡，补最小 fail-loud/可观测性或修产品传参/环境 |
| `DIAG_EVENT_RELAY` | D2 中 App Server/runner 日志证明已有 turn 事件，但 Omnigent `ctx.emit`/CLI 侧无事件 | 交 Hermes 开发卡，修 JSONL 读取、事件过滤或 relay |
| `DIAG_TRANSIENT_R4` | D0/D1 通过且 D2 C 在 300 秒内可信成功、sentinel 命中 | 不直接判 Gate；另发全新 Gate 2 六轮 RUN 卡 |
| `DIAG_INCONCLUSIVE` | 身份、拓扑、exit、时间线、清理、泄漏或证据任一不可信 | 修诊断卡/环境后用新 RUN_ID 重做 |

补充规则：

- D0/D1 出现明确的 provider/auth/model 错误时，报告脱敏错误码与摘要；不得静默换 model。
- `gpt-5.6-sol` 若当前不可用，只能建议后续另卡验证候选模型；本 RUN 不得换模型后继续拼证据。
- 单纯“提高 idle timeout”不是根因修复；除非证据证明模型持续产生可观测进度且仅 240 秒阈值过短，否则不得建议。
- `DIAG_TRANSIENT_R4` 也不等于 Gate 2 PASS，仍需六轮全新 RUN。

---

## 12. finally 清理

无论 D0/D1/D2 在哪里停止，finally 都必须执行：

1. 冻结本 RUN 创建的全部 PID 列表；先正常停止，再仅对这些 PID tree 做必要 TERM/KILL。
2. 不得 blanket kill、`pkill`、按进程名批量 kill 或触碰其它 URL/端口。
3. 确认本 RUN PID 全 dead；D2 端口 free；命令行匹配 RUN_ID/端口/runtime 的遗留数为 0。
4. 删除目标必须是绝对路径并包含完整 RUN_ID；精确删除 `$RUNTIME_ROOT`。
5. 生成 `codex-tmp-before-cleanup.txt`，只处理 start 快照后新增、创建时间落在本 RUN 窗口、叶名精确匹配 `omnigent-codex-home-*` 的目录。
6. 删除前确认目标属于 `$WORKTREE\.codex-tmp`、目标本身非 reparse；后代 reparse 只删链接本身，禁止读取/跟随 Target。
7. 精确删除本 RUN home 内链接、普通文件、空目录和 home；不得删除 `.codex-tmp` 父目录，不得用通配符、`git clean` 或递归跟随链接。
8. 生成 `codex-tmp-delete-actions.txt` 与 `codex-tmp-end.txt`；结束直接子项集合必须与 start 完全一致。
9. 生成 `cleanup.txt`：PID dead、runtime_deleted、port_free（若未启 D2 写 NOT_APPLICABLE）、leftover=0、codex-tmp set_equal。

清理任一项不可信，主分类必须降为 `DIAG_INCONCLUSIVE`。

---

## 13. 最终泄漏扫描

完成 identity end、git status end、blob end、诊断分类和 cleanup 后，最后创建 `leak-scan.txt`：

- 扫描当时 evidence 根全部文件；
- `files_present_before_scan == files_scanned`；
- prompt 正文 hits=0；
- credential/token/cookie/header 值 hits=0；
- auth/config 正文 hits=0；
- symlink Target hits=0。

`leak-scan.txt` 必须是 evidence 最后生成的文件。扫描后不得再改其它 evidence 文件。若计数不等或 hits 非 0，分类=`DIAG_INCONCLUSIVE`。

---

## 14. 完成报告格式

新增 `docs/fixes/handoffs/GROK_DIAGNOSIS_14.md`，至少写明：

1. 唯一 RUN_ID、evidence/runtime、执行时间窗。
2. 本轮唯一诊断分类；明确“不是 Gate 2 verdict”。
3. D0：CLI/model/auth 布尔身份、exit/timeout、首事件与 sentinel 结果。
4. D1：initialize/thread/turn 映射、首 frame、终态、exit/timeout。
5. D2（若执行）：server/host/runner/App Server 进程与事件时间线、可信 exit、错误摘要。
6. 哪些层未执行及其停止依据。
7. r4 仍为 Gate 2 FAIL；Gate 1 仍为相对 PASS、非全仓 GREEN；不可 merge。
8. identity/blob/git status 前后一致性。
9. `.codex-tmp` start/end 集合、精确删除和 PID/runtime/端口清理结果。
10. leak-scan 顺序、计数和 hits。
11. 下一步只能二选一：
    - 环境/模型/CLI 配置卡；或
    - Hermes 最小源码修复卡（列出精确疑点文件与所需失败测试，但本轮不修改）。

不得宣称运行 pytest、Ruff、Gate 1 或完整 Gate 2；本卡不要求且禁止这些动作。

---

## 15. 禁止项

- 禁止修改源码、tests、政策、STATUS、旧 handoff/evidence。
- 禁止 pytest、Ruff、Gate 1、完整 Gate 2 六轮。
- 禁止同 evidence 根重试、换端口续跑、换模型续跑或拼接旧 RUN。
- 禁止读取/打印 auth Target、credential 值、config/prompt 正文。
- 禁止调高/关闭 240 秒产品 idle watchdog 冒充修复。
- 禁止使用 receipt-mismatch/resume/fork/单测代替真实 C 或未来 Gate 轮次。
- 禁止 commit/push/merge/tag 或自行批准 merge。

---

## 16. 完成标准

只有同时满足以下条件，阶段 14 才可交回 Codex：

1. 只新增 `GROK_DIAGNOSIS_14.md`，仓库其它文件未被本轮改变。
2. 全新 RUN/evidence/runtime；未拼接旧 RUN；每层最多一次。
3. D0 先执行；只有 D0 通过才执行 D1；只有 D0/D1 可信才执行 D2。
4. 每个已执行层都有真实 exit/timeout、时间线、首事件/错误和脱敏证据。
5. 诊断分类严格符合矩阵且唯一；未冒充 Gate 2 verdict。
6. 模型固定 `gpt-5.6-sol`；未静默换模型或仅拉长 timeout。
7. identity、HEAD、八个 blob 开始/结束一致。
8. 所有本 RUN PID dead、runtime 删除、端口 free（如适用）、leftover=0。
9. `.codex-tmp` end 集合等于 start，只精确删除本 RUN 新 home。
10. leak-scan 最后生成、计数相等、hits=0。
11. 报告明确 Gate 1 相对 PASS、非全仓 GREEN；Gate 2 r4 仍 FAIL；不可 merge。

完成后停止，等待 Codex 只读验收。
