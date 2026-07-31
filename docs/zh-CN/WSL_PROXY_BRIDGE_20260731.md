# WSL 代理桥接版本记录（2026-07-31）

## 变更目的

让 Ubuntu-24.04 继续使用既有环境变量 `172.31.80.1:17892`，但把 Windows
端目标改为当前 Clash Verge 混合代理端口 `127.0.0.1:7897`，不改 TUN、OpenCodex
或 Codex 配置。

## 变更前（已记录）

```text
172.31.80.1:17892 -> 127.0.0.1:7892
```

这是系统原有映射；没有删除原配置备份，回滚时可恢复到上面这一行。

## 变更后

```text
172.31.80.1:17892 -> 127.0.0.1:7897
```

作用范围仅为 WSL 网关上的一个 TCP 端口。Windows 上的 OpenCodex `10100`、
Clash TUN 和其他端口不变。

## 回滚命令

```powershell
netsh interface portproxy delete v4tov4 listenaddress=172.31.80.1 listenport=17892
netsh interface portproxy add v4tov4 listenaddress=172.31.80.1 listenport=17892 connectaddress=127.0.0.1 connectport=7892
```

## 验证

完成桥接后，先从 WSL 请求 PyPI，再运行候选仓库的 `uv sync --extra all --extra dev`。
若失败，只撤销这条映射，不删除 Ubuntu 或 VHDX。
