# 分支、Tag 与 GitHub 工作流（修订版）

适用：`professoryu06/omnigent-zh-cn`。上游：`omnigent-ai/omnigent`（见 [UPSTREAM.md](../../UPSTREAM.md)）。

---

## 1. 保护区

| 资源 | 规则 |
|------|------|
| `main` | 禁止直推功能；仅 PR |
| 发布 Tag | 已发布不改写；本工作流**不擅自打 Tag** |
| 上游 | 只读 remote；贡献走 fork + PR |

---

## 2. 分支类型

| 前缀 | 用途 |
|------|------|
| `fix/core-*` | 经复现的正确性/隔离/组合修复 |
| `fix/scale-*` | 性能（延后） |
| `ops/*` | runbook / L0 |
| `docs/*` | 文档（如 PR #2） |
| `upstream/sync-YYYYMMDD` | 上游同步 |
| `upstream-pr/*` / `backport/*` | 上游贡献或紧急 backport |
| `repro/*` | 仅复现/测试基建 |

---

## 3. Tag / 发布语义

**唯一允许的发布 Tag 序列（单调递增）：**

```text
v0.6.0-zhcn.1
v0.6.0-zhcn.2
```

后续：`v0.6.0-zhcn.3`、…

- `core` / `scale` **只能**写入 changelog、release notes、labels、补丁清单，或用于**分支名**（如 `fix/core-*` / `fix/scale-*`）。
- **禁止** `fix-core.N` / `fix-scale.N`（或任何等价双轨 Tag）。该命名**已废弃**；**无例外、无「若坚持使用」路径**。

**本轮：不创建 Tag、不发布包、不合并 PR。**

---

## 4. Commit / PR

- 文档、复现测试、不同功能修复尽量**分开提交**  
- 每个功能问题：**独立分支 + 独立 PR**  
- PR body 必含：用户可观察问题、根因证据、范围/未范围、预修复失败、修复后命令与结果、风险回滚、上游状态、是否贡献上游  

---

## 5. 状态权威

- 勿在文档中把单一 commit 写成永久「当前 head」  
- 权威：`gh pr view N --json headRefOid` + `docs/fixes/STATUS.md`  
- 「已修复」仅测试证据 + 代码提交
