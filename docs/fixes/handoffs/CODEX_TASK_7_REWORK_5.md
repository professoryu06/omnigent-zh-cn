# CODEX TASK 7 REWORK 5 — 审计惰性 pytest tmux 后完成隔离 HOME 双侧 Gate 1

**执行者：** Grok（Gate 1 执行者；非独立审查者）  
**日期：** 2026-07-29  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** Gate 1=`INVALID`；Gate 2=未执行、未判定；不可 merge。  
**阶段边界：** 不终止tmux；把精确匹配、无子进程的历史pytest tmux分类为非阻塞惰性残留，然后在新run中完成隔离HOME的baseline→candidate全仓。其他树绑定进程仍阻塞。

## 1. 必读与交付

1. `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_4.md`
2. `docs/fixes/handoffs/CODEX_TASK_7_REWORK_4.md`
3. `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_3.md`
4. `docs/fixes/PRE_MERGE_GATES.md`
5. `pyproject.toml`第217–225、311–323行

只允许新建：

`docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_5.md`

不得修改任何旧任务卡、报告或r2–r5 evidence。

## 2. INVALID验收与根因

Codex已只读验收r5 `INVALID`成立：

- r4遗留baseline host/server已由Grok精确TERM，未KILL，端口6767已空。
- 两树身份、receipt、四保护blob与venv包列表匹配。
- r5全仓未启动，无JUnit/失败集，不得判PASS/FAIL。
- blanket `assert_tree_quiescent`因两个cwd=baseline的tmux返回非空，按原卡停止正确。

Codex现场只读复核两个tmux：

| PID快照 | 启动时间 | cwd | socket命令路径 | 子进程 |
|---|---|---|---|---|
| `36338` | 2026-07-29 10:41 | baseline树 | `/tmp/pytest-of-administrator/pytest-3/test_server_survives_inner_pro0/tmux.sock` | 无 |
| `61722` | 2026-07-29 14:23 | baseline树 | `/tmp/pytest-of-administrator/pytest-6/test_server_survives_inner_pro0/tmux.sock` | 无 |

共同特征：

- executable为`/usr/bin/tmux`，PPID为WSL `/init`；
- cmdline来自`test_server_survives_inner_pro*`；
- 使用`remain-on-exit on`、`exit-empty off`；
- `new-session -d -s main ... sh -c 'exit 0'`，pane命令已经退出；
- 无子进程，不监听TCP 6767；仅保留tmux server/self-pipe/Unix socket。

结论：它们是历史pytest留下的惰性tmux server，不是用户交互tmux，也不是仍在运行的pytest/runner/host。原卡“任何cwd进程均阻塞”过宽。

本轮不kill、不重建树；改为精确分类。只有完全符合§5的惰性pytest tmux可列入白名单，任何偏差仍判`INVALID`。

## 3. 固定身份与保护

- baseline树：`/tmp/omnigent-gate1-baseline-20260729-0106-dc83140-r2`
- candidate树：`/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2`
- baseline HEAD：`81594243f7a17303b9ba477b938ac323f938c2e4`
- candidate HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- 源HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`

保护blob：

| 文件 | 期望blob |
|---|---|
| `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` |
| `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` |
| `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` |
| `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` |

## 4. 新run与隔离HOME

创建全新r6，不得复用r5 seed/RUN_HOME：

```bash
set -euo pipefail
RUN_ID="$(date +%Y%m%d-%H%M)-dc83140-grok-r6"
LINUX_EVIDENCE_ROOT="/tmp/omnigent-premerge-evidence/$RUN_ID"
EVIDENCE_ROOT="/mnt/c/Users/Administrator/gate1-evidence/$RUN_ID"
BASELINE_TREE='/tmp/omnigent-gate1-baseline-20260729-0106-dc83140-r2'
CANDIDATE_TREE='/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2'
SEED_HOME="/tmp/omnigent-gate1-home-${RUN_ID}-seed"
RUN_HOME="/tmp/omnigent-gate1-home-${RUN_ID}-active"

mkdir -p "$LINUX_EVIDENCE_ROOT" "$EVIDENCE_ROOT"
test ! -e "$SEED_HOME"
test ! -e "$RUN_HOME"
install -d -m 700 "$SEED_HOME" "$RUN_HOME"
install -d -m 700 \
  "$SEED_HOME/.config" "$SEED_HOME/.cache" \
  "$SEED_HOME/.local" "$SEED_HOME/.local/share"
```

沿用`CODEX_TASK_7_REWORK_4.md` §4的`restore_run_home`，但变量必须是本轮r6路径。baseline和candidate运行前必须分别恢复同一个绝对`RUN_HOME`并与空seed `cmp`。

禁止读取、复制、删除真实用户HOME中的credentials、数据库或artifacts。递归删除只允许本卡创建且通过绝对路径检查的r6 `RUN_HOME`。

## 5. 精确tmux分类函数

替换旧卡的blanket `assert_tree_quiescent`。本函数不发送任何信号，只把完全匹配的惰性pytest tmux写入白名单，其余进程写入blocking文件。

```bash
classify_tree_processes() {
  tree="$1"
  label="$2"
  user_name="$(id -un)"
  allowed="$LINUX_EVIDENCE_ROOT/${label}-allowed-pytest-tmux.txt"
  blocking="$LINUX_EVIDENCE_ROOT/${label}-blocking-processes.txt"
  : > "$allowed"
  : > "$blocking"

  for proc in /proc/[0-9]*; do
    pid="${proc##*/}"
    test "$pid" = "$$" && continue
    cwd="$(readlink "$proc/cwd" 2>/dev/null || true)"
    test "$cwd" = "$tree" || continue

    exe="$(readlink "$proc/exe" 2>/dev/null || true)"
    cmd="$(tr '\0' ' ' < "$proc/cmdline" 2>/dev/null | sed 's/ $//' || true)"
    ppid="$(awk '{print $4}' "$proc/stat" 2>/dev/null || true)"
    start="$(awk '{print $22}' "$proc/stat" 2>/dev/null || true)"
    state="$(awk '{print $3}' "$proc/stat" 2>/dev/null || true)"

    if test "$exe" = '/usr/bin/tmux'; then
      socket="$(printf '%s\n' "$cmd" | awk '{for(i=1;i<=NF;i++) if($i=="-S"){print $(i+1); exit}}')"
      case "$socket" in
        "/tmp/pytest-of-${user_name}/pytest-"*/test_server_survives_inner_pro*/tmux.sock) ;;
        *) printf 'PID=%s\tREASON=tmux_socket_not_allowed\tCMD=%s\n' "$pid" "$cmd" >> "$blocking"; continue ;;
      esac

      case "$cmd" in
        *" -f /dev/null "*"remain-on-exit on"*"exit-empty off"*"new-session -d -s main"*"sh -c 'exit 0'"*) ;;
        *) printf 'PID=%s\tREASON=tmux_cmd_not_allowed\tCMD=%s\n' "$pid" "$cmd" >> "$blocking"; continue ;;
      esac

      mapfile -t children < <(pgrep -P "$pid" || true)
      if (( ${#children[@]} != 0 )); then
        printf 'PID=%s\tREASON=tmux_has_children\tCHILDREN=%s\n' \
          "$pid" "${children[*]}" >> "$blocking"
        continue
      fi

      case "$state" in S|I) ;;
        *) printf 'PID=%s\tREASON=tmux_state_%s\n' "$pid" "$state" >> "$blocking"; continue ;;
      esac

      printf 'PID=%s\tPPID=%s\tSTART=%s\tSTATE=%s\tCWD=%s\tSOCKET=%s\tCMD=%s\n' \
        "$pid" "$ppid" "$start" "$state" "$cwd" "$socket" "$cmd" >> "$allowed"
      continue
    fi

    printf 'PID=%s\tREASON=non_whitelisted_tree_process\tEXE=%s\tCMD=%s\n' \
      "$pid" "$exe" "$cmd" >> "$blocking"
  done

  allowed_count="$(wc -l < "$allowed")"
  if (( allowed_count > 16 )); then
    printf 'REASON=too_many_allowed_tmux\tCOUNT=%s\n' "$allowed_count" >> "$blocking"
  fi

  ss -ltnp > "$LINUX_EVIDENCE_ROOT/${label}-listeners.txt" 2>&1 || true
  test ! -s "$blocking"
  ! grep -F ':6767' "$LINUX_EVIDENCE_ROOT/${label}-listeners.txt"
}
```

允许项必须全部满足：exact cwd、`/usr/bin/tmux`、pytest临时socket模式、指定测试名、`exit 0` dead-pane配置、无子进程、休眠状态、数量≤16。不得仅因进程名叫tmux就允许。

不得调用`tmux kill-server`，不得TERM/KILL这些白名单tmux；它们只记录，不进入Gate失败集。

## 6. host/server清理与前置身份

沿用`CODEX_TASK_7_REWORK_4.md` §5的`cleanup_tree_host_server`，只处理精确host/server模块。不得扩展到tmux。

前置顺序：

```bash
cleanup_tree_host_server "$BASELINE_TREE" 'pre-baseline-hostserver'
cleanup_tree_host_server "$CANDIDATE_TREE" 'pre-candidate-hostserver'
classify_tree_processes "$BASELINE_TREE" 'pre-baseline-processes'
classify_tree_processes "$CANDIDATE_TREE" 'pre-candidate-processes'
```

只要`*-blocking-processes.txt`非空或端口6767被占用，即`INVALID`并停止。只有`*-allowed-pytest-tmux.txt`非空不阻止运行。

重新执行上一卡§6的环境、两venv包列表、HEAD/status/patch/manifest/untracked blob/receipt/四保护blob复核。任一不匹配即`INVALID`；不得sync、安装、重建或修树。

## 7. 全仓测试命令

沿用上一卡的r6 `restore_run_home`，并使用以下完整命令。只允许这两次全仓；不得重跑定向/Ruff/diff-check。

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
  cd "$previous_dir"
}

run_full_suite baseline "$BASELINE_TREE"
```

baseline必须到达summary，tee 0且JUnit存在、非空、可解析；否则`INVALID`。

baseline完成后：

```bash
cleanup_tree_host_server "$BASELINE_TREE" 'post-baseline-hostserver'
classify_tree_processes "$BASELINE_TREE" 'post-baseline-processes'
classify_tree_processes "$CANDIDATE_TREE" 'candidate-before-run-processes'
run_full_suite candidate "$CANDIDATE_TREE"
```

只有三个classify结果均无blocking且6767为空才允许candidate。

candidate完成后：

```bash
cleanup_tree_host_server "$CANDIDATE_TREE" 'post-candidate-hostserver'
classify_tree_processes "$CANDIDATE_TREE" 'post-candidate-processes'
```

白名单tmux可保留；任何其他残留必须记录并按`INVALID`处理，不得临时扩大白名单或kill。

两侧必须顺序执行并各自从同一个空seed恢复相同绝对RUN_HOME。保持每测试`--timeout=300 --timeout-method=signal`；禁止`-p no:timeout`或提高300秒。

## 8. JUnit、失败集和判定

严格执行`CODEX_TASK_7_REWORK_4.md` §8的统一JUnit dotted nodeid解析器，仅使用本轮r6两侧JUnit：

```bash
comm -13 \
  "$LINUX_EVIDENCE_ROOT/baseline-fail-ids.txt" \
  "$LINUX_EVIDENCE_ROOT/candidate-fail-ids.txt" \
  > "$LINUX_EVIDENCE_ROOT/new-failures.txt"
```

- candidate exit0、JUnit有效、身份/HOME/进程分类有效 → `PASS（绝对）`。
- 两侧完整、candidate失败集⊆baseline、new-failures空、baseline known逐项有依据 → `PASS（相对 main）`。
- candidate新增真实case failure/error → `FAIL`。
- 任一侧不完整、outer timeout、WSL/tee/JUnit/身份/HOME/blocking进程证据损坏 → `INVALID`。

若需相对PASS，`baseline-known-failures.md`必须逐本轮baseline nodeid写同环境原因与依据；仅写“main也失败”不足。

惰性tmux不属于pytest case失败，也不单独改变Gate判定；其分类证据缺失或不合规则`INVALID`。

任何PASS仍须Codex只读验收；Gate 2仍未执行、未判定，不代表可merge。

## 9. 报告、禁止项与完成标准

将r6 Linux evidence全量复制到新的Windows evidence根并比对SHA-256；不得覆盖r2–r5。

报告必须包含：

1. r5 `INVALID`已验收，以及blanket quiescence过宽的根因。
2. 每个白名单tmux的PID/PPID/start/state/cwd/exe/socket/cmdline/子进程数。
3. 明确白名单tmux未收到任何信号，未调用tmux kill-server。
4. r6 RUN_ID、两证据根、隔离HOME seed与两侧home-before cmp。
5. host/server精确清理与端口6767证据。
6. 环境、venv包列表、HEAD/patch/manifest/receipt/四保护结果。
7. 两侧完整summary、pytest/tee exit、JUnit parse、失败nodeid、new-failures。
8. baseline known逐项依据（仅相对PASS需要）。
9. Gate 1最终判定；Gate 2仍未执行、未判定；不可merge。
10. 未改源码/tests/config/旧handoff，未commit/push/merge/tag或编辑PR/Issue。

禁止：

- 不得修改`omnigent/`、`tests/`、`pyproject.toml`、`uv.lock`、CI、r05或旧handoff。
- 不得kill/TERM/KILL/tmux kill-server处理白名单tmux；不得pkill/killall/负PID/组kill/WSL shutdown。
- 不得把非精确匹配tmux加入白名单；blocking非空必须停止。
- 不得读取/复制/删除真实HOME；只可重置经路径校验的本轮r6 RUN_HOME。
- 不得拼接r2–r5全仓；不得复用r5未运行结果。
- 不得`-p no:timeout`、提高300秒、skip/xfail或排除失败测试。
- 不得重跑定向/Ruff/diff-check/Gate 2，不得sync/安装/重建树。
- 不得stage/commit/push/merge/tag、发版或编辑PR/Issue。

完成标准：

1. 历史与本轮惰性pytest tmux均通过精确分类，无信号、无子进程、无6767影响。
2. 其他树绑定进程全部为零；host/server仅按精确函数清理。
3. 两侧使用同一隔离HOME初始seed且身份/依赖完全匹配。
4. baseline与candidate均在r6真实完成并生成可解析JUnit；否则诚实`INVALID`。
5. 失败比较只来自r6；Gate判定符合§8。
6. 只新增本报告与r6 evidence；Gate 2未执行；无commit/push/merge/tag。
