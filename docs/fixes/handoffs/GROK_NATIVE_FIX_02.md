# GROK_NATIVE_FIX_02 — CODEX_REVIEW_GROK_NATIVE_01 两阻塞修复

- 执行者：Hermes 3.8（用户授权修复）
- 日期：2026-08-03
- 工作树：`F:\codex-ai\omnigent-zh-next`（branch `integration/omnigent-zh-20260731`，HEAD `c2982266`）
- 依据：`CODEX_REVIEW_GROK_NATIVE_01.md`（Codex 审查，裁决 REWORK_REQUIRED，2 个阻塞问题）
- 未 commit / push / merge；凭据全部 `[REDACTED]`

---

## 1. 阻塞 1 修复：headless harness 不再创建 REPL/tmux 终端

**根因**（Codex 审查确认）：`grok-native` 是 headless CLI subprocess（`IntegrationMode.CLI_SUBPROCESS`），
`is_native_harness("grok-native") is False` → runner 通用非 native 分支
（`omnigent/runner/app.py:2855`）对 `not is_native_harness(harness_name)` 自动调用
`_auto_create_repl_terminal` → 创建 `terminal_tui_main` + tmux socket（违反"无 tmux/PTY"约束）。

**修复**（3 文件）：
| 文件 | 改动 |
|---|---|
| `omnigent/harness_plugins.py` | `HarnessContribution` 新增 `headless_harnesses` 字段；`_BUILTIN_CONTRIBUTION` 注册 `headless_harnesses=frozenset({"grok-native"})`；新增 `headless_harnesses()` 聚合函数 |
| `omnigent/harness_aliases.py` | 新增 `HEADLESS_HARNESSES` 常量 + `is_headless_harness()` 谓词 |
| `omnigent/runner/app.py` | 通用 REPL 分支条件加 `and not is_headless_harness(harness_name)`（:2855）+ import |

**机制**：headless 集合走 `_merge_set` 聚合（与 native_harnesses 同机制），grok-native 显式注册；
runner 首次创建 REPL 的通用分支跳过 headless harness。重建路径 `_recreate_repl_terminal`（:6812）
只在 REPL 已存在时触发，headless 首次不建故自然不触发，无需改动。

## 2. 阻塞 2 修复：代理隔离（仅显式 OMNIGENT_GROK_PROXY 才注入）

**根因**（Codex 审查确认）：`clean_agent_env` 的 `BASE_ALLOW_PREFIXES` 含 `HTTP_`/`HTTPS_`/`ALL_PROXY`/`NO_PROXY`，
父进程继承的代理变量原样通过；grok 只强制 `NO_PROXY` 未删除继承代理。

**修复**（2 文件，同逻辑）：
| 文件 | 位置 |
|---|---|
| `omnigent/grok_native_bridge.py` | `build_grok_native_spawn_env`：构造 env 后先 pop 8 个代理键（大写+小写），再强制 `NO_PROXY=127.0.0.1,localhost`，仅 `OMNIGENT_GROK_PROXY` 非空时注入 HTTP/HTTPS/ALL_PROXY |
| `omnigent/inner/grok_native_executor.py` | `GrokNativeExecutor._build_spawn_env`：同上逻辑 |

## 3. 回归测试（3 新增）

| 测试 | 覆盖 |
|---|---|
| `tests/test_grok_native_dispatch.py::test_grok_native_is_classified_as_headless_harness` | 阻塞 1：grok-native ∈ HEADLESS_HARNESSES；`is_headless_harness` 对 grok-native=True、claude-native/codex/grok/None=False |
| `tests/inner/test_grok_native_isolation.py::test_spawn_env_strips_inherited_proxy_when_grok_proxy_unset` | 阻塞 2 负向：父环境有 6 个代理变量 + NO_PROXY=x，子进程 env 全无代理，NO_PROXY 强制 |
| `tests/inner/test_grok_native_isolation.py::test_spawn_env_injects_proxy_only_when_grok_proxy_set` | 阻塞 2 正向：OMNIGENT_GROK_PROXY 设置时注入三件套且覆盖继承值 |

## 4. 测试结果（WSL Ubuntu-24.04, .venv/bin/python）

- **定向 47/47 passed**：`test_grok_native_dispatch` + `test_grok_native_isolation` + `test_grok_native_session` + `test_harness_plugins` + `test_harness_dispatch`（含 3 个新回归）
- **相关回归 90 passed / 1 failed**：`test_harness_capabilities` + `test_native_coding_agents` + `test_harness_aliases` + `test_wrapper_labels` + `test_harness_dispatch`
- 唯一失败 `test_catalog_rows_carry_setup_steps` = **pre-existing**（用户 `~/.omnigent/config.yaml` 的 `acp:grok-code` 动态行无 setup_steps，Codex 上次验收同为 1 failed；与本次修复无关，未修改测试期望）
- `py_compile` 7 文件全部 OK

## 5. 待 Codex 复核项（对应审查 §Gate 2 边界）

1. 定向测试（已 47/47）
2. headless 无 REPL/tmux 证据（需真机验证：新 grok 会话不再产生 `terminal_tui_main`/tmux socket —— 本修复是机制层，未做真机重跑）
3. 代理负向/正向测试（已含）
4. 真机双轮验收无需重跑（Codex 原话："不需要重跑已经成功的两轮真机验收"）

## 6. 边界声明

- 未 commit/push/merge/tag；未改 TUN/Clash/OpenCodex/10100/`~/.codex/config.toml`。
- 不宣称 Gate 2 PASS、全仓 GREEN 或 mergeable；Gate 2 仍待 Codex 另开独立卡。
