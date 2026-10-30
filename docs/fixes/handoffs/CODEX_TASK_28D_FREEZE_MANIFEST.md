# CODEX_TASK_28D_FREEZE_MANIFEST — Gate 2 基线冻结逐文件清单（只读）

- 执行者：Hermes 3.8（只读清单生成，非提交执行）
- 生成日期：2026-08-03
- 仓库：`https://github.com/professoryu06/omnigent-zh-cn.git`
- 分支：`docs/fix-plans-core-secondary`
- 冻结 HEAD：`5c8b9ce96f7552d380276fe6de04651f2b19531a`（Commit 3 后）
- 依据：已落地的 3 个 commit（`git show --name-only` 权威统计）
- 约束遵守：未修改/stage/commit/删除任何文件；未跑测试

---

## 0. 实际文件统计（重新统计）

| 类别 | 数量 | 来源 |
|---|---|---|
| A 类源码 | 23 | Commit 1 |
| A 类测试 | 21 | Commit 1 |
| C 类文档（非 handoffs） | 11 | Commit 2 |
| handoffs Markdown | 113 | Commit 2 |
| Commit 3（STATUS + freeze manifest） | 2 | Commit 3 |
| **已提交合计** | **170** | 3 commit 总量（44+124+2） |
| 排除（B/D，未提交） | 3 条目 | `nul`、`evidence/`、`CODEX_REVIEW_GROK_NATIVE_01.md` |

## 1. A 类源码清单（23 文件，Commit 1）

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

## 2. A 类测试清单（21 文件，Commit 1）

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

## 3. C 类文档清单（11 文件，Commit 2，非 handoffs）

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

## 4. handoffs 准许纳入清单（113 Markdown，Commit 2）

整目录 `docs/fixes/handoffs/` 共 **113 个 Markdown** 已纳入，涵盖：
- CODEX_TASK_1..24（含 REWORK/PLAN/POLICY 变体）、CODEX_TASK_27、CODEX_TASK_28_PLAN、CODEX_TASK_28A_MONITOR
- CODEX_REVIEW_14..20（含 REWORK）
- GROK_COMPLETION/DIAGNOSIS/REVIEW/FULLRUN/GATE2_POLICY（含 REWORK 变体）
- HERMES_COMPLETION/DIAGNOSIS/REVIEW/GATE1_POLICY
- HANDOFF_20260724_r04/r05、REVIEW_PACKAGE_20260724_core、FINAL_FOR_REVIEWER_20260724
- QWEN_TASK_r04/r05、GROK_DAILY_OPS_LOG_2026-07-30

> 完整 113 文件清单以 `git show --name-only c3c4eba` 为准（本 manifest 不逐行重复；如需逐行清单可另生成）。

## 5. 排除项（B/D 类，明确不提交不删除）

| 条目 | 类别 | 说明 |
|---|---|---|
| `nul` | D | 30B 垃圾文件（`bash: chcp: command not found` 误重定向），另列清理卡 |
| `evidence/`（含 grok-native-01/） | B | grok 功能验收 evidence，随 grok 功能卡处理，不删 |
| `docs/fixes/handoffs/CODEX_REVIEW_GROK_NATIVE_01.md` | B | 冻结后新产生的 grok 相关 review 文档（8-3 19:51，7190B），**未纳入**，随 grok 卡处理 |
| B 类 grok/WSL 功能代码 | B | 在 `omnigent-zh-next` 另仓（28D 已确认），本仓不存在 |
| 异常路径 `C\357\200\272/` | D | 在 `omnigent-zh-next` 工作树（r27 路径 bug 副本），另卡清理 |

## 6. 敏感/配置检查（3 个 commit 全量 staged diff 扫描）

- **无 config.toml 混入**：命中 4 条均为 `codex_executor.py` 代码内对私有 CODEX_HOME config.toml 的消毒/写入逻辑（非仓库配置）
- **无 .env**：零命中
- **无凭据**：`secrets.token_urlsafe(32)`/`token_hex(8)` 为代码生成的绑定 token（非硬编码）；`AWS_SECRET_ACCESS_KEY` 为测试 monkeypatch 模拟值
- **无代理配置混入**：`_CODEX_DEFAULT_PROXY = "http://127.0.0.1:7897"` 为代码常量（OpenCodex 注入代理的拒绝逻辑），非用户代理配置
- ✅ **PASS：无 config.toml、.env、凭据或代理配置**

## 7. 边界声明

- 本 manifest 纯只读生成：未修改/stage/commit/删除任何文件；未跑测试/full-run/Gate 2。
- 不宣称 Gate 2 PASS、全仓 GREEN 或 mergeable。
- 凭据全部 `[REDACTED]`；10100/OpenCodex/`~/.codex/config.toml`/TUN/Clash 未触碰。

---

**等待用户批准逐文件清单，批准前禁止 commit。**
