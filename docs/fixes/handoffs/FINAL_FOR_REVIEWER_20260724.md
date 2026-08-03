# 给审查 Agent 的交接（用户将转发）

## 一句话
请审查 omnigent-zh-cn 的 **PR#2 未提交 r04 门槛脚本修复** + **PR#3/#4/#5 定向复验结果**；**不要 merge / 不要 push / 不要打 Tag**。

## 工作副本
`F:\codex-ai\git项目部署\tmp\omnigent-review`  
分支：`docs/fix-plans-core-secondary`

## 必读
1. `docs/fixes/handoffs/REVIEW_PACKAGE_20260724_core.md`
2. `docs/fixes/handoffs/HANDOFF_20260724_r04.md`
3. `docs/fixes/PRE_MERGE_GATES.md`（r04 后）
4. `docs/fixes/STATUS.md`

## 必查命令
```bash
gh pr view 2 --json headRefOid,state,url,title
gh pr view 3 --json headRefOid,state,url,title
gh pr view 4 --json headRefOid,state,url,title
gh pr view 5 --json headRefOid,state,url,title
cd "F:/codex-ai/git项目部署/tmp/omnigent-review"
git status -sb
git diff --stat
```

## 已知事实
- r04：Gate 脚本 P1 已修（PIPESTATUS + EVIDENCE_ROOT）
- 定向测试：PR3=2绿 / PR4=7绿 / PR5=57绿（Windows，≠ Gate1）
- Gate1/Gate2：未跑；WSL 启动失败 0x800705aa
- #2853 仅为 Phase1 fail-loud
- 无 push、无 merge、无新 Tag

## 请输出
## 审查结论
## 发现问题（按 P0/P1/P2）
## 下一步（最多 3 条）
