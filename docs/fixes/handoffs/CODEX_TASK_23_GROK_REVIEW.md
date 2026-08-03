# CODEX_TASK_23_GROK_REVIEW — Codex/OpenCodex 隔离修复只读审查卡

你是 Grok，只读审查者，不是实现者，也不是 Gate 2 签字人。先等待 Hermes 完成 `CODEX_TASK_23.md`，然后审查其实现 diff、测试结果和新的 full-run evidence。

## 必查结论

确认 Omnigent 的 Codex child 是否真正使用了私有 `CODEX_HOME`，是否只桥接订阅认证，是否彻底隔离 OpenCodex 的 10100 和用户模型配置。

## 必查项

1. 用户 `C:\Users\Administrator\.codex\config.toml` 是否未被修改；OpenCodex/bun 是否仍存活，10100 是否仍可用。
2. `omnigent/inner/codex_executor.py` 是否不再把第三方 `config.toml` 原样复制到 Omnigent 会话。
3. 私有配置是否移除 `openai_base_url`、`openai_api_base`、`gpt-5.6-luna` 和指向 `127.0.0.1:10100` 的 provider；是否没有把 `https://api.openai.com/v1` 硬编码成订阅默认路径。
4. `auth.json` 是否以只读桥接方式可用，日志和 evidence 是否没有泄露凭据。
5. child env 是否剔除 `OPENAI_BASE_URL`、`OPENAI_API_BASE` 和未授权 gateway 变量。
6. argv 是否显式含 `-c model=\"gpt-5.6-sol\"`；gateway 模式和订阅直连模式是否互斥。
7. 裸 `codex` 是否仍走 `omnigent.inner.codex_harness`，显式 `codex-native` 是否仍保持原语义；不得用 native terminal 修复本问题。
8. claude-native、codex-native、JSON create、multipart host launch、parent runner inheritance、managed host 是否有回归证据。
9. 定向 pytest 和隔离测试是否真实执行且未改测试期望掩盖失败；240s watchdog、TUN、代理、认证内容是否未改。
10. full-run 是否只有一次、全新 RUN_ID、CLI 0.146.0 path/size/SHA 正确；真实 assistant `CONTROLLER_OK`、`turn/completed`、C exit=0，且无 10100/404/426、无 TerminalRegistry.launch。
11. cleanup、runtime 删除、PID/端口、final-check、manifest、leak-scan 顺序是否可信，evidence 是否持久存在。

## 裁决

只选一个：

- `ACCEPT_ISOLATION_READY_FOR_CODEX_FINAL_REVIEW`
- `ACCEPT_WITH_NOTES`
- `RECLASSIFY_INCONCLUSIVE`
- `REJECT_PROTOCOL`

不得把单次 full-run 写成 Gate 2 PASS、全仓 GREEN 或可 merge。若失败，按配置泄漏、认证、模型/网关、协议流、runner 路由分别分类，不得重跑完整 Gate 2。

## 交付

写入新的 `docs/fixes/handoffs/GROK_REVIEW_23.md`，列出 PASS/FAIL/NA、证据文件名、回归面和唯一下一步建议。不要修改源码、旧报告、用户 Codex 配置或本 RUN evidence，不 commit/push/merge/tag。
