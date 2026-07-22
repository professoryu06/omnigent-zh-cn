# 核心验收矩阵

| ID | Issue | 步骤摘要 | Pass 标准 |
|----|-------|----------|-----------|
| C-2853 | #2853 | native agent + 独特 prompt 要求 commit trailer | trailer 出现；或 strict 模式明确报错 |
| C-2747 | #2747 | 单文件 YAML 声明非默认 harness | 实际 launch harness 一致 |
| C-2746 | #2746 | 单文件声明 model | 实际 model 一致 |
| C-2854 | #2854 | create + harness_override + initial_items | turn0 harness == override |
| C-3016 | #3016 | 强制 snapshot 失败后再成功 | workspace 非全局 runner cwd |
| C-2539 | #2539 | 同 parent 连续 2+ named 子会话 | 均成功非 404 |
| C-2967 | #2967 | 超长上下文再 turn | 不永久 Prompt is too long |

记录格式：

```
date: 2026-07-22
commit: <sha>
omnigent: 0.6.0.dev0
C-2853: FAIL | notes: ...
```
