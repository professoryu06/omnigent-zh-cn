# WSL 修复记录（2026-07-31）

## 结论

Ubuntu-24.04 已恢复可用，不需要重新注册或删除发行版。

根因是机器上同时存在旧入口 `C:\Windows\System32\wsl.exe` 和新版
`C:\Program Files\WSL\wsl.exe`。旧入口无法处理当前 Ubuntu 的 `Modern=1`
注册信息，并伴随 Hyper-V `0x800705AA` 错误；新版 WSL 2.7.10.0 可正常启动。

## 保护措施

- Ubuntu VHDX 原文件未删除、未注销。
- 备份：`C:\Users\Administrator\omnigent-diagnostics\backups\20260731-Ubuntu-24.04-ext4.vhdx`
- 源/备份 SHA-256：
  `8883480DD079355BCA71272CAC8BB1727E7D2B7E6AACB230D11913F7F230F30C`

## 验证结果

使用新版入口：`C:\Program Files\WSL\wsl.exe`

- `Ubuntu-24.04 -- echo WSL_OK`：成功
- Python：`3.12.3`
- uv：`0.11.33`
- Node：`v22.23.1`
- npm：`10.9.8`
- tmux：`3.4`
- bubblewrap：`0.9.0`
- Codex CLI：`0.144.4`
- tmux 创建/查询/清理 smoke：通过
- bwrap 基础 sandbox smoke：通过

启动时仍有 systemd user session 警告，但不影响当前 tmux/bwrap/native 基础能力。

## 后续注意

Omnigent 的 WSL 任务卡必须固定使用新版 WSL 入口，或让系统 PATH 优先指向新版；
不要再把旧 `System32\wsl.exe` 的失败输出当作 Ubuntu 未注册。当前未执行 WSL 注销、
VHDX 重建或大范围服务重置。
