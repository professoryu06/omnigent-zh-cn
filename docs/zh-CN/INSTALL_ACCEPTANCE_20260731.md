# 中文候选安装与验收记录（2026-07-31）

## 候选身份

- 目录：`F:\codex-ai\omnigent-zh-next`
- 分支：`integration/omnigent-zh-20260731`
- Git checkpoint：`997607b1`；基线回滚标签：`integration-base-20260731`
- upstream 基线：`7bdaf78c10e16a26e7fb84c254afa2fa96451ffc`
- 中文来源：`omnigent-zh-cn` `81594243f7a17303b9ba477b938ac323f938c2e4`
- Python：3.12.13；uv：0.12.0；Node：24.14.0
- 包名：`omnigent-zh-cn==0.8.0.dev0+zhcn.1`
- 命令：`omnigent-zh`、`omni-zh`（共用 `omnigent.cli:main`）

## 已完成

- 独立 `.venv`，`uv sync --extra all --extra dev` 成功。
- `omnigent-zh platform-info --json` 成功，Windows 返回 `sdk_or_web`，
  `native_tmux_supported=false`。
- `omnigent-zh server --background --no-open` → `server status` → `/health`
  最小链路通过（HTTP 200）；随后已用 `server stop` 清理。
- 中文发行元数据、发行审计、跨平台工作流测试：8 passed。
- Web i18n 单元测试：11 passed。
- Web 生产构建：通过；仅有既有 CSS pseudo-element 与大 chunk 警告。
- Python compile 与 ruff（移植文件）：通过。
- host/runner 集成测试 `tests/server/integration/test_hosts_api.py`：25 passed。
- BUG-1：runner env allowlist 增加 `PYTHONUTF8` / `PYTHONIOENCODING`，成功 banner
  改为 ASCII。
- BUG-2：保留 upstream 单一 registry 的裸 `codex` SDK / `codex-native` terminal
  分流，未把裸 codex 重新映射到 tmux。
- BUG-3：multipart `host_id` 现在沿用 JSON host-launch 的权限、绑定、frame 和
  单次 launch helper。

## 未通过/未执行

- 完整 Python pytest、Gate 1、Gate 2 六轮：未执行。
- Codex 订阅 full-run 与 0.146.0 native CLI：未执行；review 分支 Route-A 代理
  方案不自动带入候选。
- WSL2：改用新版 `C:\Program Files\WSL\wsl.exe` 后已恢复；Ubuntu-24.04 可启动，
  Python 3.12.3、uv 0.11.33、Node 22.23.1、tmux 3.4、bwrap 0.9.0、Codex
  0.144.4 均可用，tmux/bwrap smoke 通过。Ubuntu VHDX 已备份，原文件未动。
- WSL 候选依赖安装已创建独立 `.venv-wsl`，但 uv 下载 `lark==1.3.1` 时访问
  PyPI 超时；这属于 WSL 出站代理/TUN 路径待处理，不代表 WSL 或 tmux 修复失败。
- 随后将既有 WSL 桥接从 `172.31.80.1:17892 -> 127.0.0.1:7892` 更新为
  `172.31.80.1:17892 -> 127.0.0.1:7897`，PyPI 访问恢复，候选 Linux 依赖安装成功。
- WSL 候选定向验收：35 passed；独立环境为 `.venv-wsl`，未覆盖 Windows `.venv`。
- 中文 UI：i18n provider/词条已接入入口，但 upstream 新组件尚未逐一替换为 `t()`；
  所以“词条层可用”不等于“全量界面翻译完成”。

## 结论

这是可继续验收的干净候选，不是可发布或可 merge 版本。下一步先单独修复/恢复
WSL2，随后做 Windows SDK、WSL native、Codex isolation，再执行 Gate 1/2；任何一次
full-run 都不能代替 Gate 2。
