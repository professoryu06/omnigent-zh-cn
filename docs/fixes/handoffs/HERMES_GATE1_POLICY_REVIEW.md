# HERMES GATE 1 POLICY REVIEW — 独立政策审查

**审查者：** Hermes（独立政策审查者；非 Grok）
**日期：** 2026-07-29
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
**证据根（只读）：** `C:\Users\Administrator\gate1-evidence\20260729-1715-dc83140-grok-r6\`

---

## 最终建议

**`RECOMMEND_POLICY_AMENDMENT`**

---

## 1. 现行文字 plain meaning 与治理意图

### 1.1 PRE_MERGE_GATES.md §1.2 关键语句

> 集成树 `pytest -q` **绝对全绿**（0 failed, 0 errors） → **Gate 1 PASS（绝对全绿）**

> clean main **已有**失败，且集成树失败 nodeid **⊆** main 失败集（同环境、同依赖） → **Gate 1 PASS（相对 main 无新增失败）** — 必须在 `baseline-fail-ids.txt` / `integrate-fail-ids.txt` 列出两边失败 nodeid，并标注每个基线失败「**已知环境/已知 flaky**」

> 集成树出现 main **没有**的失败或 error → **Gate 1 FAIL** — 阻塞 merge

### 1.2 Plain meaning

相对 PASS 的限定词是「已知环境/已知 flaky」。这是一个**封闭枚举**：只有两类失败可以作为已知 baseline：

1. **已知环境**（known_environment）：失败可归因于 Gate 执行环境缺失（缺包、缺服务、缺凭据、缺资源布局），而非 main 代码逻辑。
2. **已知 flaky**（known_flaky）：失败在同一代码上交替 pass/fail，有独立复现证据。

**确定性 main 代码失败**（deterministic code failure on main）不在此枚举内。85 项 `known_main_code_failure` 按现行文字**不能**作为相对 PASS 的已知 baseline。

### 1.3 治理意图推断

Gate 1 的设计意图是**回归门槛**：证明候选不引入新破坏。但限定词「已知环境/已知 flaky」反映了一个更严格的假设：**clean main 应该是全绿的，或者只有环境/flaky 噪声**。当 main 有 85 个确定性代码失败时，这个假设不成立。

这不是源码审查问题，而是**门槛语义与现实不匹配**的问题。

### 1.4 不能用审查报告暗中替代政策修改

本报告不修改 `PRE_MERGE_GATES.md`。如果允许 main 代码失败作为 baseline，必须通过显式政策修订，不能通过解释性改写。

---

## 2. KEEP_STRICT vs RECOMMEND_POLICY_AMENDMENT 风险对比

### 2.1 KEEP_STRICT 误阻风险

| 风险 | 评估 |
|---|---|
| Gate 永远无法推进 | **高**。85 项 main 代码失败不属于当前 Omnigent 修复范围（#3016/#3175/#3178/#3060/#2853），修复它们需要跨范围工作。 |
| 迫使跨范围修复 | **高**。为通过 Gate 1 必须修复 85 项无关 main 失败，远超当前 PR 范围。 |
| 等待 main 更新 | **不确定**。main 何时修复这 85 项不可预测。 |
| 候选实际安全性 | 候选无新增失败、定向 136 passed、Ruff clean、保护 blob 全匹配——实际回归风险极低。 |

**结论：KEEP_STRICT 的误阻风险高，可能导致 Gate 无限期阻塞。**

### 2.2 RECOMMEND_POLICY_AMENDMENT 误放风险

| 风险 | 评估 | 缓解 |
|---|---|---|
| 同 nodeid 仍失败但错误原因变坏 | **中**。仅比较 nodeid 不够。 | 要求归一化语义指纹相同（本报告 §3 已验证 126/126 相同）。 |
| 大量代码路径无 GREEN 覆盖 | **中**。126 项失败意味着相关路径未被验证。 | Gate 2 AgentCenter smoke 覆盖关键真实流程；定向 136 passed 覆盖本次修复。 |
| 政策修订被滥用 | **低**。 | 修订文字要求逐项分类、指纹比较、显式批准。 |

**结论：误放风险可通过语义指纹 + 逐项分类 + 显式批准充分缓解。**

---

## 3. 126 项双侧 JUnit 归一化语义指纹

### 3.1 方法

只读解析 r6 双侧 JUnit XML（`baseline-junit.xml`、`candidate-junit.xml`），对 126 个共享 nodeid 比较：

- 异常类型（`type` 属性）
- 归一化消息（`message` 属性）

归一化规则：
- **去除**：树绝对路径（`/tmp/omnigent-gate1-*`、`/mnt/*`、`C:\*`）、UUID、session/conv/runner ID、PID、内存地址（`0x...`）、耗时（`N.Ns`）、端口号、pytest 运行编号（`pytest-N`）、随机 hex ID（`elicit_<hex>`）
- **保留**：异常类型、实际/期望值、HTTP 状态码、模块名、策略动作、断言表达式

### 3.2 结果

| 指标 | 数量 |
|---|---|
| **same_semantic_fingerprint** | **126** |
| **different_semantic_fingerprint** | **0** |

初始比较显示 2 项"不同"，经二次归一化确认为伪差异：

1. `test_egress_allows_matching_https_get[linux_bwrap]`：差异仅为 `pytest-7` vs `pytest-8`（pytest 临时目录运行编号），归一化后相同。
2. `test_non_mcp_entry_popped_by_events_handler_on_accept`：差异仅为 `elicit_2ea710ae...` vs `elicit_b929fa62...`（随机 relay hex ID），断言消息、异常类型、语义内容完全相同。

**结论：126 个共享失败全部具有相同的归一化语义指纹。Candidate 未使任何共享失败的错误原因变坏。**

---

## 4. 41 项环境 / 85 项 main 代码分类抽查

### 4.1 环境类（41 项，eligible=yes）

抽查 6 个根因组：

| 组 | 数量 | 根因 | 抽查结论 |
|---|---|---|---|
| ENV_MISSING_PSYCOPG | 3 | 缺 psycopg 包 | ✅ 环境 |
| ENV_MISSING_DEPLOY_DOCKER | 6 | 缺 deploy.docker 模块 | ✅ 环境 |
| ENV_POLLY_RESOURCE_NOT_DIRECTORY | 3 | 资源布局损坏 | ✅ 环境 |
| ENV_BUNDLED_EXAMPLE_NOT_DIRECTORY | 9 | 打包示例解析失败 | ✅ 环境 |
| ENV_NO_RUNNER_BOUND | 16 | 无 runner 绑定（503） | ✅ 环境 |
| ENV_ISOLATED_HOME_NO_DEFAULT_CREDENTIAL | 3 | 隔离 HOME 无凭据 | ✅ 环境 |
| ENV_BWRAP_EGRESS_NETWORK | 1 | 沙箱出口 403 | ✅ 环境 |

分类合理，均为 Gate 执行环境缺失，非代码逻辑问题。

### 4.2 Main 代码类（85 项，eligible=no）

抽查 4 个根因组：

| 组 | 数量 | 根因 | 抽查结论 |
|---|---|---|---|
| MAIN_INTEGRATION_HANG_TIMEOUT | 11 | 集成测试 300s 超时 | ✅ 确定性代码失败（无 flaky 证据） |
| MAIN_POLICY_FIXTURE_KEYERROR | 10 | 测试夹具 KeyError | ✅ 确定性代码失败 |
| 其余 22 组 | 64 | 各类 main 代码/测试契约不一致 | ✅ 确定性代码失败 |

分类合理。这些是 main 上的确定性代码失败，不是环境或 flaky。按现行文字不能作为相对 PASS 的已知 baseline。

---

## 5. 建议政策修订文字

以下为 `PRE_MERGE_GATES.md` §1.2 的**建议修订**（不编辑文件，仅供 Codex/用户决策）：

### 建议替换 §1.2 表格第二行

**现行文字：**

> clean main **已有**失败，且集成树失败 nodeid **⊆** main 失败集（同环境、同依赖） → **Gate 1 PASS（相对 main 无新增失败）** — 必须在 `baseline-fail-ids.txt` / `integrate-fail-ids.txt` 列出两边失败 nodeid，并标注每个基线失败「已知环境/已知 flaky」

**建议文字：**

> clean main **已有**失败，且候选树失败 nodeid **⊆** main 失败集（同环境、同依赖、同隔离状态） → **Gate 1 PASS（相对 main 无新增失败）** — 必须同时满足以下全部条件：
>
> 1. baseline 与 candidate 在同 OS、同依赖（`uv sync --locked --extra dev --extra all`）、同隔离 HOME 下完整运行，JUnit 可解析。
> 2. candidate 失败 nodeid 集合是 baseline 子集；candidate-only 失败为零。
> 3. 每个共享失败必须有具体分类与证据，分为三类且不得混称：
>    - `known_environment`：可归因 Gate 执行环境缺失（缺包/缺服务/缺凭据/缺资源布局）。
>    - `known_flaky`：有独立复现证据证明同代码交替 pass/fail。
>    - `documented_main_code_failure`：main 上的确定性代码失败，在同环境可复现，已具体记录根因。
> 4. 每个共享失败的归一化语义指纹（去除路径/UUID/PID/地址/耗时，保留异常类型/实际期望值/HTTP 状态/模块名/策略动作）必须 baseline 与 candidate 相同；异常类型、实际/期望值或关键错误码变化视为可能恶化，必须独立审查。
> 5. 新增测试必须全部通过；定向套件、Ruff、diff-check 和保护 blob 保持有效。
> 6. 三类失败必须分别统计，不得混称。`documented_main_code_failure` 不得称为环境或 flaky。
> 7. 相对 PASS 不等于全仓 GREEN、不等于 Gate 2 PASS、不等于可 merge。

### 建议新增脚注

> **政策修订记录：** 原版仅允许 `known_environment` / `known_flaky` 作为已知 baseline。r6 证据证明 main 有 85 项确定性代码失败（非环境/flaky），候选无新增且 126 项共享失败语义指纹完全相同。为解除误阻，增加 `documented_main_code_failure` 第三类，但要求逐项分类、语义指纹比较和显式批准。本修订须由 Codex/用户显式批准后生效。

---

## 6. 安全条件核对（§6）

| 条件 | r6 证据 | 状态 |
|---|---|---|
| 同 OS/依赖/隔离完整运行 + 有效 JUnit | Ubuntu 24.04 / uv locked --extra dev --extra all / 隔离 HOME / JUnit 可解析 | ✅ |
| candidate 失败 ⊆ baseline，candidate-only = 0 | 126 = 126，new-failures.txt 空 | ✅ |
| 每个共享失败有具体分类 | Grok triage 30 组，41 env + 85 main code，0 unclassified | ✅ |
| 归一化语义指纹相同 | 126/126 same（本报告 §3） | ✅ |
| 新增测试全通过，定向/Ruff/diff-check/blob 有效 | 定向 136 passed，Ruff clean，diff-check clean，四 blob 匹配 | ✅ |
| 三类分别统计 | 41 env / 0 flaky / 85 main code | ✅ |
| 相对 PASS ≠ 全仓 GREEN ≠ Gate 2 ≠ merge | 明确声明 | ✅ |

---

## 7. Gate 状态声明

- **Gate 1 最终状态仍由 Codex/用户决定。** 本报告仅建议政策修订，不签发 Gate 1 PASS。
- **Gate 2 未执行、未判定。**
- **不可 merge。**
- 政策修订须由 Codex/用户显式批准后才能生效。
- 即使政策修订生效且 Gate 1 相对 PASS，Gate 2 仍为独立阻塞项。

---

## 8. 禁止项遵守声明

- 未运行 pytest、Ruff、Gate 1、Gate 2、AgentCenter、浏览器 E2E 或真实 CLI smoke。
- 未修改 `PRE_MERGE_GATES.md`、STATUS、r05、源码/tests/config 或任何旧 handoff。
- 未修改或覆盖 r6/r2–r5 evidence。
- 未把 85 项 main 代码失败重新包装成环境/flaky。
- 未仅凭 nodeid 相等断言失败语义相同（已做归一化指纹比较）。
- 未签发 Gate 1 PASS、Gate 2 PASS 或 merge 许可。
- 未启动/终止 WSL 进程，未清理 tmux/host/server。
- 未 stage/commit/push/merge/tag、发版或编辑 PR/Issue。
- 只新增本报告。
