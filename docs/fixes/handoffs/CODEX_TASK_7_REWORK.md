# CODEX TASK 7 REWORK — Gate 1 INVALID 证据链重跑

**执行者：** Hermes（Gate 1重跑执行者）

**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**当前状态：** Gate 1=`INVALID`，不是FAIL也不是PASS；Gate 2仍未执行、未判定；不可merge。

**阶段边界：** 只修复Gate 1执行环境与证据脚本并重跑，不修改产品源码/测试/门槛文档，不执行Gate 2，不commit/push/merge/tag。

## 1. 问题与已确认根因

### P1 — 全仓收集被缺失Databricks SDK中断

旧证据根：

```text
C:\Users\Administrator\gate1-evidence\20260728-1732-dc83140\
```

`baseline-pytest.txt`与`candidate-pytest.txt`均记录：

- `tests/inner/test_databricks_executor.py`：`ModuleNotFoundError: No module named 'databricks'`
- `tests/inner/test_openai_agents_sdk_executor.py`：同样缺`databricks.sdk.config`
- `PYTEST_EXIT:2`，collection interrupted；全仓测试未实际运行。

根因不是缺`openai-agents-sdk`。`pyproject.toml`默认依赖已有`openai-agents`，项目可选extra `all`包含`databricks-sdk`；旧命令仅装`dev`，遗漏`all`。

重跑必须对baseline和candidate都使用：

```bash
uv sync --locked --extra dev --extra all
```

不得用只写`--extra all`替换`dev`，也不得使用`--all-extras`把全部重型provider依赖混入Gate。

### P1 — 整树CRLF覆盖制造69.7MB伪patch和diff-check噪声

旧任务用tar把整个Windows工作树覆盖到Linux候选。Windows源树由`core.autocrlf=true`检出为CRLF，Linuxclone使用LF；因此大量未修改文件被视为每行trailing whitespace：

- `candidate-tracked.patch`约69.7MB
- `diff-check.txt`约120MB
- candidate status包含大量伪修改

根因是候选重建方式，不是产品源码存在全仓尾随空格。重跑不得整树overlay；必须由Windows Git导出只包含真实dirty tracked文件的规范化patch，在Linux clean candidate上`git apply`，仅逐个复制untracked源文件并规范化CRLF→LF。

### P1 — diff-check退出码没有立即冻结

旧报告记录diff-check退出码不可信。无论旧脚本实际使用`$?`还是延迟读取`PIPESTATUS`，重跑必须在pipeline结束后第一条语句执行：

```bash
statuses=("${PIPESTATUS[@]}")
```

然后分别写`DIFF_CHECK_EXIT`与`TEE_EXIT`。不得从后续`echo`或`tee`读取状态。

### P2 — serve blob为行尾视图差异，不是保护基线变化

当前Windows源工作树核对：

```text
git hash-object --path=tests/runner/transports/ws_tunnel/test_serve.py ...
= 6116218097f2352c467524fd0ddf0838315aa524
```

WSL在`core.autocrlf=false`下直接哈希CRLF原始字节得到`ae9e6bb5...`。这不是Grok返工修改，也不得更新保护值。重跑对源工作树使用Windows Git或显式`-c core.autocrlf=true --path=...`得到规范化blob；Linux candidate应用规范化patch后也必须得到`611621...`。

### P2 — baseline-known-failures缺失

新run必须始终创建`baseline-known-failures.md`：

- baseline exit 0时写“None — baseline absolute green”。
- baseline有效但非零时，每个nodeid逐项写同环境原因与依据。
- collection/internal/infrastructure error不得作为相对main已知失败；应判INVALID。

## 2. 精确文件与保护范围

必读：

1. `docs/fixes/handoffs/CODEX_TASK_7.md`
2. `docs/fixes/handoffs/HERMES_COMPLETION_7.md`
3. `docs/fixes/PRE_MERGE_GATES.md`
4. `docs/fixes/handoffs/HERMES_REVIEW_6.md`
5. `pyproject.toml`
6. `uv.lock`

旧证据目录只读保留，不覆盖、不清理。

源工作树只允许新建：

7. `docs/fixes/handoffs/HERMES_COMPLETION_7_REWORK.md`

禁止修改：

- `omnigent/`与`tests/`全部文件
- `pyproject.toml`、`uv.lock`、CI
- `STATUS.md`、`PRE_MERGE_GATES.md`、r05
- `HERMES_COMPLETION_7.md`及其他既有handoff

临时clone、`.venv`、patch/JUnit/日志只允许位于新的Linux `/tmp` run和Windows持久化证据目录。

## 3. 失败测试与重跑原则

本阶段不新增、删除、skip或修改测试。旧collection error是无效环境证据，不是允许长期保留的baseline失败。

依赖安装后先运行最小收集前检：

```bash
uv run python -c "import databricks.sdk.config; import agents; print('gate1-imports-ok')"
uv run pytest --collect-only -q \
  tests/inner/test_databricks_executor.py \
  tests/inner/test_openai_agents_sdk_executor.py
```

两棵树都必须import成功、collect-only exit 0。任一失败即`INVALID`，不得继续全仓并声称形成有效Gate。

全仓运行后：

- candidate exit 0才可能绝对PASS。
- 相对PASS只接受测试case failure/error的有效nodeid子集。
- collection interruption、pytest internal error、JUnit/tee损坏一律INVALID。
- 136定向GREEN和Ruff clean继续作为正面参考，但不能复用旧数字代替新run。

## 4. 最小改法：Windows导出、Linux应用

### 4.1 新run与Windows权威快照

在Windows PowerShell中执行，使用Windows Git的`core.autocrlf=true`规范化视图：

```powershell
$Source = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$RunId = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmm') + '-dc83140-r2'
$PersistRoot = Join-Path 'C:\Users\Administrator\gate1-evidence' $RunId
New-Item -ItemType Directory -Path $PersistRoot | Out-Null
$RunId | Set-Content -Encoding utf8NoBOM "$PersistRoot\run-id.txt"
$RunId | Set-Content -Encoding utf8NoBOM 'C:\Users\Administrator\gate1-evidence\current-run-id.txt'

git -C $Source rev-parse HEAD | Set-Content -Encoding utf8NoBOM "$PersistRoot\source-head.txt"
git -C $Source rev-parse origin/main | Set-Content -Encoding utf8NoBOM "$PersistRoot\main-sha.txt"
git -C $Source status --short --branch | Set-Content -Encoding utf8NoBOM "$PersistRoot\source-status-before.txt"

git -C $Source diff --binary --output="$PersistRoot\candidate-tracked.patch" HEAD -- omnigent tests
$Tracked = @(git -C $Source diff --name-only HEAD -- omnigent tests | Sort-Object)
$Untracked = @(git -C $Source ls-files --others --exclude-standard -- omnigent tests | Sort-Object)
[IO.File]::WriteAllLines("$PersistRoot\candidate-tracked-files.txt", $Tracked, [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllLines("$PersistRoot\candidate-untracked-files.txt", $Untracked, [Text.UTF8Encoding]::new($false))
$Untracked | ForEach-Object {
  "$($_)=$(git -C $Source -c core.autocrlf=true hash-object --path=$_ $_)"
} | Set-Content -Encoding utf8NoBOM "$PersistRoot\candidate-untracked-blobs.txt"

git -C $Source bundle create "$PersistRoot\source.bundle" --all
Get-FileHash -Algorithm SHA256 "$PersistRoot\candidate-tracked.patch","$PersistRoot\candidate-tracked-files.txt","$PersistRoot\candidate-untracked-files.txt","$PersistRoot\candidate-untracked-blobs.txt","$PersistRoot\source.bundle" |
  Format-Table -AutoSize | Out-String |
  Set-Content -Encoding utf8NoBOM "$PersistRoot\snapshot-sha256.txt"

@(
  'tests/runner/test_session_workspace_cache.py',
  'tests/runner/test_app_codex_native_model.py',
  'tests/runner/test_runner_idle_active_work.py',
  'tests/runner/transports/ws_tunnel/test_serve.py'
) | ForEach-Object {
  "$($_)=$(git -C $Source -c core.autocrlf=true hash-object --path=$_ $_)"
} | Set-Content -Encoding utf8NoBOM "$PersistRoot\source-protection-before.txt"
```

必须确认：

- source HEAD=`dc83140c73ceb12fa165753c1880c19f68da86f4`
- tracked manifest只含当前Windows Git真实dirty源码/测试，不出现整仓文件。
- untracked manifest只含`omnigent/`或`tests/`下当前新文件。
- patch大小应与真实改动量相符；若再次出现数十MB整树patch，停止并判INVALID，不继续。

### 4.2 WSL新证据根与clone

在WSL2 Ubuntu 24.04中设置路径。`RUN_ID`必须与PowerShell生成值一致：

```bash
set -euo pipefail
export SOURCE_REPO='/mnt/f/codex-ai/git项目部署/tmp/omnigent-review'
export RUN_ID="$(tr -d '\r\n' < /mnt/c/Users/Administrator/gate1-evidence/current-run-id.txt)"
export PERSIST_ROOT="/mnt/c/Users/Administrator/gate1-evidence/$RUN_ID"
export EVIDENCE_ROOT="/tmp/omnigent-premerge-evidence/$RUN_ID"
export BASELINE_TREE="/tmp/omnigent-gate1-baseline-$RUN_ID"
export CANDIDATE_TREE="/tmp/omnigent-gate1-candidate-$RUN_ID"
export CANDIDATE_HEAD=dc83140c73ceb12fa165753c1880c19f68da86f4
export MAIN_SHA="$(tr -d '\r\n' < "$PERSIST_ROOT/main-sha.txt")"
mkdir -p "$EVIDENCE_ROOT"

cp "$PERSIST_ROOT/source.bundle" "$EVIDENCE_ROOT/source.bundle"
cp "$PERSIST_ROOT/candidate-tracked.patch" "$EVIDENCE_ROOT/candidate-tracked.patch"
cp "$PERSIST_ROOT/candidate-tracked-files.txt" "$EVIDENCE_ROOT/candidate-tracked-files.txt"
cp "$PERSIST_ROOT/candidate-untracked-files.txt" "$EVIDENCE_ROOT/candidate-untracked-files.txt"
cp "$PERSIST_ROOT/candidate-untracked-blobs.txt" "$EVIDENCE_ROOT/candidate-untracked-blobs.txt"

git clone "$EVIDENCE_ROOT/source.bundle" "$BASELINE_TREE"
git -C "$BASELINE_TREE" checkout --detach "$MAIN_SHA"
git clone "$EVIDENCE_ROOT/source.bundle" "$CANDIDATE_TREE"
git -C "$CANDIDATE_TREE" checkout --detach "$CANDIDATE_HEAD"

git -C "$CANDIDATE_TREE" apply --check "$EVIDENCE_ROOT/candidate-tracked.patch"
git -C "$CANDIDATE_TREE" apply "$EVIDENCE_ROOT/candidate-tracked.patch"
```

固定目录包含`RUN_ID`，不得复用旧clone。若需删除本次失败clone，先确认解析后的绝对路径位于`/tmp/omnigent-gate1-*-<RUN_ID>`，不得删除源工作树或旧证据。

### 4.3 仅复制untracked并规范化LF

先验证manifest路径安全，再复制：

```bash
while IFS= read -r path; do
  [ -z "$path" ] && continue
  case "$path" in
    omnigent/*.py|omnigent/**/*.py|tests/*.py|tests/**/*.py) ;;
    *) echo "INVALID untracked path: $path" >&2; exit 4 ;;
  esac
  test -f "$SOURCE_REPO/$path"
  mkdir -p "$CANDIDATE_TREE/$(dirname "$path")"
  python3 - "$SOURCE_REPO/$path" "$CANDIDATE_TREE/$path" <<'PY'
from pathlib import Path
import sys
src, dst = map(Path, sys.argv[1:])
data = src.read_bytes().replace(b"\r\n", b"\n")
dst.write_bytes(data)
PY
done < "$EVIDENCE_ROOT/candidate-untracked-files.txt"
```

然后验证candidate文件集合与Windows manifest完全一致：

```bash
git -C "$CANDIDATE_TREE" diff --name-only HEAD -- omnigent tests | sort \
  > "$EVIDENCE_ROOT/reconstructed-tracked-files.txt"
git -C "$CANDIDATE_TREE" ls-files --others --exclude-standard -- omnigent tests | sort \
  > "$EVIDENCE_ROOT/reconstructed-untracked-files.txt"
while IFS= read -r path; do
  [ -z "$path" ] || printf '%s=%s\n' "$path" \
    "$(git -C "$CANDIDATE_TREE" hash-object --path="$path" "$CANDIDATE_TREE/$path")"
done < "$EVIDENCE_ROOT/reconstructed-untracked-files.txt" \
  > "$EVIDENCE_ROOT/reconstructed-untracked-blobs.txt"
diff -u "$EVIDENCE_ROOT/candidate-tracked-files.txt" \
        "$EVIDENCE_ROOT/reconstructed-tracked-files.txt" \
  | tee "$EVIDENCE_ROOT/tracked-manifest-diff.txt"
diff -u "$EVIDENCE_ROOT/candidate-untracked-files.txt" \
        "$EVIDENCE_ROOT/reconstructed-untracked-files.txt" \
  | tee "$EVIDENCE_ROOT/untracked-manifest-diff.txt"
diff -u "$EVIDENCE_ROOT/candidate-untracked-blobs.txt" \
        "$EVIDENCE_ROOT/reconstructed-untracked-blobs.txt" \
  | tee "$EVIDENCE_ROOT/untracked-blob-diff.txt"

git -C "$CANDIDATE_TREE" diff --binary HEAD -- omnigent tests \
  > "$EVIDENCE_ROOT/reconstructed-candidate.patch"
cmp "$EVIDENCE_ROOT/candidate-tracked.patch" \
    "$EVIDENCE_ROOT/reconstructed-candidate.patch"
git -C "$CANDIDATE_TREE" status --short --branch \
  | tee "$EVIDENCE_ROOT/candidate-status.txt"
```

任一manifest diff或patch cmp非零即INVALID。candidate status不得再出现全仓CRLF伪修改。

## 5. 依赖修复与收集前检

baseline与candidate分别执行并捕获sync pipeline真实状态：

```bash
sync_tree() {
  label="$1"
  tree="$2"
  cd "$tree"
  set +e
  set -o pipefail
  uv sync --locked --extra dev --extra all 2>&1 \
    | tee "$EVIDENCE_ROOT/${label}-sync.txt"
  statuses=("${PIPESTATUS[@]}")
  set +o pipefail
  set -e
  printf 'UV_EXIT:%s\nTEE_EXIT:%s\n' "${statuses[0]}" "${statuses[1]}" \
    | tee -a "$EVIDENCE_ROOT/${label}-sync.txt"
  test "${statuses[0]}" -eq 0
  test "${statuses[1]}" -eq 0
  set -o pipefail
}

set -euo pipefail
sync_tree baseline "$BASELINE_TREE"
sync_tree candidate "$CANDIDATE_TREE"
```

收集前检在两棵树分别执行；不经过tee判定进程状态，每条必须exit 0：

```bash
for pair in "baseline:$BASELINE_TREE" "candidate:$CANDIDATE_TREE"; do
  label="${pair%%:*}"
  tree="${pair#*:}"
  cd "$tree"
  set +e
  uv run python -c "import databricks.sdk.config; import agents; print('gate1-imports-ok')" \
    > "$EVIDENCE_ROOT/${label}-imports.txt" 2>&1
  import_exit="$?"
  set -e
  cat "$EVIDENCE_ROOT/${label}-imports.txt"
  echo "IMPORT_EXIT:$import_exit" | tee -a "$EVIDENCE_ROOT/${label}-imports.txt"
  test "$import_exit" -eq 0

  set +e
  uv run pytest --collect-only -q \
    tests/inner/test_databricks_executor.py \
    tests/inner/test_openai_agents_sdk_executor.py \
    > "$EVIDENCE_ROOT/${label}-collect-preflight.txt" 2>&1
  collect_exit="$?"
  set -e
  cat "$EVIDENCE_ROOT/${label}-collect-preflight.txt"
  echo "COLLECT_EXIT:$collect_exit" | tee -a "$EVIDENCE_ROOT/${label}-collect-preflight.txt"
  test "$collect_exit" -eq 0
done
```

若缺Databricks或Agents导入、collect-only仍非零，Gate 1=`INVALID`；报告真实错误，不改依赖文件。

## 6. 全仓测试命令、失败集与known文件

沿用`CODEX_TASK_7.md`的`run_full_suite`函数，在新run中重新执行baseline和candidate全仓；不得复制旧run结果。旧函数在读取状态后还必须追加`set -o pipefail`恢复shell状态，再返回调用者。

每个pipeline结束后立即冻结：

```bash
statuses=("${PIPESTATUS[@]}")
pytest_exit="${statuses[0]}"
tee_exit="${statuses[1]}"
```

要求：

- JUnit存在且可解析。
- tee exit 0。
- pytest非零时，失败列表必须包含真实case nodeid；collection/internal error判INVALID。
- 新建`baseline-known-failures.md`。

失败列表与known文件：

```bash
for label in baseline candidate; do
  awk '/^(FAILED|ERROR) / {print $2}' "$EVIDENCE_ROOT/${label}-pytest.txt" \
    | sort -u > "$EVIDENCE_ROOT/${label}-fail-ids.txt"
done
comm -13 "$EVIDENCE_ROOT/baseline-fail-ids.txt" \
         "$EVIDENCE_ROOT/candidate-fail-ids.txt" \
  > "$EVIDENCE_ROOT/new-failures.txt"
```

若baseline exit 0：

```bash
printf 'None — baseline absolute green.\n' \
  > "$EVIDENCE_ROOT/baseline-known-failures.md"
```

若baseline有效但有case失败，Hermes必须手工为每个`baseline-fail-ids.txt`条目写原因与证据；不得把“baseline也失败”本身当已知理由。

## 7. 新定向、Ruff与可靠diff-check

重新运行`CODEX_TASK_7.md` §7.4当前候选定向套件和§7.5 Ruff，产生新run数字；不得引用旧`136 passed`替代。

tracked diff-check：

```bash
cd "$CANDIDATE_TREE"
set +e
set -o pipefail
git diff --check HEAD 2>&1 | tee "$EVIDENCE_ROOT/diff-check-tracked.txt"
statuses=("${PIPESTATUS[@]}")
git_exit="${statuses[0]}"
tee_exit="${statuses[1]}"
set +o pipefail
set -e
set -o pipefail
printf 'DIFF_CHECK_EXIT:%s\nTEE_EXIT:%s\n' "$git_exit" "$tee_exit" \
  | tee -a "$EVIDENCE_ROOT/diff-check-tracked.txt"
```

untracked文件逐个检查。`git diff --no-index`在内容不同但无空白错误时可返回1，因此以`--check`输出是否为空为判据，同时记录原始exit：

```bash
: > "$EVIDENCE_ROOT/diff-check-untracked.txt"
while IFS= read -r path; do
  [ -z "$path" ] && continue
  tmp="$(mktemp)"
  set +e
  git diff --no-index --check /dev/null "$CANDIDATE_TREE/$path" > "$tmp" 2>&1
  rc="$?"
  set -e
  printf '%s EXIT=%s\n' "$path" "$rc" >> "$EVIDENCE_ROOT/diff-check-untracked.txt"
  cat "$tmp" >> "$EVIDENCE_ROOT/diff-check-untracked.txt"
  if [ -s "$tmp" ]; then
    rm -f "$tmp"
    echo "untracked whitespace error: $path" >&2
    exit 5
  fi
  rm -f "$tmp"
done < "$EVIDENCE_ROOT/candidate-untracked-files.txt"
```

Gate 1只有在tracked `git_exit=0`、tracked tee=0且所有untracked输出无空白错误时才满足diff-check。

## 8. 保护值与证据持久化

保护值不更新：

- workspace：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model：`be43ec45816e8ece4192822506df8072580910e0`
- idle：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve：`6116218097f2352c467524fd0ddf0838315aa524`

Linux candidate使用规范化LF内容核对四值。源工作树最终值由Windows Git显式`core.autocrlf=true`核对，不接受`ae9e6bb5...`替换serve基线。

在PowerShell最终执行：

```powershell
$Source = 'F:\codex-ai\git项目部署\tmp\omnigent-review'
$RunId = Get-Content -Raw 'C:\Users\Administrator\gate1-evidence\current-run-id.txt'
$RunId = $RunId.Trim()
$PersistRoot = Join-Path 'C:\Users\Administrator\gate1-evidence' $RunId
git -C $Source status --short --branch | Set-Content -Encoding utf8NoBOM "$PersistRoot\source-status-after.txt"
git -C $Source diff --binary --output="$PersistRoot\candidate-tracked-after.patch" HEAD -- omnigent tests
Get-FileHash -Algorithm SHA256 "$PersistRoot\candidate-tracked.patch","$PersistRoot\candidate-tracked-after.patch" |
  Format-Table -AutoSize | Out-String |
  Set-Content -Encoding utf8NoBOM "$PersistRoot\source-patch-before-after.sha256.txt"

@(
  'tests/runner/test_session_workspace_cache.py',
  'tests/runner/test_app_codex_native_model.py',
  'tests/runner/test_runner_idle_active_work.py',
  'tests/runner/transports/ws_tunnel/test_serve.py'
) | ForEach-Object {
  "$($_)=$(git -C $Source -c core.autocrlf=true hash-object --path=$_ $_)"
} | Set-Content -Encoding utf8NoBOM "$PersistRoot\source-protection-after.txt"
```

before/after patch SHA必须相同，四个保护值必须匹配。把整个新`EVIDENCE_ROOT`复制到`PersistRoot`，不得覆盖旧run。

## 9. Pass/Fail规则

沿用`CODEX_TASK_7.md` §8，并增加：

- 两棵树import/collect-preflight非零 → INVALID。
- 全仓出现collection/internal error → INVALID，不允许相对PASS。
- candidate absolute green + 新定向/Ruff/diff-check全绿 + 证据有效 → PASS（绝对）。
- 有效case失败时，candidate失败集⊆baseline、`new-failures.txt`为空、known文件逐项有依据、其余检查全绿 → PASS（相对main）。
- candidate新增真实case失败或定向/Ruff/diff-check真实失败 → FAIL。
- WSL崩溃、证据/clone/manifest损坏 → INVALID，使用新RUN_ID重建，不拼接两次run。

任何PASS仅表示Gate 1满足；Gate 2仍未执行，不可merge。

## 10. 禁止项

- 不得修改源工作树的源码、测试、依赖、lockfile、CI、STATUS、PRE_MERGE_GATES、r05或既有handoff。
- 不得用`--all-extras`、手工`pip install`或编辑依赖文件绕过locked安装。
- 不得加skip、删测试、改pytest配置或挑选性重跑。
- 不得整树tar overlay到Linux candidate。
- 不得复用或覆盖旧INVALID证据根；不得把旧136 passed/Ruff冒充新run。
- 不得把collection error列入相对main已知case失败后宣称PASS。
- 不得更新serve保护blob为`ae9e6bb5...`。
- 不得在源工作树checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean、stage或commit。
- 不得commit/push/merge/tag、发版或编辑PR/Issue。
- 不得执行Gate 2、AgentCenter/浏览器/真实Codex smoke。

## 11. 完成标准

1. 旧run保持只读，新的RUN_ID与证据根独立。
2. Windows Git导出的tracked patch只含真实dirty文件，Linux candidate通过`git apply`重建，无整树CRLF伪修改。
3. baseline/candidate均用`uv sync --locked --extra dev --extra all`，Databricks与Agents import及两文件collect-preflight通过。
4. 两棵树全仓pytest真实完成收集；若未完成则明确INVALID。
5. pytest/tee、Ruff/tee、diff-check/tee均立即冻结并记录各自退出码。
6. JUnit、失败nodeid、`new-failures.txt`和`baseline-known-failures.md`完整。
7. 新run定向、Ruff、tracked/untracked diff-check按真实结果记录。
8. 源工作树before/after patch SHA、status、HEAD和四保护blob保持；serve仍为`611621...`。
9. 新建`docs/fixes/handoffs/HERMES_COMPLETION_7_REWORK.md`，明确五态判定、证据根、全部命令/退出码、真实summary和剩余风险。
10. 只创建新报告；无commit/push/merge/tag；Gate 2仍未执行、未判定。

仅当新报告为有效PASS，Codex才可策划Gate 2；INVALID/FAIL/NOT_EXECUTED均继续阻塞。
