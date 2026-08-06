# 次重要验收矩阵

| ID | Issue | 步骤摘要 | Pass 标准 |
|----|-------|----------|-----------|
| S-3012 | #3012 | JWT 过期后 host reconnect | **上游 refresh（#3013）合并后**：自动刷新恢复。**当前 L0**：明确「session 已过期」诊断 + **人工** `omnigent login`。L0 **不**解决无人值守生命周期，也**不**声称脚本可自动恢复。 |
| S-3004 | #3004 | 单 turn 流式压测 | 查询次数/耗时显著下降 |
| S-3003 | #3003 | 连续 policy 评估 | engine 非每次 rebuild |
| S-2702 | #2702 | 多 native terminal 空闲 | runner CPU 下降 |
| S-3001 | #3001 | 大量 sessions list | 延迟与 page 相关 |

优先在核心候选有证据修复后再投入 Scale 自动化。
