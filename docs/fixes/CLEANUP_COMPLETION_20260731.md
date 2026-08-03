# 清理与候选整合执行记录（2026-07-31）

## 已执行

- 清理前快照：`PROJECT_PROGRESS_20260731.md`（先于任何清理写入）。
- 清单：`CLEANUP_MANIFEST_20260731.md`。
- 两个指向已停止 `127.0.0.1:54721` 的孤儿 host 进程已按 PID 定点停止，并复核为 dead；未使用 `taskkill /IM`、`pkill` 或 `tmux kill-server`。
- 20 个已完成的 `AppData\Local\Temp\omnigent-*` 运行目录已移动到可恢复隔离区：
  `C:\Users\Administrator\omnigent-diagnostics\cleanup-quarantine-20260731\`。
  这是可恢复隔离，不是证据删除；evidence 根目录未触碰。
- Ubuntu VHDX 原文件保留。备份：
  `C:\Users\Administrator\omnigent-diagnostics\backups\20260731-Ubuntu-24.04-ext4.vhdx`。
  源/备份 SHA-256 均为
  `8883480DD079355BCA71272CAC8BB1727E7D2B7E6AACB230D11913F7F230F30C`。
- 当前仍运行的 OpenCodex `bun.exe` PID 15536 / 10100 与 Clash Verge `verge-mihomo.exe` PID 15440 / 7897 未触碰。
- `nul` 通过只读检查已不存在；Windows Git 状态仍会显示历史的 `?? nul` 伪路径，未进行危险递归删除。

## 候选目录

- `F:\codex-ai\omnigent-zh-next`
- branch `integration/omnigent-zh-20260731`
- HEAD `7bdaf78c10e16a26e7fb84c254afa2fa96451ffc`
- 使用文件级 overlay；没有 commit、push、merge 或 tag。
- 中文候选包 `omnigent-zh-cn==0.8.0.dev0+zhcn.1`，命令 `omnigent-zh` / `omni-zh`。
- 详细冲突边界与安装验收：候选目录 `docs/zh-CN/INTEGRATION_CONFLICTS_20260731.md`、
  `docs/zh-CN/INSTALL_ACCEPTANCE_20260731.md`。

## 尚未授权/尚未通过

- 未删除 VHDX、未重建 WSL、未切换 TUN/代理、未改 OpenCodex 配置。
- WSL 当前仍无法正常列出/启动 Ubuntu；tmux/bwrap/native harness 验收待单独修复卡。
- 候选 full pytest、Codex 0.146.0 subscription full-run、Gate 1/2 未执行；不可发布或 merge。
