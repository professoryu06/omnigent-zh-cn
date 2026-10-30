# HERMES DIAGNOSIS — Gate 1 FINAL Full Review (r6)

- **RUN_ID**: `20260805-164315-5c8b9ce-hermes-gate1-r6`
- **Date (UTC)**: 2026-08-05 16:43:15 → 21:47:53 (duration 5h04m38s)
- **Executor**: Hermes (acceptance-only, no source/test/STATUS changes)
- **Authority**: classification belongs to Codex; this report records evidence + strict-rule application.

## 1. Scope & Trees

| Tree | Path | HEAD | Worktree state |
|---|---|---|---|
| main | F:\codex-ai\git项目部署\tmp\omnigent-gate1-main | `81594243f7a17303b9ba477b938ac323f938c2e4` | clean |
| candidate | F:\codex-ai\git项目部署\tmp\omnigent-review | `5c8b9ce96f7552d380276fe6de04651f2b19531a` + Grok R5 uncommitted fix (4 files) | 4 modified files preserved, untouched |

Grok R5 uncommitted files (preserved, not reset):
1. `omnigent/inner/codex_executor.py`
2. `tests/inner/test_codex_executor.py`
3. `tests/inner/test_codex_runtime_isolation.py`
4. `tests/server/integration/test_session_host_launch.py`

Read-only reference: `C:\Users\Administrator\omnigent-diagnostics\20260806-001202-5c8b9ce-grok-gate1-race-obs\`

## 2. Platform (authoritative = WSL/Linux)

- Launcher: `C:\Program Files\WSL\wsl.exe` (Store) — WSL2 kernel `6.18.33.2-microsoft-standard-WSL2`, NOT Windows fallback
- Ubuntu 24.04 / Python 3.12.3 / uv 0.11.33 / tmux 3.4
- Proxy ambient: `HTTP_PROXY=http://172.31.80.1:17892`, `NO_PROXY=localhost,127.0.0.1,::1,172.31.80.1`
- Deps: `uv sync --locked --extra dev --extra all` → SYNC_EXIT=0 both trees
- pytest: `--timeout=300 --timeout-method=signal`, tmux persistent session `gate1r6`, 300min cap (finished in 304min wall incl. sync/ruff/compileall/diff)
- Full JUnit produced, NOT truncated (DONE marker reached)

## 3. Full-run Results

| Metric | main | candidate |
|---|---|---|
| tests | 15162 | 15301 |
| failures | 135 | 135 |
| errors | 3 | 3 |
| skipped | 110 | 110 |
| fail_or_error | 138 | 138 |
| PYTEST_EXIT | 1 | 1 |
| PIPE_EXIT | 0 | 0 |
| COMPILEALL_EXIT | 0 | 0 |
| RUFF_EXIT | 1 | 1 |

JUnit: `main-pytest.xml` (2.3MB), `cand-pytest.xml` (2.4MB) in evidence root.

## 4. Diff (fail-set comparison)

```
shared=137  only_main=1  only_cand=1
```

### candidate-only (1) — NOT auto-exempted per r6 strict rule
`tests/server/integration/test_session_host_launch::test_host_session_message_relaunches_offline_runner`
- Failure form in r6: **AssertionError** — "a message to a host-bound, runner-offline, non-stopped session must trigger host.launch_runner so the host can re-spawn a runner; none arrived — the relaunch branch in post_event did not fire" (`assert None is not None`), at `tests/server/integration/test_session_host_launch.py:1001` (a Grok-R5-modified file)
- Note: form shifted from r5's TimeoutError/CancelledError to a deterministic-looking AssertionError in this full run — the relaunch branch in `post_event` did not fire under full-suite load.
- Targeted 20× rerun (same tree, ambient proxy): **PASS=20 FAIL=0** (`targeted-relaunch-20x.txt`). Recorded, but per strict rule a passing rerun does NOT exempt the candidate-only failure.

### main-only (1)
`tests.cli.test_update_check::test_find_repo_root_finds_git_dir` — `assert None is not None` (environment: /mnt/f git worktree pointer unreadable by WSL git; known_environment, also main-only in r4/r5)

### Disappeared vs r5
- `test_ws_tunnel_status_reports_registration` — **passed both trees in r6** (was candidate-only in r5)
- `test_create_app_metrics_middleware_counts_http_requests` — **passed both trees in r6** (was candidate-only in r5)

### Focus-nodeid checks
- relaunch: candidate-only FAIL (above)
- ws_tunnel / metrics: passed both sides
- NO_PROXY nodeid `tests.inner.test_codex_runtime_isolation::test_custom_model_provider_does_not_inherit_subscription_proxy`: **ABSENT in main** (Grok-R5-added test, expected), **passed in candidate** → PASS-both by design

## 5. Shared Semantic Fingerprint

```
shared=137 raw_semantic_mismatch=1 folded_mismatch=0
```
Normalization applied: object addresses, random session ids (`conv_<HEX>`), tmp dirs, worktree paths, pytest-N, PIDs. Fold rule per race-obs §7.1: TimeoutError/CancelledError → TIMEOUT_CANCEL_FAMILY.

Single raw mismatch, explained item-by-item:
- `tests.server.integration.test_session_host_launch::test_message_relaunch_harness_not_configured_persists_error_turn`: main=`TimeoutError`, cand=`CancelledError`. Same timeout-cancel family (folded-family-equal=True) → not a semantic divergence.

Diff tool note: r6's `gate1-r6-diff.py` signature extractor was fixed before analysis (initial version read JUnit text first line = variable repr, yielding 91 false mismatches; fixed to read the `message` attribute with full normalization; validated against r5 known results: shared=137/only_main=1/only_cand=3, raw=1 folded=0).

## 6. Ruff / compileall

- compileall EXIT=0 both trees (no syntax breakage)
- Ruff EXIT=1 both trees:
  - main: 6× E902 "No such file or directory" → all 6 target files absent from the main tree (candidate-added files in ruff's file list) = **spec-missing noise**, same as r4/r5
  - cand: 2× E902 (`test_loader_executor_nested.py`, `test_codex_native_model_from_spec.py` — absent in cand too = spec-missing noise) + 4 real lint findings, all in `tests/inner/test_codex_runtime_isolation.py` (a Grok-R5-modified file): F401 unused `json` import, 2× E501 line-too-long, PIE810 startswith-tuple. Style-level, non-blocking, but worth a follow-up cleanup card.

## 7. Cleanup & Leak-scan

- pytest-of temp dirs: 7 found, 3 removed (older than this run); leak-scan shows residual tmux sockets from pytest fixtures across runs (fixture teardown artifact, pre-existing)
- Ports: 6767 = live production omnigent (untouched, as required); no Gate-test server leaked on 6868
- `cleanup_done`; no new persistent processes attributable to r6

## 8. Strict-Rule Application & Verdict

r6 strict rules:
1. **`new-failures.txt` non-empty ⇒ cannot PASS.** `new-failures.txt` contains 1 entry (relaunch). → PASS not permitted.
2. **candidate-only passing rerun ⇒ no auto-exemption.** relaunch 20/20 rerun pass is recorded but does NOT exempt it.
3. **shared semantic mismatches ⇒ item-by-item.** 1 raw mismatch explained (§5), folded to 0.
4. **No targeted-20× substitute for full Gate 1.** Full double-tree run performed; 20× used only as auxiliary evidence.

Evidence chain is complete and auditable → NOT inconclusive.

### Verdict: **GATE1_FAIL (strict rule)**
Relative to clean main, candidate carries exactly **one candidate-only failure** (`test_host_session_message_relaunches_offline_runner`) that persisted through the full run in a deterministic-looking AssertionError form, even though it passes 20/20 in isolation. Under r6's strict rules this cannot be PASS. Classification authority remains with Codex; recommended disposition: treat as a single flaky/race-sensitive candidate-only item (known_flaky candidate) requiring either a Grok fix round or an explicit project-level waiver decision — not a silent exemption.

## 9. Artifacts (evidence root)

`C:\Users\Administrator\omnigent-diagnostics\20260805-164315-5c8b9ce-hermes-gate1-r6\`:
- `env.txt` (platform/versions/HEAD/status/proxy), `run.log`
- `main-pytest.xml` / `cand-pytest.xml` / `main-pytest.txt` / `cand-pytest.txt`
- `main-counts.txt` / `cand-counts.txt`, `main-fail-ids.txt` / `cand-fail-ids.txt`
- `main-only-failures.txt`, `new-failures.txt` / `new-failures-detail.txt`
- `semantic-fingerprint.txt` (from diff.py), `gate1-r6-diff.py`
- `main-ruff.txt` / `cand-ruff.txt`, `main-compileall.txt` / `cand-compileall.txt`
- `cleanup-leak-scan.txt`, `targeted-relaunch-20x.txt`
- `verification-total1/2/3*.txt`, `verify-total1/2/3-script.sh` (r6 artifact verification loop, final ALL PASS)

Nothing committed. No push/merge/tag. Gate 2 status, frozen SHA, STATUS/PRE_MERGE_GATES untouched.
