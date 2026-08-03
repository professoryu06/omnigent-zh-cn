# CODEX TASK 7 REWORK 2 — Gate 1 剩余全仓复跑（Grok）

**执行者：** Grok（Gate 1 执行者；本轮不是独立审查者）  
**日期：** 2026-07-29  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** Gate 1=`INVALID`；Gate 2=未执行、未判定；不可 merge。  
**阶段边界：** 只补齐 Gate 1 的 baseline/candidate Linux 全仓 pytest 与失败集证据。不得修改产品源码、测试、配置或既有报告；不得执行 Gate 2。

## 1. 必读

1. `docs/fixes/handoffs/HERMES_COMPLETION_7_REWORK.md`
2. `docs/fixes/handoffs/CODEX_TASK_7_REWORK.md`
3. `docs/fixes/handoffs/CODEX_TASK_7.md`
4. `docs/fixes/PRE_MERGE_GATES.md`
5. `pyproject.toml` 第 217–225、311–323 行的 pytest-timeout 说明

完成报告只允许新建：

`docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_2.md`

不得修改上述必读文件，也不得修改 `HERMES_COMPLETION_7_REWORK.md` 来修饰旧证据。

## 2. 问题与已确认事实

第二次 Gate 1 仍为 `INVALID`，原因是 baseline/candidate 全仓 pytest 都未形成可解析 JUnit，不能比较完整失败集。

本轮必须按以下事实处理，不得沿用旧报告中的错误推断：

- `pyproject.toml` 的 `timeout = 300` 是**每个测试的 wallclock 上限**，不是 15,000 多项测试的全套总时限。
- `timeout_method = "thread"` 在单测超时后会终止整个 pytest 进程，所以旧 run 无 JUnit；这不证明“全套总时间超限”。
- 旧候选日志实际写的是 `Running 15242 items in this shard`，并至少运行到约 `57%`，不是报告所写的 `15162 / 3–4%`。
- 旧 `baseline-pytest.txt` 已被覆盖到只剩 structlog 一行；旧证据不能证明 baseline 与 candidate 在同一 nodeid 超时。
- 旧 run 没有完整 case 级失败集，因此空的 `new-failures.txt` 只表示“没有可比较数据”，不能作为 `0 new failures` 的 Gate 结论。
- 旧 run 中定向 `136 passed`、Ruff clean、tracked/untracked diff-check 与四个保护 blob 是正面证据；只有在复用身份核验全部通过时，本轮可以引用，不能冒充全仓 GREEN。

禁止用 `-p no:timeout` 形成 Gate PASS。禁用插件会移除项目明确要求的单测挂起保护。也禁止把每测试上限提高到 3600 秒后宣称与标准 Gate 等价。

## 3. 精确路径与固定身份

### 3.1 只读源工作树

`F:\codex-ai\git项目部署\tmp\omnigent-review`

源 HEAD 必须仍为：

`dc83140c73ceb12fa165753c1880c19f68da86f4`

四个保护 blob 必须仍为：

| 名称 | 文件 | 期望 blob |
|---|---|---|
| workspace | `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` |
| model | `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` |
| idle | `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` |
| serve | `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` |

注意：serve 保护对象是 `tests/.../test_serve.py`，不是产品文件 `omnigent/.../serve.py`。

### 3.2 可复用 WSL 树

- baseline：`/tmp/omnigent-gate1-baseline-20260729-0106-dc83140-r2/`
- candidate：`/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2/`
- baseline HEAD：`81594243f7a17303b9ba477b938ac323f938c2e4`
- candidate HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`，并包含已验证 dirty candidate patch/untracked 文件

### 3.3 旧证据（只读）

`C:\Users\Administrator\gate1-evidence\20260729-0106-dc83140-r2\`

不得覆盖或追加旧证据中的任何文件。为本轮创建全新的动态 run：

```bash
RUN_ID="$(date +%Y%m%d-%H%M)-dc83140-grok-r3"
LINUX_EVIDENCE_ROOT="/tmp/omnigent-premerge-evidence/$RUN_ID"
EVIDENCE_ROOT="/mnt/c/Users/Administrator/gate1-evidence/$RUN_ID"
mkdir -p "$LINUX_EVIDENCE_ROOT" "$EVIDENCE_ROOT"
printf '%s\n' "$RUN_ID" > "$EVIDENCE_ROOT/run-id.txt"
```

临时执行日志先写 Linux evidence，再复制到 Windows evidence，避免 WSL/NTFS 管道写入不稳定；最终两处的 SHA-256 必须一致。

## 4. 最小执行法

### 4.1 只复用，不重复已完成检查

本轮默认复用旧树、`.venv` 与第二次 run 已通过的 sync/import/collect/定向/Ruff/diff-check。不要重新运行定向 pytest、Ruff 或 Gate 2。

复用前必须只读核验并保存 receipt：

```bash
set -euo pipefail
BASELINE_TREE='/tmp/omnigent-gate1-baseline-20260729-0106-dc83140-r2'
CANDIDATE_TREE='/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2'
OLD_EVIDENCE='/mnt/c/Users/Administrator/gate1-evidence/20260729-0106-dc83140-r2'

test -d "$BASELINE_TREE/.venv"
test -d "$CANDIDATE_TREE/.venv"
test "$(git -C "$BASELINE_TREE" rev-parse HEAD)" = '81594243f7a17303b9ba477b938ac323f938c2e4'
test "$(git -C "$CANDIDATE_TREE" rev-parse HEAD)" = 'dc83140c73ceb12fa165753c1880c19f68da86f4'

git -C "$CANDIDATE_TREE" status --short > "$LINUX_EVIDENCE_ROOT/candidate-status-reuse.txt"
git -C "$CANDIDATE_TREE" diff --binary HEAD > "$LINUX_EVIDENCE_ROOT/candidate-patch-reuse.patch"
cmp "$LINUX_EVIDENCE_ROOT/candidate-status-reuse.txt" "$OLD_EVIDENCE/candidate-status.txt"
cmp "$LINUX_EVIDENCE_ROOT/candidate-patch-reuse.patch" "$OLD_EVIDENCE/reconstructed-candidate.patch"

sha256sum \
  "$OLD_EVIDENCE/candidate-status.txt" \
  "$OLD_EVIDENCE/reconstructed-candidate.patch" \
  "$OLD_EVIDENCE/targeted-current.txt" \
  "$OLD_EVIDENCE/ruff.txt" \
  "$OLD_EVIDENCE/diff-check-tracked.txt" \
  "$OLD_EVIDENCE/diff-check-untracked.txt" \
  "$OLD_EVIDENCE/candidate-protection-blobs.txt" \
  > "$LINUX_EVIDENCE_ROOT/reused-evidence.sha256"
```

还必须按 `CODEX_TASK_7_REWORK.md` §4 的相同算法重新生成 candidate tracked/untracked manifest 与 untracked blob map，并分别与旧 evidence 的 `reconstructed-*` 文件 `cmp`。四项均为零才允许复用。

运行前记录：

```bash
ps -ef | grep -E '/tmp/omnigent-gate1-(baseline|candidate)-20260729-0106-dc83140-r2' \
  | grep -v grep > "$LINUX_EVIDENCE_ROOT/pre-run-processes.txt" || true
```

若存在仍在运行的旧 pytest/runner/host 子进程，停止本轮并判 `INVALID`；不得 broad `pkill` 或杀其他 WSL 工作负载。若树、`.venv`、HEAD、status、patch、manifest、blob 任一不匹配，也停止并判 `INVALID`，不得在本卡内重建或修源工作树。

### 4.2 保留 300 秒保护并让 JUnit 可落盘

本轮只允许在 WSL2 Ubuntu 24.04 上把 timeout 处理方法从 `thread` 临时覆盖为 `signal`；仍保留每测试 300 秒上限。目的仅是让超时成为可审计的 case 级失败并允许 session 继续产生完整 JUnit，而不是跳过超时。

对 baseline、candidate 顺序执行以下函数。外层 6 小时 watchdog 只防基础设施永久卡死；它不是 pytest 单测上限。

```bash
run_full_suite() {
  label="$1"
  tree="$2"
  log="$LINUX_EVIDENCE_ROOT/${label}-pytest.txt"
  junit="$LINUX_EVIDENCE_ROOT/${label}-junit.xml"

  cd "$tree"
  set +e
  set -o pipefail
  PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=60s 21600s \
    uv run pytest -q --color=no \
      --timeout=300 --timeout-method=signal \
      --junitxml="$junit" 2>&1 | tee "$log"
  statuses=("${PIPESTATUS[@]}")
  command_exit="${statuses[0]}"
  tee_exit="${statuses[1]}"
  set +o pipefail
  set -e
  set -o pipefail

  printf '%s\n' "$command_exit" > "$LINUX_EVIDENCE_ROOT/${label}-pytest.exit"
  printf '%s\n' "$tee_exit" > "$LINUX_EVIDENCE_ROOT/${label}-tee.exit"
  printf 'COMMAND_EXIT:%s\nTEE_EXIT:%s\n' "$command_exit" "$tee_exit" \
    | tee -a "$log"
}

run_full_suite baseline "$BASELINE_TREE"
run_full_suite candidate "$CANDIDATE_TREE"
```

禁止并行跑两棵全仓树；它们必须在同一 WSL 实例、同一依赖锁定环境类别中顺序运行，以免资源竞争污染对照。

若任一 `command_exit=124`、外层 watchdog 介入、WSL 崩溃、tee 非零、JUnit 缺失/空/不可解析、pytest internal/collection error，则 Gate 1=`INVALID`，不得继续拼接旧 run 或宣称相对 PASS。

### 4.3 JUnit、失败 nodeid 与新失败

两次 session 都正常到达 pytest summary 后：

```bash
for label in baseline candidate; do
  test -s "$LINUX_EVIDENCE_ROOT/${label}-junit.xml"
  python3 -c 'import sys, xml.etree.ElementTree as ET; ET.parse(sys.argv[1]); print("junit-ok")' \
    "$LINUX_EVIDENCE_ROOT/${label}-junit.xml" \
    > "$LINUX_EVIDENCE_ROOT/${label}-junit-parse.txt"

  awk '/^(FAILED|ERROR) / {print $2}' "$LINUX_EVIDENCE_ROOT/${label}-pytest.txt" \
    | sed 's/[[:space:]]*$//' | sort -u \
    > "$LINUX_EVIDENCE_ROOT/${label}-fail-ids.txt"
done

comm -13 \
  "$LINUX_EVIDENCE_ROOT/baseline-fail-ids.txt" \
  "$LINUX_EVIDENCE_ROOT/candidate-fail-ids.txt" \
  > "$LINUX_EVIDENCE_ROOT/new-failures.txt"
```

如果 pytest exit 非零而 `*-fail-ids.txt` 为空，先核对 JUnit 中是否有 case 级 failure/error。不能从日志/JUnit生成完整 nodeid 时判 `INVALID`，不得把空集写成无新增失败。

若 baseline 有失败，必须创建 `baseline-known-failures.md`，逐一列出每个 baseline nodeid、失败类型（含 timeout）、同环境证据与为何属于 main 基线。仅写“baseline 也失败”不够。若 baseline 绝对全绿，文件写 `None — baseline absolute green.`。

### 4.4 持久化与源树保护

将本轮 Linux evidence 全量复制到新的 Windows evidence 根，生成双方 SHA-256 清单并逐项比对。不得覆盖 r2 证据。

运行结束后用 Windows Git只读核对源 HEAD、`git status --short` 与四个保护 blob；必须与运行前完全一致。只允许源工作树新增本报告文件，不允许源码/tests/config/lockfile或既有 handoff 变化。

## 5. 判定规则

- **PASS（绝对）：** candidate 全仓 exit 0、JUnit有效、复用 receipt 全部匹配，且旧定向/Ruff/diff-check/保护证据有效。
- **PASS（相对 main）：** baseline/candidate 都完整结束并有有效 JUnit；candidate 失败集是 baseline 失败集子集；`new-failures.txt` 为空；每个 baseline case 失败在 known 文件有同环境依据；复用证据全部有效。
- **FAIL：** candidate 出现 baseline 没有的真实 case failure/error，或候选保护/质量检查发生真实回归。
- **INVALID：** 运行未完成、watchdog/WSL/tee/JUnit/证据/复用身份损坏、collection/internal error，或失败集不可审计。

`--timeout-method=signal` 的命令行偏差必须在报告中显式写明。它仍保留 300 秒单测上限；不得描述为默认 `thread` 模式通过。

任何 PASS 只允许 Codex验收并策划 Gate 2；**不代表 Gate 2 PASS，不代表可 merge。**

## 6. 禁止项

- 不得修改 `omnigent/`、`tests/`、`pyproject.toml`、`uv.lock`、CI、r05 文档或既有 handoff。
- 不得运行 `-p no:timeout`，不得提高 300 秒单测上限来掩盖挂起，不得加 skip/xfail、删测试或挑选性排除失败 nodeid。
- 不得重跑定向 pytest、Ruff、diff-check、Gate 2、AgentCenter smoke、浏览器 E2E或真实 Codex CLI smoke；本轮只补全仓缺口。
- 不得把旧 `new-failures.txt` 空文件当作有效无新增结论。
- 不得覆盖任何旧 evidence；不得拼接不同 run 的 baseline/candidate 全仓结果。
- 不得 checkout/switch/fetch/pull/rebase/cherry-pick/stash/reset/clean 源工作树。
- 不得 stage/commit/push/merge/tag、发版或编辑 PR/Issue。
- 不得让 Grok在本报告中签发 merge 许可；Gate 结果仍需 Codex只读验收。

## 7. 完成报告必须包含

`GROK_COMPLETION_7_REWORK_2.md` 至少写明：

1. 新 `RUN_ID`、Linux/Windows evidence 绝对路径及双方 SHA-256 比对结果。
2. 两棵复用树的 HEAD、`.venv`、status/patch/manifest/blob `cmp` 结果与 reused evidence receipt。
3. 对旧报告 `15162 / 3–4% / 同位置 / new-failures=0` 不可审计之处的纠正说明。
4. baseline/candidate 完整命令、pytest/tee退出码、summary、JUnit路径和 parse 结果。
5. baseline/candidate 全部失败 nodeid、`new-failures.txt` 内容、`baseline-known-failures.md` 逐项依据。
6. `--timeout-method=signal` 是本轮命令行证据模式，仍为每测试 300 秒；未使用 `-p no:timeout`。
7. 旧定向 `136 passed`、Ruff/diff-check与四保护 blob仅作为经 receipt 核验的既有证据引用，未重跑。
8. 源工作树运行前后 HEAD/status/四保护 blob无变化；只新增本报告。
9. Gate 1最终只能是 `PASS（绝对）`、`PASS（相对 main）`、`FAIL`或`INVALID`之一，并逐条对照本卡规则。
10. Gate 2仍未执行、未判定；不代表可 merge；无commit/push/merge/tag。

## 8. 完成标准

1. 不覆盖旧证据，且复用树身份/快照/保护检查全部可审计。
2. baseline与candidate全仓均真实跑到pytest summary并生成可解析JUnit；否则诚实判`INVALID`。
3. 失败nodeid与新增失败由本轮完整run产生，不使用旧空列表冒充。
4. 300秒单测保护仍启用；未禁用timeout插件，未提高单测上限。
5. Gate 1判定严格符合§5；任何PASS仍待Codex只读验收。
6. 只新增`GROK_COMPLETION_7_REWORK_2.md`；未修改源码/tests/config/旧报告，未执行Gate 2，未commit/push/merge/tag。
