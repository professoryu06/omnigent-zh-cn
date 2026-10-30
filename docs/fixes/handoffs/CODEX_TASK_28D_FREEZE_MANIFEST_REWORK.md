# CODEX_TASK_28D_FREEZE_MANIFEST_REWORK — 清单修订（只读，以真实 git show 为准）

- 执行者：Hermes 3.8（只读修订，非提交执行）
- 修订日期：2026-08-03
- 仓库：`https://github.com/professoryu06/omnigent-zh-cn.git`
- 分支：`docs/fix-plans-core-secondary`
- 当前 HEAD：`5c8b9ce96f7552d380276fe6de04651f2b19531a`（3 commit 已落地）
- 约束遵守：未修改源码/stage/commit/删除任何文件；未跑测试

---

## 0. 修订要点（5 项必须明确写出）

1. **`CODEX_TASK_28D_FREEZE_MANIFEST.md` 当前仍未跟踪**（`git ls-files` 计数 = 0）；本 REWORK 文档同为未跟踪新文件，二者均**不在**已提交的 170 文件内。
2. **当前排除项（未提交未删除）**：`CODEX_REVIEW_GROK_NATIVE_01.md`（B 类，冻结后新产生，随 grok 卡）、`evidence/`（B 类 grok evidence，随 grok 卡）、`nul`（D 类垃圾文件，清理卡）。
3. **170 个已提交文件不包含当前 manifest**：Commit 1/2/3 的 `git show --name-only` 清单中**无** `CODEX_TASK_28D_FREEZE_MANIFEST.md`（该文件为提交后生成，见 §1 证据）。
4. **当前工作树仍 dirty**：`git status --porcelain` 显示 4 个 untracked（manifest、REWORK、CODEX_REVIEW_GROK_NATIVE_01.md、evidence/、nul——注：实际 4 条目含 manifest 自身与 REWORK 自身）。**不是 clean 工作树**。
5. **manifest 修订前禁止开始 Gate 2**：在清单修订完成、用户批准、后续 commit 落地、工作树 clean 前，Gate 2 不得启动。

## 1. 真实 git show 统计（权威，非推测）

| Commit | SHA | 文件数 | 内容 |
|---|---|---|---|
| 1 | `e691d08cbfca5e1a36656ced8a0f317b495ffbbe` | **44** | A 类源码 + 测试（23 源码 + 21 测试） |
| 2 | `c3c4ebad074ddce6b458c77dfe06e1ab76498e84` | **124** | C 类文档 11 + handoffs 113 |
| 3 | `5c8b9ce96f7552d380276fe6de04651f2b19531a` | **2** | `docs/fixes/BASELINE_FREEZE_20260803.md` + `docs/fixes/STATUS.md` |
| **合计** | — | **170** | 44+124+2，与 `git show --name-only` 逐项核对一致 |

Commit 3 完整文件清单（git 实测）：
```
docs/fixes/BASELINE_FREEZE_20260803.md
docs/fixes/STATUS.md
```

## 2. A 类源码清单（23 文件，Commit 1，git show 实测）

```
omnigent/cli.py
omnigent/codex_native_app_server.py
omnigent/harness_aliases.py
omnigent/host/connect.py
omnigent/inner/antigravity_native_executor.py
omnigent/inner/claude_native_executor.py
omnigent/inner/codex_executor.py
omnigent/inner/codex_native_executor.py
omnigent/inner/cursor_native_executor.py
omnigent/inner/goose_native_executor.py
omnigent/inner/hermes_native_executor.py
omnigent/inner/kimi_native_executor.py
omnigent/inner/kiro_native_executor.py
omnigent/inner/loader.py
omnigent/inner/native_prompt_delivery.py        (新文件)
omnigent/inner/pi_native_executor.py
omnigent/inner/qwen_native_executor.py
omnigent/native_server_harness.py
omnigent/runner/_entry.py
omnigent/runner/app.py
omnigent/runner/transports/ws_tunnel/serve.py
omnigent/server/routes/_workspace_validation.py
omnigent/server/routes/sessions.py
```

## 3. A 类测试清单（21 文件，Commit 1，git show 实测）

```
tests/cli/test_backend.py
tests/e2e_ui/chat/test_chat_file_path_links.py
tests/e2e_ui/conftest.py
tests/host/test_connect.py
tests/inner/test_codex_native_executor.py
tests/inner/test_codex_native_system_prompt_apply.py   (新)
tests/inner/test_codex_runtime_isolation.py             (新)
tests/inner/test_loader.py
tests/inner/test_native_system_prompt_delivery.py       (新)
tests/runner/test_app_codex_native_model.py             (新)
tests/runner/test_app_codex_native_prompt_delivery.py   (新)
tests/runner/test_app_sessions_native.py
tests/runner/test_codex_terminal_ensure_guard.py        (新)
tests/runner/test_runner_idle_active_work.py            (新)
tests/runner/test_session_workspace_cache.py            (新)
tests/runner/transports/ws_tunnel/test_serve.py
tests/server/integration/test_session_mcp_servers.py
tests/server/routes/test_workspace_validation.py
tests/server/routes/test_workspace_validation_helpers.py
tests/server/test_multipart_host_launch.py              (新)
```

## 4. C 类文档清单（11 文件，Commit 2，非 handoffs，git show 实测）

```
AGENTS.md
docs/fixes/CLEANUP_COMPLETION_20260731.md   (新)
docs/fixes/CLEANUP_MANIFEST_20260731.md     (新)
docs/fixes/POST_FIX_HANDOFF_PROMPT.md
docs/fixes/PRE_MERGE_GATES.md
docs/fixes/PROJECT_OWNER_WORKFLOW_20260731.md (新)
docs/fixes/PROJECT_PROGRESS_20260731.md     (新)
docs/fixes/STATUS.md
docs/fixes/TEST_PROGRESS_20260731.md        (新)
docs/fixes/WSL_PROXY_BRIDGE_20260731.md     (新)
docs/fixes/WSL_REPAIR_20260731.md           (新)
```

## 5. handoffs 准许纳入清单（113 Markdown，Commit 2）

整目录 `docs/fixes/handoffs/` 共 **113 个 Markdown**（git show c3c4eba 实测计数）。涵盖 CODEX_TASK/REVIEW 系列、GROK_*/HERMES_*/HANDOFF_*/QWEN_TASK 系列、FINAL_FOR_REVIEWER/REVIEW_PACKAGE 等完整交接链。

> 注：该 113 文件中**不包含** `CODEX_TASK_28D_FREEZE_MANIFEST.md`（提交后才生成）与 `CODEX_TASK_28D_FREEZE_MANIFEST_REWORK.md`（本文件，提交后生成）。

## 6. 当前排除项（明确列出，未提交未删除）

| 条目 | 类别 | 处理 |
|---|---|---|
| `docs/fixes/handoffs/CODEX_REVIEW_GROK_NATIVE_01.md` | B | 冻结后新产生的 grok review 文档（8-3 19:51），随 grok 功能卡 |
| `evidence/`（含 grok-native-01/） | B | grok 验收 evidence，随 grok 卡归档/gitignore，不删 |
| `nul` | D | 30B 垃圾文件，另列清理卡（rm nul） |
| `CODEX_TASK_28D_FREEZE_MANIFEST.md` + 本 REWORK | 待定 | 清单文档，经批准后决定是否纳入后续 commit |

## 7. 敏感/配置检查（3 commit 全量 staged diff）

- 无 config.toml 混入（命中均为 codex_executor.py 内私有 CODEX_HOME 消毒逻辑）
- 无 .env、无硬编码凭据（secrets.token_urlsafe/token_hex 为代码生成；AWS_SECRET_ACCESS_KEY 为测试 monkeypatch 模拟值）
- 无代理配置混入（`_CODEX_DEFAULT_PROXY = "http://127.0.0.1:7897"` 为代码常量，OpenCodex 隔离逻辑）
- ✅ PASS

## 8. 边界声明

- 本 REWORK 纯只读：未修改/stage/commit/删除任何文件；未跑测试/full-run/Gate 2。
- 不宣称 Gate 2 PASS、全仓 GREEN 或 mergeable。
- 凭据全部 `[REDACTED]`；10100/OpenCodex/`~/.codex/config.toml`/TUN/Clash 未触碰。
- **当前工作树仍 dirty（4 个 untracked），清单修订 + 批准 + 后续 commit 前，禁止开始 Gate 2。**

---

**等待用户批准逐文件清单，批准前禁止 commit。**
