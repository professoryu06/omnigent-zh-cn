# CODEX TASK 8 — Gate 2 契约校准与可执行矩阵审查

**执行者：** Grok（Gate 2 契约审查者；本阶段不执行 smoke）  
**日期：** 2026-07-29  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** Gate 1=`PASS（相对 main）`；这不等于全仓 GREEN。Gate 2=未执行、未判定；不可 merge。  
**阶段边界：** 只读核对 Gate 2 的断言与阶段 5 已落地行为，给出一套无矛盾、可实机执行的最小 C/E/R 矩阵。不得运行 pytest、Ruff、Gate 或真实 CLI smoke；不得修改政策、源码或测试。

## 1. 问题

现行 `docs/fixes/PRE_MERGE_GATES.md` §2 同时规定：

- AC-2/AC-3：Executor 使用声明的 native harness，实际 harness/model 不被替换；示例为 `codex-native`。
- AC-4：非 strict 时出现“system prompt 未 apply”的 fail-loud warning。
- AC-5：strict 时在用户消息注入前失败。
- AC-6：没有 Phase 2 证据不得声称 prompt 已送达。

但阶段 5 已实现并由阶段 6 独立审查接受：fresh、非 fork 的 `codex-native` 会把 agent prompt 写入私有 `config.toml` 的 `developer_instructions`，生成 digest receipt；receipt 匹配时 `applied=True`。该成功路径按设计不应触发 AC-4 warning，strict 也不应触发 AC-5 失败。

因此，不能直接拿同一个 fresh codex-native session 同时证明“已 apply”和“未 apply”。若不先校准契约，Gate 2 会因互斥断言得到无意义的 FAIL/INVALID。

本阶段目标不是放宽 Gate，而是把以下两类证据明确分开：

1. codex-native Phase 2 正向路径：fresh apply、harness/model、receipt、实际回复。
2. 未具备 apply 通道的 native Phase 1 负向控制：non-strict warning 与 strict 注入前失败。

## 2. 必读与精确核对文件

必须完整读取：

1. `docs/fixes/PRE_MERGE_GATES.md` §2（约第245–311行）
2. `docs/fixes/handoffs/GROK_COMPLETION_5_REWORK.md`
3. `docs/fixes/handoffs/HERMES_REVIEW_6.md`
4. `docs/fixes/handoffs/HERMES_COMPLETION_7_POLICY_AMENDMENT_REWORK.md`
5. `omnigent/inner/native_prompt_delivery.py`
6. `omnigent/codex_native_app_server.py`
7. `omnigent/runner/app.py`
8. `omnigent/inner/codex_native_executor.py`
9. `tests/inner/test_codex_native_system_prompt_apply.py`
10. `tests/runner/test_app_codex_native_prompt_delivery.py`
11. `tests/inner/test_native_system_prompt_delivery.py`
12. `examples/polly/agents/codex/config.yaml`
13. `omnigent/cli.py` 中 `run` 命令、`_materialize_harness_launcher_file` 与 native dispatch 分支

只允许新建报告：

`docs/fixes/handoffs/GROK_GATE2_POLICY_REVIEW.md`

不得修改上述文件、任何旧任务卡/报告、`STATUS.md`、`POST_FIX_HANDOFF_PROMPT.md`，不得创建正式 Gate 2 evidence。

## 3. 必须回答的审查问题

报告必须逐项给出“是/否 + 文件/行号或测试名依据”：

1. fresh、非 fork codex-native receipt 匹配时，`applied` 是否为 true？
2. `applied=True` 时，非 strict 是否应当没有 fail-loud warning？
3. `applied=True` 时，`OMNIGENT_STRICT_PROMPT=1` 是否应当允许继续，而不是失败？
4. resume、fork、receipt 缺失/损坏/不匹配分别是否保持 `applied=False`？
5. 其余十个 native harness 是否仍只有 Phase 1 warn/error，没有 apply 通道？
6. 当前 AC-4/AC-5 若绑定到 fresh codex-native，是否与阶段 5 契约冲突？
7. AC-6 是否应改为：只有 receipt、私有 config 快照/摘要、启动日志和真实回复链完整时，才允许声明 codex-native Phase 2 已送达；其他 native 不得声明送达？
8. 当前 CLI 是否能用非交互 one-shot 方式创建三个独立 workspace/session，并留下 session id、workspace、harness/model 与日志证据？只做静态确认，不实际启动。

## 4. 必须给出的最小 Gate 2 矩阵

在报告中给出一张可直接转写为后续执行卡的矩阵。至少覆盖：

| 轮次 | 角色/目的 | 路径 | 必须证明 |
|---|---|---|---|
| C | Controller | 可启动的非 native 或已知可用 harness | 独立 session/workspace，短回复 |
| E-positive | Executor | fresh、非 fork `codex-native` | AC-2/AC-3；prompt digest/receipt 匹配；无 prompt 正文泄漏；真实回复；strict 可继续 |
| E-negative non-strict | Executor 负向控制 | 明确无 apply 通道的 native harness，或人为制造 receipt mismatch 的安全隔离会话 | warning 含 `chars=N`，不含 prompt 正文；用户消息保持原样 |
| E-negative strict | Executor 负向控制 | 与上一行相同能力边界的新会话 | `OMNIGENT_STRICT_PROMPT=1` 时在任何用户消息 RPC/注入前失败 |
| R | Reviewer | 可启动的非 native 或已知可用 harness | 独立 session/workspace，短回复 |

不得用 resume/fork 冒充 fresh Phase 2 正向证明；不得用单元测试冒充真实 Gate 2 smoke；不得让负向控制修改真实用户的共享 Codex 配置。

报告还必须明确：

- 负向控制应选哪个具体 harness，选择依据是什么；若本机没有第二个 native CLI，应判 `NOT_EXECUTED` 还是允许安全 receipt-mismatch 控制，必须按代码与政策给出建议。
- C/R 使用哪个现有 CLI/harness；需要的 credential 只记录环境变量名/认证是否存在，绝不记录值/token。
- pinned model 如何从当前真实可用模型中选定，并如何证明“YAML model = launch model”；不得预先编造模型名。
- 三个 workspace 的绝对路径规划、端口、HOME/配置隔离、进程清理边界及日志脱敏规则。
- 后续真正执行时每一轮的命令模板、预期退出码、证据文件名和超时。

## 5. 只读检查命令

允许使用以下类型的命令；可增加同类只读 `rg`/`git diff`/`Get-Content`，不可启动产品进程：

```powershell
rg -n "AC-[1-6]|OMNIGENT_STRICT_PROMPT|documented_main_code_failure" `
  docs/fixes/PRE_MERGE_GATES.md

rg -n "note_native_system_prompt|applied=|receipt_matches_prompt|developer_instructions|write_prompt_receipt|clear_prompt_receipt" `
  omnigent/inner/native_prompt_delivery.py `
  omnigent/codex_native_app_server.py `
  omnigent/runner/app.py `
  omnigent/inner/codex_native_executor.py

rg -n "applied|strict|warning|receipt|fresh|fork|resume|developer_instructions" `
  tests/inner/test_codex_native_system_prompt_apply.py `
  tests/runner/test_app_codex_native_prompt_delivery.py `
  tests/inner/test_native_system_prompt_delivery.py

rg -n "@cli.command|def run\(|--prompt|--system-prompt|--model|--server|_dispatch_native_terminal_harness" `
  omnigent/cli.py

git status --short --branch
git diff --check -- docs/fixes/handoffs/GROK_GATE2_POLICY_REVIEW.md
```

禁止运行 `omnigent-zh`、`uv run`、pytest、Ruff、server/host、Codex/Claude/Qwen/Hermes CLI、浏览器或网络请求。本阶段也不得用 `--help` 启动入口；从源码静态确认。

## 6. 禁止项

- 不得修改 `omnigent/`、`tests/`、配置、lockfile、CI、Gate 1 evidence 或任一旧 handoff。
- 不得修改 `PRE_MERGE_GATES.md`；本轮只提出最小逐字修订建议，由 Codex/用户另行批准。
- 不得运行测试、Gate 2、真实模型、CLI smoke 或启动/终止任何 host/server/tmux。
- 不得读取、复制、打印 credentials、token、真实用户 HOME 内容或 prompt 正文。
- 不得把 Gate 1 相对 PASS 写成全仓 GREEN。
- 不得宣称 Gate 2 PASS、可 merge 或批准合并。
- 不得 stage/commit/push/merge/tag、发版或编辑 PR/Issue。

## 7. 完成标准

只有同时满足以下条件，本阶段才可交回 Codex：

1. `GROK_GATE2_POLICY_REVIEW.md` 对 §3 八个问题逐项作答并附精确依据。
2. 明确认定当前 AC-4/AC-5 与 codex-native Phase 2 是否冲突，不能模糊处理。
3. 给出一套将正向 apply 与负向 fail-loud 分开的最小 C/E/R 实机矩阵。
4. 给出 `PRE_MERGE_GATES.md` §2 的最小逐字修订建议，但未实际修改政策。
5. 给出后续 Gate 2 执行卡所需的命令模板、证据文件、预期退出码、隔离和清理边界；未知环境项写成显式 preflight，不编造结果。
6. 报告明确：Gate 1=`PASS（相对 main）`但非全仓 GREEN；Gate 2仍未执行、未判定；不可 merge。
7. 本轮工作树变化仅新增 `GROK_GATE2_POLICY_REVIEW.md`，无其他文件变化。
8. 未运行任何测试/产品进程，未触发任何禁止项。

完成后停止，等待 Codex 只读验收。若建议修订政策，Codex/用户批准后另发政策修订卡；不得自行修改或直接执行 Gate 2。
