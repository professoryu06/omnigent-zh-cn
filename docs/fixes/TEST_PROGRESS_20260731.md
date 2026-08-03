# 测试进度记录（2026-07-31）

## 本轮范围

- 候选目录：`F:\codex-ai\omnigent-zh-next`
- Git HEAD：`6ee6d71e`
- 分支：`integration/omnigent-zh-20260731`
- 未执行完整 Gate 2、真实 Codex full-run 或 merge。

## 通过

- Windows 候选元数据/发行审计/平台能力/host API：`38 passed`
- Web i18n：`11 passed`
- Web production build：通过
- WSL 候选元数据/平台能力/host API：`35 passed`
- WSL Codex native 单元组合：`350 passed`
- WSL bwrap + Codex executor/harness/native executor：`200 passed`
- WSL `platform-info --json`：`linux / is_wsl=true / native_cli`
- WSL tmux smoke：通过
- WSL bwrap smoke：通过
- WSL 候选 server background/status/health：`/health` 返回 `{"status":"ok"}`
- WSL 依赖安装：uv sync 成功，独立环境 `.venv-wsl`

## Windows 已知环境失败

Windows Codex native 组合为 `338 passed, 1 skipped, 3 failed`。三个失败都在
`tests/test_codex_native_state.py`：测试把 POSIX `/repo`、`/original` 作为绝对路径，
但 Windows `pathlib.Path` 正确判定它们不是 Windows 绝对路径。该失败不是本轮整合
修改引入，也未修改测试期望掩盖它。

## 网络与回滚

- WSL 代理桥接：`172.31.80.1:17892 -> 127.0.0.1:7897`
- PyPI 访问已恢复，uv 依赖安装成功。
- 原映射 `7892` 已记录；回滚脚本：
  `F:\codex-ai\omnigent-zh-next\scripts\rollback-wsl-proxy-bridge.ps1`

## 下一步

1. 修正或隔离 Windows POSIX-path 测试债务（另开修复卡，不改变业务语义）。
2. 审查候选 Codex 私有 `CODEX_HOME` / OpenCodex 隔离契约。
3. 新 RUN_ID 执行一次 Windows Codex 0.146.0 subscription full-run。
4. 再执行候选 Gate 1，最后才是 Gate 2 六轮。
