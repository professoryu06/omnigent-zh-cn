# CODEX TASK 8 POLICY AMENDMENT — 校准 Gate 2 Phase 2 正向与 Phase 1 负向断言

**执行者：** Hermes（文档执行者；非 Gate 2 执行者）  
**日期：** 2026-07-29  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**批准状态：** Codex 已只读验收 `GROK_GATE2_POLICY_REVIEW.md` 的核心冲突结论，并批准本卡限定范围内的政策修订。  
**当前 Gate：** Gate 1=`PASS（相对 main）`，不等于全仓 GREEN；Gate 2=未执行、未判定；不可 merge。  
**阶段边界：** 只修改 `docs/fixes/PRE_MERGE_GATES.md` 的 Gate 2 规格及其中已过时的 Gate 1 执行快照；不得运行测试、Gate 或真实 CLI。

## 1. 问题与验收结论

现行 Gate 2 把以下互斥行为绑定到同一个 fresh codex-native Executor：

- 阶段 5 Phase 2 正向路径：receipt 匹配，`applied=True`，无 fail-loud warning，strict 继续。
- 旧 AC-4/AC-5 负向路径：要求 warning，并要求 strict 注入前失败。

Grok 的只读审查结论成立：同一会话不能同时证明“已 apply”和“未 apply”。Gate 2 必须拆成：

1. E-positive：fresh、非 fork codex-native 的 Phase 2 正向 apply。
2. E-negative：真实 warn-only native harness 的 Phase 1 非 strict/strict 负向控制。

本卡采纳该主结论，但收紧两项边界：

- **禁止**把 receipt-mismatch、resume 或 fork codex-native 当作 E-negative 替代品。receipt 缺失不能可靠证明 private config 中没有历史 `developer_instructions`；这种控制不等价于“无 apply 通道”。
- E-positive strict 必须是**新的 fresh、非 fork session/runner，从进程启动前就带 `OMNIGENT_STRICT_PROMPT=1`**。禁止在已启动 runner 后修改父 shell 环境并声称子进程已收到该变量。

若本机没有第二个可启动的、能力矩阵为 `warn` 的 native CLI，Gate 2=`NOT_EXECUTED/未完成`，阻塞 merge；不得降级为 codex receipt-mismatch。

## 2. 必读与允许修改范围

必须完整读取：

1. `docs/fixes/handoffs/GROK_GATE2_POLICY_REVIEW.md`
2. `docs/fixes/handoffs/CODEX_TASK_8.md`
3. `docs/fixes/PRE_MERGE_GATES.md`
4. `docs/fixes/handoffs/HERMES_REVIEW_6.md`
5. `omnigent/inner/native_prompt_delivery.py`（只读）
6. `omnigent/codex_native_app_server.py`（只读）
7. `omnigent/runner/app.py`（只读）
8. `omnigent/inner/codex_native_executor.py`（只读）

只允许修改：

- `docs/fixes/PRE_MERGE_GATES.md`

只允许新建：

- `docs/fixes/handoffs/HERMES_COMPLETION_8_POLICY_AMENDMENT.md`

不得修改任何源码、测试、配置、lockfile、CI、`STATUS.md`、`POST_FIX_HANDOFF_PROMPT.md`、旧任务卡、旧报告或 evidence。

## 3. Gate 2 §2.1 固定配置的最小改法

把单一 Executor 概念拆成五个逻辑轮次：

| 轮次 | harness | session 要求 | 目的 |
|---|---|---|---|
| C | 可用非 native | 独立 workspace/session | Controller 短回复 |
| E-pos | `codex-native` | fresh、非 fork、STRICT 未设置 | Phase 2 apply 正向证据 |
| E-pos-strict | `codex-native` | **新的** fresh、非 fork session/runner；启动前 STRICT=1 | receipt 匹配时 strict 仍继续 |
| E-neg-warn / E-neg-strict | 能力矩阵为 `warn` 的**非 codex** native harness | 两个新 session；分别从启动前 STRICT 未设置/STRICT=1 | Phase 1 warning 与注入前失败 |
| R | 可用非 native | 独立 workspace/session | Reviewer 短回复 |

配置示例必须满足：

- E-pos/E-pos-strict 使用单文件 YAML 的 `executor.type: omnigent`、`executor.config.harness: codex-native` 与真实 preflight 后 pin 的 `executor.model`。
- E-negative 使用 `native_prompt_delivery.py` 能力矩阵中值为 `warn` 的**非 codex** native harness；不得预先写死本机不存在的 CLI。文档可列 `claude-native` 为首选示例，但必须写“以 preflight 实际可用者为准”。
- C/R 使用当前真实可用的非 native harness，配置路径和 model 均由 preflight 确定。
- 所有 role prompt 非空且使用短 token 回复；证据中不得保存 prompt 正文。
- E-pos、E-pos-strict、E-neg-warn、E-neg-strict 禁止共用 session id。

## 4. Gate 2 §2.2 启动步骤的最小改法

启动模板必须明确以下顺序：

1. 新建独立 Gate 2 evidence root，不复用 Gate 1 evidence。
2. preflight：Omnigent CLI 路径/版本、codex CLI、第二个 warn-only native CLI、credential **存在性布尔值**、真实可用模型、端口、现有进程；不得打印 secret/token。
3. 建立 C、E-pos、E-pos-strict、E-neg-warn、E-neg-strict、R 的独立 workspace/session；每个 workspace 放唯一 sentinel，证明文件不串。
4. C/R 执行 one-shot 短回复。
5. E-pos 在 STRICT 未设置时，以 fresh、非 fork codex-native 启动；证明 receipt/config 摘要、harness/model、真实回复、无 fail-loud warning。
6. E-pos-strict 新建 fresh、非 fork session/runner，**在启动命令之前**设置 `OMNIGENT_STRICT_PROMPT=1`；证明 receipt 匹配并继续成功。
7. E-neg-warn 新建 warn-only native session，启动前确保 STRICT 未设置；证明 warning 含 `chars=N`、不含 prompt 正文，用户消息未拼接 role prompt。
8. E-neg-strict 再新建 warn-only native session/runner，启动前设置 STRICT=1；证明在任何用户消息 RPC/注入前失败。
9. 记录 session id、绝对 workspace、harness、YAML model、实际 launch model、strict、退出码、日志文件。
10. 只清理由本 RUN_ID 启动并可精确绑定的进程；禁止 blanket `pkill`、`tmux kill-server`、无差别 TERM/KILL。

模板必须明确：

- `run --harness codex-native -p ...` 会走 native TUI 且拒绝 REPL 参数，不能作为 E-positive；E-positive 必须使用 `run <executor-yaml> -p ...` 的 session/runner/app-server 路径。
- 环境变量只在子进程启动时继承；禁止对已启动 runner 事后设置 STRICT 后复用。
- receipt 证据只保存 `harness_id/channel/chars/sha256`；private config 只保存键存在性、model、chars 与 digest 摘要，不复制 `developer_instructions` 正文。
- 任何 log、异常、argv、env、receipt、报告中不得出现 prompt 正文或 credential 值。

## 5. Gate 2 §2.3 断言表

用下列语义替换旧 AC-4/AC-5 单轨断言；AC-1/2/3 保留并精确绑定 E-positive：

| ID | 必须断言 | 最低证据 |
|---|---|---|
| AC-1 | C、E-pos、E-pos-strict、E-neg-warn、E-neg-strict、R workspace 路径均不同，sentinel 不串 | `sessions.txt` + workspace 清单 |
| AC-2 | E-pos/E-pos-strict YAML 声明与实际 `harness_kind` 均为 `codex-native`，未被 model prefix 替换 | launch 日志/会话快照 |
| AC-3 | E-pos/E-pos-strict 实际 model 与各自 YAML pin 字符串相等 | launch 日志 + private config model 摘要 |
| AC-4-pos | E-pos 非空 prompt receipt 四项匹配，private config 有 `developer_instructions` 键，真实回复成功，且无 `not applying` warning | receipt/config 摘要 + launch/smoke log |
| AC-4-neg | E-neg-warn 必须出现含 `chars=N` 的 fail-loud warning，且任何证据无 prompt 正文 | `e-neg-warn.log` + 泄漏扫描 |
| AC-5-pos | E-pos-strict 从进程启动前 STRICT=1；receipt 匹配，仍能完成真实 turn | env-presence（无值）+ 时间序日志 |
| AC-5-neg | E-neg-strict 从进程启动前 STRICT=1；在任何用户消息 RPC/注入前失败，无成功模型回复 | 时间序日志/错误事件 |
| AC-6 | 只有 AC-2、AC-3、AC-4-pos、AC-5-pos 全部具备实机证据时，才可写“codex-native Phase 2 已送达”；其余 native 永远不得声称送达；单元测试或无 warning 不能替代证据链 | 审查文案 + E-positive evidence |

判定规则必须写清：

- 所有必跑轮次及 AC-1～AC-6 全部满足，且 evidence 可解析 → Gate 2 PASS。
- CLI、credential、真实模型或第二个 warn-only native 缺失 → Gate 2 `NOT_EXECUTED/未完成`，阻塞 merge。
- 环境具备且实际断言失败 → Gate 2 FAIL。
- 日志/退出码/session 映射缺失、证据串轮或无法判断注入时序 → Gate 2 INVALID，必须重跑；不得拼接不同 run。

## 6. 同步修复过时执行快照

`PRE_MERGE_GATES.md` 的“本环境执行记录”仍写 Gate 1 未执行，与已验收状态冲突。只在该表内做最小更新：

- Gate 1 Linux 全仓：`PASS（相对 main）`；注明 baseline/candidate 都非全绿。
- 写明 r6：baseline 123 failed + 3 errors；candidate 123 failed + 3 errors；双方 126 个失败/错误 nodeid 相同，归一化语义指纹 126/126 相同，candidate-only=0。
- 写入只读证据根：`C:\Users\Administrator\gate1-evidence\20260729-1715-dc83140-grok-r6\`。
- Gate 2：仍为未执行、未判定。
- 结论：合并门槛仍未达到；不可 merge。

不得修改 Gate 1 九条安全条件或其批准记录。

## 7. 文档验证命令

仅允许只读文档验证；不得运行产品/测试：

```powershell
rg -n "E-positive|E-negative|AC-4-pos|AC-4-neg|AC-5-pos|AC-5-neg|Phase 2|NOT_EXECUTED|INVALID" `
  docs/fixes/PRE_MERGE_GATES.md

rg -n "PASS（相对 main）|126/126|candidate-only|20260729-1715-dc83140-grok-r6|Gate 2.*未执行|不可 merge" `
  docs/fixes/PRE_MERGE_GATES.md

rg -n "receipt-mismatch|resume|fork|进程启动前|第二个.*native|prompt 正文|credential" `
  docs/fixes/PRE_MERGE_GATES.md

git diff --check -- docs/fixes/PRE_MERGE_GATES.md
git diff -- docs/fixes/PRE_MERGE_GATES.md
git status --short --branch
```

报告必须记录真实输出/退出码。不得用格式化器自动重写整份文档。

## 8. 禁止项

- 不得修改 `omnigent/`、`tests/`、STATUS、POST_FIX、配置、依赖、lockfile、CI、旧 handoff 或 evidence。
- 不得改变 Gate 1 九条安全条件、批准记录或 r6 evidence。
- 不得运行 pytest、Ruff、Gate 1/2、AgentCenter、浏览器、Omnigent/Codex/Claude 等真实 CLI。
- 不得启动、终止或清理 host/server/runner/tmux。
- 不得读取、复制、打印 credential/token 或 prompt 正文。
- 不得 stage/commit/push/merge/tag、发版或编辑 PR/Issue。
- 不得声称 Gate 2 PASS、全仓 GREEN 或可 merge。

## 9. 完成标准

1. 只修改 `PRE_MERGE_GATES.md` 的 Gate 2 §2 和过时执行快照；只新增本轮完成报告。
2. 正向 codex Phase 2 与负向 warn-only native 已分轨，断言无互斥。
3. 明确禁止 codex receipt-mismatch/resume/fork 充当 E-negative。
4. E-pos-strict 明确为进程启动前 STRICT=1 的新 fresh、非 fork session/runner。
5. AC-1～AC-6、PASS/FAIL/INVALID/NOT_EXECUTED 判定和 evidence 最低字段完整。
6. Gate 1 记录更新为 PASS（相对 main），但明确非全仓 GREEN；Gate 2仍未执行、未判定；不可 merge。
7. Markdown 表格结构连续，代码围栏配对，`git diff --check` exit 0。
8. HEAD 和四个保护 blob 未变。
9. 未运行任何测试、Gate 或产品进程，未触发任何禁止项。

完成后写 `docs/fixes/handoffs/HERMES_COMPLETION_8_POLICY_AMENDMENT.md`，附精确 diff 摘要、结构验证、关键短语、HEAD/保护 blob、最终 `git status --short --branch`。然后停止，等待 Codex 只读验收；不得直接执行 Gate 2。
