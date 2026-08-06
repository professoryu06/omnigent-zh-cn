# Ticket: #<issue>

## 功能目标

（一句话：修完后哪个功能行为变为正确）

## 选中方案

- [ ] A 止血 L0
- [ ] B 功能修复 L1
- [ ] C 上游完整 L2

## 代码改动范围

-

## 测试

```bash
# commands
```

## 分支 / PR / Tag

- branch:
- pr:
- tag: （本轮默认不创建 Tag；若发布，使用单调序列 `v0.6.0-zhcn.N`，由 release 流程决定）

## 回滚

`git revert <sha>`，或回退到上一发布 tag（例如 `v0.6.0-zhcn.N` 的前一号）。
**不要**使用已废弃的 `v*-zhcn.fix-core.N` / `fix-scale.N` 双轨命名。
