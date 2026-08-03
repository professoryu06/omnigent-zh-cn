# WSL 代理桥接版本记录（2026-07-31）

原有映射：`172.31.80.1:17892 -> 127.0.0.1:7892`。

本次用户确认采用最小影响方案，将目标改为当前 Clash Verge 端口：
`172.31.80.1:17892 -> 127.0.0.1:7897`。

回滚：

```powershell
netsh interface portproxy delete v4tov4 listenaddress=172.31.80.1 listenport=17892
netsh interface portproxy add v4tov4 listenaddress=172.31.80.1 listenport=17892 connectaddress=127.0.0.1 connectport=7892
```

不改 TUN、OpenCodex 10100、Ubuntu VHDX 或 evidence。
