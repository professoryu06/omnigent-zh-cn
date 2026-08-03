# CODEX TASK 7 REWORK 3 — 精确定向清理后补齐 Gate 1 全仓

**执行者：** Grok（Gate 1 执行者；非独立审查者）  
**日期：** 2026-07-29  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** Gate 1=`INVALID`；Gate 2=未执行、未判定；不可 merge。  
**阶段边界：** 只允许清理精确绑定旧 candidate 临时树的遗留 host/server，然后复用已核验树补跑 baseline→candidate Linux 全仓。不得修改源码、测试、配置或既有证据。

## 1. 必读与输入

1. `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_2.md`
2. `docs/fixes/handoffs/CODEX_TASK_7_REWORK_2.md`
3. `docs/fixes/handoffs/HERMES_COMPLETION_7_REWORK.md`
4. `docs/fixes/handoffs/CODEX_TASK_7_REWORK.md`
5. `docs/fixes/PRE_MERGE_GATES.md`
6. `pyproject.toml` 第 217–225、311–323 行

本轮完成报告只允许新建：

`docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_3.md`

不得修改任何旧任务卡、报告或 evidence。

## 2. 已验收事实与问题

`GROK_COMPLETION_7_REWORK_2.md` 的 `INVALID` 成立：

- baseline/candidate `.venv`、HEAD、candidate status/patch/manifest/untracked blob 与四保护 blob均匹配。
- r2 正面证据 receipt 的七项 SHA-256 已由 Codex只读复核，全部匹配。
- r3没有启动全仓、没有JUnit/pytest exit/fail-ids；停止行为符合上一卡。
- 旧r2未完成全仓与r3不得拼接成Gate结果。
- 现场只读复核确认以下两个进程仍存活：

```text
45236  /tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2/.venv/bin/python -m omnigent.host._daemon_entry --local
45237  /tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2/.venv/bin/python -m omnigent.cli server --host 127.0.0.1 --port 6767 ...
```

- 两者cwd均为candidate树；`45237`的PPID为`45236`并监听`127.0.0.1:6767`。
- `45236`的PPID `30064` 是WSL `/init`，不属于candidate树，严禁终止。

PID可能变化或复用。不得因本卡列出旧PID就直接kill；必须按§4从现场重新发现并验证 `/proc` 身份。

## 3. 精确路径与保护身份

### 3.1 临时树

- baseline：`/tmp/omnigent-gate1-baseline-20260729-0106-dc83140-r2`
- candidate：`/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2`
- baseline HEAD：`81594243f7a17303b9ba477b938ac323f938c2e4`
- candidate HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`

### 3.2 只读旧证据

- r2：`C:\Users\Administrator\gate1-evidence\20260729-0106-dc83140-r2\`
- r3：`C:\Users\Administrator\gate1-evidence\20260729-1143-dc83140-grok-r3\`

两者均不得覆盖、追加或删除。

### 3.3 源工作树与四保护 blob

源 HEAD 必须始终为：

`dc83140c73ceb12fa165753c1880c19f68da86f4`

| 文件 | 期望 blob |
|---|---|
| `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` |
| `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` |
| `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` |
| `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` |

## 4. 最小改法：只清理精确匹配的两个进程

### 4.1 新 evidence

创建全新 run，不得写入r2/r3：

```bash
set -euo pipefail
RUN_ID="$(date +%Y%m%d-%H%M)-dc83140-grok-r4"
LINUX_EVIDENCE_ROOT="/tmp/omnigent-premerge-evidence/$RUN_ID"
EVIDENCE_ROOT="/mnt/c/Users/Administrator/gate1-evidence/$RUN_ID"
BASELINE_TREE='/tmp/omnigent-gate1-baseline-20260729-0106-dc83140-r2'
CANDIDATE_TREE='/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2'
R2='/mnt/c/Users/Administrator/gate1-evidence/20260729-0106-dc83140-r2'
R3='/mnt/c/Users/Administrator/gate1-evidence/20260729-1143-dc83140-grok-r3'

mkdir -p "$LINUX_EVIDENCE_ROOT" "$EVIDENCE_ROOT"
printf '%s\n' "$RUN_ID" > "$LINUX_EVIDENCE_ROOT/run-id.txt"
```

### 4.2 现场发现与不可变身份记录

只匹配candidate树解释器及以下两个模块：

```bash
HOST_PREFIX="$CANDIDATE_TREE/.venv/bin/python -m omnigent.host._daemon_entry --local"
SERVER_PREFIX="$CANDIDATE_TREE/.venv/bin/python -m omnigent.cli server "

ps -eo user=,pid=,ppid=,pgid=,sid=,lstart=,args= \
  > "$LINUX_EVIDENCE_ROOT/processes-before-all.txt"
grep -F "$CANDIDATE_TREE" "$LINUX_EVIDENCE_ROOT/processes-before-all.txt" \
  > "$LINUX_EVIDENCE_ROOT/processes-before-bound.txt" || true
ss -ltnp > "$LINUX_EVIDENCE_ROOT/listeners-before.txt" 2>&1 || true

mapfile -t HOST_PIDS < <(
  pgrep -u "$(id -u)" -f "^${HOST_PREFIX}$" || true
)
mapfile -t SERVER_PIDS < <(
  pgrep -u "$(id -u)" -f "^${SERVER_PREFIX}" || true
)

if (( ${#HOST_PIDS[@]} > 1 || ${#SERVER_PIDS[@]} > 1 )); then
  echo 'INVALID: unexpected process multiplicity' \
    | tee "$LINUX_EVIDENCE_ROOT/cleanup-decision.txt"
  exit 20
fi
```

零进程表示它们已由外部准确清理，可继续身份复核；一或两个进程则逐个验证。不得把任何其他进程加入数组。

对每个匹配PID保存并验证：

```bash
: > "$LINUX_EVIDENCE_ROOT/cleanup-targets.txt"
declare -A EXPECTED_START EXPECTED_CWD EXPECTED_CMD
for pid in "${SERVER_PIDS[@]}" "${HOST_PIDS[@]}"; do
  test -n "$pid" || continue
  test -r "/proc/$pid/cmdline"
  cmd="$(tr '\0' ' ' < "/proc/$pid/cmdline" | sed 's/ $//')"
  cwd="$(readlink "/proc/$pid/cwd")"
  start_ticks="$(awk '{print $22}' "/proc/$pid/stat")"
  ppid="$(awk '{print $4}' "/proc/$pid/stat")"

  test "$cwd" = "$CANDIDATE_TREE"
  case "$cmd" in
    "$HOST_PREFIX"|"$SERVER_PREFIX"*) ;;
    *) echo "INVALID unexpected cmdline PID=$pid: $cmd" >&2; exit 21 ;;
  esac

  printf 'PID=%s\tPPID=%s\tSTART=%s\tCWD=%s\tCMD=%s\n' \
    "$pid" "$ppid" "$start_ticks" "$cwd" "$cmd" \
    >> "$LINUX_EVIDENCE_ROOT/cleanup-targets.txt"
  EXPECTED_START["$pid"]="$start_ticks"
  EXPECTED_CWD["$pid"]="$cwd"
  EXPECTED_CMD["$pid"]="$cmd"
done

if (( ${#HOST_PIDS[@]} == 1 && ${#SERVER_PIDS[@]} == 1 )); then
  server_ppid="$(awk '{print $4}' "/proc/${SERVER_PIDS[0]}/stat")"
  test "$server_ppid" = "${HOST_PIDS[0]}"
fi
```

若host与server同时存在，server的PPID必须等于host PID；不等即`INVALID`。不得终止PPID、`/init`、tmux、pytest或任何未列入`cleanup-targets.txt`的进程。

### 4.3 PID级TERM与受保护的必要KILL

先server、后host发送TERM：

```bash
for pid in "${SERVER_PIDS[@]}" "${HOST_PIDS[@]}"; do
  test -n "$pid" || continue
  if test -r "/proc/$pid/stat"; then
    current_start="$(awk '{print $22}' "/proc/$pid/stat")"
    current_cwd="$(readlink "/proc/$pid/cwd")"
    current_cmd="$(tr '\0' ' ' < "/proc/$pid/cmdline" | sed 's/ $//')"
    test "$current_start" = "${EXPECTED_START[$pid]}"
    test "$current_cwd" = "${EXPECTED_CWD[$pid]}"
    test "$current_cmd" = "${EXPECTED_CMD[$pid]}"
    kill -TERM "$pid"
    printf 'TERM PID=%s START=%s\n' "$pid" "$current_start" \
      >> "$LINUX_EVIDENCE_ROOT/cleanup-signals.txt"
  else
    printf 'EXITED_BEFORE_TERM PID=%s\n' "$pid" \
      >> "$LINUX_EVIDENCE_ROOT/cleanup-signals.txt"
  fi
done

for _ in $(seq 1 40); do
  alive=0
  for pid in "${SERVER_PIDS[@]}" "${HOST_PIDS[@]}"; do
    test -n "$pid" || continue
    kill -0 "$pid" 2>/dev/null && alive=1
  done
  (( alive == 0 )) && break
  sleep 0.5
done

for pid in "${SERVER_PIDS[@]}" "${HOST_PIDS[@]}"; do
  test -n "$pid" || continue
  if kill -0 "$pid" 2>/dev/null; then
    current_start="$(awk '{print $22}' "/proc/$pid/stat")"
    current_cwd="$(readlink "/proc/$pid/cwd")"
    current_cmd="$(tr '\0' ' ' < "/proc/$pid/cmdline" | sed 's/ $//')"
    test "$current_start" = "${EXPECTED_START[$pid]}"
    test "$current_cwd" = "${EXPECTED_CWD[$pid]}"
    test "$current_cmd" = "${EXPECTED_CMD[$pid]}"
    kill -KILL "$pid"
    printf 'KILL PID=%s START=%s\n' "$pid" "$current_start" \
      >> "$LINUX_EVIDENCE_ROOT/cleanup-signals.txt"
  fi
done
```

上段KILL只会在20秒后仍存活且PID的start ticks、cwd、cmdline仍与内存中不可变快照完全相同时执行。任一`test`失败必须停止并判`INVALID`，不得放宽检查或重试其他kill方法。

严格禁止：

- `pkill`、`killall`、进程组负PID kill；
- `wsl --shutdown`、`wsl --terminate`；
- 终止PID `30064`、`/init`、tmux或其他WSL任务；
- 删除数据库、artifact目录、socket、pytest临时目录或candidate树文件。

### 4.4 清理后零残留断言

```bash
ps -eo user=,pid=,ppid=,pgid=,sid=,lstart=,args= \
  > "$LINUX_EVIDENCE_ROOT/processes-after-cleanup-all.txt"
{
  pgrep -a -u "$(id -u)" -f "^${HOST_PREFIX}$" || true
  pgrep -a -u "$(id -u)" -f "^${SERVER_PREFIX}" || true
} > "$LINUX_EVIDENCE_ROOT/processes-after-cleanup-bound.txt"
ss -ltnp > "$LINUX_EVIDENCE_ROOT/listeners-after-cleanup.txt" 2>&1 || true

test ! -s "$LINUX_EVIDENCE_ROOT/processes-after-cleanup-bound.txt"
if grep -F ':6767' "$LINUX_EVIDENCE_ROOT/listeners-after-cleanup.txt"; then
  echo 'INVALID: port 6767 still occupied; do not kill unrelated owner' \
    | tee "$LINUX_EVIDENCE_ROOT/cleanup-decision.txt"
  exit 22
fi
printf 'TARGETED_CLEANUP_OK\n' > "$LINUX_EVIDENCE_ROOT/cleanup-decision.txt"
```

只有本节全部通过才允许进入全仓。

## 5. 清理后复用身份复核

不得重新sync、重建或修改树。按`CODEX_TASK_7_REWORK_2.md` §4.1重新核对并保存：

1. 两棵`.venv`存在；baseline/candidate HEAD精确匹配§3.1。
2. candidate status与r2 `candidate-status.txt` `cmp`为0。
3. candidate binary patch与r2 `reconstructed-candidate.patch` `cmp`为0。
4. tracked/untracked manifest及untracked blob map与r2 reconstructed文件全部`cmp`为0。
5. r3 `reused-evidence.sha256`中的七项逐项重新计算并匹配。
6. candidate四保护blob匹配§3.3。

任一不匹配即`INVALID`；不得修复树、不得重建、不得继续全仓。

## 6. 唯一允许的测试：全仓 baseline→candidate

本轮不重跑定向、Ruff、diff-check、import或collect-preflight。它们仅可通过匹配receipt引用。

仍保留每测试300秒上限；只在WSL Ubuntu 24.04命令行覆盖timeout处理方法为`signal`，禁止`-p no:timeout`。

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
```

baseline结束后、candidate开始前，必须记录两树相关进程与端口6767。若baseline留下任何绑定baseline/candidate树的host/server/pytest/runner进程，或端口6767仍被占用，判`INVALID`并停止；本卡不授权清理baseline残留或其他端口所有者。

仅当前述中间检查干净时运行：

```bash
run_full_suite candidate "$CANDIDATE_TREE"
```

两棵树禁止并行。任一出现外层exit 124、WSL崩溃、tee非零、collection/internal error、JUnit缺失/空/不可解析，均判`INVALID`。

candidate结束后再次记录进程与端口。若残留，本轮不再kill；报告中列出并按证据完整性判定，禁止隐瞒。

## 7. JUnit、失败集和判定

仅使用本轮r4完整全仓产物：

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

pytest非零但日志/JUnit不能产生完整case nodeid时判`INVALID`。baseline有case失败时，`baseline-known-failures.md`必须逐nodeid写失败类型、同环境依据和main基线证据；仅写“baseline也失败”不够。

判定：

- candidate exit0、JUnit有效、receipt/保护有效 → `PASS（绝对）`。
- 两边完整结束且candidate失败集⊆baseline、new-failures空、known逐项有依据 → `PASS（相对 main）`。
- candidate出现baseline没有的真实case failure/error → `FAIL`。
- 运行/环境/JUnit/tee/证据链未完成或不可审计 → `INVALID`。

任何PASS仍须Codex只读验收；Gate 2仍未执行、未判定，不代表可merge。

## 8. 持久化与报告

将r4 Linux evidence完整复制到新的Windows evidence根，生成两边SHA-256清单并逐项比对。不得覆盖r2/r3。

报告 `GROK_COMPLETION_7_REWORK_3.md` 必须包含：

1. r3 `INVALID` 已由Codex验收成立。
2. 新RUN_ID及Linux/Windows evidence绝对路径。
3. 清理前现场进程、每个目标PID的PPID/start ticks/cwd/cmdline。
4. 实际发送的TERM/KILL记录；若未需KILL也明确写明。
5. 明确未使用pkill/killall/进程组kill/WSL shutdown，未碰`/init`、tmux及其他进程。
6. 清理后进程与端口6767零残留证据。
7. 清理后复用身份、receipt、四保护blob复核结果。
8. baseline/candidate本轮完整命令、summary、pytest/tee退出码、JUnit及parse结果。
9. 两边全部失败nodeid、new-failures与baseline-known-failures逐项依据。
10. 运行后残留进程/端口检查与源HEAD/status/四保护blob。
11. Gate 1最终判定及逐条规则；Gate 2仍未执行、未判定；不可merge。
12. 未修改源码/tests/config/旧handoff，未commit/push/merge/tag或编辑PR/Issue。

## 9. 禁止项

- 不得修改`omnigent/`、`tests/`、`pyproject.toml`、`uv.lock`、CI、r05或既有handoff。
- 不得覆盖、追加、删除r2/r3 evidence；不得拼接r2/r3未完成全仓与r4。
- 不得`pkill`、`killall`、负PID kill、`wsl --shutdown/--terminate`或终止未精确验证的进程。
- 不得删除树、数据库、artifact、socket、pytest临时目录；不得重建树。
- 不得使用`-p no:timeout`，不得提高300秒上限，不得skip/xfail/排除失败测试。
- 不得重跑定向pytest、Ruff、diff-check、Gate 2或AgentCenter smoke。
- 不得checkout/switch/fetch/pull/rebase/cherry-pick/stash/reset/clean源工作树。
- 不得stage/commit/push/merge/tag、发版或编辑PR/Issue。
- 不得把Gate 1 PASS写成Gate 2 PASS或可merge。

## 10. 完成标准

1. 只对经`/proc`验证且绑定candidate树的host/server执行PID级清理；其他进程零影响。
2. 清理后candidate树相关进程和端口6767均为空。
3. 两棵复用树与r2/r3 receipt身份在清理后仍完全匹配。
4. baseline/candidate顺序全仓都真实结束并生成可解析JUnit；否则诚实判`INVALID`。
5. 失败集完全来自本轮r4，不拼接旧run。
6. 保留`--timeout=300 --timeout-method=signal`；未禁用插件、未提高上限。
7. Gate 1判定符合§7；任何PASS仍待Codex验收。
8. 只新增本报告与r4 evidence；源代码/tests/config/旧证据未改；Gate 2未执行；无commit/push/merge/tag。
