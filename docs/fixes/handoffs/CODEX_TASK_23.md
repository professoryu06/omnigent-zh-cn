# CODEX_TASK_23 — Codex 订阅与 OpenCodex 长期隔离实现卡

## 执行顺序

你是 Hermes，实现者。完整阅读 `docs/fixes/handoffs/CODEX_TASK_23_PLAN.md` 后实施并测试；完成后交给 Grok 只读审查，最后由 Codex 验收。

## 目标

本机 OpenCodex + Codex 必须继续使用用户现有 `~/.codex` 和 10100；Omnigent 的 `harness: codex` 必须在私有 `CODEX_HOME` 中使用 Codex 订阅认证，不能继承 OpenCodex 的 endpoint/model 配置。

## 硬约束

- 不修改/删除用户 `C:\Users\Administrator\.codex\config.toml`。
- 不停止 `opencodex` 或 bun，不释放/占用 10100。
- 不改 TUN、代理、认证内容、产品政策或 240s idle watchdog。
- native CLI 固定 0.146.0，使用任务卡约定 path/SHA；模型固定 `gpt-5.6-sol`。
- 不跑完整 Gate 2 六轮；不 commit/push/merge/tag。
- 所有凭据输出为 `[REDACTED]`。

## 必须实现

1. 保留当前私有会话 `CODEX_HOME`，但不再把用户完整 `config.toml` 原样复制给 Omnigent。
2. 用 `tomlkit` 生成私有、可审计的配置副本，移除 `openai_base_url`、`openai_api_base`、用户模型覆盖和任何指向 OpenCodex/`127.0.0.1:10100` 的 provider 路由；订阅直连模式不得硬编码 `https://api.openai.com/v1`。
3. 只桥接 `auth.json` 以使用 Codex 订阅认证，绝不在日志打印内容。
4. Codex child 启动 argv 必须显式包含 `-c model=\"gpt-5.6-sol\"`；环境变量不能替代该覆盖。
5. child env 必须剔除 `OPENAI_BASE_URL`、`OPENAI_API_BASE` 和未授权 gateway endpoint。只有显式 gateway 模式才能注入 gateway 配置，且与订阅直连互斥。
6. 启动日志只记录脱敏的私有 `CODEX_HOME`、CLI path/version/SHA、model/provider mode；不得记录 token。
7. 保持裸 `codex` SDK harness 与显式 `codex-native` 的既有分流，不得以 native terminal 解决本问题。

## 必须测试

- 新增/修改隔离测试，覆盖：OpenCodex 污染配置、私有配置清理、auth bridge、child env scrub、显式 model override、10100 阻断。
- 复跑：

```powershell
.venv\Scripts\python.exe -m pytest `
  tests/test_harness_dispatch.py `
  tests/runner/test_codex_terminal_ensure_guard.py `
  tests/server/test_multipart_host_launch.py `
  tests/host/test_connect.py::test_build_runner_env_forwards_python_utf8_encoding_knobs `
  tests/host/test_connect.py::test_host_connected_banner_is_ascii_encodable_under_gbk `
  tests/cli/test_backend.py::test_build_host_daemon_env_local_forwards_python_utf8_encoding_knobs `
  tests/runner/test_app_sessions_native.py::test_create_session_terminal_ensure_routes_codex_native `
  tests/inner/test_codex_native_executor.py -q
```

- 运行相关 Python 编译检查。
- 仅在上述通过后做一次新的 Omnigent full-run；不得重试业务请求：
  `omnigent-zh.exe run <agent_dir> -p "Reply with CONTROLLER_OK and stop." --server <url>`。

## Full-run 验收材料

报告必须给出新的 RUN_ID/evidence 根，并提供以下文件或等价证据：

- 私有 `CODEX_HOME` 的绝对路径、start/end、配置 SHA-256（不得泄露内容）。
- child env 的脱敏摘要，证明无 10100 endpoint。
- native CLI 0.146.0 path/size/SHA start=end。
- OpenCodex/bun 仍存活，10100 未被 Omnigent 占用或关闭。
- resolved harness=`codex`、module=`omnigent.inner.codex_harness`、未进入 `TerminalRegistry.launch`。
- 真实 assistant `CONTROLLER_OK`、`turn/completed`、C exit=0、未触发 240s idle。
- cleanup：PID dead、runtime 删除、端口状态、leak-scan 最后且 0 hits。

交付：实现 diff、测试结果、full-run 报告和持久 evidence。完成后不要自行宣称 Gate 2 PASS 或可 merge，并把结果交给 Grok 审查。
