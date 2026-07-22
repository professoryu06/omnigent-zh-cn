# Omnigent 问题修复方案总览

**仓库：** [professoryu06/omnigent-zh-cn](https://github.com/professoryu06/omnigent-zh-cn)  
**上游：** [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent)  
**基线版本：** 本机 `omnigent 0.6.0.dev0`（2026-07-14）；分析日期 2026-07-22  
**配套分析：** [omnigent-issues-analysis-report.md](../omnigent-issues-analysis-report.md)（若尚未同步，见分析报告）

---

## 1. 修复分层（按功能，不是按标签）

| 层 | 含义 | 目标效果 | 方案类型 |
|----|------|----------|----------|
| **L0 运维兜底** | 不改核心源码，配置/脚本/角色定义绕过 | 今天就能稳住 | 本仓库 `ops/` + agent YAML |
| **L1 分发补丁** | 在 zh-cn fork 修功能，先惠及我们 | 正确性/稳定性落地 | `fix/*` 分支 + tag `v*-zhcn.fix*` |
| **L2 上游贡献** | PR 回 `omnigent-ai/omnigent` | 长期可同步、不分叉腐烂 | upstream PR + cherry-pick 回 zh-cn |

**原则：**

1. **核心问题（正确性）**：优先 L1 补丁 + 同步提 L2；L0 只作临时止血。  
2. **次重要问题（长跑/性能）**：优先 L0 运维 + 观察；需要时再 L1/L2。  
3. **禁止**在 `main` 上直接改功能；一律走分支 → PR → tag。

---

## 2. 问题清单与方案入口

### 2.1 核心（正确性）— 详见 [CORE_FIX_PLANS.md](./CORE_FIX_PLANS.md)

| Issue | 功能点 | 不修会怎样 | 推荐路径 |
|-------|--------|------------|----------|
| #2853 | 角色 prompt 下发 | 角色身份静默丢失 | L1 补丁 + L2 PR；L0 暂用 SDK harness |
| #2747 | YAML harness 解析 | 声明的 harness 被忽略 | L1 与 #2746 同批 |
| #2746 | YAML model 解析 | 模型被换成默认 | L1 与 #2747 同批 |
| #2854 | harness_override 首 turn | 第一枪跑错引擎 | L1 小补丁；L0 空 session 绕过 |
| #3016 | session 工作区缓存 | 多 agent 串目录 | L1 必修；L0 删 session |
| #2539 | named 子 session | 第二个子 agent 404 | L1 必修 |
| #2967 | 上下文满不 compact | 长 gate 砖死 | L1 策略补丁 + L0 会话轮换 |

### 2.2 次重要（稳定性/性能）— 详见 [SECONDARY_FIX_PLANS.md](./SECONDARY_FIX_PLANS.md)

| Issue | 功能点 | 不修会怎样 | 推荐路径 |
|-------|--------|------------|----------|
| #3012 | host JWT 续期 | 8h 后重连永久 403 | L0 定时 re-login；L1/L2 refresh token |
| #3004 | stream 事件查库 | 并发压垮 DB | L1 缓存；先观察 |
| #3003 | policy 每评重建 | tool call 变慢 | L1 引擎复用 |
| #2702 | idle tmux 高频 | runner CPU 高 | L1 降频/批处理 |
| #3001 | sessions 列表预取 | UI 变钝 | L1 懒加载；低优先 |

---

## 3. Git / GitHub 版本管理（强制）

完整约定见 [ops/versioning/BRANCHING.md](../../ops/versioning/BRANCHING.md)。

### 3.1 分支命名

```
main                              # 可发布主干，仅合并 PR
docs/fix-plans-core-secondary     # 本方案文档
fix/core-2853-native-prompt       # 单 issue 或同功能簇
fix/core-workspace-3016
fix/core-spec-parse-2746-2747     # 同功能可合并一分支
fix/core-child-session-2539
fix/core-compact-2967
fix/core-harness-override-2854
fix/scale-jwt-renew-3012
fix/scale-stream-acl-3004
fix/scale-policy-cache-3003
fix/scale-idle-tmux-2702
upstream/sync-YYYYMMDD            # 上游同步
ops/repro-matrix                  # 复现脚本与门禁
```

### 3.2 Tag 约定

| Tag 模式 | 用途 |
|----------|------|
| `v0.6.x-zhcn.N` | 常规中文分发版本 |
| `v0.6.x-zhcn.fix-core.N` | 含核心正确性补丁的发布点 |
| `v0.6.x-zhcn.fix-scale.N` | 含长跑/性能补丁的发布点 |
| `repro-core-YYYYMMDD` | 复现矩阵可复现快照 |

### 3.3 每个功能修复的标准流水线

```text
1. 从 main 拉 fix/<scope>-<issue>
2. 写/更新 docs/fixes/tickets/<issue>.md（目标·改点·测试）
3. 改代码 + tests/
4. 本地：相关单测 + scripts/repro/ 对应 case
5. gh pr create --base main --title "fix(<scope>): ..."
6. CI 绿 → squash merge
7. 需要对外可用：打 tag + 更新 CHANGELOG 条目
8. 上游可贡献：另开分支 cherry-pick 干净提交 → PR omnigent-ai/omnigent
9. 上游合并后：upstream/sync-* 合回，去掉重复补丁，保留测试
```

### 3.4 与上游的关系

- **不直接 push 上游 main。**  
- zh-cn 补丁默认带前缀注释：`# zh-cn-fix: issue #NNNN`，便于同步时识别。  
- 上游已合的 issue：在 `docs/fixes/STATUS.md` 标 `upstream-merged`，下一轮 sync 删掉重复补丁。

---

## 4. 推荐实施顺序（功能依赖）

```text
第 1 波（身份与路由正确）
  #2853 → #2747+#2746 → #2854

第 2 波（编排可组合）
  #3016 → #2539

第 3 波（长任务存活）
  #2967

第 4 波（长跑与吞吐，按需）
  #3012 → #3004 → #3003 → #2702 → #3001
```

---

## 5. 文档索引

| 文件 | 内容 |
|------|------|
| [CORE_FIX_PLANS.md](./CORE_FIX_PLANS.md) | 核心问题：功能修复方案 A/B/C |
| [SECONDARY_FIX_PLANS.md](./SECONDARY_FIX_PLANS.md) | 次重要：功能修复方案 A/B/C |
| [STATUS.md](./STATUS.md) | 跟踪表：分支 / PR / tag / 状态 |
| [../omnigent-issues-analysis-report.md](../omnigent-issues-analysis-report.md) | 原始 issue 筛选报告 |
| [../../ops/versioning/BRANCHING.md](../../ops/versioning/BRANCHING.md) | 分支 / tag / PR 细则 |
| [../../scripts/repro/README.md](../../scripts/repro/README.md) | 复现与验收脚本说明 |
