# CODEX TASK 7 POLICY REVIEW — Gate 1 相对 main 基线资格独立审查

**审查者：** Hermes（独立政策审查者；不得由Grok自审）  
**日期：** 2026-07-29  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** r6证明candidate无新增失败，但85项属于`known_main_code_failure`，不符合现行环境/flaky限定；Gate 1未获Codex验收。Gate 2未执行、未判定；不可 merge。  
**阶段边界：** 只读审查Gate政策含义与风险，给出政策建议。不得运行测试，不得修改政策、源码、证据或旧报告，不得直接签发Gate PASS或merge许可。

## 1. 必读

1. `docs/fixes/PRE_MERGE_GATES.md`，尤其§1.2
2. `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_5.md`
3. `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_5_TRIAGE.md`
4. `docs/fixes/handoffs/CODEX_TASK_7_REWORK_5_TRIAGE.md`
5. r6 evidence：`C:\Users\Administrator\gate1-evidence\20260729-1715-dc83140-grok-r6\`

重点证据：双侧JUnit/日志、126项fail-id、`new-failures.txt`、HOME/包列表/身份/进程分类与triage映射。

只允许新建：

`docs/fixes/handoffs/HERMES_GATE1_POLICY_REVIEW.md`

## 2. 已固定事实

以下事实已经Codex只读核对，本卡不重跑：

- baseline与candidate均完成；exit 1、tee 0、JUnit可解析。
- 两侧failure/error nodeid各126项，集合完全相等；candidate无新增nodeid。
- candidate额外通过80项测试；没有candidate-only失败。
- 隔离HOME初始状态、venv包列表、树身份、candidate快照和四保护blob一致。
- blocking进程证据为空；惰性pytest tmux符合白名单且未被kill。
- Grok triage已映射全部126项，自检exit 0。
- 分类：41项`known_environment` eligible=yes；85项`known_main_code_failure` eligible=no；0项known_flaky；0项unclassified。
- 现行`PRE_MERGE_GATES.md`文字要求baseline失败逐项标注“已知环境/已知flaky”。

因此：

- “candidate无新增失败”证据成立；
- “按现行文字可相对PASS”证据不成立；
- 不得通过解释性改写直接把85项代码失败变成环境/flaky。

## 3. 审查问题

独立回答：Gate 1的原始治理意图究竟是：

1. **严格环境/flaky门槛**：只有可归因环境或flaky的main失败可进入相对基线；任何确定性main代码失败都阻止Gate 1，即使candidate没有新增失败；还是
2. **标准回归门槛**：任何在同环境clean main可复现、已具体记录且candidate未新增/未恶化的失败都可作为已知baseline，包括确定性main代码失败。

这不是源码审查，也不是“是否喜欢85个失败”；重点是门槛语义、误放风险、误阻风险和可审计性。

## 4. 必做只读分析

### 4.1 现行文字解释

逐句引用不超过必要长度并解释：

- `PRE_MERGE_GATES.md` §1.2表格与失败列表要求；
- STATUS中Gate 1的目标；
- r05证据真实性/相对main设计意图。

明确区分：

- 现行文字的plain meaning；
- 若允许main代码失败，需要修改/澄清的具体语句；
- 不能用审查报告暗中替代政策修改。

### 4.2 风险分析

至少评估：

- **KEEP_STRICT误阻风险：** 为本次有限修复承担85项无关main既有失败，可能导致Gate永远无法推进或迫使跨范围修复。
- **允许main baseline误放风险：** 同一nodeid仍失败可能掩盖candidate使错误原因变坏；仅比较nodeid不够。
- 126项失败意味着大量代码路径没有形成GREEN，Gate 2能否弥补关键真实流程覆盖。
- candidate新增80个通过测试、定向136 passed与Ruff/diff证据能提供什么、不能提供什么。

### 4.3 共享失败指纹抽查/统计

只读解析r6双侧JUnit，对126个共享nodeid比较：

- failure/error类型；
- 根异常/首条稳定消息；
- 去除树绝对路径、随机UUID/会话ID、PID、内存地址和耗时后的归一化消息。

不得把原始traceback字节不相同直接当语义不同；也不得过度归一化掉实际/期望值、HTTP状态、异常类型、缺失模块名、策略动作等关键差异。

输出：

- `same_semantic_fingerprint`数量；
- `different_semantic_fingerprint`数量；
- 每个不同项的nodeid、baseline/candidate稳定消息与是否可能由candidate导致。

若无法可靠归一化，结论必须是证据不足，不得假设相同。

## 5. 允许的结论

报告最终只能给出以下一个建议，不得直接改Gate状态：

### `KEEP_STRICT`

含义：保持环境/flaky限定；85项main代码失败使Gate 1不能PASS。必须说明：

- 是否应修复85项、等待main更新或建立新的clean-main基线；
- 这是否超出当前Omnigent修复范围；
- Gate 2继续阻塞。

### `RECOMMEND_POLICY_AMENDMENT`

含义：建议显式修订Gate为“同环境、具体记录、candidate无新增且共享失败未语义恶化”的标准相对回归门槛。必须：

- 给出`PRE_MERGE_GATES.md`的精确建议文字，但**不得编辑文件**；
- 明确85项不得称环境/flaky，只能称documented clean-main code baseline；
- 要求共享失败归一化指纹无语义恶化；
- 说明政策修订须由Codex/用户显式批准，不能由本报告追认Gate PASS；
- Gate 2在政策正式决策前仍阻塞。

### `INSUFFICIENT_EVIDENCE`

含义：政策意图或失败指纹不足以支持前两者；列出缺口，继续阻塞Gate 2。

## 6. 若建议修订，最低安全条件

建议文字至少包含以下条件：

1. baseline/candidate必须在同OS、依赖、隔离状态下完整运行并有有效JUnit。
2. candidate失败nodeid必须是baseline子集，candidate-only失败为零。
3. 每个共享失败必须有具体分类与证据，不能只有“main也失败”。
4. 每个共享失败的归一化语义指纹必须相同；异常类型、实际/期望值或关键错误码变化视为可能恶化，必须独立审查。
5. 新增测试必须全部通过，定向套件、Ruff、diff-check和保护blob保持有效。
6. `known_environment`、`known_flaky`、`documented_main_code_failure`必须分别统计，不得混称。
7. 相对PASS不等于全仓GREEN、不等于Gate 2 PASS、不等于可merge。

## 7. 禁止项

- 不得运行pytest、Ruff、Gate 1、Gate 2、AgentCenter、浏览器E2E或真实CLI smoke。
- 不得修改`PRE_MERGE_GATES.md`、STATUS、r05、源码/tests/config或任何旧handoff。
- 不得修改或覆盖r6/r2–r5 evidence。
- 不得把85项main代码失败重新包装成环境/flaky。
- 不得仅凭nodeid相等断言失败语义相同。
- 不得签发Gate 1 PASS、Gate 2 PASS或merge许可。
- 不得启动/终止WSL进程，不得清理tmux/host/server。
- 不得stage/commit/push/merge/tag、发版或编辑PR/Issue。

## 8. 完成标准

`HERMES_GATE1_POLICY_REVIEW.md`必须包含：

1. 现行文字plain meaning与治理意图分析。
2. KEEP_STRICT与修订方案的误阻/误放风险对比。
3. 126项双侧JUnit归一化语义指纹统计和所有不同项。
4. 对41项环境、85项main代码分类的抽查结论。
5. 三选一最终建议：`KEEP_STRICT`、`RECOMMEND_POLICY_AMENDMENT`或`INSUFFICIENT_EVIDENCE`。
6. 若建议修订，提供满足§6的精确政策文字，但不编辑仓库政策。
7. 明确Gate 1仍待Codex/用户决策；Gate 2未执行、未判定；不可merge。
8. 只新增本报告；未运行测试、未改证据/源码/政策；无commit/push/merge/tag。
