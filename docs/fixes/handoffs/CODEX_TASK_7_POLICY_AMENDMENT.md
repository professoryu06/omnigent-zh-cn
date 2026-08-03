# CODEX TASK 7 POLICY AMENDMENT — 落地 documented main baseline 安全条款

**执行者：** Hermes（政策文档执行者）  
**批准者：** Codex（2026-07-29；批准受§4安全条件约束的政策修订）  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** 政策修订获Codex批准但尚未落地；Gate 1仍待文档落地后的只读验收。Gate 2未执行、未判定；不可 merge。  
**阶段边界：** 只修改`docs/fixes/PRE_MERGE_GATES.md`的Gate 1相对main政策，并新建完成报告。不得修改STATUS、源码/tests、证据或Gate结果，不得运行测试。

## 1. 批准依据与必读

必读：

1. `docs/fixes/handoffs/HERMES_GATE1_POLICY_REVIEW.md`
2. `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_5_TRIAGE.md`
3. `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_5.md`
4. `docs/fixes/PRE_MERGE_GATES.md` §1.2
5. r6 evidence：`C:\Users\Administrator\gate1-evidence\20260729-1715-dc83140-grok-r6\`

Codex只读复核：

- baseline/candidate各126个共享failure/error nodeid，candidate-only=0；
- 41项`known_environment`、0项`known_flaky`、85项`known_main_code_failure`；
- 独立归一化复算为`same_semantic=126`、`different_semantic=0`；
- 定向136 passed、Ruff/diff-check与四保护blob已有有效receipt；
- KEEP_STRICT会迫使当前有限修复承担85项无关main失败，误阻风险高；
- 逐项分类、语义指纹和显式批准可约束政策修订的误放风险。

因此批准增加第三类`documented_main_code_failure`，但不批准“任何main失败自动放行”。

## 2. 精确文件

只允许：

- 修改：`docs/fixes/PRE_MERGE_GATES.md`
- 新建：`docs/fixes/handoffs/HERMES_COMPLETION_7_POLICY_AMENDMENT.md`

不得修改：

- `docs/fixes/STATUS.md`
- `docs/fixes/POST_FIX_HANDOFF_PROMPT.md`
- 任何旧handoff
- `omnigent/`、`tests/`、`pyproject.toml`、`uv.lock`、CI
- r2–r6任何evidence

## 3. 最小文档改法

在`PRE_MERGE_GATES.md` §1.2中，用以下内容替换现有“clean main已有失败”表格行。保持绝对全绿、candidate新增失败和Windows不足三行语义不变。

```markdown
| clean main **已有**失败，且候选树失败 nodeid **⊆** main 失败集（同环境、同依赖、同隔离状态） | **Gate 1 PASS（相对 main 无新增失败）** — 必须同时满足下列“相对 PASS 安全条件”；任一缺失均不得 PASS |
```

紧接表格后、失败列表生成示例前，新增：

```markdown
#### 相对 PASS 安全条件

相对 main PASS 必须同时满足：

1. baseline 与 candidate 在同 OS、同依赖、同隔离状态下完整运行，且两侧 JUnit 均存在、非空、可解析，pytest/tee 退出码均被独立冻结。
2. candidate 失败 nodeid 集合是 baseline 的子集，`new-failures.txt` 为空；任何 candidate-only failure/error 均为 Gate 1 FAIL。
3. 每个共享失败必须有具体分类与证据，且只能分别记录为：
   - `known_environment`：可归因 Gate 执行环境缺失，例如缺包、缺服务、缺凭据、网络限制或资源布局异常；
   - `known_flaky`：有独立复现证据证明同一代码与环境下交替 pass/fail；
   - `documented_main_code_failure`：clean main 上可复现的确定性代码失败，已记录具体根因，且不属于本候选引入的回归。
4. 每个共享失败的归一化语义指纹必须在 baseline 与 candidate 之间相同。归一化可以去除树绝对路径、pytest 临时运行编号、随机 UUID/会话 ID/PID/内存地址和耗时，但必须保留异常类型、实际/期望值、HTTP 状态码、模块名、策略动作与其他影响失败语义的字段。
5. 任一共享 nodeid 的异常类型、实际/期望值、关键错误码或其他稳定语义发生变化时，视为可能恶化；必须逐项独立审查，不能仅凭 nodeid 相同计入相对 PASS。
6. 候选新增测试必须全部通过；当前候选的定向套件、Ruff、diff-check和保护 blob证据必须有效且无回归。
7. 三类baseline失败必须分别统计，不得把`documented_main_code_failure`称为环境或flaky，也不得只写“main也失败”。
8. 使用`documented_main_code_failure`形成相对PASS必须有一次明确、可审计的Codex/用户批准；报告或执行者不得自行扩大门槛。
9. 相对PASS不等于全仓GREEN，不等于Gate 2 PASS，不等于可merge。
```

随后新增政策修订记录：

```markdown
> **政策修订记录（2026-07-29，Codex显式批准）：** 原版只允许`known_environment`/`known_flaky`作为已知baseline。r6同环境双侧证据显示，clean main另有85项确定性代码失败；candidate无新增失败，126个共享失败的归一化语义指纹全部相同。为避免有限范围修复被无关main失败无限期误阻，增加`documented_main_code_failure`第三类，同时强制逐项分类、语义指纹比较、候选新增测试/定向质量证据和显式批准。该修订不追认全仓GREEN、Gate 2或merge许可。
```

## 4. 不可删除或弱化的安全条件

以下任一缺失即验收不通过：

1. 同OS、同依赖、同隔离状态与完整双侧JUnit。
2. candidate-only失败为零。
3. 三类逐项分类，不得混称。
4. 归一化语义指纹比较，且保留异常类型、实际/期望值、HTTP状态、模块名与策略动作。
5. 语义变化必须独立审查，不能只比nodeid。
6. 新增测试全部通过，定向/Ruff/diff-check/保护证据有效。
7. documented main baseline必须显式批准。
8. 相对PASS不等于全仓GREEN、Gate 2或merge。

不得把上述文字压缩成“candidate失败集⊆baseline即可PASS”。

## 5. 只读/文档验证命令

不得运行pytest、Ruff或Gate。完成编辑后只运行：

```powershell
git diff --check -- docs/fixes/PRE_MERGE_GATES.md

rg -n "documented_main_code_failure|归一化语义指纹|candidate-only|显式.*批准|不等于全仓.*GREEN|Gate 2|可merge" `
  docs/fixes/PRE_MERGE_GATES.md

git diff -- docs/fixes/PRE_MERGE_GATES.md
git status --short
```

保存编辑前后以下只读身份到完成报告：

- 源HEAD；
- 四保护blob；
- `STATUS.md` SHA-256；
- `POST_FIX_HANDOFF_PROMPT.md` SHA-256；
- 所有旧handoff文件的名称+SHA-256清单。

编辑前后除`PRE_MERGE_GATES.md`和新完成报告外必须一致。

## 6. 完成报告

`HERMES_COMPLETION_7_POLICY_AMENDMENT.md`必须包含：

1. 实际修改的文件和精确diff摘要。
2. 新表格行、九条安全条件及政策修订记录均已落地的逐项核对。
3. `git diff --check`和`rg`真实输出/退出码。
4. HEAD、四保护blob、STATUS、POST_FIX及旧handoff前后身份。
5. 明确未运行pytest/Ruff/Gate/Smoke。
6. 明确本轮只落地政策，未判定Gate 1、未执行Gate 2、不可merge。
7. 无stage/commit/push/merge/tag或PR/Issue编辑。

## 7. 禁止项

- 不得修改STATUS或把Gate 1写成PASS。
- 不得修改POST_FIX、旧handoff、源码/tests/config/lockfile/CI或evidence。
- 不得删减§4任何安全条件。
- 不得运行pytest、Ruff、Gate 1、Gate 2、AgentCenter、浏览器E2E或真实CLI smoke。
- 不得启动/终止WSL进程或清理tmux/host/server。
- 不得stage/commit/push/merge/tag、发版或编辑PR/Issue。
- 不得宣称全仓GREEN、Gate 2 PASS或可merge。

## 8. 完成标准

1. 仅`PRE_MERGE_GATES.md`发生政策修改，并只新增完成报告。
2. 第三类名称精确为`documented_main_code_failure`。
3. 九条安全条件和2026-07-29批准记录完整、无弱化。
4. `git diff --check`通过，关键短语全部可检索。
5. STATUS、POST_FIX、旧handoff、源码/tests/config/evidence零修改。
6. Gate 1仍待Codex只读验收；Gate 2未执行、未判定；不可merge。
7. 无commit/push/merge/tag。
