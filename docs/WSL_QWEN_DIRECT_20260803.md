# WSL Qwen Token Plan 直连记录

日期：2026-08-03

## 当前路由

```text
Qwen Code 0.20.1
  → https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
  → DASHSCOPE_API_KEY（仅保存在 WSL ~/.qwen/.env）
  → qwen3.8-max-preview
```

Qwen 不经过 CCSwitch、OpenCodex 的 10100，也不复用 Claude 的 provider。

## 模型名说明

用户提出的 `qwen3.8-review` 不是 Token Plan 的真实 API 模型 ID，直接请求会返回
`model_not_found`。本地 Qwen 配置保留了 `qwen3.8-review (Token Plan)` 显示标签，
实际请求使用 Token Plan 已提供的 `qwen3.8-max-preview`，否则无法完成请求。

Token Plan 的 OpenAI 兼容地址来自[千问 Token Plan 官方快速开始](https://platform.qianwenai.com/docs/token-plan/team/token-plan-team-quickstart)。

## 验证结果

- Token Plan `/models` 返回 200；密钥认证有效。
- 真实 API 请求：`qwen3.8-max-preview` 返回 `TOKENPLAN_qwen3.8-max-preview_OK`。
- Omnigent `qwen-native` 首轮返回 `QWEN38_OMNIGENT_OK`。
- 同一会话第二轮返回 `QWEN38_FOLLOWUP_OK`，证明可持续交互。
- 会话结束状态为 idle；未观察到 OpenCodex/10100 路径。
- 测试完成后已恢复 Claude 代理 host。

## 启动脚本

使用 `scripts/start_qwen_direct.sh`。脚本清理进程级代理变量，保留本机
`~/.qwen/.env` 中的密钥，并指向 Token Plan 专用地址；不会修改原始 OpenCodex
配置，也不会影响 Claude 的 CCSwitch/代理路径。

## 安全提醒

密钥只写入 WSL 的 `~/.qwen/.env`，权限为 600，不写入仓库。由于密钥曾在聊天中
粘贴，验证后应到 Token Plan 控制台撤销并重新生成。
