# CODEX TASK 7 REWORK 5 TRIAGE — 补齐相对 Gate 1 的 baseline 已知失败依据

**执行者：** Grok（r6证据分类执行者；非Gate独立审查者）  
**日期：** 2026-07-29  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** Grok报告 `PASS（相对 main）`，但Codex验收暂不接受；Gate 1仍待判定。Gate 2未执行、未判定；不可 merge。  
**阶段边界：** 只读分析已有r6 JUnit/日志并补齐126项baseline失败的真实分类依据。禁止重跑pytest/Ruff/Gate，禁止修改r6 evidence或旧报告。

## 1. 必读与固定输入

1. `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_5.md`
2. `docs/fixes/handoffs/CODEX_TASK_7_REWORK_5.md`
3. `docs/fixes/PRE_MERGE_GATES.md` §1.2
4. r6 evidence：`C:\Users\Administrator\gate1-evidence\20260729-1715-dc83140-grok-r6\`

重点文件：

- `baseline-junit.xml`
- `candidate-junit.xml`
- `baseline-pytest.txt`
- `candidate-pytest.txt`
- `baseline-fail-ids.txt`
- `candidate-fail-ids.txt`
- `new-failures.txt`
- `baseline-known-failures.md`
- `environment.txt`
- `baseline-packages.txt` / `candidate-packages.txt`
- 双侧HOME、进程分类、exit/tee与SHA证据

只允许新建交接：

`docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_5_TRIAGE.md`

不得修改 `GROK_COMPLETION_7_REWORK_5.md`、`baseline-known-failures.md` 或r6 evidence。

## 2. 问题与验收缺口

r6双侧运行本身已只读核对：

- baseline/candidate均exit 1、tee 0、JUnit可解析；
- 两侧JUnit失败/错误nodeid各126项，集合完全相等；
- `new-failures.txt`为空；
- 两侧隔离HOME seed、包列表、身份、保护与blocking进程证据匹配。

但现有 `baseline-known-failures.md` 不满足相对PASS的最后条件：

- 126个section全部使用相同模板；
- 126项都只写“在main HEAD baseline中观察到”与相同证据路径；
- 没有给出具体环境根因、flaky历史或分类依据；
- 文件自己明确写着“Not claimed as intentional product bugs without further triage”。

`PRE_MERGE_GATES.md`与任务卡均要求每个baseline失败标明已知环境/已知flaky依据，并明确禁止仅用“baseline也失败”代替原因。

因此当前只能确认“candidate没有新增失败”；还不能确认所有126项都符合允许相对PASS的baseline known条件。

## 3. 失败证据概况

Codex只读解析r6 baseline JUnit得到126个failure/error。高频消息包括：

| 数量 | JUnit首条消息示例 |
|---:|---|
| 12 | `runner_unavailable: No runner bound for session` |
| 10 | `KeyError: 'ag_test/abc123'` |
| 7 | `TimeoutError` |
| 6 | `ModuleNotFoundError: No module named 'deploy.docker'` |
| 5 | `forwarder never reached the expected state` |
| 4 | policy allow/deny assertion mismatch |
| 4 | `pytest-timeout >300s` |
| 3 | `ModuleNotFoundError: No module named 'psycopg'` |
| 3 | Polly resource `NotADirectoryError`（setup error） |
| 其余 | CLI allowlist、native fork history、runner状态、guardrail等断言 |

这些消息显然不都能仅凭“main也失败”自动归为环境或flaky。必须逐组分析。

## 4. 最小改法：分组根因 + 126项精确映射

不得为126项机械重复同一句话。先建立根因组，再把每个nodeid精确映射到一个组。

每个根因组必须包含：

1. `group_id`：稳定短标识，例如 `ENV_NO_RUNNER`、`ENV_MISSING_PSYCOPG`、`FLAKY_TIMEOUT_X`、`MAIN_CODE_ASSERTION_X`、`UNCLASSIFIED_X`。
2. `category`，只能取：
   - `known_environment`
   - `known_flaky`
   - `known_main_code_failure`
   - `unclassified`
3. 具体根因：说明缺失了什么环境条件、为何会超时/波动，或哪项main代码行为与断言不符。
4. 证据：必须引用r6 JUnit message/traceback、pytest日志或只读环境/package/HOME证据；可以引用r4同nodeid历史结果作为重复性辅助。
5. `relative_gate_eligible`：`yes`或`no`。

资格规则：

- `known_environment`：只有证据明确表明Gate环境缺外部服务、credential、runner、可选依赖或隔离HOME状态时才可`yes`。
- `known_flaky`：必须有至少两次同环境历史表现、明确随机/时序特征或项目已有flaky标注；一次timeout不能自动叫flaky。
- `known_main_code_failure`：可诚实记录为main既有代码失败，但按当前Gate规格**不能**冒充已知环境/flaky，`relative_gate_eligible=no`。
- `unclassified`：必须`no`。
- “candidate也失败”“baseline是main”“失败集相等”只能证明无新增，不能作为根因或资格依据。

允许多个nodeid引用同一根因组，但每个nodeid必须在映射中出现且只能出现一次。

## 5. 报告固定格式

`GROK_COMPLETION_7_REWORK_5_TRIAGE.md` 必须依次包含：

### 5.1 r6不变事实

- 两侧summary、exit/tee/JUnit状态；
- 126/126且集合相等；
- new-failures空；
- 明确本轮未重跑任何测试。

### 5.2 根因组

每组使用以下完整字段：

```markdown
### GROUP `<group_id>`
- category: `<allowed category>`
- relative_gate_eligible: `yes|no`
- node_count: `<N>`
- root_cause: `<具体原因>`
- evidence: `<具体r6文件、JUnit消息/traceback或历史证据>`
- limitation: `<仍不能证明的部分；无则写 none>`
```

### 5.3 可机器核对的126项映射

必须包含以下标记和TAB分隔正文：

```text
BEGIN_NODE_MAP
<exact dotted nodeid>\t<failure|error|timeout>\t<group_id>\t<yes|no>
...
END_NODE_MAP
```

nodeid必须逐字来自r6 `baseline-fail-ids.txt`。第四列必须等于对应group的`relative_gate_eligible`。

### 5.4 分类统计与结论

列出每个category的组数、node数和eligible yes/no数。

结论只能二选一：

- `RELATIVE_PASS_EVIDENCE_COMPLETE`：126项全部属于有具体依据的`known_environment`或`known_flaky`，且全部eligible=yes。
- `RELATIVE_PASS_EVIDENCE_INCOMPLETE`：任一项属于`known_main_code_failure`、`unclassified`，或依据不足/eligible=no。

不得自行把第二种结论写成Gate PASS。最终Gate判定仍由Codex验收。

## 6. 只读分析与自检命令

允许读取、解析和统计现有文件；禁止执行pytest/Ruff或任何产品CLI smoke。

完成报告后，用以下Python只读核对映射完整性：

```bash
python - \
  'C:/Users/Administrator/gate1-evidence/20260729-1715-dc83140-grok-r6/baseline-fail-ids.txt' \
  'docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_5_TRIAGE.md' <<'PY'
from pathlib import Path
import sys

expected_path = Path(sys.argv[1])
report_path = Path(sys.argv[2])
expected = [line for line in expected_path.read_text(encoding="utf-8").splitlines() if line]
text = report_path.read_text(encoding="utf-8")
body = text.split("BEGIN_NODE_MAP\n", 1)[1].split("\nEND_NODE_MAP", 1)[0]
rows = [line for line in body.splitlines() if line]

parsed = []
for line in rows:
    fields = line.split("\t")
    assert len(fields) == 4, line
    nodeid, kind, group_id, eligible = fields
    assert kind in {"failure", "error", "timeout"}, line
    assert group_id, line
    assert eligible in {"yes", "no"}, line
    parsed.append(nodeid)

assert len(expected) == 126, len(expected)
assert len(parsed) == 126, len(parsed)
assert len(set(parsed)) == 126, "duplicate nodeid"
assert sorted(parsed) == sorted(expected), "missing or extra nodeid"
print("TRIAGE_NODE_MAP_OK count=126")
PY
```

Windows路径在WSL执行时改用对应`/mnt/c/...`绝对路径，但不得改动输入文件。

报告还必须记录：

- `SECTION/GROUP`数量；
- 四类node统计；
- eligible yes/no总数；
- 上述自检真实exit与输出。

## 7. 禁止项

- 不得运行pytest、Ruff、Gate 1、Gate 2、AgentCenter、浏览器E2E或真实CLI smoke。
- 不得修改、覆盖、追加r6 evidence或r2–r5旧证据。
- 不得修改`GROK_COMPLETION_7_REWORK_5.md`或任何旧handoff。
- 不得修改`omnigent/`、`tests/`、`pyproject.toml`、`uv.lock`、CI或r05。
- 不得把“失败集相等”自动写成known environment/flaky。
- 不得把一次timeout自动写成known flaky。
- 不得把`known_main_code_failure`标eligible=yes。
- 不得启动/终止任何WSL进程，不得清理tmux/host/server。
- 不得stage/commit/push/merge/tag、发版或编辑PR/Issue。
- 不得执行Gate 2或宣称可merge。

## 8. 完成标准

1. 只新增`GROK_COMPLETION_7_REWORK_5_TRIAGE.md`。
2. r6证据与源代码/tests/config/旧handoff零修改。
3. 126个baseline nodeid逐字、唯一、完整映射到根因组。
4. 每组有具体root cause、证据、限制与资格，不使用通用模板冒充原因。
5. 机器自检输出`TRIAGE_NODE_MAP_OK count=126`。
6. 最终结论严格为`RELATIVE_PASS_EVIDENCE_COMPLETE`或`RELATIVE_PASS_EVIDENCE_INCOMPLETE`。
7. 不重新运行任何测试/Gate；Gate 2仍未执行、未判定；无commit/push/merge/tag。
8. 只有`RELATIVE_PASS_EVIDENCE_COMPLETE`经Codex再次只读验收后，才可生成Gate 2任务卡。
