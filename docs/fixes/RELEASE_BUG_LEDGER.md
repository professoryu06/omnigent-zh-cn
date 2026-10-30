# RELEASE_BUG_LEDGER — Omnigent 第一版发布 BUG 台账

- 日期：2026-08-06；基线：`8ef79ac348711d523053019cdb2f36e8cbbfef7e`
- Evidence：`20260806-160933-8ef79ac-hermes-release-control`
- 状态定义：**FIXED** = 修复已入 staged/commit 候选且有回归测试；**TARGETED_ONLY** = 仅定向验证或部分缓解，未全量验收；**UNRESOLVED** = 根因已定位但未解决/未被接受；**ISOLATED** = 已隔离（不进入第一版或私有边界隔离）；**ENVIRONMENT_ONLY** = 属环境/外部组件问题，不改 Omnigent 源码解决
- 本台账不构成任何 Gate 判定；凭据一律 `[REDACTED]`

## 一、核心 BUG（BUG-1 ~ BUG-4）

| ID | 名称 | 根因 | 修复位置 | 状态 | 证据出处 |
|---|---|---|---|---|---|
| BUG-1 | Windows 编码（Host daemon GBK 崩溃） | host/connect 非 ASCII banner/输出触发 GBK 编码崩溃 | `omnigent/cli.py`、`omnigent/host/connect.py`、`tests/host/test_connect.py`（UTF-8 环境边界；基线已含 `0c17eb5` UTF-8 CLI 输出部分） | **FIXED**（Task30 staged 候选内，待 release 分支定向回归确认） | CODEX_TASK_22 §BUG-1；e691d08 |
| BUG-2 | codex/native terminal 分流（核心阻塞） | 裸 `codex` harness 误走 tmux/PTY native terminal 路径 | `omnigent/harness_aliases.py`、`tests/runner/test_codex_terminal_ensure_guard.py`、`tests/test_harness_dispatch.py` | **FIXED**（Task30 staged；定向 44 tests 曾全绿） | CODEX_TASK_22/23；e691d08 |
| BUG-3 | multipart host launch 不启动 runner | `POST /v1/sessions` multipart 带 `metadata.host_id` 时不 launch runner | `omnigent/server/routes/sessions.py`、`tests/server/test_multipart_host_launch.py` | **FIXED**（Task30 staged；注意与 relaunch 竞态条目区分） | CODEX_TASK_22 §BUG-3；e691d08 |
| BUG-4 | OpenCodex/10100/config 隔离 | opencodex 向 `~/.codex/config.toml` 注入 `openai_base_url=http://127.0.0.1:10100/v1`，Codex CLI 0.146.0 把 Responses WS 打到 10100（404/426），伴 Rust 10106 | Omnigent 侧：私有 CODEX_HOME 隔离（`codex_executor.py` 隔离 hunk，Task30 staged）；opencodex/10100 本体不动 | **ISOLATED + ENVIRONMENT_ONLY**（私有 CODEX_HOME 阻断 config 劫持；10100 属外部组件，永久不连接/不占用/不释放） | CODEX_TASK_22 §BUG-4（RUN `20260731-035708-dc83140-hermes-responses10100-cli0146-r1`） |

## 二、Native prompt / Codex 网络 / TUI / 进程清理

| ID | 名称 | 根因 | 修复位置 | 状态 | 证据出处 |
|---|---|---|---|---|---|
| NP-1 | native prompt fail-loud（#2853） | native executor 不声明/不校验 system prompt 送达 | `omnigent/inner/native_prompt_delivery.py` + 9 个 `*_native_executor.py` 能力声明（Task30 staged）；Phase-1 warn + `OMNIGENT_STRICT_PROMPT` | **TARGETED_ONLY**（mitigated/fail-loud phase 1；真实 prompt 送达未实现，AgentCenter E2E 未验证；禁止写成完整 fixed） | STATUS.md #2853 强制措辞；PR #5（OPEN，ISOLATE） |
| NET-1 | Codex TUN/WSL 网络（Route-A） | Codex 0.146.0 + Clash proxy 不兼容，subscription child proxy 边界下 Rust 10106/11003，真实响应前全部失败 | Route-A child-only proxy 边界已实现于 `codex_executor.py`（4 个 full-run evidence r1–r4 全部失败） | **UNRESOLVED**（implemented but NOT accepted as a fix；proxy/Route-A hunk 不进第一版；需 CLI 版本/上游独立决策） | CODEX_TASK_24_PLAN §10；manifest §5 |
| TUI-1 | TUI 启动期远程同步超时 | Codex TUI 拉起后未产生 `thread/started`（启动期同步阻塞，涉及 240s idle watchdog 边界） | 无源码修复（TASK_27 为只读诊断卡） | **UNRESOLVED**（诊断完成，修复需另发实施卡；240s watchdog 不得修改） | CODEX_TASK_27 |
| PROC-1 | DELETE 后子进程清理 | 产品 `DELETE /v1/sessions/{id}` 后 runner-side cleanup 为 best-effort，不杀 harness/app-server 子进程树（28C 实测需手动 SIGTERM→SIGKILL） | session/cleanup 边界修复在 e691d08 staged（`ws_tunnel/serve.py`、`sessions.py`），具体 hunk 归属待 release 分支复核 | **TARGETED_ONLY**（候选含修复，未全量验收） | HERMES_DIAGNOSIS_28C §6 |

## 三、测试竞态 / 外部接入

| ID | 名称 | 根因 | 修复位置 | 状态 | 证据出处 |
|---|---|---|---|---|---|
| RACE-1 | relaunch 测试竞态 | `test_host_session_message_relaunches_offline_runner`：全量负载下 `post_event` relaunch 分支不触发（r6 形态=AssertionError） | Grok R5 修复在 `tests/server/integration/test_session_host_launch.py`（review 树未提交，ISOLATE）；定向 50×/20× 全过 | **UNRESOLVED**（定向通过≠豁免；r6 全量 Gate 1 仍 candidate-only → GATE1_FAIL 严格判定；修复文件不进第一版，须独立决策） | r6 报告 `HERMES_DIAGNOSIS_GATE1_20260805-164315…r6.md`；GROK_FIX_RELAUNCH_RACE_20260806 |
| EXT-1 | Claude-DS/CCSwitch 连接 | WSL 内无法访问 Windows CCSwitch `127.0.0.1:15721`，Claude-DS 外部调用路径失败（与已修复的 Codex 订阅直连路径无关） | 无有效候选（失败未产生可审查代码） | **UNRESOLVED（BLOCKED）**（事故已归档；不得误写成修复完成；`start_omnigent_claude_direct.sh` ISOLATE） | CODEX_TASK_29_DIRECT_CODEX_REPLAN §1 |
| EXT-2 | Qwen 接入 | Qwen 直连为实验路径 | `scripts/start_qwen_direct.sh`（zh-next，ISOLATE） | **TARGETED_ONLY**（TASK_29_QWEN_VERIFY = TARGETED_VALIDATION，未改源码） | CODEX_TASK_29_QWEN_VERIFY |
| EXT-3 | Grok 接入 | Grok native 为实验性执行器，仅存在于 zh-next 脏运行树 | `omnigent/grok_native*.py`、`inner/grok_native_executor.py` 等（zh-next untracked，ISOLATE） | **ISOLATED**（不进第一版；需独立功能卡/独立 worktree/独立 evidence） | manifest §6 |
| EXT-4 | Pi 接入 | native prompt 能力声明（与其他 native executor 同批） | `omnigent/inner/pi_native_executor.py`（Task30 staged） | **FIXED**（能力声明随 FIRST-V1 移植；无独立直连验证） | manifest §4.1 |

## 四、模型约束差异（待处理，不改测试凑绿）

| ID | 内容 | 状态 |
|---|---|---|
| MODEL-1 | 项目 Codex 唯一允许 `gpt-5.6-luna` + reasoning_effort=max；但 `tests/harness_bench/test_bench.py:602,612,624,637,650,660`、`tests/harness_bench/__main__.py:32`、`README.md:23,27`、`tests/runner/test_codex_terminal_ensure_guard.py:27` 硬编码 `gpt-5.6-sol` | **待处理差异**（只记录；是否改为 luna 由 Codex 专项卡决策；本轮不改） |
| MODEL-2 | `tests/inner/test_codex_runtime_isolation.py`：sol=订阅默认、luna=用户覆盖（隔离语义有意设计） | 保留，评审时单独说明 |

## 五、第一版准入汇总

- 进入第一版：BUG-1/2/3 修复（staged）、BUG-4 私有 CODEX_HOME 隔离 hunk、NP-1 fail-loud phase-1、PROC-1 session/cleanup 修复、EXT-4 Pi 能力声明 —— 全部经 Task30 逐文件移植 + 定向回归 + Gate 1 对照后才算数。
- 不进入第一版：NET-1 Route-A proxy hunk、RACE-1 的 4 个 ISOLATE 文件、EXT-1/2/3、PR #5、zh-next Grok native。
- 永久边界：OpenCodex 与 Omnigent Codex 隔离；10100 不连接/不占用/不释放；TUN/Clash/240s watchdog 不修改。
