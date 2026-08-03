# GROK_FULLRUN_20260731 — Controller C full-run (BUG-1/2/3 post-fix)

> Read-only full-run executor. No source changes. Not Gate 2 PASS. Not mergeable.

## RUN

| Field | Value |
|---|---|
| RUN_ID | 20260731-114121-dc83140-grok-fullrun-cli0146-r1 |
| Evidence | C:\\Users\\Administrator\\omnigent-diagnostics\\20260731-114121-dc83140-grok-fullrun-cli0146-r1\\ |
| Evidence exists | True (persistent) |
| Worktree | F:\\codex-ai\\git项目部署\\tmp\\omnigent-review |
| HEAD | dc83140c73ceb12fa165753c1880c19f68da86f4 |
| Branch | docs/fix-plans-core-secondary |
| Attempt | Controller C 1_of_1 |

## Outcome

**primary:** FAIL_CODEX_RESPONSES_STREAM_AFTER_SPAWN

| Check | Result |
|---|---|
| C exit | **1** (not 0) |
| Assistant CONTROLLER_OK | **False** |
| User prompt contains phrase | True (title + user message only — not counted) |
| turn/completed | False |
| 240s idle timeout | **False** (failed at ~48s) |
| outer 300s timeout | False |

## What worked (BUG path)

| Layer | Result |
|---|---|
| Server READY | True (pid 26256, 10 health samples) |
| Host online | True (pid 27484, host_id=host_0d637c9f…) |
| BUG-3 runner launch | **True** — runner_id=
unner_token_d8407afaf25a89577e90be98fafc3982, runner_pid≈18324 |
| BUG-2 harness dispatch | **True** — canonical=codex module=omnigent.inner.codex_harness mode=sdk |
| TerminalRegistry.launch | **False** (not observed) |
| codex-native ensure | Not taken (correct for bare codex) |
| Native CLI spawn | **True** pid=23872 path matches fixed 0.146.0 SHA c343ba4… size 358650672 |
| BUG-1 host stability | Host stayed online during C (~48s) |

## What failed (after spawn)

Codex app-server / executor stream disconnected:

`	ext
error sending request for url (http://127.0.0.1:10100/v1/responses)
session_status=failed
last_task_error_code=runner_error
`

Boundary classification: **auth / model gateway / responses endpoint** after successful runner+CLI spawn.  
Not BUG-3 (runner launched). Not primary BUG-2 mis-route to codex-native (dispatch was sdk/codex_harness).

### Secondary Windows noise (not the turn-kill path)

Runner logged non-fatal:

`	ext
Failed to auto-create omnigent REPL terminal
create_terminal_instance → RuntimeError: Native terminal harnesses (tmux/PTY) are not supported on Windows
`

This is the **omnigent REPL terminal** auto-create path, not _auto_create_codex_terminal for codex-native. Session continued into Codex CLI; failure was later responses stream.

## Native identity

| Field | Value |
|---|---|
| Task-card path | C:\\Users\\Administrator\\.codex\\codex-win32-x64\\...\\codex.exe (**missing**) |
| Resolved path used | npm vendor path (only SHA/size match) |
| version | codex-cli 0.146.0 |
| size | 358650672 |
| sha256 | bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb |

HARNESS_CODEX_PATH set before server/host/C; OMNIGENT_RUNNER_ENV_PASSTHROUGH=HARNESS_CODEX_PATH.

## TUN

Meta adapter Up at start; executor did not change TUN.

## Precheck note

Competing Windows Store Codex + leftover host daemons observed; not killed. Isolated OMNIGENT_DATA_DIR + new port used.

## Cleanup / leak-scan

| Item | Result |
|---|---|
| server/host/C/runner killed | True |
| port free | True |
| runtime delete | attempted (see cleanup.txt; may leave empty/partial under TEMP short path) |
| leak-scan hits | **0** |
| required-check | see d2-required-files-check.txt |

## Gate boundary

- Gate 1 remains relative-main PASS (prior conclusion).
- **This full-run is NOT Gate 2 PASS.**
- **Do not merge on this result.**

## Next (for Codex only-read验收)

1. Fix/verify model path for gpt-5.6-sol → why Codex hits 127.0.0.1:10100/v1/responses and disconnects.
2. Optionally harden Windows: skip omnigent REPL terminal auto-create when unsupported (secondary UX noise).
3. Re-run one full-run after model/gateway fix; require true **assistant** item with CONTROLLER_OK and C exit=0.

## Deliverables path

Evidence root (persistent):

C:\\Users\\Administrator\\omnigent-diagnostics\\20260731-114121-dc83140-grok-fullrun-cli0146-r1\\

Key files: d2-business-result-corrected.json, d2-session-final.json, 
unner-logs-tail.txt, outcome.json, leak-scan.txt, manifest.txt.
