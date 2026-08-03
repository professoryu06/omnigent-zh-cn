# CODEX REVIEW 14 — 阶段 14 分层诊断只读验收

> **验收者：** Codex（只读验收/编排）
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
> **验收对象：** `docs/fixes/handoffs/GROK_DIAGNOSIS_14.md`
> **证据根：** `C:\Users\Administrator\omnigent-diagnostics\20260730-1415-dc83140-grok-codex-idle-diag`

## 1. 验收结论

**REJECT**

不接受报告主张的 `DIAG_RUNNER_SPAWN`。本轮证据应按任务卡矩阵改判为：

```text
DIAG_INCONCLUSIVE
```

原因是两项硬性前置条件不成立：

1. 开始预检明确记录 `count=1 / pass=False`，但任务卡规定发现旧 r4 或当前 RUN 匹配进程时必须停止并判 `DIAG_INCONCLUSIVE`；现有证据没有 PID 30480 的 name、PPID、创建时间或归属证明，不能事后假定它只是诊断驱动自身。
2. D1 没有取得可信 turn 终态：`d1-meta.txt` 为 `exit=1`、`terminal_state=item/completed`，而 `d1-frames-sanitized.txt` 表明该 `item/completed` 的 `item_type=userMessage`；sentinel 命中来自输入消息回显，不是模型输出。没有 `turn/completed`、`turn/failed` 或 assistant/model item，故 `D1_PASS=True` 不满足任务卡完成条件。

由于 D2 的执行前提是 D0 与 D1 均可信通过，D1 不通过后仍执行 D2，分层停止条件已被违反。D2 的观测可保留为根因线索，但不能支撑本轮唯一正式分类为 `DIAG_RUNNER_SPAWN`。

本验收没有修改 Grok 原报告或仓库源码，也没有重跑 D0/D1/D2、pytest、Ruff 或 Gate。

---

## 2. Identity、HEAD 与八个 blob

只读独立核对结果：

- 当前 HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`，与 start/end 及冻结值一致。
- 以下八个当前工作树 blob 均与 start/end/任务卡固定值一致：
  - `_workspace_validation.py`：`5bf5e587b9177a9ecbce572b11656edac31ea7fe`
  - `sessions.py`：`0375e5f951d82c01c9f67e8cf7b41a90aff10330`
  - validator 测试：`63291bfa4bc47c196e04a218c82b782ecb613786`
  - helper 测试：`4cae0f53cb724c991a1c502c2919e37da7b7737a`
  - workspace 保护：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
  - model 保护：`be43ec45816e8ece4192822506df8072580910e0`
  - idle 保护：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
  - serve 保护：`6116218097f2352c467524fd0ddf0838315aa524`
- `git-status-start.txt` 与 `git-status-end.txt` 去除各自 UTC 首行后逐行相同。

Identity/关键 blob 本身通过；它们不能弥补预检和 D1 的流程缺口。

---

## 3. 分层顺序与证据核对

### 3.1 开始预检

`precheck-leftover-pids.txt` 原文要点：

```text
r4_or_current_run_match_pids=30480
count=1
pass=False
note=only_check_no_kill
```

任务卡 §5 要求匹配进程数为 0；发现残留必须停止。本 RUN 没有停止，也没有提供足以排除 PID 30480 的安全归属证据。这一项单独即可触发 `DIAG_INCONCLUSIVE`。

### 3.2 D0

D0 的有效测量证据基本完整：

- 使用 native `codex.exe` 0.142.5；模型固定 `gpt-5.6-sol`。
- `exit=0`、`timeout=False`、约 30.34 秒。
- 4 个 JSON 事件：`thread.started`、`turn.started`、`item.completed`、`turn.completed`。
- sentinel 命中，存在真实 turn 完成事件。
- 有 5 秒步进时间线、最终 stdout/stderr bytes 和脱敏错误摘要。

因此 D0 可接受为“该 native Codex one-shot 在本机、本认证、本模型下可完成”。D0 不能证明产品侧实际选择了同一个可执行文件。

### 3.3 D1

D1 顺序上晚于 D0，但完成条件不成立：

- initialize、thread/start、turn/start 响应均有映射。
- 收到 `turn/started` 与 `userMessage` 的 `item/started`、`item/completed`。
- 没有 `turn/completed`、`turn/failed` 或 assistant/model 输出 item。
- `sentinel_hit=True` 是输入 userMessage 携带 sentinel 后被协议回显，不能当作模型完成证据。
- 探针在 `item/completed` 后结束，进程最终 `exit=1`；报告也承认这不是严格 turn 终态。

这只能证明 App Server 可以 initialize/start thread/start turn 并回显输入事件，不能按任务卡写成完整 `D1_PASS=True`。

### 3.4 D2

D2 本身的观测事实可读且内部大体一致：

- 只执行一次 C；未执行 Gate 2 后五轮。
- 模型仍为 `gpt-5.6-sol`。
- 外层预算 300 秒；产品报错仍是 240 秒 idle watchdog，未被拉长或关闭。
- server READY 并连续观察 10 秒；foreground host 双 online。
- C `exit=1`、`timeout=False`、约 259.62 秒；server/host 结束时仍健康。
- 新建 D2 私有 home `omnigent-codex-home-qos19h69`；未再次出现 0202 路径 400。
- 约 5–7 秒一次的进程采样没有看到 PPID 属于本 RUN runner 树的 `codex.exe`。

但以下原因使 D2 不足以把分类锁定为 `DIAG_RUNNER_SPAWN`：

1. D2 在 D1 未满足通过条件后仍被执行。
2. D0/D1 明确绕过 PATH shim，直接使用 vendor native `codex.exe`；产品 D2 没有冻结或记录 `HARNESS_CODEX_PATH`/最终 `CodexExecutor._codex_path`。二者不是已证明相同的 CLI 入口。
3. 进程采样间隔约 5–7 秒，只能证明“采样点未见长期存活的本 RUN codex.exe”，不能排除 shim/中间进程或 App Server 在两个采样点之间启动后立即退出。
4. 没有 App Server spawn 失败、早退 exit、实际 argv executable 或 `_reader_loop` 已启动的直接证据，无法区分“从未 spawn”和“短命退出后 pending initialize 永久等待”。

因此：

- 不改判为 `DIAG_CODEX_CHILD_STALL`，因为没有观测到可信归属本 RUN 且持续存活的 App Server 子进程。
- 不接受 `DIAG_RUNNER_SPAWN`，因为严格前置条件与可执行文件同一性没有成立。
- 唯一安全分类是 `DIAG_INCONCLUSIVE`。

---

## 4. finally、`.codex-tmp` 与 leak-scan

可以确认的结果：

- `.codex-tmp` start 直接子项集合为空，end 也为空，`set_equal_start=True`。
- `cleanup.txt` 记录 `pids_all_dead=True`、`runtime_deleted=True`、端口 50581 free、`leftover_zero=True`。
- evidence 根在 leak-scan 前有 42 个文件；加上 `leak-scan.txt` 后实际为 43 个。
- `leak-scan.txt` 是 evidence 中 LastWriteTime 最晚的文件；记录 `42 == 42`、各类 hits=0、`pass=True`。
- 旧 `gate2-evidence` 在本 RUN 时间窗内未发现文件写入。

证据缺口：

- `codex-tmp-delete-actions.txt` 只写 `deleted_attempted=d0,d1,d2 homes`，没有逐项绝对目标路径、叶名、归属校验、目标本身 reparse 状态、后代链接删除顺序或每步结果。
- `cleanup.txt` 只有汇总布尔值，没有任务卡要求的冻结 PID 清单与逐 PID dead 结果。
- Grok 报告 LastWriteTime 为 06:37:21Z，`leak-scan.txt` 为 06:37:39Z；报告中的 leak-scan 成功表述早于实际最终 scan。Codex 已独立读取最终 scan，但原报告的证据时序仍应记录为债务。

所以能接受“当前 `.codex-tmp` 集合已回到空、端口当前释放、最终 scan 文件存在且 hits=0”的结果；不能接受报告声称的全部精确安全删除步骤均已有可审计证据。

---

## 5. 仓库范围

只读范围核对结果：

- start/end git status 的路径、状态、大小清单一致。
- 八个关键 blob 未变，当前 HEAD 未变。
- `CODEX_TASK_14.md` 写入后，handoffs 目录内只有 `GROK_DIAGNOSIS_14.md` 的 LastWriteTime 落在 Grok 本 RUN 时间窗；没有其它 handoff 在该时间窗被改写。
- 旧 Gate evidence 在本 RUN 时间窗内没有写入记录。
- 当前没有证据显示 Grok 修改了源码、tests、政策、STATUS 或旧 handoff。

因此仓库范围项可接受：Grok 的唯一仓库交付为 `GROK_DIAGNOSIS_14.md`。本验收新增的 `CODEX_REVIEW_14.md` 不属于 Grok 交付。

---

## 6. 证据缺口清单

必须修正的缺口：

1. 预检 `count=1/pass=False` 后未停止；PID 30480 归属不可审计。
2. D1 把 `userMessage item/completed` 当作 terminal，并把输入回显 sentinel 当作成功；缺少 turn 终态和模型输出。
3. D1 `exit=1` 却标 `D1_PASS=True`，不符合任务卡。
4. D1 不通过后仍执行 D2，违反条件式顺序。
5. 产品 D2 的实际 Codex executable 未冻结，无法与 D0/D1 的 vendor native binary 做同入口对照。
6. 5–7 秒采样无法排除 App Server 短命退出，缺少 spawn/early-exit 直接证据。
7. `.codex-tmp` 删除动作与 PID 清理只有汇总，缺少逐目标安全检查证据。
8. 完成报告早于最终 leak-scan 文件生成。

---

## 7. 下一步唯一建议

选择：**环境/CLI 固定 native Codex 卡**，暂不发 Hermes 源码修复卡。

理由：现有证据已经显示 D0/D1 使用 vendor native `codex.exe`，而 PATH 入口为 npm/opencodex shim；产品 D2 未证明使用同一个 binary。先消除可执行文件差异，才能判断是否真的需要改 spawn/fail-loud 源码。

下一卡入口必须写清：

- `omnigent/inner/codex_harness.py::_build_codex_executor()`：读取 `HARNESS_CODEX_PATH` 并传入 `CodexExecutor`。
- `omnigent/inner/codex_executor.py::_find_codex_cli()`：未显式配置时回落到 `shutil.which("codex")`。
- `omnigent/inner/codex_executor.py::CodexExecutor.__init__()`：形成最终 `_codex_path`。
- `omnigent/inner/codex_executor.py::_CodexAppServerSession.start()`：用 `_codex_path app-server` 启动真实子进程。

下一卡必须使用全新 RUN_ID，并要求：

1. 开始预检排除诊断驱动自身后必须为 `count=0/pass=True`；非零立即停止。
2. 在 foreground host/runner 启动前显式设置 `HARNESS_CODEX_PATH` 为与 D0 相同的 vendor native `codex.exe`，并记录最终 executable 的路径 SHA-256/版本，不记录敏感命令行。
3. D1 必须等到 `turn/completed`、`turn/failed` 或可信 provider terminal；assistant/model 输出 sentinel 才算成功，`userMessage` 回显不得计数。
4. D1 未通过不得执行 D2。
5. D2 如执行，应在 spawn 窗口使用更密集、可审计的进程创建/退出观测，区分“未 spawn”“立即退出”“持续存活无事件”。
6. 使用新的 evidence/runtime 根；不得续写或拼接本 RUN。
7. 完成精确 PID、runtime、端口和 `.codex-tmp` 清理后，再生成最终 leak-scan，最后才写仓库完成报告。

只有固定 native binary 后仍复现且取得可信 spawn/early-exit 证据，才进入 Hermes 最小 spawn/fail-loud 源码开发卡。

---

## 8. Gate 与 merge 状态

- Gate 1 仍为 `PASS（相对 main）`，不等于全仓 GREEN；阶段 10 之后最终候选仍需重新执行 Gate 1。
- Gate 2 r4 仍为 `FAIL`。
- 阶段 14 本诊断改判 `DIAG_INCONCLUSIVE`，不是 Gate 2 verdict，更不是 Gate 2 PASS。
- **不可 merge。**
- 未 commit/push/merge/tag。

验收停止，等待下一张环境/CLI 固定 native Codex 任务卡。
