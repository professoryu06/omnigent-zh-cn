# CODEX_TASK_30 — Omnigent 源码整合逐文件清单

日期：2026-08-06  
性质：只读盘点后的整合清单；本文件不代表已合并、已发布或 Gate 通过。

## 1. 当前“最新”定义

| 对象 | 身份 | SHA/状态 | 结论 |
|---|---|---|---|
| GitHub main | 中文交付仓正式发布基线 | 8ef79ac348711d523053019cdb2f36e8cbbfef7e，PR #3/#4 已合并 | 当前最新、唯一权威发布基线 |
| omnigent-main-merged | main 的干净本地副本 | 8ef79ac，clean | 第一版整合起点 |
| omnigent-review | 本地修复候选 | 5c8b9ce；e691d08 已提交，另有 4 个未提交文件 | 不得整体复制或直接部署 |
| omnigent-zh-next | 上游参考/实验运行树 | c2982266，含 Grok/WSL 脏改动 | 当前 6767 正在使用，但不是发布基线 |
| PR #2 | 文档计划 | OPEN，head dc83140 | 不进入源码整合 |
| PR #5 | native prompt fail-loud | OPEN，head 1f42a89 | 单独审查，不自动并入 |

当前 6767 server/host 的代码路径为 /mnt/f/codex-ai/omnigent-zh-next；修改 review 或 main-merged 不会自动更新正在运行的服务。

## 2. 第一版整合原则

第一版从 main 8ef79ac 新建干净 worktree。不得 cherry-pick 整个 e691d08 后覆盖 main，因为 e691d08 的基线早于 PR #3/#4，并与已经合并的 runner/loader 文件重叠。

处理标记：

- FIRST-V1：第一版候选，逐 hunk 审查后进入；
- PRESERVE-MAIN：main 已有，保留 main，不从旧候选覆盖；
- MIXED-HUNK：同一文件同时含已验收基线和未验收后续改动，只移植批准 hunk；
- ISOLATE：继续留在独立候选，不进入第一版；
- DOC-ONLY：只同步文档，不进入源码运行树；
- KEEP-EVIDENCE：保留但不提交、不删除、不拼接。

## 3. main 已有内容：只保留，不从 e691d08 覆盖

| 文件 | 标记 | 说明 |
|---|---|---|
| omnigent/runner/app.py | PRESERVE-MAIN + MIXED-HUNK | PR #3/#4 已改；只补入 e691d08 中不冲突且已审查的 hunk |
| omnigent/inner/loader.py | PRESERVE-MAIN + MIXED-HUNK | PR #4 已改；保留 nested harness/model 语义 |
| tests/runner/test_session_workspace_cache.py | PRESERVE-MAIN | PR #3 已合并 |
| tests/inner/test_loader_executor_nested.py | PRESERVE-MAIN | PR #4 已合并，e691d08 旧基线缺失该文件 |
| tests/runner/test_codex_native_model_from_spec.py | PRESERVE-MAIN | PR #4 已合并，e691d08 旧基线缺失该文件 |

## 4. e691d08 第一版候选文件

以下文件来自本地提交 e691d08（BUG-1/2/3/24、Codex 隔离、prompt fail-loud、ws/session 修复）。它们只能在 main 8ef79ac 上逐文件、逐 hunk 移植并通过定向验证后进入第一版。

### 4.1 源码文件

| 文件 | 标记 | 第一版语义 |
|---|---|---|
| omnigent/cli.py | FIRST-V1 | 本地 daemon 环境转发/Windows 编码边界 |
| omnigent/codex_native_app_server.py | FIRST-V1 | Codex native app-server 适配 |
| omnigent/harness_aliases.py | FIRST-V1 | 裸 codex 与 codex-native 分流 |
| omnigent/host/connect.py | FIRST-V1 | ASCII banner、UTF-8 环境与 host 清理 |
| omnigent/inner/antigravity_native_executor.py | FIRST-V1 | native prompt fail-loud 统一入口 |
| omnigent/inner/claude_native_executor.py | FIRST-V1 | native prompt 能力声明/fail-loud |
| omnigent/inner/codex_executor.py | MIXED-HUNK | 只纳入私有 CODEX_HOME/OpenCodex 隔离；Route-A/后续 proxy hunk 隔离 |
| omnigent/inner/codex_native_executor.py | FIRST-V1 | Codex native prompt/模型边界 |
| omnigent/inner/cursor_native_executor.py | FIRST-V1 | native prompt 能力声明 |
| omnigent/inner/goose_native_executor.py | FIRST-V1 | native prompt 能力声明 |
| omnigent/inner/hermes_native_executor.py | FIRST-V1 | native prompt 能力声明 |
| omnigent/inner/kimi_native_executor.py | FIRST-V1 | native prompt 能力声明 |
| omnigent/inner/kiro_native_executor.py | FIRST-V1 | native prompt 能力声明 |
| omnigent/inner/loader.py | PRESERVE-MAIN + MIXED-HUNK | 保留 PR #4，补入非冲突修复 |
| omnigent/inner/native_prompt_delivery.py | FIRST-V1 | Phase-1 fail-loud；真实 prompt apply 仍需单独验收 |
| omnigent/inner/pi_native_executor.py | FIRST-V1 | native prompt 能力声明 |
| omnigent/inner/qwen_native_executor.py | FIRST-V1 | native prompt 能力声明 |
| omnigent/native_server_harness.py | FIRST-V1 | native prompt 能力声明 |
| omnigent/runner/_entry.py | FIRST-V1 | runner 环境/身份边界 |
| omnigent/runner/app.py | PRESERVE-MAIN + MIXED-HUNK | 保留 PR #3/#4，补入已审查的 harness/terminal/session hunk |
| omnigent/runner/transports/ws_tunnel/serve.py | FIRST-V1 | tunnel 注册/状态与清理边界 |
| omnigent/server/routes/_workspace_validation.py | FIRST-V1 | workspace 校验与绑定辅助逻辑 |
| omnigent/server/routes/sessions.py | FIRST-V1 | multipart host_id 绑定并启动 runner |

### 4.2 测试文件

| 文件 | 标记 | 第一版语义 |
|---|---|---|
| tests/cli/test_backend.py | FIRST-V1 | daemon 环境转发 |
| tests/e2e_ui/chat/test_chat_file_path_links.py | FIRST-V1 | 路径链接回归 |
| tests/e2e_ui/conftest.py | FIRST-V1 | E2E 测试边界 |
| tests/host/test_connect.py | FIRST-V1 | GBK/UTF-8/host 清理 |
| tests/inner/test_codex_native_executor.py | FIRST-V1 | Codex native 执行器 |
| tests/inner/test_codex_native_system_prompt_apply.py | FIRST-V1 | Codex native prompt receipt |
| tests/inner/test_codex_runtime_isolation.py | MIXED-HUNK | 纳入 e691d08 基础隔离测试，R5 proxy/NO_PROXY 新增段隔离 |
| tests/inner/test_loader.py | FIRST-V1 | loader 回归；不得删除 main 的 PR #4 测试 |
| tests/inner/test_native_system_prompt_delivery.py | FIRST-V1 | Phase-1 fail-loud |
| tests/runner/test_app_codex_native_model.py | FIRST-V1 | native model 解析回归 |
| tests/runner/test_app_codex_native_prompt_delivery.py | FIRST-V1 | runner prompt 交付回归 |
| tests/runner/test_app_sessions_native.py | FIRST-V1 | native session/terminal 边界 |
| tests/runner/test_codex_terminal_ensure_guard.py | FIRST-V1 | 裸 codex 不进入 native terminal |
| tests/runner/test_runner_idle_active_work.py | FIRST-V1 | active work 不被 idle watchdog 误杀 |
| tests/runner/test_session_workspace_cache.py | PRESERVE-MAIN | 使用 PR #3 已合并版本 |
| tests/runner/transports/ws_tunnel/test_serve.py | FIRST-V1 | tunnel 生命周期 |
| tests/server/integration/test_session_mcp_servers.py | FIRST-V1 | MCP session 回归 |
| tests/server/routes/test_workspace_validation.py | FIRST-V1 | workspace 权限/绑定 |
| tests/server/routes/test_workspace_validation_helpers.py | FIRST-V1 | 校验辅助函数 |
| tests/server/test_multipart_host_launch.py | FIRST-V1 | multipart host_id launch |
| tests/test_harness_dispatch.py | FIRST-V1 | harness dispatch 矩阵 |

## 5. 本地 4 个未提交文件：继续隔离

这些文件不能整文件纳入第一版：

| 文件 | 标记 | 原因 |
|---|---|---|
| omnigent/inner/codex_executor.py | MIXED-HUNK / ISOLATE | 后续 subscription proxy、ambient proxy/NO_PROXY 清理与 Route-A；Route-A full-run r1–r4 未成功 |
| tests/inner/test_codex_executor.py | ISOLATE | 对应 R5 proxy/provider 契约测试，必须与实现 hunk 一起单独复核 |
| tests/inner/test_codex_runtime_isolation.py | MIXED-HUNK / ISOLATE | e691d08 基础测试可纳入，R5 新增 proxy/NO_PROXY 测试隔离 |
| tests/server/integration/test_session_host_launch.py | ISOLATE | relaunch 竞态同步修复虽定向 50× 通过，但全量 Gate 1 曾出现 candidate-only 失败，需独立决策 |

## 6. 继续隔离的其他内容

| 内容 | 标记 | 原因 |
|---|---|---|
| PR #5 fix/core-2853-native-prompt | ISOLATE | OPEN；与 e691d08 prompt 文件有重叠，先做分支审查再决定 |
| PR #2 docs/fix-plans-core-secondary | DOC-ONLY | OPEN；不作为运行源码 |
| omnigent-zh-next 的 grok_native.py、grok_native_bridge.py、inner/grok_native_executor.py、inner/grok_native_harness.py | ISOLATE | 实验性 Grok Native，当前运行树脏改动 |
| omnigent-zh-next 的 Grok Native 测试 | ISOLATE | 需独立功能卡、独立 worktree、独立 evidence |
| scripts/start_omnigent_claude_direct.sh | ISOLATE | Claude/CCSwitch/WSL 路由尚未解决 |
| scripts/start_omnigent_wsl_backend.sh | ISOLATE | WSL 运行脚本，不能与第一版 Codex 源码混入 |
| scripts/start_qwen_direct.sh | ISOLATE | Qwen 直连实验，独立验证 |
| omnigent-zh-next 的 C\357\200\272/ | KEEP-EVIDENCE | 异常目录，另开清理卡，不在整合时删除 |
| review 的 evidence/ | KEEP-EVIDENCE | 诊断证据不得删除、改写或拼接 |
| review 的 nul | KEEP-EVIDENCE | 异常残留，另开清理卡 |

## 7. 第一版禁止带入的行为

- 不覆盖 main 已合并的 PR #3/#4 文件；
- 不把 Route-A 代理失败改写为已修复；
- 不把一次 Codex full-run 写成 Gate 1/Gate 2 PASS；
- 不把 Claude-DS 的 CCSwitch/WSL 失败归因到 Codex 隔离修复；
- 不修改 TUN、Clash、OpenCodex、10100 或 240s watchdog；
- 不在当前 omnigent-zh-next 运行树直接修改；
- 不删除旧 evidence、VHDX、nul 或异常目录；
- 不在未有新验证证据前提交或部署。

## 8. 后续整合顺序

1. 从 origin/main 8ef79ac 创建新整合 worktree；
2. 先保留 PR #3/#4 现状；
3. 按第 4 节逐文件移植 e691d08，遇到 MIXED-HUNK 手工审查；
4. 运行 BUG-1/2/3、Codex isolation、prompt fail-loud 定向测试；
5. 单独决定第 5 节 4 个文件是否进入候选；
6. 新候选完成 Linux Gate 1 对照后才可讨论合并；
7. 从候选 worktree 重启产品并做 UI/SDK 冒烟；
8. 实际 SHA 确认后再同步 STATUS、Obsidian 和发布记录。

## 9. 当前结论

第一版应以 GitHub main 8ef79ac 为底座，选择性移植 e691d08 的已审查基础修复；Route-A、R5 proxy/NO_PROXY、relaunch 竞态、Grok Native、Claude-DS/CCSwitch、Qwen 直连继续隔离。当前未执行源码合并、服务替换、commit、push 或 merge。
