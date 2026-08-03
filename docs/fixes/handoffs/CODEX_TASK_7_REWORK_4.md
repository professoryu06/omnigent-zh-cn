# CODEX TASK 7 REWORK 4 — 隔离 HOME 的 Gate 1 双侧重跑

**执行者：** Grok（Gate 1 执行者；非独立审查者）  
**日期：** 2026-07-29  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** Gate 1=`INVALID`；Gate 2=未执行、未判定；不可 merge。  
**阶段边界：** 精确清理当前 baseline 遗留 host/server，在同一WSL、同一锁定依赖、同一隔离HOME初始状态下重新顺序执行完整 baseline→candidate。不得修改源码/tests/config，不得复用旧全仓结果形成判定。

## 1. 必读与交付

1. `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_3.md`
2. `docs/fixes/handoffs/CODEX_TASK_7_REWORK_3.md`
3. `docs/fixes/handoffs/CODEX_TASK_7_REWORK_2.md`
4. `docs/fixes/PRE_MERGE_GATES.md`
5. `pyproject.toml` 第217–225、311–323行

只允许新建报告：

`docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_4.md`

不得修改任何旧任务卡、报告或r2/r3/r4 evidence。

## 2. 已验收事实与为什么必须双侧重跑

Codex已只读验收 `GROK_COMPLETION_7_REWORK_3.md`：Gate 1=`INVALID`成立。

已确认：

- r4 baseline全仓完整结束：`128 failed, 14921 passed, 103 skipped, 7 xfailed, 237 warnings, 3 errors, 3 subtests passed, 4 rerun`；exit 1、tee 0、JUnit可解析。
- r4 candidate未启动，不能判PASS/FAIL。
- baseline结束后仍残留：

```text
60275  …/baseline-…r2/.venv/bin/python -m omnigent.host._daemon_entry --local
60276  …/baseline-…r2/.venv/bin/python -m omnigent.cli server --host 127.0.0.1 --port 6767 …
```

- server使用真实用户HOME下的 `~/.omnigent-zh-cn/chat.db` 与 artifacts。baseline可能改变共享HOME状态；没有baseline开跑前的HOME快照。

因此，本卡**不允许仅跑candidate后与r4 baseline组合**。那会让candidate读取baseline运行后的共享状态，无法证明“同环境、同初始状态”。r4 baseline仅作诊断参考，不进入本轮失败集比较。

本轮创建一个任务专属的空HOME seed，并在baseline、candidate之前分别把同一个active HOME恢复到完全相同的seed；两侧使用相同绝对HOME路径，消除用户HOME、数据库、artifact与路径差异。

## 3. 固定树、身份与旧证据

### 3.1 WSL树

- baseline：`/tmp/omnigent-gate1-baseline-20260729-0106-dc83140-r2`
- candidate：`/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2`
- baseline HEAD：`81594243f7a17303b9ba477b938ac323f938c2e4`
- candidate HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`

### 3.2 只读证据

- r2：`C:\Users\Administrator\gate1-evidence\20260729-0106-dc83140-r2\`
- r3：`C:\Users\Administrator\gate1-evidence\20260729-1143-dc83140-grok-r3\`
- r4：`C:\Users\Administrator\gate1-evidence\20260729-1411-dc83140-grok-r4\`

r4 baseline关键文件的Codex只读SHA-256仅作完整性参考，不授权用于本轮判定：

| 文件 | SHA-256 |
|---|---|
| `baseline-pytest.txt` | `611f1fe2a027b5830fea0468c14949f6b739a54b9922c10271c77940797bb0a7` |
| `baseline-junit.xml` | `46dca1310a290302b4a70e063be5a95d6a3c8f7013c46fab78cc0e202637bb86` |
| `baseline-fail-ids.txt` | `9ebaf3ebf94f8bf086c8658b71c46d701c9798682843acc53c61afa5631f25cc` |

### 3.3 源工作树保护

源HEAD必须保持 `dc83140c73ceb12fa165753c1880c19f68da86f4`。

| 文件 | 期望blob |
|---|---|
| `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` |
| `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` |
| `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` |
| `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` |

## 4. 新run与受控临时HOME

```bash
set -euo pipefail
RUN_ID="$(date +%Y%m%d-%H%M)-dc83140-grok-r5"
LINUX_EVIDENCE_ROOT="/tmp/omnigent-premerge-evidence/$RUN_ID"
EVIDENCE_ROOT="/mnt/c/Users/Administrator/gate1-evidence/$RUN_ID"
BASELINE_TREE='/tmp/omnigent-gate1-baseline-20260729-0106-dc83140-r2'
CANDIDATE_TREE='/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2'
SEED_HOME="/tmp/omnigent-gate1-home-${RUN_ID}-seed"
RUN_HOME="/tmp/omnigent-gate1-home-${RUN_ID}-active"

mkdir -p "$LINUX_EVIDENCE_ROOT" "$EVIDENCE_ROOT"
printf '%s\n' "$RUN_ID" > "$LINUX_EVIDENCE_ROOT/run-id.txt"

case "$SEED_HOME" in /tmp/omnigent-gate1-home-*-seed) ;;
  *) echo 'INVALID seed path' >&2; exit 30 ;;
esac
case "$RUN_HOME" in /tmp/omnigent-gate1-home-*-active) ;;
  *) echo 'INVALID active home path' >&2; exit 31 ;;
esac

test ! -e "$SEED_HOME"
test ! -e "$RUN_HOME"
install -d -m 700 "$SEED_HOME" "$RUN_HOME"
install -d -m 700 \
  "$SEED_HOME/.config" "$SEED_HOME/.cache" \
  "$SEED_HOME/.local" "$SEED_HOME/.local/share"
```

不得复制真实HOME、credentials、`.omnigent*`、数据库或artifact到seed。seed只含上述空目录。

统一恢复函数：

```bash
restore_run_home() {
  phase="$1"
  resolved="$(readlink -f "$RUN_HOME")"
  case "$resolved" in /tmp/omnigent-gate1-home-*-active) ;;
    *) echo "INVALID resolved active home: $resolved" >&2; return 32 ;;
  esac

  rm -rf --one-file-system -- "$resolved"
  install -d -m 700 "$resolved"
  cp -a "$SEED_HOME/." "$resolved/"

  find "$resolved" -printf '%P|%y|%m|%s\n' | sort \
    > "$LINUX_EVIDENCE_ROOT/${phase}-home-before.txt"
  find "$SEED_HOME" -printf '%P|%y|%m|%s\n' | sort \
    > "$LINUX_EVIDENCE_ROOT/${phase}-seed.txt"
  cmp "$LINUX_EVIDENCE_ROOT/${phase}-home-before.txt" \
      "$LINUX_EVIDENCE_ROOT/${phase}-seed.txt"
}
```

`rm -rf`仅授权用于本卡创建且通过上述绝对路径检查的`RUN_HOME`。不得删除真实HOME、旧树、旧evidence、数据库、artifact或其他`/tmp`目录。

## 5. 精确host/server清理函数

此函数只允许清理参数树中精确模块匹配的host/server；先server后host，TERM后20秒仍存活才在start ticks/cwd/cmdline未变时KILL。

```bash
cleanup_tree_host_server() {
  tree="$1"
  label="$2"
  host_prefix="$tree/.venv/bin/python -m omnigent.host._daemon_entry --local"
  server_prefix="$tree/.venv/bin/python -m omnigent.cli server "

  ps -eo user=,pid=,ppid=,pgid=,sid=,lstart=,args= \
    > "$LINUX_EVIDENCE_ROOT/${label}-processes-before.txt"
  ss -ltnp > "$LINUX_EVIDENCE_ROOT/${label}-listeners-before.txt" 2>&1 || true

  mapfile -t host_pids < <(pgrep -u "$(id -u)" -f "^${host_prefix}$" || true)
  mapfile -t server_pids < <(pgrep -u "$(id -u)" -f "^${server_prefix}" || true)
  if (( ${#host_pids[@]} > 1 || ${#server_pids[@]} > 1 )); then
    echo 'INVALID unexpected host/server multiplicity' >&2
    return 40
  fi

  declare -A expected_start expected_cwd expected_cmd
  : > "$LINUX_EVIDENCE_ROOT/${label}-cleanup-targets.txt"
  for pid in "${server_pids[@]}" "${host_pids[@]}"; do
    test -n "$pid" || continue
    test -r "/proc/$pid/cmdline"
    cmd="$(tr '\0' ' ' < "/proc/$pid/cmdline" | sed 's/ $//')"
    cwd="$(readlink "/proc/$pid/cwd")"
    start="$(awk '{print $22}' "/proc/$pid/stat")"
    ppid="$(awk '{print $4}' "/proc/$pid/stat")"
    test "$cwd" = "$tree"
    case "$cmd" in "$host_prefix"|"$server_prefix"*) ;;
      *) echo "INVALID unexpected cmdline PID=$pid" >&2; return 41 ;;
    esac
    expected_start["$pid"]="$start"
    expected_cwd["$pid"]="$cwd"
    expected_cmd["$pid"]="$cmd"
    printf 'PID=%s\tPPID=%s\tSTART=%s\tCWD=%s\tCMD=%s\n' \
      "$pid" "$ppid" "$start" "$cwd" "$cmd" \
      >> "$LINUX_EVIDENCE_ROOT/${label}-cleanup-targets.txt"
  done

  if (( ${#host_pids[@]} == 1 && ${#server_pids[@]} == 1 )); then
    test "$(awk '{print $4}' "/proc/${server_pids[0]}/stat")" = "${host_pids[0]}"
  fi

  : > "$LINUX_EVIDENCE_ROOT/${label}-cleanup-signals.txt"
  for pid in "${server_pids[@]}" "${host_pids[@]}"; do
    test -n "$pid" || continue
    if test -r "/proc/$pid/stat"; then
      test "$(awk '{print $22}' "/proc/$pid/stat")" = "${expected_start[$pid]}"
      test "$(readlink "/proc/$pid/cwd")" = "${expected_cwd[$pid]}"
      test "$(tr '\0' ' ' < "/proc/$pid/cmdline" | sed 's/ $//')" = "${expected_cmd[$pid]}"
      kill -TERM "$pid"
      printf 'TERM PID=%s START=%s\n' "$pid" "${expected_start[$pid]}" \
        >> "$LINUX_EVIDENCE_ROOT/${label}-cleanup-signals.txt"
    fi
  done

  for _ in $(seq 1 40); do
    alive=0
    for pid in "${server_pids[@]}" "${host_pids[@]}"; do
      test -n "$pid" || continue
      kill -0 "$pid" 2>/dev/null && alive=1
    done
    (( alive == 0 )) && break
    sleep 0.5
  done

  for pid in "${server_pids[@]}" "${host_pids[@]}"; do
    test -n "$pid" || continue
    if kill -0 "$pid" 2>/dev/null; then
      test "$(awk '{print $22}' "/proc/$pid/stat")" = "${expected_start[$pid]}"
      test "$(readlink "/proc/$pid/cwd")" = "${expected_cwd[$pid]}"
      test "$(tr '\0' ' ' < "/proc/$pid/cmdline" | sed 's/ $//')" = "${expected_cmd[$pid]}"
      kill -KILL "$pid"
      printf 'KILL PID=%s START=%s\n' "$pid" "${expected_start[$pid]}" \
        >> "$LINUX_EVIDENCE_ROOT/${label}-cleanup-signals.txt"
    fi
  done

  {
    pgrep -a -u "$(id -u)" -f "^${host_prefix}$" || true
    pgrep -a -u "$(id -u)" -f "^${server_prefix}" || true
  } > "$LINUX_EVIDENCE_ROOT/${label}-processes-after.txt"
  ss -ltnp > "$LINUX_EVIDENCE_ROOT/${label}-listeners-after.txt" 2>&1 || true
  test ! -s "$LINUX_EVIDENCE_ROOT/${label}-processes-after.txt"
}

assert_tree_quiescent() {
  tree="$1"
  label="$2"
  : > "$LINUX_EVIDENCE_ROOT/${label}-tree-bound-processes.txt"
  for proc in /proc/[0-9]*; do
    pid="${proc##*/}"
    test "$pid" = "$$" && continue
    cwd="$(readlink "$proc/cwd" 2>/dev/null || true)"
    test "$cwd" = "$tree" || continue
    cmd="$(tr '\0' ' ' < "$proc/cmdline" 2>/dev/null | sed 's/ $//' || true)"
    printf 'PID=%s\tCWD=%s\tCMD=%s\n' "$pid" "$cwd" "$cmd" \
      >> "$LINUX_EVIDENCE_ROOT/${label}-tree-bound-processes.txt"
  done
  ss -ltnp > "$LINUX_EVIDENCE_ROOT/${label}-listeners.txt" 2>&1 || true
  test ! -s "$LINUX_EVIDENCE_ROOT/${label}-tree-bound-processes.txt"
  ! grep -F ':6767' "$LINUX_EVIDENCE_ROOT/${label}-listeners.txt"
}
```

禁止`pkill`、`killall`、负PID kill、进程组kill、`wsl --shutdown/--terminate`。不得终止`/init`、tmux、其他pytest或任何未进入`cleanup-targets.txt`的进程。

## 6. 前置清理与同依赖身份

先清理当前r4遗留baseline host/server，再确认端口6767为空：

```bash
cleanup_tree_host_server "$BASELINE_TREE" 'pre-baseline-residue'
cleanup_tree_host_server "$CANDIDATE_TREE" 'pre-candidate-residue'
assert_tree_quiescent "$BASELINE_TREE" 'pre-baseline-quiescent'
assert_tree_quiescent "$CANDIDATE_TREE" 'pre-candidate-quiescent'
```

记录同一WSL环境及依赖：

```bash
{
  cat /proc/sys/kernel/random/boot_id
  uname -a
  cat /etc/os-release
  uv --version
  "$BASELINE_TREE/.venv/bin/python" -V
  "$CANDIDATE_TREE/.venv/bin/python" -V
} > "$LINUX_EVIDENCE_ROOT/environment.txt" 2>&1

for item in "baseline:$BASELINE_TREE" "candidate:$CANDIDATE_TREE"; do
  label="${item%%:*}"
  tree="${item#*:}"
  "$tree/.venv/bin/python" - <<'PY' \
    > "$LINUX_EVIDENCE_ROOT/${label}-packages.txt"
import importlib.metadata as md
rows = sorted(
    (dist.metadata.get("Name", "").lower(), dist.version)
    for dist in md.distributions()
)
for name, version in rows:
    print(f"{name}=={version}")
PY
done
cmp "$LINUX_EVIDENCE_ROOT/baseline-packages.txt" \
    "$LINUX_EVIDENCE_ROOT/candidate-packages.txt"
```

同时重新执行 `CODEX_TASK_7_REWORK_3.md` §5 的HEAD/status/patch/manifest/untracked blob/receipt/四保护blob只读复核。任一不匹配、venv包列表不同或端口被其他进程占用，判`INVALID`并停止；不得sync、安装、重建或修树。

## 7. 唯一允许的测试：隔离HOME双侧全仓

运行函数：

```bash
run_full_suite() {
  label="$1"
  tree="$2"
  restore_run_home "$label"

  previous_dir="$PWD"
  cd "$tree"
  set +e
  set -o pipefail
  HOME="$RUN_HOME" \
  XDG_CONFIG_HOME="$RUN_HOME/.config" \
  XDG_CACHE_HOME="$RUN_HOME/.cache" \
  XDG_DATA_HOME="$RUN_HOME/.local/share" \
  PYTHONUNBUFFERED=1 \
  timeout --signal=INT --kill-after=60s 21600s \
    uv run pytest -q --color=no \
      --timeout=300 --timeout-method=signal \
      --junitxml="$LINUX_EVIDENCE_ROOT/${label}-junit.xml" \
      2>&1 | tee "$LINUX_EVIDENCE_ROOT/${label}-pytest.txt"
  statuses=("${PIPESTATUS[@]}")
  command_exit="${statuses[0]}"
  tee_exit="${statuses[1]}"
  set +o pipefail
  set -e
  set -o pipefail

  printf '%s\n' "$command_exit" > "$LINUX_EVIDENCE_ROOT/${label}-pytest.exit"
  printf '%s\n' "$tee_exit" > "$LINUX_EVIDENCE_ROOT/${label}-tee.exit"
  printf 'COMMAND_EXIT:%s\nTEE_EXIT:%s\n' "$command_exit" "$tee_exit" \
    | tee -a "$LINUX_EVIDENCE_ROOT/${label}-pytest.txt"

  find "$RUN_HOME" -printf '%P|%y|%m|%s\n' | sort \
    > "$LINUX_EVIDENCE_ROOT/${label}-home-after.txt"
  cd "$previous_dir"
}
```

顺序：

```bash
run_full_suite baseline "$BASELINE_TREE"
```

baseline必须到达pytest summary，tee 0且JUnit存在、非空、可解析。若不满足即`INVALID`，不得进入candidate。

baseline证据冻结后，只清理精确绑定baseline树的host/server：

```bash
cleanup_tree_host_server "$BASELINE_TREE" 'post-baseline-residue'
assert_tree_quiescent "$BASELINE_TREE" 'post-baseline-quiescent'
assert_tree_quiescent "$CANDIDATE_TREE" 'candidate-still-quiescent'
```

上述断言会逐个检查 `/proc/*/cwd`；若还有其他绑定baseline/candidate树的pytest/runner/helper进程，或端口6767仍被占用，判`INVALID`，不得 broad kill。

candidate开始前，`restore_run_home candidate`会把同一绝对`RUN_HOME`恢复为seed。随后：

```bash
run_full_suite candidate "$CANDIDATE_TREE"
```

candidate也必须到达summary、tee 0、JUnit有效。完成并冻结证据后：

```bash
cleanup_tree_host_server "$CANDIDATE_TREE" 'post-candidate-residue'
assert_tree_quiescent "$CANDIDATE_TREE" 'post-candidate-quiescent'
```

两侧禁止并行。必须保留每测试 `--timeout=300 --timeout-method=signal`；禁止`-p no:timeout`或提高300秒上限。

## 8. JUnit失败集

使用同一JUnit算法为两侧生成可比较的dotted nodeid：

```bash
for label in baseline candidate; do
  test -s "$LINUX_EVIDENCE_ROOT/${label}-junit.xml"
  python3 - "$LINUX_EVIDENCE_ROOT/${label}-junit.xml" \
    "$LINUX_EVIDENCE_ROOT/${label}-fail-ids.txt" <<'PY'
import sys
import xml.etree.ElementTree as ET

src, dst = sys.argv[1:]
root = ET.parse(src).getroot()
ids = set()
for case in root.iter("testcase"):
    if case.find("failure") is None and case.find("error") is None:
        continue
    classname = case.attrib.get("classname", "")
    name = case.attrib.get("name", "")
    ids.add(f"{classname}::{name}")
with open(dst, "w", encoding="utf-8", newline="\n") as handle:
    for nodeid in sorted(ids):
        handle.write(nodeid + "\n")
print(f"junit-ok fail_ids={len(ids)}")
PY
done

comm -13 \
  "$LINUX_EVIDENCE_ROOT/baseline-fail-ids.txt" \
  "$LINUX_EVIDENCE_ROOT/candidate-fail-ids.txt" \
  > "$LINUX_EVIDENCE_ROOT/new-failures.txt"
```

pytest非零但JUnit不能生成完整case nodeid时判`INVALID`。不得混用r4 dotted列表与本轮log斜杠nodeid。

如果需要相对PASS，创建`baseline-known-failures.md`，对本轮每个baseline nodeid逐项写失败类型、同环境原因与依据。仅写“main也失败”不够；无法完成逐项定性则不得相对PASS。

## 9. 判定

- candidate exit0、JUnit有效、两侧HOME/身份/receipt有效 → `PASS（绝对）`。
- 两侧完整结束、candidate失败集⊆baseline、`new-failures.txt`空、baseline known逐项有依据 → `PASS（相对 main）`。
- candidate出现baseline没有的真实case failure/error → `FAIL`。
- 任一侧未完成、outer timeout、WSL/tee/JUnit/证据/环境身份损坏、collection/internal error → `INVALID`。

r4 baseline仅作诊断参考，**不得**进入本轮`comm`或Gate判定。

任何PASS仍需Codex只读验收；Gate 2仍未执行、未判定，不代表可merge。

## 10. 持久化、报告与禁止项

将新Linux evidence全量复制到新的Windows evidence根，生成双方SHA-256清单并逐项匹配。不得覆盖r2/r3/r4。

`GROK_COMPLETION_7_REWORK_4.md` 必须包含：

1. r4 `INVALID` 已由Codex验收；拒绝candidate-only的共享HOME依据。
2. 新RUN_ID、Linux/Windows evidence路径及双侧SHA-256结果。
3. 初始baseline残留PID的start ticks/cwd/cmdline、TERM/KILL与零残留证据。
4. seed与两侧`*-home-before.txt`的cmp结果；两侧使用同一绝对RUN_HOME且均从空seed恢复。
5. WSL boot/environment、两venv包列表cmp、HEAD/status/patch/manifest/receipt/四保护结果。
6. 两侧完整命令、summary、pytest/tee exit、JUnit parse与时长。
7. baseline后精确清理、candidate前端口/进程卫生；candidate后清理结果。
8. 两侧JUnit失败nodeid、new-failures、需要时逐项baseline-known依据。
9. Gate 1严格判定；Gate 2仍未执行、未判定；不可merge。
10. 未改源码/tests/config/旧handoff，未commit/push/merge/tag或编辑PR/Issue。

禁止：

- 不得修改`omnigent/`、`tests/`、`pyproject.toml`、`uv.lock`、CI、r05或旧handoff。
- 不得把r4 baseline与新candidate组合判定；不得拼接r2/r3/r4全仓。
- 不得读取/复制/删除真实用户HOME中的credentials、数据库或artifacts。
- 除经绝对路径检查的本轮`RUN_HOME`外，不得递归删除任何路径。
- 不得使用pkill/killall/负PID/进程组kill/WSL shutdown。
- 不得使用`-p no:timeout`、提高300秒、skip/xfail或排除失败测试。
- 不得重跑定向pytest、Ruff、diff-check、Gate 2或AgentCenter smoke。
- 不得sync/安装依赖、重建树、checkout/switch/fetch/pull/rebase/cherry-pick/stash/reset/clean源树。
- 不得stage/commit/push/merge/tag、发版或编辑PR/Issue。

## 11. 完成标准

1. 旧baseline残留仅以PID级受保护信号清理；其他进程零影响。
2. baseline/candidate使用同一绝对隔离HOME，且各自运行前均与同一空seed完全匹配。
3. 两venv依赖列表、树身份、candidate快照和四保护全部匹配。
4. 两侧全仓均在本轮真实完成并产生可解析JUnit；否则诚实判`INVALID`。
5. 失败比较完全来自本轮，不使用旧全仓结果。
6. 保留300秒单测保护；未禁用timeout插件。
7. Gate判定符合§9；任何PASS仍待Codex验收。
8. 只新增本报告与新evidence；Gate 2未执行；无commit/push/merge/tag。
