# Host JWT 续期（#3012 方案 A）

## 目的

在上游 refresh 落地前，避免 host 在 session JWT 过期后 reconnect 永久 403。

## 做法

1. 确认 auth 模式：`omnigent login`（accounts/OIDC）才需要本方案。  
2. 将 TTL 记入运维日历；默认 8h，也可用环境变量拉长（仅推迟）。  
3. 在 TTL 到期前 1 小时执行一次交互或自动化 re-login（按你们账号体系选型）。  
4. 403 排障顺序：**先查 token 过期** → 再查 ACL/版本。

## 脚本占位

后续在本目录添加：

- `relogin.ps1`（Windows host）  
- `relogin.sh`（macOS / WSL）  

合入分支建议：`ops/host-jwt-relogin`。
