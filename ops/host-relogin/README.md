# Host 登录会话过期 — 临时运维说明（#3012 / L0）

## 这不是什么

- **不是**无人值守自动恢复方案。  
- **不是** refresh-token 生命周期修复。  
- 定时跑 `omnigent login` **不能**视为可靠自动恢复（login 可能需要交互/浏览器）。

## 可以做什么

1. **诊断：** host tunnel 403 时，先怀疑「stored login session expired」，再查 ACL/版本。  
2. **推迟：** 按环境变量提高 session TTL（仅推迟到期）。  
3. **恢复：** **人工**在可交互环境执行 `omnigent login <server>` 后重启/重连 host。  
4. **跟踪上游：** https://github.com/omnigent-ai/omnigent/pull/3013（login-issued refresh grants）。  

## Refresh 设计风险（上游 PR 说明，运维需知）

- 每个 host **replica 应使用独立 grant**；共享同一 token 文件副本会在旋转时互相吊销。  
- 同机并发刷新必须有锁；否则 reuse-detection 可能吊销 grant。

## 默认工程策略

验证/合并上游 #3013，**不要**在 zh-cn 另写一套 refresh 协议。
