# 次要与条件性修复方案（修订版）

---

## #3012 Host JWT 过期后 reconnect 403（条件性 P0/P1）

### 何时升级

双机部署、频繁重连、无人值守 host 长跑 → 升为 P0/P1。  
单机短会话开发 → 可保持观察。

### 上游状态（权威以 gh 为准）

| 项 | 记录 |
|----|------|
| Upstream PR | https://github.com/omnigent-ai/omnigent/pull/3013 |
| 关系 | Closes #3012 |
| 生成时快照 | **OPEN + draft**；作者称本地 155 tests passed；CI Security Gate 等多为 FAILURE/SKIPPED（需再查 head） |
| 代码范围 | `cli_auth` refresh + lock；login 发 refresh grant；host/runner token factory；错误文案 |

**默认策略：** 跟踪并验证 #3013；**不要**在 zh-cn 再实现另一套 refresh 协议。  
仅紧急部署且上游长期停滞时，才考虑 **临时 backport**（单独分支，标明上游 SHA）。

### Refresh 风险（必须写进运维认知）

1. **每个 host replica 独立 grant** — 旋转 + reuse 检测会吊销共享 token 文件的副本（设计如此）。  
2. **同机并发刷新需要锁** — #3013 使用 advisory file lock（lock → re-check → refresh），避免 stale replay 触发 reuse-revocation。

### 方案 A — L0（临时 runbook，**不**等于无人值守恢复）

允许描述为：

- 提高 session TTL（仅推迟）  
- **人工**重新 `omnigent login`  
- 明确诊断：403 时先查「登录会话是否过期」，勿误判为 ACL/版本  

**禁止**写成：

- 「定时执行 `omnigent login` 即可无人值守恢复」（login 可能交互，不可靠自动恢复）  
- 「L0 解决了生命周期问题」

### 方案 B / C

- **不在本 fork 重复实现**；验证 #3013 合并后 sync。  
- 若 backport：完整移植测试，不发明第二协议。

### 分支

- 默认：无（跟踪）  
- 紧急：`backport/upstream-3013-jwt-renew`（需书面理由）

---

## Scale（#3004 / #3003 / #2702 / #3001）

本轮：**基线测量 + 计划 only**。  
在核心候选（尤其 #3016/#2853）有证据修复前，**不大改 server/runner 热路径**。

| Issue | L0 | L1 方向（延后） |
|-------|----|-----------------|
| #3004 | 限并行 fan-out | stream 路径缓存 conversation+ACL |
| #3003 | 减少 policy 热路径依赖 | 复用 policy engine |
| #2702 | 少开 native terminal | 降频/批处理 idle capture |
| #3001 | 清理旧会话 | 分页、去掉全量 id 预取 |

---

## #2575 pi-native Databricks 非 Claude

- 上游 PR：https://github.com/omnigent-ai/omnigent/pull/2833  
- 生成时快照：OPEN，未 merge；DCO ACTION_REQUIRED 等  
- **无本地复现与明确缺口时不 backport**
