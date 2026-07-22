# 修复状态跟踪

更新规则：每开分支 / 提 PR / 打 tag / 上游合并，改一行并 commit。

| Issue | 层 | 分支 | PR (zh-cn) | Upstream PR | Tag | 状态 |
|-------|----|------|------------|-------------|-----|------|
| #2853 | core | `fix/core-2853-native-prompt` | — | — | — | planned |
| #2747 | core | `fix/core-spec-parse-2746-2747` | — | — | — | planned |
| #2746 | core | `fix/core-spec-parse-2746-2747` | — | — | — | planned |
| #2854 | core | `fix/core-harness-override-2854` | — | — | — | planned |
| #3016 | core | `fix/core-workspace-3016` | — | — | — | planned |
| #2539 | core | `fix/core-child-session-2539` | — | — | — | planned |
| #2967 | core | `fix/core-compact-2967` | — | — | — | planned |
| #3012 | scale | `ops/host-jwt-relogin` → `fix/scale-jwt-renew-3012` | — | — watch | — | planned |
| #3004 | scale | `fix/scale-stream-acl-3004` | — | — | — | planned |
| #3003 | scale | `fix/scale-policy-cache-3003` | — | — | — | planned |
| #2702 | scale | `fix/scale-idle-tmux-2702` | — | — | — | planned |
| #3001 | scale | `fix/scale-sessions-list-3001` | — | — | — | planned |

状态枚举：`planned` → `in-progress` → `pr-open` → `merged` → `tagged` → `upstream-merged` / `wontfix`

## 文档波次

| 波次 | 内容 | 分支 | 状态 |
|------|------|------|------|
| 0 | 分析报告 + 修复方案 + 版本约定 | `docs/fix-plans-core-secondary` | in-progress |
