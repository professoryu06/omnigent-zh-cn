# 审查 agent 提示词（复制下方代码块全文）

把下面从 `你是独立审查 agent` 到文末的整段复制给另一个 agent。

---

```text
你是独立审查 agent。请审查 Omnigent-zh-cn 当前 4 个 open PR，判断是否可合并，并给出最多 3 条下一步。必须基于最新 PR head 与 diff，不要只复述文档。

## 仓库
https://github.com/professoryu06/omnigent-zh-cn
上游：https://github.com/omnigent-ai/omnigent

## 开始前必须读真实 head
gh pr view 2 --json headRefName,headRefOid,state,url,title
gh pr view 3 --json headRefName,headRefOid,state,url,title
gh pr view 4 --json headRefName,headRefOid,state,url,title
gh pr view 5 --json headRefName,headRefOid,state,url,title

PR：
- #2 文档：https://github.com/professoryu06/omnigent-zh-cn/pull/2
- #3 #3016：https://github.com/professoryu06/omnigent-zh-cn/pull/3
- #4 #2747/#2746：https://github.com/professoryu06/omnigent-zh-cn/pull/4
- #5 #2853 fail-loud：https://github.com/professoryu06/omnigent-zh-cn/pull/5

交接说明（PR #2 分支上）：
docs/fixes/REVIEW_HANDOFF_2026-07-22.md
docs/fixes/STATUS.md

## 生成时 head 快照（仅对照，以 gh 为准）
- #2：b5601649bfbb486a697de7e3b1c6ba02624a9bec
- #3：744e3a04a9b041b7bf3c2ae25cd22f96f5945038
- #4：30c04c3a173543f2802f3d8277a1660a616b393a
- #5：1f42a898fbd07e358f87de5cba391a93af1f43b9

## 历史审查结论与整改
- PR #3：approve（不要再改代码，除非回归）
- PR #4：approve（不要再改代码，除非回归）
- PR #2：曾 request-changes（Tag 双轨）→ 执行方声称已删「若使用/若坚持 fix-core.N」例外，只允许 v0.6.0-zhcn.N，fix-core/fix-scale 仅废弃禁止
- PR #5：曾 request-changes（docstring「ignored — set at session creation」）→ 执行方声称已改为 Phase-1 fail-loud 语义；功能仍是 mitigated 非 apply

## 必须核实的点
### PR #5（最严）
1. 行为仍是 fail-loud only：warn / OMNIGENT_STRICT_PROMPT，不 apply prompt
2. docstring 不再声称 set at session creation / 已送达 / 已应用
3. 日志/错误不得含 system_prompt 原文或测试 sentinel
4. 多 native 路径有 fail-loud 证据（不只 claude）
5. 文案不得把 fail-loud 写成「角色 prompt 已恢复/完整 fixed」

### PR #2
1. Tag 只允许 v0.6.0-zhcn.N 单调序列
2. fix-core.N / fix-scale.N 只出现在明确废弃/禁止语境，无「若坚持」例外
3. #3012 无「脚本可自动恢复」
4. #2853 仍是 mitigated/fail-loud Phase1

### PR #3 / #4
- 快速确认 head 未遭无关改动；逻辑与测试仍成立即可

## 建议命令（能跑则跑）
# PR5
uv run pytest tests/inner/test_native_system_prompt_delivery.py tests/inner/test_claude_native_executor.py tests/inner/test_codex_native_executor.py -q
uv run ruff check omnigent/inner/*native*.py omnigent/inner/native_prompt_delivery.py omnigent/native_server_harness.py tests/inner/test_native_system_prompt_delivery.py

# PR4
uv run pytest tests/inner/test_loader_executor_nested.py tests/runner/test_codex_native_model_from_spec.py -q

# PR3
uv run pytest tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries -q

# PR2 文档
rg -n "fix-core|fix-scale|若坚持|若使用|脚本可恢复|完整 fixed|set at session creation|prompt 已送达" docs ops scripts

跑不了测试就基于 diff 审查并写明限制。

## 纪律
- 不 merge、不打 Tag、不关上游 issue
- 不实现 Phase2 prompt apply / #2854 / #2539 / #2967 / Scale
- 区分：已证实 / mitigated(fail-loud) / 未复现 / 仅上游报告
- 不覆盖他人新提交；head 已变则先读新增 diff

## 输出格式（必须）
## 审查结论
- 总体：approve / approve-with-changes / request-changes
- PR #2：…
- PR #3：…
- PR #4：…
- PR #5：…

## 是否达到完成标准
- [ ] #3 可合并
- [ ] #4 可合并
- [ ] #5 fail-loud 正确且文档不误导，状态仍是 Phase1 mitigated
- [ ] #2 Tag 语义无双轨例外
- [ ] 四 PR open、未 merge、本轮未创建新 Tag（既有 v0.6.0-zhcn.1）

## 发现问题
- [P0/P1/P2] …

## 下一步（最多 3 条）
1. …
2. …
3. …
```
