# 次重要验收矩阵

| ID | Issue | 步骤摘要 | Pass 标准 |
|----|-------|----------|-----------|
| S-3012 | #3012 | JWT 过期后 host reconnect | 自动续期或明确过期错误 + 脚本可恢复 |
| S-3004 | #3004 | 单 turn 流式压测 | 查询次数/耗时显著下降 |
| S-3003 | #3003 | 连续 policy 评估 | engine 非每次 rebuild |
| S-2702 | #2702 | 多 native terminal 空闲 | runner CPU 下降 |
| S-3001 | #3001 | 大量 sessions list | 延迟与 page 相关 |

优先在 **fix-core 波次完成** 后再投入自动化。
