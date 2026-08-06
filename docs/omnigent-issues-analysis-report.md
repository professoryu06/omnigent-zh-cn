# Omnigent GitHub Issues 分析报告

**分析目标：** 从 [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent/issues) 仓库的 issues 中，筛选出对 AgentCenter 项目（Omnigent-zh-cn + agentpeihe 双机部署、多厂商 AI CLI 编排）有价值的 bug 和功能优化项。

**分析方法：** 多 agent 协作分析 + 交叉验证。
- 第一阶段：3 个分析 agent 分别从 bug、feature/性能优化、战略契合三个角度并行分析 100 条 issues。
- 第二阶段：23 个验证 agent 对每个候选 issue 进行 skeptical review，判断 keep/lower/drop。
- 第三阶段：1 个综合 agent 输出优先级结论。

**数据基础：** 通过 `gh issue list --repo omnigent-ai/omnigent --limit 100 --state all` 获取，共 100 条 issues（75 open / 25 closed），时间截至 2026-07-22。

**用户场景：**
- 部署 Omnigent-zh-cn 在 macOS M1 + Windows WSL2
- 使用 agentpeihe 关卡协议编排多 agent
- 角色：Controller（诸葛丞相）、Executor（关二爷）、Reviewer（法正）
- 目标 harness：claude-sdk、claude-native、codex-native、kimi-native、qwen-native、hermes-native、pi

---

## 一、分析方法论

### 1.1 候选 issue 来源

从 100 条 issues 中，按以下标签和关键词初步筛选：
- **Bug 类**：`Bug`、`P0-critical`、`P1-high`、`P2-medium`
- **Feature/性能类**：`enhancement`、`Performance`、`help wanted`
- **战略契合类**：`comp:harnesses`、`comp:runner`、`comp:server`、`comp:policies`、`comp:web-ui`

### 1.2 验证标准

每个候选 issue 经过独立验证 agent 审查：
1. issue 标题/编号与推荐理由是否一致
2. 优先级是否与标签、状态、讨论质量匹配
3. 是否 genuinely 影响 Omnigent-zh-cn + agentpeihe 多 agent 编排
4. 是否存在 red flags（stale、duplicate、needs-info、已关闭无复现等）

### 1.3 优先级定义

| 优先级 | 含义 |
|--------|------|
| critical | 会导致核心功能完全不可用，无 workaround |
| high | 显著影响部署稳定性或性能，有 workaround 但成本高 |
| medium | 有价值但可暂缓，或方向未完全定型 |
| low | 影响面窄或有明确绕过，建议仅 watch |

---

## 二、最值得跟进的问题（按类别分组）

### 2.1 会话隔离与持久化可靠性

这一类问题直接影响多 agent 并发时的工作区隔离、会话生命周期和长时间运行的稳定性。

#### #3016 [Bug] A transient session-snapshot failure permanently pins a session to the global runner workspace

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:runner`、`triaged`
- **核心问题**：一次失败的 `_session_snapshot` 会导致 `workspace=None` 被永久缓存到 `_session_workspace_cache`。由于 harness env 在首次 spawn 时就被 bake，后续所有 harness（pi、claude-sdk、native）都会在 runner 的全局 cwd 中启动，而不是在 session 的 git-worktree 中。
- **为什么跟进**：
  - 直接破坏多 agent fan-out 的工作区隔离
  - 缓存中毒后无法通过 agent reset 恢复，只能删除 session
  - 影响所有 harness 类型
- **对 AgentCenter 的影响**：gate 各阶段（如 Executor 写代码、Reviewer 复核）可能污染同一目录，导致文件冲突或错误结果。
- **red flags**：无
- **建议优先级**：high

#### #3012 Hosts authenticated via `omnigent login` permanently 403 on first reconnect after session-JWT expiry (default 8h) — no renewal path

- **状态**：OPEN，标签 `P1-high`、`comp:server`、`triaged`
- **核心问题**：通过 `omnigent login` 认证的主机，session JWT（默认 8 小时）过期后，任何 reconnect（pod 重启、网络抖动）都会返回 403，且没有自动续期路径，必须人工重新运行 `omnigent login`。
- **为什么跟进**：
  - 无人值守部署会在 8 小时后永久断线
  - 这是跨机器协作（Phase 2）的基础设施风险
- **对 AgentCenter 的影响**：如果未来用 NAS/云服务器做中央 Server，host runner 长期运行必然遇到此问题。
- **red flags**：无
- **建议优先级**：high

#### #2967 [Bug] A full context window bricks a session with "Prompt is too long" — the harness turn path never auto-compacts

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:runner`、`comp:harnesses`、`triaged`
- **核心问题**：harness turn 路径每次都会重放完整历史，没有 proactive compaction。上下文窗口满后，每一 turn 都会失败，只能换模型或重建 session。
- **为什么跟进**：
  - 长 agent 会话（agentpeihe gate 协议常见）会永久卡住
  - claude-sdk 路径明确受影响
- **对 AgentCenter 的影响**：复杂任务的多轮 gate 执行会因上下文过长而中断。
- **red flags**：无
- **建议优先级**：high

---

### 2.2 Native Harness 路由与 Prompt 下发正确性

这一类问题直接影响 Controller/Executor/Reviewer 角色的正确性和安全性。

#### #2853 [Bug] Native harnesses silently drop the agent spec `prompt:` at runtime

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:harnesses`、`triaged`
- **核心问题**：native harness（claude-native、codex-native、cursor-native、hermes-native、opencode-native 等）在运行时会直接 `del` 掉 agent spec 的 `prompt:` / `system_prompt`，而 SDK 路径和 pi harness 会正常下发，且无任何报错或警告。
- **为什么跟进**：
  - Controller/Executor/Reviewer 的角色指令依赖 per-role prompt
  - prompt 被静默丢弃会导致 gate 协议指令无法到达 agent，行为不可控
- **对 AgentCenter 的影响**：使用 native harness 的角色会完全丢失身份定义和安全约束。
- **red flags**：
  - `pi` 不是 native harness，不应与 claude-native 等混为一谈
  - 存在 workaround：改用 SDK harness 或非 native harness
- **建议优先级**：high（原分析误标 critical，验证后降为 high）

#### #2854 [Bug] Cross-harness `harness_override` is ignored on the `initial_items` kickoff turn

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:harnesses`、`triaged`
- **核心问题**：创建 session 时如果同时带 cross-harness override 和 `initial_items`，kickoff turn 会执行原始 harness，而 snapshot 和后续 turns 执行 override。两个 harness 同时为一个 session 活跃。
- **为什么跟进**：
  - 破坏 per-step harness 保证
  - agentpeihe gate 协议依赖不同阶段使用不同 harness
- **对 AgentCenter 的影响**：gate 阶段切换 harness 时，首 turn 会跑错模型。
- **red flags**：
  - 存在 workaround：先创建空 session 再发第一条消息
  - 描述中有两个竞争性的根因假设，fix point 需验证
- **建议优先级**：high

#### #2747 [Bug] Single-file agent YAML silently ignores executor.type/config nesting

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:repr`、`comp:harnesses`、`triaged`
- **核心问题**：单文件 agent YAML 中声明的 `executor.type` / `executor.config.harness` 被静默忽略，harness 由模型前缀推断（`_HARNESS_FOR_MODEL_PREFIX`）。
- **为什么跟进**：
  - AgentCenter 可能用单文件 YAML 定义角色
  - `kimi-native` / `qwen-native` 等角色可能被错误路由到 openai-agents 或 claude-sdk
- **对 AgentCenter 的影响**：角色 harness 声明失效，模型能力和工具面不一致。
- **red flags**：无
- **建议优先级**：high

#### #2746 [Bug] Native launches disagree on where the spec model lives

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:harnesses`、`triaged`
- **核心问题**：codex-native 从 `executor.config.model` 而非 `executor.model` 读取模型，导致单文件 agent 声明的模型被静默替换为 provider 默认模型。
- **为什么跟进**：
  - 与 #2747 同属于 native harness 对 spec 的解析不一致
  - 破坏 Executor/Reviewer 的模型固定策略
- **对 AgentCenter 的影响**：Reviewer 可能实际跑在不同模型上，异厂商复核纪律失效。
- **red flags**：无
- **建议优先级**：high

#### #2575 pi-native: non-Claude Databricks models (GLM, Gemini, …) hang

- **状态**：OPEN，标签 `P1-high`、`comp:harnesses`，已有 fix PR #2833
- **核心问题**：pi-native 的 provider 被硬编码为 Anthropic surface，非 Claude 的 Databricks 模型（GLM、Gemini 等）会被发到错误 API 端点，导致 turn 永久挂起。
- **为什么跟进**：
  - AgentCenter 目标 harness 之一
  - 影响多厂商模型接入
- **对 AgentCenter 的影响**：GLM/Gemini 等模型通过 pi-native 无法使用。
- **red flags**：无
- **建议优先级**：high

#### #2539 Named sys_session_send returns 404 after first child from a bundled session-scoped agent

- **状态**：OPEN，标签 `P1-high`、`comp:runner`、`triaged`
- **核心问题**：从 bundled session-scoped agent 使用 named `sys_session_send` 创建第一个子会话成功后，后续所有 named 子会话都会返回 404。根因是 `SqlAlchemyAgentStore._session_id_for_agent()` 使用无序 `LIMIT 1`，破坏了单所有者假设。
- **为什么跟进**：
  - gate 协议可能用 named `sys_session_send` 创建 Controller/Executor/Reviewer 子会话
  - 直接破坏多 agent 创建能力
- **对 AgentCenter 的影响**：无法可靠创建多个子 agent。
- **red flags**：无
- **建议优先级**：high

---

### 2.3 Fan-out 下的性能瓶颈

这一类问题在多 agent 并发时会被放大，直接影响系统吞吐和响应延迟。

#### #3003 [Performance] Policy engine rebuilt per evaluation

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:policies`、`comp:server`、`triaged`
- **核心问题**：每次策略评估都会重建 `build_policy_engine`，重新加载 conversation 状态 4-5 次，包含两次 `_load_tree_conversations` 全树扫描。claude-native 上每个 tool call 阻塞约 1s。
- **为什么跟进**：
  - agentpeihe gate 协议可能用 policy verdict 作为 gate 条件
  - 每个 tool call 都付高额延迟
- **对 AgentCenter 的影响**：gate 执行变慢，复杂任务延迟累积。
- **red flags**：仅 1 天新 issue，维护者尚未回应
- **建议优先级**：high

#### #3004 [Performance] Every streamed event re-loads conversation + ACL

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:server`、`triaged`
- **核心问题**：每个 streamed event POST 都会重新加载 conversation metadata、labels 和 ACL，产生 16.4 次查询和 9.7 次 pool checkout。单 turn 可达 ~13k 查询。
- **为什么跟进**：
  - fan-out + 流式状态更新会放大这个问题
  - 直接压垮 runner/DB
- **对 AgentCenter 的影响**：多 agent 同时运行时 server 可能成为瓶颈。
- **red flags**：无
- **建议优先级**：high

#### #2702 Native idle-detection fork+exec's tmux capture-pane at 5 Hz per terminal

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:runner`、`comp:harnesses`、`triaged`
- **核心问题**：每个 native terminal 都会为 idle detection 反复 fork/exec `tmux capture-pane`。多 terminal fan-out 下会成为 runner 系统时间主导者（实测 16 idle-watcher threads 占 ~20.6% CPU）。
- **为什么跟进**：
  - 直接相关于 tmux + native harness + 多 agent 并发
  - 作者后续修正为 1 Hz per terminal，但开销仍然显著
- **对 AgentCenter 的影响**：并发 agent 越多，runner 开销越大。
- **red flags**：标题写 5 Hz，实际为 1 Hz per terminal
- **建议优先级**：high

#### #3001 [Performance] GET /v1/sessions pre-fetches every accessible conversation id per request

- **状态**：OPEN，标签 `P1-high`、`Bug`、`comp:server`、`triaged`
- **核心问题**：sessions list 是核心 Web UI 可观测性接口，但每次都预取所有可访问 conversation id，固定 ~230ms 开销，与 page size 无关。
- **为什么跟进**：
  - agent 越多会话越多，sidebar/dashboard 越慢
- **对 AgentCenter 的影响**：Web UI 可观测性下降。
- **red flags**：无
- **建议优先级**：high

---

### 2.4 中优先级观望项

这些问题有价值，但要么方向未定型，要么影响面较窄，要么已有 workaround。

| Issue | 理由 | 观望原因 |
|-------|------|---------|
| [#2856](https://github.com/omnigent-ai/omnigent/issues/2856) | Pi extension 的 AskUserQuestion/权限提示未被 Omnigent 透传 | 仅标记 enhancement；推荐理由中 agentpeihe gate 场景是推断 |
| [#2756](https://github.com/omnigent-ai/omnigent/issues/2756) | 暴露原子的 session-event 入队决策接口 | 标记 experimental，API 可能变动 |
| [#2849](https://github.com/omnigent-ai/omnigent/issues/2849) | Web UI 切换会话每次都全量回填 transcript | 体验摩擦，非阻塞 |
| [#2754](https://github.com/omnigent-ai/omnigent/issues/2754) | turn-scoped 流式 API | 维护者尚未确认方向 |
| [#2644](https://github.com/omnigent-ai/omnigent/issues/2644) | 确定性 PASS/FAIL 质量门设计讨论 | #2598 已提供原语，这里只是控制流接入 |
| [#2629](https://github.com/omnigent-ai/omnigent/issues/2629) | web_fetch 子 agent spawn 因 harness 回退崩溃 | 有人称 PR #1725 已修复，待确认 |

---

## 三、验证过程中被降级或剔除的问题

### 3.1 被剔除的 issue

| Issue | 原推荐 | 验证结论 | 原因 |
|-------|--------|---------|------|
| #2590 | Feature，medium | drop | issue 已关闭，无 comments，大概率 not-planned/duplicate |
| #2890 | Feature，medium | drop | issue 已关闭，无 comments 说明原因，无关联 PR |

### 3.2 被降级的 issue

| Issue | 原推荐 | 验证结论 | 原因 |
|-------|--------|---------|------|
| #2853 | critical | high | 仓库标签为 P1-high 非 critical，且存在改用 SDK harness 的 workaround |
| #2629 | high | medium | 有人声称 PR #1725 已修复， reporter 7 天未确认 |

---

## 四、对 AgentCenter 项目的影响评估

### 4.1 当前部署（Phase 1）最可能踩到的坑

1. **#2853 native harness 丢弃 prompt**：如果 Controller/Executor/Reviewer 使用 native harness，角色指令会失效。
2. **#2747 / #2746 单文件 YAML 解析不一致**：模型和 harness 被错误推断/替换。
3. **#2904 claude-native tmux read-only**：聊天注入失败，需要 workaround。
4. **#2967 上下文窗口满后卡住**：长 gate 会话会中断。

### 4.2 未来扩展（Phase 2）最需要关注的基础设施问题

1. **#3012 host JWT 过期后 403**：跨机器部署的无人值守 runner 会掉线。
2. **#3016 session workspace 污染**：多 agent fan-out 的工作区隔离失效。
3. **#3003 / #3004 / #2702 性能瓶颈**：agent 数量增加后 server/runner 会被压垮。

---

## 五、行动建议

### 5.1 立即订阅（高优先级，可能爆炸）

- #3016、#3012、#2967、#2854、#2853、#3003、#3004

### 5.2 测试环境验证

- 多 agent fan-out 下是否会触发 #3016 工作区污染
- 单文件 YAML 角色是否会触发 #2747 / #2746 错误路由
- native harness 角色是否触发 #2853 prompt 丢失

### 5.3 生产部署兜底

- 针对 #3012：设定 8h 内人工或脚本化重新登录流程
- 针对 #2967：准备长会话触发后的应急预案（换模型/重建 session）

### 5.4 暂缓投入

- #2629、#2744、#2644、#2754 只 watch，不主动推进

---

## 六、数据附录

### 6.1 100 条 issues 的标签分布

| 标签 | 数量 |
|------|------|
| triaged | 94 |
| Bug | 64 |
| P2-medium | 43 |
| P1-high | 43 |
| comp:harnesses | 43 |
| comp:server | 36 |
| help wanted | 34 |
| enhancement | 31 |
| comp:runner | 30 |
| comp:web-ui | 21 |
| comp:infra | 11 |
| comp:tui | 10 |
| P3-low | 6 |
| comp:policies | 6 |
| comp:repr | 6 |
| needs-triage | 4 |
| P0-critical | 1 |
| documentation | 1 |

### 6.2 数据来源命令

```bash
gh issue list --repo omnigent-ai/omnigent --limit 100 --state all \
  --json number,title,state,labels,comments,author,createdAt,updatedAt,body,reactionGroups,url \
  > /tmp/omnigent_issues.json
```

### 6.3 Workflow 统计

- 分析 agent 数：3（bug / feature / strategic）
- 验证 agent 数：23
- 综合 agent 数：1
- 总 agent 数：27
- 总 token 消耗：~658k
- 总 tool 调用：136

---

*报告生成时间：2026-07-22*
*分析范围：omnigent-ai/omnigent 前 100 条 issues（按 GitHub 默认排序）*
