# CODEX TASK 7 — Gate 1 Linux 全仓执行与证据

**执行者：** Hermes（Gate 1执行者）

**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**阶段边界：** 只执行 Gate 1。不得执行 Gate 2，不得修改源工作树的源码、测试、r05或既有handoff，不得commit/push/merge/tag。Gate 1结果只能记录为 `PASS（绝对）`、`PASS（相对 main）`、`FAIL`、`INVALID`或`NOT_EXECUTED`；不得预设PASS。

## 1. 问题与目标

阶段 6结论为 `approve`：P0无、P1无，允许进入Gate策划但不代表可merge。三项P2继续保留：

1. Grok返工缺少实际pre-fix RED退出码。
2. 真实Codex CLI smoke未运行。
3. `HERMES_COMPLETION_5.md` 对旧测试链的措辞过宽。

Gate 1必须在Ubuntu 22.04/24.04 x86_64、Python 3.12、uv locked依赖下，对同一环境中的clean main和当前候选运行全仓pytest。当前候选不是某个已提交SHA，而是：

```text
候选 = HEAD dc83140c73ceb12fa165753c1880c19f68da86f4
     + 当前源工作树中 omnigent/ 与 tests/ 的累计dirty/untracked改动
```

不得继续使用 `PRE_MERGE_GATES.md` 中PR #3/#4/#5示例SHA来冒充当前候选；这些远端PR不包含阶段1/3/5全部累计返工。候选必须被快照、哈希并复制到Linux临时树后执行。

Gate 1目标：

- 优先证明候选全仓绝对全绿。
- 若clean main已有失败，只能在候选失败nodeid是main失败集子集、无新增失败且每个基线失败有同环境已知原因时判为相对PASS。
- 任一候选新增失败为FAIL。
- 证据捕获无效、环境不合格或候选快照不可复现时不得PASS。

## 2. 必读与精确文件

必读：

1. `docs/fixes/PRE_MERGE_GATES.md`（Gate 0与Gate 1权威规则）
2. `docs/fixes/STATUS.md`
3. `docs/fixes/handoffs/CODEX_TASK_6.md`
4. `docs/fixes/handoffs/HERMES_REVIEW_6.md`
5. `docs/fixes/handoffs/GROK_COMPLETION_5_REWORK.md`
6. `docs/fixes/handoffs/HERMES_COMPLETION_5.md`

源工作树保护文件：

7. `tests/runner/test_session_workspace_cache.py`
8. `tests/runner/test_app_codex_native_model.py`
9. `tests/runner/test_runner_idle_active_work.py`
10. `tests/runner/transports/ws_tunnel/test_serve.py`

本阶段在源工作树中只允许新建：

11. `docs/fixes/handoffs/HERMES_COMPLETION_7.md`

所有pytest/JUnit/patch/hash/环境证据必须写入Linux绝对路径：

```text
/tmp/omnigent-premerge-evidence/<run-id>/
```

不得把证据目录、临时clone、`.venv`或测试输出写入源仓库。

## 3. 失败测试与已知门槛偏差

### 3.1 本阶段不制造RED

Gate 1不是实现阶段，不写或修改测试。全仓命令出现的任何fail/error都是真实Gate证据：不得修测试、删nodeid、加skip、重跑挑绿或把非零写成GREEN。

### 3.2 旧定向命令已过期

当前 `PRE_MERGE_GATES.md` 的旧“定向67”命令引用两个已不存在文件：

- `tests/inner/test_loader_executor_nested.py`
- `tests/runner/test_codex_native_model_from_spec.py`

当前实际对应文件是：

- `tests/inner/test_loader.py`中的阶段3定向nodeid
- `tests/runner/test_app_codex_native_model.py`

不得修改 `PRE_MERGE_GATES.md`；在证据和报告中写明偏差，并执行第7节的“当前候选定向套件”。旧定向67历史状态不因本轮自动更新。

### 3.3 环境不合格

以下任一情况只能记 `NOT_EXECUTED`，不得使用Windows结果替代：

- 非Ubuntu 22.04/24.04 x86_64 Linux。
- Python不是3.12.x。
- 无法使用`uv sync --locked --extra dev`。
- 缺`tmux`或`bubblewrap`且无法在一次性环境中提供。
- 当前dirty候选无法只读挂载/复制到Linux。

若证据目录不可写、tee失败、JUnit缺失或候选复制校验失败，记 `INVALID`。

## 4. 最小改法：可逆Gate执行方法

1. 源工作树只读：记录HEAD/status/blob与候选patch，不checkout/switch/stage/commit。
2. 在Linux `/tmp`创建一次性baseline和candidate clone；允许在这些临时clone中detached checkout、复制候选文件和创建`.venv`。
3. baseline固定为源仓库本地对象中的`origin/main`。
4. candidate固定为`dc83140...`，再覆盖源工作树当前文件内容；用patch SHA-256、untracked列表和最终status证明候选身份。
5. 两棵树使用同一uv版本、同一lockfile、同一Ubuntu环境。
6. 所有pipeline同时记录pytest与tee退出码；失败后继续只是为了baseline/candidate比较，不得改变结果。
7. 临时目录可在报告验收后清理；本阶段不得清理证据目录。

这套方法遵循可逆发布前检查：不改生产状态，不污染源工作树，任何失败都停在Gate而非继续合并。

## 5. Gate 0环境预检

在拟执行的Linux环境中运行并保存到`env-preflight.txt`：

```bash
set -euo pipefail
uname -a
uname -m
cat /etc/os-release
python3 --version
uv --version
git --version
tmux -V
bwrap --version
```

必须人工确认：Ubuntu 22.04或24.04、x86_64、Python 3.12.x。只允许在一次性容器/VM/WSL环境内安装缺失依赖；不得擅自修改长期宿主机。没有合格环境则直接写`HERMES_COMPLETION_7.md`为`NOT_EXECUTED`，附预检输出与缺口。

`SOURCE_REPO`必须指向当前源工作树的只读挂载。WSL示例：

```bash
export SOURCE_REPO='/mnt/f/codex-ai/git项目部署/tmp/omnigent-review'
test -d "$SOURCE_REPO/.git"
test "$(git -C "$SOURCE_REPO" rev-parse HEAD)" = "dc83140c73ceb12fa165753c1880c19f68da86f4"
```

若使用native Linux或容器，只能把`SOURCE_REPO`换成该工作树的只读挂载绝对路径，并在报告记录实际值；不能换成远端PR或clean clone。

## 6. 候选快照与临时树

环境合格后执行：

```bash
set -euo pipefail
export CANDIDATE_HEAD=dc83140c73ceb12fa165753c1880c19f68da86f4
export MAIN_SHA="$(git -C "$SOURCE_REPO" rev-parse origin/main)"
export RUN_ID="$(date -u +%Y%m%d-%H%M)-$(git -C "$SOURCE_REPO" rev-parse --short HEAD)"
export EVIDENCE_ROOT="/tmp/omnigent-premerge-evidence/$RUN_ID"
export BASELINE_TREE=/tmp/omnigent-gate1-baseline
export CANDIDATE_TREE=/tmp/omnigent-gate1-candidate
mkdir -p "$EVIDENCE_ROOT"

{
  echo "SOURCE_REPO=$SOURCE_REPO"
  echo "MAIN_SHA=$MAIN_SHA"
  echo "CANDIDATE_HEAD=$CANDIDATE_HEAD"
  echo "RUN_ID=$RUN_ID"
  echo "EVIDENCE_ROOT=$EVIDENCE_ROOT"
  git -C "$SOURCE_REPO" status --short --branch
} | tee "$EVIDENCE_ROOT/commits-and-status.txt"

git -C "$SOURCE_REPO" diff --binary HEAD -- omnigent tests \
  > "$EVIDENCE_ROOT/candidate-tracked.patch"
git -C "$SOURCE_REPO" ls-files --others --exclude-standard -- omnigent tests \
  | sort > "$EVIDENCE_ROOT/candidate-untracked-files.txt"
sha256sum "$EVIDENCE_ROOT/candidate-tracked.patch" \
  "$EVIDENCE_ROOT/candidate-untracked-files.txt" \
  > "$EVIDENCE_ROOT/candidate-snapshot.sha256"

git -C "$SOURCE_REPO" bundle create "$EVIDENCE_ROOT/source.bundle" --all
git clone "$EVIDENCE_ROOT/source.bundle" "$BASELINE_TREE"
git -C "$BASELINE_TREE" checkout --detach "$MAIN_SHA"
git clone "$EVIDENCE_ROOT/source.bundle" "$CANDIDATE_TREE"
git -C "$CANDIDATE_TREE" checkout --detach "$CANDIDATE_HEAD"

# 把当前工作树内容覆盖到临时候选；保留临时候选自身.git。
(
  cd "$SOURCE_REPO"
  tar --exclude=.git --exclude=.venv --exclude=.pytest_cache \
      --exclude='__pycache__' --exclude='*.pyc' -cf - .
) | (
  cd "$CANDIDATE_TREE"
  tar -xf -
)

git -C "$CANDIDATE_TREE" status --short --branch \
  | tee "$EVIDENCE_ROOT/candidate-status.txt"
git -C "$CANDIDATE_TREE" diff --binary HEAD -- omnigent tests \
  > "$EVIDENCE_ROOT/reconstructed-candidate.patch"
sha256sum "$EVIDENCE_ROOT/reconstructed-candidate.patch" \
  > "$EVIDENCE_ROOT/reconstructed-candidate.sha256"
cmp "$EVIDENCE_ROOT/candidate-tracked.patch" \
    "$EVIDENCE_ROOT/reconstructed-candidate.patch"

while IFS= read -r path; do
  [ -z "$path" ] || test -e "$CANDIDATE_TREE/$path"
done < "$EVIDENCE_ROOT/candidate-untracked-files.txt"
```

若固定临时目录已存在，不得盲目删除。先确认它们解析到上述两个`/tmp/omnigent-gate1-*`绝对路径且不含需保留数据，再在一次性环境中清理并重建；不能清理源工作树。

`cmp`非零表示候选复制无效，Gate 1=`INVALID`。同时确认`candidate-untracked-files.txt`中的每个文件均存在于candidate；缺任一文件同样`INVALID`。

## 7. 测试命令与证据

### 7.1 同环境依赖

```bash
(
  cd "$BASELINE_TREE"
  uv sync --locked --extra dev
) 2>&1 | tee "$EVIDENCE_ROOT/baseline-sync.txt"
(
  cd "$CANDIDATE_TREE"
  uv sync --locked --extra dev
) 2>&1 | tee "$EVIDENCE_ROOT/candidate-sync.txt"
```

任一sync非零即`INVALID`或`NOT_EXECUTED`（按是否为环境缺失分类），不得使用非locked依赖继续并声称PASS。

### 7.2 clean main与candidate全仓

在bash中定义并执行：

```bash
run_full_suite() {
  label="$1"
  tree="$2"
  cd "$tree"
  set +e
  set -o pipefail
  uv run pytest -q --junitxml="$EVIDENCE_ROOT/${label}-pytest.xml" \
    2>&1 | tee "$EVIDENCE_ROOT/${label}-pytest.txt"
  statuses=("${PIPESTATUS[@]}")
  pytest_exit="${statuses[0]}"
  tee_exit="${statuses[1]}"
  set +o pipefail
  set -e
  {
    echo "PYTEST_EXIT:$pytest_exit"
    echo "TEE_EXIT:$tee_exit"
  } | tee -a "$EVIDENCE_ROOT/${label}-pytest.txt"
  printf '%s\n' "$pytest_exit" > "$EVIDENCE_ROOT/${label}-pytest.exit"
  printf '%s\n' "$tee_exit" > "$EVIDENCE_ROOT/${label}-tee.exit"
}

set -euo pipefail
run_full_suite baseline "$BASELINE_TREE"
run_full_suite candidate "$CANDIDATE_TREE"
```

### 7.3 失败nodeid与新增失败

```bash
for label in baseline candidate; do
  awk '/^(FAILED|ERROR) / {print $2}' \
    "$EVIDENCE_ROOT/${label}-pytest.txt" \
    | sort -u > "$EVIDENCE_ROOT/${label}-fail-ids.txt"
done

comm -13 "$EVIDENCE_ROOT/baseline-fail-ids.txt" \
         "$EVIDENCE_ROOT/candidate-fail-ids.txt" \
  > "$EVIDENCE_ROOT/new-failures.txt"
```

若pytest非零但对应fail-id列表为空，说明可能是collection/internal/infrastructure异常，不能做子集PASS，判`INVALID`并在报告记录首个错误。

### 7.4 当前候选定向套件

只在candidate中运行；它是额外必要证据，不替代全仓：

```bash
cd "$CANDIDATE_TREE"
set +e
set -o pipefail
uv run pytest -q \
  tests/runner/test_session_workspace_cache.py \
  tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries \
  tests/runner/test_app_codex_native_model.py \
  tests/inner/test_loader.py::TestLoadFromDict::test_executor_bundle_nesting_rejected \
  tests/inner/test_loader.py::TestLoadFromDict::test_executor_extra_keys_tolerated \
  tests/inner/test_loader.py::TestLoadFromDict::test_tools_agent_executor_bundle_nesting_rejected \
  tests/host/test_connect.py::test_watch_runner_silent_on_clean_exit \
  tests/host/test_connect.py::test_watch_runner_reports_unexpected_exit \
  tests/host/test_connect.py::test_watch_runner_silent_on_intentional_stop \
  tests/runner/test_runner_idle_active_work.py \
  tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task \
  tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes \
  tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes \
  tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown \
  tests/inner/test_native_system_prompt_delivery.py \
  tests/inner/test_codex_native_system_prompt_apply.py \
  tests/runner/test_app_codex_native_prompt_delivery.py \
  tests/inner/test_claude_native_executor.py \
  tests/inner/test_codex_native_executor.py \
  tests/test_codex_native_app_server.py \
  2>&1 | tee "$EVIDENCE_ROOT/targeted-current.txt"
statuses=("${PIPESTATUS[@]}")
set +o pipefail
set -e
printf 'PYTEST_EXIT:%s\nTEE_EXIT:%s\n' "${statuses[0]}" "${statuses[1]}" \
  | tee -a "$EVIDENCE_ROOT/targeted-current.txt"
```

### 7.5 Ruff与diff

```bash
cd "$CANDIDATE_TREE"
set +e
set -o pipefail
uv run ruff check \
  omnigent/runner/app.py \
  omnigent/runner/_entry.py \
  omnigent/runner/transports/ws_tunnel/serve.py \
  omnigent/host/connect.py \
  omnigent/inner/loader.py \
  omnigent/inner/native_prompt_delivery.py \
  omnigent/inner/*native*.py \
  omnigent/native_server_harness.py \
  tests/runner/test_session_workspace_cache.py \
  tests/runner/test_app_codex_native_model.py \
  tests/runner/test_runner_idle_active_work.py \
  tests/runner/test_app_codex_native_prompt_delivery.py \
  tests/runner/test_app_sessions_native.py \
  tests/runner/transports/ws_tunnel/test_serve.py \
  tests/host/test_connect.py \
  tests/inner/test_loader.py \
  tests/inner/test_native_system_prompt_delivery.py \
  tests/inner/test_codex_native_system_prompt_apply.py \
  tests/inner/test_codex_native_executor.py \
  tests/test_codex_native_app_server.py \
  2>&1 | tee "$EVIDENCE_ROOT/ruff.txt"
statuses=("${PIPESTATUS[@]}")
set +o pipefail
set -e
printf 'RUFF_EXIT:%s\nTEE_EXIT:%s\n' "${statuses[0]}" "${statuses[1]}" \
  | tee -a "$EVIDENCE_ROOT/ruff.txt"

git diff --check 2>&1 | tee "$EVIDENCE_ROOT/diff-check.txt"
echo "DIFF_CHECK_EXIT:${PIPESTATUS[0]}" | tee -a "$EVIDENCE_ROOT/diff-check.txt"
```

定向、Ruff、diff-check任一非零均阻止Gate 1 PASS，除非结果被判为`INVALID`并重建完整有效证据；不得修源码后继续本阶段。

### 7.6 源工作树最终保护核对

```bash
{
  echo "HEAD=$(git -C "$SOURCE_REPO" rev-parse HEAD)"
  echo "WORKSPACE_BLOB=$(git -C "$SOURCE_REPO" hash-object tests/runner/test_session_workspace_cache.py)"
  echo "MODEL_BLOB=$(git -C "$SOURCE_REPO" hash-object tests/runner/test_app_codex_native_model.py)"
  echo "IDLE_BLOB=$(git -C "$SOURCE_REPO" hash-object tests/runner/test_runner_idle_active_work.py)"
  echo "SERVE_BLOB=$(git -C "$SOURCE_REPO" hash-object tests/runner/transports/ws_tunnel/test_serve.py)"
  git -C "$SOURCE_REPO" status --short --branch
} | tee "$EVIDENCE_ROOT/source-final-status.txt"
```

## 8. Pass/Fail判定

### PASS（绝对）

必须同时满足：

- candidate全仓pytest exit 0。
- candidate tee exit 0且JUnit存在。
- 定向、Ruff、diff-check全部exit 0。
- 候选快照/cmp/保护检查有效。

### PASS（相对 main）

只在以下全部满足时允许：

- baseline pytest非零且证据有效。
- candidate失败nodeid集合是baseline子集。
- `new-failures.txt`为空。
- 每个baseline失败都在`baseline-known-failures.md`中写明同环境已知原因或flaky依据；无法解释的失败不能标相对PASS。
- 定向、Ruff、diff-check全部exit 0。

### FAIL

- `new-failures.txt`非空；或
- 定向/Ruff/diff-check有真实候选失败；或
- 候选行为失败且不是证据基础设施问题。

### INVALID / NOT_EXECUTED

- `INVALID`：tee/JUnit/快照/复制/失败列表/证据目录等证据链损坏。
- `NOT_EXECUTED`：没有合格Linux环境或依赖前置无法满足，未形成有效全仓运行。

任何非PASS结果均阻塞Gate 2和merge推进，除非Codex另行策划环境补跑或返工。

## 9. 禁止项

- 不得在源工作树执行checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean、stage或commit。
- 不得commit/push/merge/tag、发版或编辑PR/Issue。
- 不得修改源工作树的`omnigent/`、`tests/`、r05、STATUS、PRE_MERGE_GATES或既有handoff。
- 不得运行Gate 2、AgentCenter smoke、浏览器E2E或真实Codex CLI smoke。
- 不得使用Windows全仓或阶段6定向结果替代Linux Gate 1。
- 不得使用旧PR SHA集成树替代当前dirty候选。
- 不得安装skip插件、修改pytest配置、删除失败、重复运行挑选一次绿色结果。
- 不得把baseline/candidate同失败但未解释的情况自动写成相对PASS。
- 不得把Gate 1 PASS写成Gate 2 PASS或可merge。
- 临时clone中的checkout、文件覆盖和依赖安装仅限固定`/tmp/omnigent-gate1-*`，不授权修改源工作树。

## 10. 完成标准

1. 源工作树HEAD、status与四个保护blob在前后均记录且不变：
   - `02cce3ca6e28233d5d0cac350a7be6316ff582d2`
   - `be43ec45816e8ece4192822506df8072580910e0`
   - `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
   - `6116218097f2352c467524fd0ddf0838315aa524`
2. 环境、candidate snapshot、patch hash、MAIN_SHA与CANDIDATE_HEAD可审计。
3. clean main与candidate在同一合格Linux环境、同一locked依赖下运行。
4. 两条全仓pipeline均记录pytest/tee退出码与JUnit；失败nodeid和新增失败列表完整。
5. 当前候选定向、Ruff和diff-check有真实退出码。
6. 结果严格按第8节五种状态之一判定，不夸大。
7. 新建`docs/fixes/handoffs/HERMES_COMPLETION_7.md`，包含：环境、证据根绝对路径、所有SHA/hash、完整命令与summary、失败nodeid、判定理由、源工作树最终status、剩余风险。
8. 只在结果为PASS时允许Codex策划Gate 2；仍不得称可merge。
9. 只创建本阶段报告；无commit/push/merge/tag；Gate 2仍未执行、未判定。

若没有合格Linux环境，也必须提交诚实的`NOT_EXECUTED`报告；这算阶段7执行已报告，不算Gate 1通过。
