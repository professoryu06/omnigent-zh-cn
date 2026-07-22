# Omnigent-zh-cn 修复与审查交接包

**用途：** 给**独立审查 agent / 人工审查者**使用。读完本文 + 四个 PR 的 diff 即可判断是否可合并。  
**生成时快照时间：** 2026-07-22  
**权威 head：** 以 `gh pr view N --json headRefOid` 为准（下表为生成时快照，会过期）。

---

## 1. 仓库与 PR 一览

| 资源 | URL |
|------|-----|
| 分发仓 | https://github.com/professoryu06/omnigent-zh-cn |
| 上游 | https://github.com/omnigent-ai/omnigent |
| PR #2 文档方案 | https://github.com/professoryu06/omnigent-zh-cn/pull/2 |
| PR #3 #3016 workspace | https://github.com/professoryu06/omnigent-zh-cn/pull/3 |
| PR #4 #2747/#2746 harness/model | https://github.com/professoryu06/omnigent-zh-cn/pull/4 |
| PR #5 #2853 fail-loud | https://github.com/professoryu06/omnigent-zh-cn/pull/5 |

### 生成时 head 快照（对照用）

| PR | 分支 | headOid（快照） | 审查方上次结论 | 本轮是否再改 |
|----|------|-----------------|----------------|--------------|
| #2 | `docs/fix-plans-core-secondary` | `b5601649bfbb486a697de7e3b1c6ba02624a9bec` | request-changes → 已改 Tag 语义 | 是（Tag 禁双轨） |
| #3 | `fix/core-workspace-3016` | `744e3a04a9b041b7bf3c2ae25cd22f96f5945038` | **approve** | **否** |
| #4 | `fix/core-spec-parse-2746-2747` | `30c04c3a173543f2802f3d8277a1660a616b393a` | **approve** | **否** |
| #5 | `fix/core-2853-native-prompt` | `1f42a898fbd07e358f87de5cba391a93af1f43b9` | request-changes → 已改 docstring | 是（docstring only） |

**状态：** 四个 PR 均 **OPEN**；**未 merge**；**本轮未创建新 Tag、未发版**（仓库已有既有 Tag v0.6.0-zhcn.1，创建于本轮 PR 之前）。

---

## 2. 问题与修复摘要（按功能）

### 2.1 #3016 — session workspace 投影缓存毒化（PR #3）

| 项 | 内容 |
|----|------|
| 用户可见 | 一次 snapshot 失败后，session 永久落在 runner 全局 cwd，worktree 隔离失效 |
| 根因 | `_session_workspace_cache` 缓存失败结果 `workspace=None`；reset 不清理 projection |
| 修复 | 仅成功 snapshot 才缓存；reset 驱逐 workspace + per-session fs registry |
| 证据 | test-first red/green；`tests/runner/test_session_workspace_cache.py` |
| 状态标签 | **根因已证实 + 修复 PR open（审查曾 approve）** |
| 残余风险 | 已在错误 cwd 启动的 harness 进程不会自动重建 |

### 2.2 #2747 / #2746 — YAML harness / codex model（PR #4）

| 项 | 内容 |
|----|------|
| 用户可见 | 声明 `codex-native` 被 model-prefix 换成 `openai-agents`；codex 忽略 `executor.model` |
| 修复 | loader 仅 alias `config.harness`；`_codex_native_model_from_spec` 优先 `executor.model` |
| 刻意未做 | nested `config.model` / `config.profile` alias（最小修改） |
| 证据 | 独立 test commits；硬断言 `harness_kind == "codex-native"` |
| 状态标签 | **根因已证实 + 修复 PR open（审查曾 approve）** |

### 2.3 #2853 — native system_prompt 静默丢弃（PR #5）

| 项 | 内容 |
|----|------|
| 用户可见 | native 角色 `prompt:` 静默丢失 |
| **Phase 1 实际交付** | **mitigated / fail-loud only** |
| 行为 | 非空且未 apply → warning（仅 `chars=N`，**无正文**）；`OMNIGENT_STRICT_PROMPT=1` → 注入前 `ExecutorError` |
| **未交付** | prompt **apply / 送达** native CLI（Phase 2 开放） |
| Strict | **仅**环境变量 `OMNIGENT_STRICT_PROMPT`；无 per-agent YAML 字段 |
| 覆盖路径 | antigravity, claude, codex, cursor, goose, hermes, kimi, kiro, pi, qwen, NativeServerHarness(opencode) |
| 最近整改 | docstring 去掉「ignored — set at session creation」等误导，改为 Phase-1 fail-loud 语义 |
| 状态标签 | **根因已证实；fail-loud 缓解已实现；apply 未实现** — **不得**标完整 fixed / 关上游 issue |

### 2.4 文档与版本语义（PR #2）

| 项 | 内容 |
|----|------|
| 优先级 | 首批待复现核心候选（非「唯一 backlog」）；P0 #2853/#3016 等 |
| Tag | **唯一** `v0.6.0-zhcn.N` 单调序列；`fix-core.N`/`fix-scale.N` **已废弃、禁止**（无「若坚持」例外） |
| #3012 | 跟踪上游 #3013；L0=诊断+人工 login；**不**承诺脚本无人值守恢复 |
| #2853 文档 | mitigated/fail-loud Phase1 vs Phase2 capture double apply |

---

## 3. 关键文件索引

| 路径 | 说明 |
|------|------|
| [REVIEW_PROMPT.md](./REVIEW_PROMPT.md) | **给审查 agent 的可复制提示词** |
| [README.md](./README.md) | 方案总览 |
| [CORE_FIX_PLANS.md](./CORE_FIX_PLANS.md) | 核心候选方案 |
| [SECONDARY_FIX_PLANS.md](./SECONDARY_FIX_PLANS.md) | #3012 / Scale |
| [STATUS.md](./STATUS.md) | 状态跟踪表 |
| [../../ops/versioning/BRANCHING.md](../../ops/versioning/BRANCHING.md) | 分支/Tag 约定 |
| [../../scripts/repro/matrix-core.md](../../scripts/repro/matrix-core.md) | 可运行矩阵规格 |
| [../AGENT_HANDOFF_omnigent_issues_and_fix_plans.md](../AGENT_HANDOFF_omnigent_issues_and_fix_plans.md) | 早期交接包（历史；以 STATUS + 本文件为准） |

---

## 4. 建议验证命令（审查方）

```bash
# 刷新 head
gh pr view 2 --json headRefOid,state,url
gh pr view 3 --json headRefOid,state,url
gh pr view 4 --json headRefOid,state,url
gh pr view 5 --json headRefOid,state,url

# PR #5（checkout fix/core-2853-native-prompt）
uv run pytest tests/inner/test_native_system_prompt_delivery.py \
  tests/inner/test_claude_native_executor.py \
  tests/inner/test_codex_native_executor.py -q
# 期望：约 57 passed（或当前最新总数全绿）

uv run ruff check omnigent/inner/*native*.py \
  omnigent/inner/native_prompt_delivery.py \
  omnigent/native_server_harness.py \
  tests/inner/test_native_system_prompt_delivery.py

# PR #4
uv run pytest tests/inner/test_loader_executor_nested.py \
  tests/runner/test_codex_native_model_from_spec.py -q

# PR #3
uv run pytest tests/runner/test_session_workspace_cache.py \
  tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries -q

# PR #2 文档漂移抽查
rg -n "fix-core|fix-scale|若坚持|脚本可恢复|完整 fixed|set at session creation|prompt 已送达" docs ops scripts
```

**执行方最近复跑（PR #5 docstring 修订后）：** 57 passed；ruff clean。  
**未跑：** 全仓 pytest。

---

## 5. 完成标准对照（审查用 checklist）

- [ ] PR #3：逻辑正确、测试红绿、无无关改动 → 可 merge（需维护者操作）
- [ ] PR #4：harness 硬断言、无多余 nested model/profile → 可 merge
- [ ] PR #5：fail-loud 正确；docstring 不声称已送达；日志无 prompt 正文；状态仍是 mitigated Phase1
- [ ] PR #2：Tag 仅 `v0.6.0-zhcn.N`；无双轨例外；#3012/#2853 措辞正确
- [ ] 四 PR 仍 open；本轮未创建新 Tag（既有 v0.6.0-zhcn.1）；无 prompt apply 实现

---

## 6. 明确未做

| 项 | 状态 |
|----|------|
| #2853 Phase2 safe apply | 未做 |
| #2854 harness_override kickoff | 未复现/未修 |
| #2539 named 子会话 | 未复现/未修 |
| #2967 auto-compact | 未复现/未修 |
| #3012 JWT refresh | 跟踪上游 #3013，未在 zh-cn 重复实现 |
| Scale #3003/#3004/#2702/#3001 | 延后 |
| merge / 新 Tag / 发版 | 禁止由执行 agent 代做（仓库既有 v0.6.0-zhcn.1 与本轮无关） |

---

## 7. 推荐合并顺序（供维护者，非执行 agent）

1. **PR #3**（#3016）— 隔离正确性，证据完整  
2. **PR #4**（#2747/#2746）— 路由正确性  
3. **PR #5**（#2853 Phase1）— 诊断缓解；合并时 release note 写清 **非**完整送达  
4. **PR #2**（文档）— 可与功能 PR 并行或最后合，避免文档与代码状态漂移  

---

*「已修复」仅当：预修复失败测试 + 修复后通过 + 已合并发布。fail-loud ≠ prompt 已送达。*
