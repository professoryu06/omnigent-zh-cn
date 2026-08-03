# CODEX_TASK_23_PLAN — Omnigent 与本机 OpenCodex/Codex 长期隔离方案

> **For agentic workers:** 先阅读本计划；实现时使用逐任务开发与测试。本文是方案，不是已完成修复，不代表 Gate 2 签字。

**Goal:** 让本机 OpenCodex + Codex 与 Omnigent 调用 Codex CLI 使用两条互不污染的运行链路；两者可以自由切换，Omnigent 使用 Codex 订阅认证且不被 OpenCodex 的 10100 路由劫持。

**Architecture:** 本机 OpenCodex 保持现有用户 `CODEX_HOME`、`config.toml` 和 10100 端口不变。Omnigent 每次 Codex 会话使用私有 `CODEX_HOME`，只桥接订阅认证文件，使用经过清理的配置和显式模型覆盖；子进程环境禁止继承第三方 base URL。只有明确启用 Omnigent 自有 gateway 时才注入 gateway 配置，订阅直连模式走 Codex CLI 自带默认 provider。

**Tech Stack:** Python、`tomlkit`、Codex CLI app-server、pytest、Windows 子进程环境。

## Global Constraints

- 不修改、删除或重写用户的 OpenCodex 配置 `C:\Users\Administrator\.codex\config.toml`。
- 不停止 `opencodex`/`bun.exe`，不释放或占用 10100；两套进程不得共享可变 provider 配置。
- Omnigent 默认必须使用 Codex 订阅认证；不得把 `https://api.openai.com/v1` 当作无条件默认值，因为这可能切换到 API key 计费路径。
- Omnigent 目标模型固定为 `gpt-5.6-sol`；最终以 Codex CLI 的显式 `-c model=...` 覆盖为准，不能只依赖环境变量。
- 产品 `240s` idle watchdog 不得修改、拉长或绕过。
- native CLI 固定 0.146.0，使用任务卡约定的绝对路径和 SHA-256；凭据和 token 在日志中统一为 `[REDACTED]`。
- 本计划不实施、不跑完整 Gate 2、不 commit/push/merge/tag；实现由 Hermes，代码审查由 Grok，最终只读验收由 Codex。

## 已确认根因

`~/.codex/config.toml` 被 OpenCodex 写入 `openai_base_url = "http://127.0.0.1:10100/v1"` 和 `model = "gpt-5.6-luna"`。`omnigent/inner/codex_executor.py` 当前会把用户 `config.toml` 复制到会话私有 `CODEX_HOME`，导致 Omnigent 的 Codex CLI 读到 OpenCodex 路由；Codex CLI 随后把 Responses 请求发送到 10100，而 OpenCodex 端点返回 404/426。该问题是共享配置污染，不是必须关闭 OpenCodex 的进程冲突。

## 目标运行边界

| 链路 | CODEX_HOME/config | 认证 | provider/endpoint | 10100 |
|---|---|---|---|---|
| 本机 OpenCodex + Codex | 用户原目录，保持不变 | 用户现有登录 | OpenCodex 配置 | 可用 |
| Omnigent `harness: codex` | 每会话私有目录；不复制第三方路由 | 只桥接 `auth.json` | Codex 默认订阅 provider；显式 gateway 时才使用 gateway | 禁止连接 |

## Task 1: 先建立隔离契约测试

**Files:**
- Create: `tests/inner/test_codex_runtime_isolation.py`
- Test seam: `omnigent/inner/codex_executor.py`

- [ ] 写测试：伪造用户 `config.toml`，包含 `openai_base_url=\"http://127.0.0.1:10100/v1\"`、`model=\"gpt-5.6-luna\"` 以及一个普通安全字段；断言生成的 Omnigent 私有配置不含 10100、不含该模型，安全字段按策略保留。
- [ ] 写测试：断言私有目录中存在订阅认证桥接文件（只检查存在/权限/路径，不读取或输出内容）。
- [ ] 写测试：断言 Codex child 环境不含 `OPENAI_BASE_URL`、`OPENAI_API_BASE` 及未授权的 gateway endpoint；明确 gateway 模式的 allowlist 行为。
- [ ] 写测试：断言最终 argv 含 `-c` 和 JSON 编码的 `model=gpt-5.6-sol`，且不会把用户 `gpt-5.6-luna` 当最终模型。
- [ ] 先运行这些测试，确认在实现前失败；不得通过修改测试期望来制造通过。

## Task 2: 实现私有 Codex 配置清理

**Files:**
- Modify: `omnigent/inner/codex_executor.py`，重点为 `_populate_codex_home_config`、`_codex_home_config_source_from_env` 附近。
- Test: `tests/inner/test_codex_runtime_isolation.py`

- [ ] 保留现有每会话私有 `CODEX_HOME` 生命周期和 cleanup 逻辑。
- [ ] 使用已存在的 `tomlkit` 读写配置，基于用户配置生成 Omnigent 专用副本；不得原地修改用户文件。
- [ ] 删除或拒绝以下路由/选择项：`openai_base_url`、`openai_api_base`、第三方 provider 的 10100/loopback endpoint、用户默认 `model` 和会把 provider 指向 OpenCodex 的字段。
- [ ] 不在订阅直连模式写入 `https://api.openai.com/v1`；删除污染项后让 Codex CLI 使用其内置订阅 provider。
- [ ] 生成后重新解析配置并做安全检查：任何字符串 URL/endpoint 命中 `127.0.0.1:10100` 时必须使本次启动失败并给出结构化、脱敏错误，而不是静默继续。
- [ ] 认证文件沿用现有 `auth.json` 桥接方式；只读复制/链接，不把凭据写入日志。

## Task 3: 强制模型和环境边界

**Files:**
- Modify: `omnigent/inner/codex_executor.py`，重点为 `_clean_codex_env`、`CodexExecutor.__init__`、`_CodexAppServerSession.start` 的 argv/env 构造。
- Test: `tests/inner/test_codex_runtime_isolation.py`

- [ ] 在订阅直连模式始终把解析后的模型加入 `codex_config_overrides`，最终 argv 使用 `-c model=\"gpt-5.6-sol\"`；`HARNESS_CODEX_MODEL` 只能作为输入，不是安全边界。
- [ ] 从 child env 移除 `OPENAI_BASE_URL`、`OPENAI_API_BASE` 以及未授权的 `HARNESS_CODEX_GATEWAY_BASE_URL`；保留已有安全环境变量 allowlist。
- [ ] 仅当 gateway 模式显式启用且 gateway/provider 配置完整时，才把 gateway base URL 和相关变量加入 child env/`-c` overrides；gateway 模式必须与订阅直连模式互斥。
- [ ] 不让用户 `config.toml` 的模型或 endpoint 覆盖显式解析结果；记录脱敏后的运行身份（私有 `CODEX_HOME`、CLI path/version/SHA、model、provider mode），不记录 token/配置值。
- [ ] 保持 `HARNESS_CODEX_PATH` 传递链路不变并验证子进程实际继承；不改 CLI 版本和 240s watchdog。

## Task 4: 回归测试与静态验证

**Files:**
- Modify only tests needed for the new contract; do not修改现有 BUG-1/2/3 语义。

- [ ] 运行隔离单元测试。
- [ ] 复跑 BUG-1/2/3 定向测试：

```powershell
.venv\Scripts\python.exe -m pytest `
  tests/test_harness_dispatch.py `
  tests/runner/test_codex_terminal_ensure_guard.py `
  tests/server/test_multipart_host_launch.py `
  tests/host/test_connect.py::test_build_runner_env_forwards_python_utf8_encoding_knobs `
  tests/host/test_connect.py::test_host_connected_banner_is_ascii_encodable_under_gbk `
  tests/cli/test_backend.py::test_build_host_daemon_env_local_forwards_python_utf8_encoding_knobs `
  tests/runner/test_app_sessions_native.py::test_create_session_terminal_ensure_routes_codex_native -q
```

- [ ] 运行与 Codex executor 相关的既有测试，至少包含 `tests/inner/test_codex_native_executor.py` 和本次新增隔离测试。
- [ ] 执行 Python 编译检查；不修改测试期望来掩盖回归。
- [ ] 检查 `git diff`，确认没有改用户配置、TUN、认证、policy、STATUS 或 240s watchdog。

## Task 5: Hermes 单次 full-run 验证卡

只在 Task 1–4 通过后执行，全新 RUN_ID 和 evidence；不拼接旧 evidence。

- 模型：`gpt-5.6-sol`。
- native CLI：0.146.0，任务卡绝对路径和 SHA-256。
- `HARNESS_CODEX_PATH` 在 server/host/C 启动前注入，并记录继承结果。
- 本机 OpenCodex 保持运行，10100 不得被释放；Omnigent child 必须证明未连接 10100。
- 命令：`omnigent-zh.exe run <agent_dir> -p "Reply with CONTROLLER_OK and stop." --server <url>`。
- 成功判据：resolved harness=`codex`、module=`omnigent.inner.codex_harness`、私有 `CODEX_HOME`、真实 assistant `CONTROLLER_OK`、`turn/completed`、C exit=0、未触发 240s idle。
- 同时记录 OpenCodex 仍可访问/未被杀死；不执行 D0/D1、后五轮或完整 Gate 2。
- evidence 实时落盘，cleanup 完成，leak-scan 最后且 hits=0；报告不得包含凭据。

## Task 6: Grok 只读审查与 Codex 最终验收

- Grok 先审查实现 diff、定向 pytest、隔离测试和 full-run evidence；重点检查 claude-native、codex-native、JSON/multipart create、parent runner inheritance、managed host 是否回归。
- Grok 不修改源码、不重跑完整 Gate 2；如 full-run 失败，只按证据分类，不把失败改写成 Gate 2 结论。
- Codex 最后只读验收：检查新 RUN_ID、私有 CODEX_HOME、配置哈希、child env、CLI path/SHA、无 10100、assistant sentinel、cleanup/leak-scan、仓库 diff 范围。
- 即使 full-run 成功，也只能说明本隔离链路通过；Gate 1 仍为相对 main PASS，Gate 2 仍需独立验收，不自动 merge。

## 失败处理

- 若仍出现 10100/404/426：先检查私有配置和 child env 是否泄漏，不修改 OpenCodex。
- 若仍出现 OS 10106：在确认配置未泄漏后另开网络/WSA 诊断卡；不得先执行未经授权的 `netsh winsock reset`。
- 若出现认证失败：确认私有 `CODEX_HOME` 只桥接正确订阅认证；不得把 API key 或 OpenCodex gateway 当作默认替代。
- 若出现 native terminal/tmux 错误：按 BUG-2 回归处理，不能通过把裸 `codex` 改成 `codex-native` 解决。
