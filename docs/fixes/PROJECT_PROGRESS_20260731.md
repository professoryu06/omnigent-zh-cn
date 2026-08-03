# Omnigent 三方整合前进度快照

生成时间：2026-07-31（清理前）

## 基线

- 当前工作树：`F:\codex-ai\git项目部署\tmp\omnigent-review`
- 当前分支：`docs/fix-plans-core-secondary`
- 当前 HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- 中文仓库基线：`81594243f7a17303b9ba477b938ac323f938c2e4`
- 上游仓库基线：`7bdaf78c10e16a26e7fb84c254afa2fa96451ffc`
- 上游最新发布版：`v0.7.0`（主线随后仍有未发布提交）
- 当前分支基于中文仓库 main，并包含本轮修复、诊断和门禁文档；未提交改动不作为已发布版本。

## 当前未提交范围

当前工作树存在未提交改动，主要包括：

- `AGENTS.md`
- `docs/fixes/POST_FIX_HANDOFF_PROMPT.md`
- `docs/fixes/PRE_MERGE_GATES.md`
- `docs/fixes/STATUS.md`
- `omnigent/cli.py`
- `omnigent/codex_native_app_server.py`
- `omnigent/harness_aliases.py`
- `omnigent/host/connect.py`
- `omnigent/inner/*_native_executor.py`
- `omnigent/inner/codex_executor.py`
- `omnigent/inner/loader.py`
- `omnigent/native_server_harness.py`
- `omnigent/runner/_entry.py`
- `omnigent/runner/app.py`
- `omnigent/runner/transports/ws_tunnel/serve.py`
- `omnigent/server/routes/_workspace_validation.py`
- `omnigent/server/routes/sessions.py`
- 对应的 CLI、host、runner、server、Codex isolation 测试
- `docs/fixes/handoffs/` 下的阶段任务卡、诊断报告、验收报告和方案文档
- 未跟踪辅助文件：`nul`、`omnigent/inner/native_prompt_delivery.py`、若干新增测试文件

完整逐项清单以清理前 `git status --short` 输出和本工作树为准；本快照不把这些改动宣称为已合并或已发布。

## 已完成测试与诊断

- BUG-1/2/3、Codex isolation 及相关回归定向测试：`44 passed`。
- 更大 Codex executor 测试分片：`154 passed, 1 failed`；唯一失败是既有 Windows real-home-auth 环境测试，不是本轮代理改动引入。
- 阶段 17 REWORK：D0/D1 PASS，结论为 `DIAG_D1_READY_FOR_D2`；并非 Gate 2 PASS。
- 阶段 24 Route-A 代理实现后 full-run r1–r4：均未得到真实 `CONTROLLER_OK`，出现 Rust `10106/11003`；未连接 10100，OpenCodex 保持存活，leak scan 为 0。
- Gate 1：相对 main PASS，非全仓 GREEN。
- Gate 2：尚未通过，当前不可 merge。

## Evidence（全部保留）

Evidence 根目录：`C:\Users\Administrator\omnigent-diagnostics\`

阶段 14–24 关键运行根：

- `20260730-1452-dc83140-grok-codex-idle-diag-r2`
- `20260730-160451-dc83140-grok-appserver-426-r1`
- `20260730-171141-dc83140-grok-cli0146-d0d1-r1`
- `20260730-180739-dc83140-grok-cli0146-d0d1-r2`
- `20260730-190615-dc83140-grok-d2-c-cli0146-r1`
- `20260730-192929-dc83140-grok-agent-observer-preflight-r1`
- `20260730-144404-dc83140-hermes-http-session-roundtrip-r1`
- `20260730-172454-dc83140-hermes-d2-run-cli0146-r2`
- `20260731-035708-dc83140-hermes-responses10100-cli0146-r1`
- `20260731-044137-dc83140-hermes-isolation-fullrun-cli0146-r1`
- `20260731-060535-dc83140-hermes-isolation-fullrun-cli0146-r2`
- `20260731-064535-dc83140-hermes-diag24-r1`
- `20260731-114121-dc83140-grok-fullrun-cli0146-r1`
- `20260731-152542-dc83140-codex-proxy-fullrun-r1`
- `20260731-153045-dc83140-codex-proxy-fullrun-r2`
- `20260731-153704-dc83140-codex-proxy-fullrun-r3`
- `20260731-154130-dc83140-codex-proxy-fullrun-r4`

不得在清理中删除、改写或拼接上述 evidence。

## 清理前平台状态

- Windows 原生存在 Omnigent 文件，但当前 server 端口 `54721` 不监听。
- 存在指向 `http://127.0.0.1:54721` 的历史 host daemon；其父进程已退出，待白名单清理。
- Windows PATH 中没有 `tmux.exe`。
- WSL 注册了 `Ubuntu-24.04`，其 VHDX 位于：
  `C:\Users\Administrator\AppData\Local\wsl\{d970ed06-a30a-4c14-ae28-e59df08f1542}\ext4.vhdx`
- 当前 `wsl.exe -d Ubuntu-24.04 -- echo WSL_OK` 返回“系统找不到指定的路径”；VHDX 在备份前不得删除。
- Clash TUN/代理仍为 PID 15440、端口 `7897`；OpenCodex 为 PID 15536、端口 `10100`；本次清理不触碰二者。

## 清理边界

本快照写入后，才允许执行以下白名单动作：清理已确认的孤儿 host、已完成运行的临时目录、无效状态文件和确认残留的 `nul`。保留 evidence、源码仓库、任务文档与 Ubuntu VHDX；不使用 blanket kill、`wsl --unregister`、`tmux kill-server` 或全盘递归删除。

