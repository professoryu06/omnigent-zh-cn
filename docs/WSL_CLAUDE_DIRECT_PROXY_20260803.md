# WSL Claude 直连 DeepSeek 记录

日期：2026-08-03

## 当前路径

Omnigent 的 `claude-native` 使用 `deepseek-claude` provider：

```text
base_url: https://api.deepseek.com/anthropic
model: deepseek-v4-flash
```

请求不经过 CCSwitch 的 `127.0.0.1:15721`。WSL host 进程通过 Clash 普通代理出站：

```text
WSL → 172.31.80.1:17892 → Windows 127.0.0.1:7897 → DeepSeek
```

TUN 保持开启。

## 已实施

- 重建 Windows `portproxy`：`0.0.0.0:17892 → 127.0.0.1:7897`。
- 新增防火墙规则 `Omnigent WSL Clash Proxy 17892`，仅允许 `172.31.80.0/20`。
- WSL host 使用独立启动脚本：`scripts/start_omnigent_claude_direct.sh`。
- 清理 WSL `~/.claude/settings.json` 中残留的 CCSwitch token/base URL；原文件已备份。
- Omnigent provider 配置已保留 CCSwitch，但默认改为 `deepseek-claude`；原配置已备份。

## 验证

- WSL 经 `172.31.80.1:17892` 请求 DeepSeek 返回 HTTP 401，证明代理链路可达。
- Omnigent 会话 `59770a8341964def92e897e9eb8896af`：
  - provider=`deepseek-claude`
  - model=`deepseek-v4-flash`
  - assistant 输出：`CLAUDE_DS_PROXY_OK`
  - 未出现 CCSwitch token 警告

## 回滚

- 恢复 WSL Claude 设置备份；
- 恢复 `/home/administrator/.omnigent/config.yaml` 的 direct 变更前备份；
- 删除 Windows `portproxy` 的 17892 条目及同名防火墙规则；
- 停止 `omnigent-host-direct`，改用原 host 启动方式。

Codex、Grok、OpenCodex（10100）未纳入本次 Claude 代理配置，后续分别验证。
