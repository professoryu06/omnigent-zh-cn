# Agent 交接审查包：Omnigent 问题分析 + 修复方案 + 当前状态

**文档用途：** 给**另一个 agent / 审查者**独立判断用。读完本文即可理解：问题从哪来、哪些是核心/次要、怎么修、Git 怎么管、现在做到哪一步。  
**请审查者：** 用怀疑态度核对优先级、方案可行性、版本管理是否合理；可指出遗漏、误判、过度工程。  
**生成日期：** 2026-07-22  
**编写方：** 基于用户提供的分析报告 + 本地 Omnigent 环境排查 + 第一性原理重排 + 修复/版本管理方案落地

---

## 0. 一页纸：现在是什么情况

| 项 | 现状 |
|----|------|
| 业务目标 | AgentCenter 场景：Omnigent-zh-cn + agentpeihe 多 agent 编排（Controller/Executor/Reviewer），目标 harness 含 claude-sdk/native、codex/kimi/qwen/hermes/pi 等 |
| 上游项目 | [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent)（Python agent 框架 / meta-harness） |
| 本方分发仓 | [professoryu06/omnigent-zh-cn](https://github.com/professoryu06/omnigent-zh-cn)（完整源码中文分发，见 `UPSTREAM.md`） |
| 本机运行时 | `omnigent 0.6.0.dev0`（built 2026-07-14）；配置在 `~/.omnigent/config.yaml`（单 host + ACP Grok Code） |
| 已完成 | ① 上游 issue 筛选分析报告；② 核心/次要第一性原理重排；③ 分层修复方案（L0/L1/L2）；④ Git 分支/tag/PR 约定；⑤ 文档已 push 并开 PR |
| **未完成** | **尚未改任何 Omnigent 功能代码**；未跑核心 issue 复现矩阵；未打 `fix-core` / `fix-scale` 发布 tag |
| 文档 PR | https://github.com/professoryu06/omnigent-zh-cn/pull/2 |
| 文档分支 | `docs/fix-plans-core-secondary` @ `3923598` |
| 本地工作副本 | `C:\Users\Administrator\omnigent-zh-cn` |
| 用户原始报告路径 | `E:\雄\个人\vibe coding\omnigent\修复test\omnigent-issues-analysis-report.md`（已同步进仓 `docs/omnigent-issues-analysis-report.md`） |

**审查焦点建议：**

1. 核心 7 项是否真的都是「正确性」？有没有该降级/升级的？  
2. L0/L1/L2 分层是否适合 zh-cn fork 的维护能力？  
3. 实施顺序是否合理？  
4. 版本管理是否过重或过轻？  
5. 有没有和官方已有 PR 重复（尤其 #3012 称有实现进行中、#2575 有 fix PR #2833）？

---

## 1. 用户场景与约束（审查时勿脱离）

### 1.1 部署与角色

- 部署：Omnigent-zh-cn 在 macOS M1 + Windows WSL2（规划）；当前本机 Windows 已有 local server/host 痕迹  
- 编排：agentpeihe 关卡协议；角色示例 — Controller（诸葛）、Executor（关二）、Reviewer（法正）  
- 目标 harness：`claude-sdk`、`claude-native`、`codex-native`、`kimi-native`、`qwen-native`、`hermes-native`、`pi`  

### 1.2 本机实测片段（非完整复现）

- CLI：`C:\Users\Administrator\.local\bin\omnigent.exe` → `0.6.0.dev0`  
- `~/.omnigent/config.yaml`：单 host `DESKTOP-OLIHSDP`，ACP 注册 Grok Code  
- 有 `chat.db`、多 agent artifacts、server/runner/host 日志；**未**在日志中系统完成「报告内每个 issue」的实证复现  
- **因此：当前结论以 GitHub issue 质量 + 场景契合度为主，本地仅作环境上下文，不是「已确认全中招」**

### 1.3 仓库边界

- `professoryu06/omnigent-zh-cn`：完整源码发行，包名/CLI 为 `omnigent-zh-cn` / `omnigent-zh` / `omni-zh`，不覆盖官方命令  
- 上游同步：**人工**（`upstream-watch` 只开 Issue 提醒，不自动 merge）  
- 用户曾提到 `shankinchina-dotcom/agentcenter` 与 commit `69e91a5`；**当前 gh 登录账号 `professoryu06` 下无法解析该仓库**。本交接以 **omnigent-zh-cn** 为版本管理主仓

---

## 2. 原始分析报告摘要（用户已写好的资料）

**完整原文：** [docs/omnigent-issues-analysis-report.md](./omnigent-issues-analysis-report.md)

### 2.1 方法论

- 数据：`gh issue list --repo omnigent-ai/omnigent --limit 100 --state all`（75 open / 25 closed，截至 2026-07-22）  
- 三阶段：3 分析 agent（bug / feature·性能 / 战略）→ 23 验证 agent skeptical review → 1 综合  
- 优先级定义：critical / high / medium / low（见原报告 §1.3）

### 2.2 报告推荐跟进（原分组）

**2.1 会话隔离与持久化**

| Issue | 报告要点 | 建议优先级 |
|-------|----------|------------|
| #3016 | snapshot 失败把 `workspace=None` 永久缓存 → harness 落全局 cwd | high |
| #3012 | login JWT 默认 8h 过期后 reconnect 永久 403，无续期 | high |
| #2967 | 上下文满无 auto-compact，session 砖死 | high |

**2.2 Native 路由与 Prompt**

| Issue | 报告要点 | 建议优先级 |
|-------|----------|------------|
| #2853 | native 静默 `del` 掉 spec `prompt:` | high（曾误标 critical） |
| #2854 | `harness_override` 在 kickoff+initial_items 时首 turn 忽略 | high |
| #2747 | 单文件 YAML 忽略 executor.type/config harness | high |
| #2746 | codex-native model 字段路径不一致 | high |
| #2575 | pi-native 非 Claude Databricks 模型挂起；有 PR #2833 | high |
| #2539 | named `sys_session_send` 第二子会话 404（LIMIT 1 无序） | high |

**2.3 Fan-out 性能**

| Issue | 报告要点 |
|-------|----------|
| #3003 | policy engine 每次评估重建，tool call ~1s |
| #3004 | 每 stream event 重载 conversation+ACL，单 turn ~13k 查询 |
| #2702 | native idle tmux capture 高频，fan-out CPU 高 |
| #3001 | sessions list 预取全部 conversation id，固定 ~230ms |

**2.4 中优观望：** #2856 #2756 #2849 #2754 #2644 #2629  

**剔除：** #2590 #2890（closed）  
**降级：** #2853 critical→high；#2629 high→medium  

### 2.3 报告行动建议（原 §5）

- 立即订阅：#3016 #3012 #2967 #2854 #2853 #3003 #3004  
- 测试验证：fan-out 工作区、YAML 路由、native prompt  
- 生产兜底：#3012 8h 重登；#2967 换模型/重建 session  
- 暂缓：#2629 #2744 #2644 #2754  

### 2.4 抽查时 issue 状态（2026-07-22）

报告所列关键号（含 #2904）经 `gh api` 抽查：**仍全部 open**。  
#2904：claude-native Web 输入 tmux read-only（报告 4.1 提到，原主列表在性能/观望外）。

---

## 3. 第一性原理重排（后续讨论用的「核心 vs 次要」）

> 不按 GitHub 标签 P1 一刀切，而按 AgentCenter 编排是否**逻辑可信**。

### 3.1 五条不可违背约束

| ID | 约束 | 失效表现 |
|----|------|----------|
| C1 | 身份正确 — 角色 prompt 到达模型 | 角色行为漂移，且可能无报错 |
| C2 | 路由正确 — harness/model 按 spec | 跑错模型/工具面 |
| C3 | 工作区隔离 — session 不共享污染 cwd | 文件互踩，gate 结果不可信 |
| C4 | 会话可延续 — 长上下文/长在线 | 复杂 gate 中途死 |
| C5 | 子 agent 可组合 — named spawn 可靠 | 多角色 fan-out 断链 |

### 3.2 分层结论

#### 核心 Core（正确性 — 结果可能是错的）

| Issue | 约束 | 为何核心 | 静默/硬失败 |
|-------|------|----------|-------------|
| **#2853** | C1 | native 角色说明书被扔 | **静默**（最危险） |
| **#2747** | C2 | YAML harness 声明失效 | 静默 |
| **#2746** | C2 | model 被默认顶掉 | 静默 |
| **#2854** | C2 | 首 turn 跑错 harness | 可感知分裂 |
| **#3016** | C3 | 工作区毒化，reset 难救 | 行为错 |
| **#2539** | C5 | 第二 named 子会话 404 | 硬失败 |
| **#2967** | C4 | 长会话永久 Prompt too long | 硬失败 |

#### 次重要 Scale（跑得难受 — 规模/长跑才爆）

| Issue | 性质 | 何时升 Core |
|-------|------|-------------|
| **#3012** | host JWT 无续期 | 双机/无人值守长跑上线时 |
| **#3004** | stream 查库放大 | 多 agent fan-out 压 server |
| **#3003** | policy 每评重建 | gate 强依赖 policy 时 |
| **#2702** | idle tmux CPU | 多 native terminal |
| **#3001** | UI 列表慢 | 会话量大时 |

#### 备用 Backup

#2856 #2756 #2849 #2754 #2644 #2629；#2575（仅 pi+非 Claude 路径）；#2904（仅 claude-native Web 注入）

### 3.3 依赖顺序（修/验）

```text
C1 #2853 → C2 #2747+#2746 → #2854
    → C3 #3016 → C5 #2539
    → C4 #2967
    → Scale #3012 → #3004/#3003 → #2702 → #3001
```

**反模式：** 先抠性能（#3003/#3004），但 native prompt 仍静默丢失。

### 3.4 大白话效果对照（给非代码审查者）

| 现象 | 多半是 | 档 |
|------|--------|----|
| 角色不听话且不报错 | #2853 | 核心 |
| 模型和预期不一致 | #2747/#2746 | 核心 |
| 多 agent 改乱同一目录 | #3016 | 核心 |
| 第二个子 agent 建失败 | #2539 | 核心 |
| 长任务突然全失败 | #2967 | 核心 |
| 换 harness 第一步怪 | #2854 | 核心 |
| 跑久/重启后一直 403 | #3012 | 次要 |
| 一并发就卡、CPU 高 | #3003/#3004/#2702 | 次要 |
| 侧边栏列表钝 | #3001 | 次要/体验 |

---

## 4. 修复方案总纲（功能向，非只贴 issue）

**完整分册：**

- [docs/fixes/README.md](./fixes/README.md) — 总览  
- [docs/fixes/CORE_FIX_PLANS.md](./fixes/CORE_FIX_PLANS.md) — 核心 A/B/C  
- [docs/fixes/SECONDARY_FIX_PLANS.md](./fixes/SECONDARY_FIX_PLANS.md) — 次要 A/B/C  
- [docs/fixes/STATUS.md](./fixes/STATUS.md) — 跟踪表  

### 4.1 三层修法（每个 issue 都适用）

| 层 | 名称 | 含义 | 落点 |
|----|------|------|------|
| **A / L0** | 止血 | 配置、脚本、角色 YAML、运维定时；不改内核 | `ops/*` |
| **B / L1** | 功能补丁 | 在 zh-cn 源码修功能 + 测试 | `fix/*` 分支 → tag `v*-zhcn.fix-*` |
| **C / L2** | 上游贡献 | PR 到 omnigent-ai/omnigent，再 sync 回 zh-cn | `upstream-pr/*` |

**原则：** 核心优先 B（A 临时）；次要先 A，再按需 B/C。禁止在 `main` 直推功能。

### 4.2 核心问题 — 方案一览

#### #2853 Native 丢 `prompt:`

| 方案 | 内容 |
|------|------|
| **A** | 关键角色改 `claude-sdk`/非 native；纪律写入 gate 文件 / 首条消息 |
| **B（推荐）** | 各 native 启动注入 system/append prompt；不支持则 WARNING 或 `strict_prompt` fail-fast |
| **C** | 统一 `HarnessPromptDelivery`；文档 + polly 全 harness 一致 |
| 分支 | `fix/core-2853-native-prompt` |
| 锚点（issue） | `*_native_executor.py` del system_prompt；对比 `claude_sdk_executor` / pi |

#### #2747 + #2746 YAML harness/model 解析

| 方案 | 内容 |
|------|------|
| **A** | 目录式 agent；模型名与 harness 前缀临时对齐 |
| **B（推荐）** | 优先级：`executor.config.harness` > `executor.type` > 前缀推断；model 字段归一 |
| **C** | 更新 `AGENT_YAML_SPEC`；推断覆盖打 warning |
| 分支 | `fix/core-spec-parse-2746-2747`（两 issue 同分支） |

#### #2854 harness_override 忽略 kickoff

| 方案 | 内容 |
|------|------|
| **A** | 先空 session 再发首消息；编排层封装 `create_session_then_kickoff()` |
| **B（推荐）** | kickoff 选 harness **先读 override**，与 snapshot/后续 turn 同源 |
| **C** | API 契约写死 + OpenAPI |
| 分支 | `fix/core-harness-override-2854` |

#### #3016 workspace 缓存毒化

| 方案 | 内容 |
|------|------|
| **A** | cwd 异常 → 删 session；避免 server 抖动时狂刷 filesystem API |
| **B（推荐）** | 仅成功且 workspace 非空才缓存；reset 驱逐投影缓存；修正 register/resolve 顺序 |
| **C** | 缓存分层 invalidation 文档化 |
| 分支 | `fix/core-workspace-3016` |
| 锚点 | `runner/app.py`：`_session_workspace_cache` 无条件写入 |

#### #2539 named 子会话 404

| 方案 | 内容 |
|------|------|
| **A** | 少用 named；顶层多 session 外拼 |
| **B（推荐）** | `_session_id_for_agent` 稳定键（owner+name），禁无序 LIMIT 1 |
| **C** | 数据模型 1:1 / 1:N 约束 + 迁移 |
| 分支 | `fix/core-child-session-2539` |

#### #2967 无 auto-compact

| 方案 | 内容 |
|------|------|
| **A** | N 轮强制新 session + 摘要；拆关卡；大窗口模型 |
| **B（推荐）** | turn 前估算 token，proactive compact；失败返回可恢复状态 |
| **C** | 可配置 compaction 模式；UI 显示 compact 事件 |
| 分支 | `fix/core-compact-2967` |

### 4.3 次要问题 — 方案一览

#### #3012 JWT 过期 403

| 方案 | 内容 |
|------|------|
| **A（先做）** | TTL-1h 定时 re-login；403 排障先查过期（`ops/host-relogin/`） |
| **B** | 存 refresh；host reconnect 刷新（对齐 device-auth / managed mint） |
| **C** | login 默认 device-auth+refresh；错误文案区分 expired |
| 注意 | issue 称实现进行中 — **先 watch 上游，避免重复** |
| 分支 | `ops/host-jwt-relogin` → `fix/scale-jwt-renew-3012` |

#### #3004 / #3003 / #2702 / #3001

| Issue | A | B |
|-------|---|---|
| #3004 | 限并行 | turn 内缓存 conversation+ACL |
| #3003 | 减少 policy 热路径 | 复用 policy engine |
| #2702 | 少开 native terminal | 降频/批处理 capture |
| #3001 | 清理会话 | 列表分页、去掉全量 id 预取 |

**节奏：** 先 #3012 L0 → 核心 `fix-core.N` 后 → #3004/#3003 → #2702 → #3001。  
Tag：`v*-zhcn.fix-scale.N`

### 4.4 运维兜底速查（上游未修前）

| 风险 | 兜底 |
|------|------|
| #2853/#2747/#2746 | 关键角色优先 SDK；校验 launch 日志中的 harness/model |
| #2854 | 先空 session 再 kickoff |
| #3016 | 删 session 重建，勿指望 agent reset |
| #2967 | 换窗口/新 session 续跑 |
| #3012 | 7h 级 re-login |

---

## 5. Git / GitHub 版本管理约定

**全文：** [ops/versioning/BRANCHING.md](../ops/versioning/BRANCHING.md)

### 5.1 分支

```text
main                              # 仅 PR 合并
docs/fix-plans-core-secondary     # 本套文档（当前）
fix/core-2853-native-prompt
fix/core-spec-parse-2746-2747
fix/core-harness-override-2854
fix/core-workspace-3016
fix/core-child-session-2539
fix/core-compact-2967
fix/scale-jwt-renew-3012
fix/scale-stream-acl-3004
fix/scale-policy-cache-3003
fix/scale-idle-tmux-2702
fix/scale-sessions-list-3001
ops/host-jwt-relogin
ops/role-prompt-workaround
upstream/sync-YYYYMMDD
upstream-pr/<issue-topic>
```

### 5.2 Tag

| 模式 | 用途 |
|------|------|
| `v0.6.x-zhcn.N` | 常规分发 |
| `v0.6.x-zhcn.fix-core.N` | 含核心正确性补丁 |
| `v0.6.x-zhcn.fix-scale.N` | 含长跑/性能补丁 |
| `repro-core-YYYYMMDD` | 复现快照（可选） |

### 5.3 标准流水线

```text
1. main 拉 fix/<scope>-<issue>
2. 填 docs/fixes/tickets/（可用 TEMPLATE.md）
3. 改代码 + tests / scripts/repro
4. gh pr create → CI → squash merge
5. 需要对外：打 tag + CHANGELOG
6. 可上游：cherry-pick 干净提交 → PR omnigent-ai/omnigent
7. 上游合并后：upstream/sync，去重补丁，留测试
```

### 5.4 远程

```text
origin   = professoryu06/omnigent-zh-cn
upstream = omnigent-ai/omnigent   # 需 git remote add，只读同步
```

补丁注释建议：`# zh-cn-fix: issue #NNNN`，便于 sync 识别。

### 5.5 验收矩阵（尚未自动化）

- [scripts/repro/matrix-core.md](../scripts/repro/matrix-core.md) — C-2853 … C-2967  
- [scripts/repro/matrix-scale.md](../scripts/repro/matrix-scale.md) — S-3012 … S-3001  
- 脚本 `run-core-smoke.ps1`：**占位，未实现**

---

## 6. 仓库内已落盘文件清单

```text
docs/
  AGENT_HANDOFF_omnigent_issues_and_fix_plans.md   ← 本文（给审查 agent）
  omnigent-issues-analysis-report.md              ← 用户原分析报告全文
  fixes/
    README.md                                     ← 修复总览
    CORE_FIX_PLANS.md                             ← 核心 A/B/C 详案
    SECONDARY_FIX_PLANS.md                        ← 次要 A/B/C 详案
    STATUS.md                                     ← 分支/PR/tag 跟踪（均为 planned）
    tickets/TEMPLATE.md                           ← 单 issue 工单模板
ops/
  versioning/BRANCHING.md                         ← 分支 tag PR 细则
  host-relogin/README.md                          ← #3012 L0 说明
scripts/repro/
  README.md
  matrix-core.md
  matrix-scale.md
```

**Git：**

| 项 | 值 |
|----|-----|
| 分支 | `docs/fix-plans-core-secondary` |
| Commit | `3923598`（本文可能为后续 commit） |
| PR | https://github.com/professoryu06/omnigent-zh-cn/pull/2 |
| 相对 main | **仅文档**，无运行时行为变化 |

---

## 7. 明确「还没做」的事（防审查误判）

| 未做 | 说明 |
|------|------|
| 未复现 7 个核心 issue | 无 pass/fail 实验记录 |
| 未修改 omnigent 业务代码 | 无 fix/* 功能分支 |
| 未向 omnigent-ai 提 PR | 无 upstream-pr |
| 未打 fix-core / fix-scale tag | 无发布物 |
| 未确认 #3012 / #2575 上游进行中 PR 现状 | 需审查时再查 |
| agentcenter 独立仓 | 当前主版本管理在 omnigent-zh-cn |

---

## 8. 建议审查清单（给另一 agent）

请逐条给出 **同意 / 反对 / 需更多证据**，并简述理由：

1. **核心 7 项**是否应作为 zh-cn 近期唯一正确性 backlog？  
2. **#3012** 放「次要」是否合理（若用户即将双机无人值守，应否升核心）？  
3. **#2853 方案 B**（注入 prompt）是否与「native 由 CLI 自管 prompt」的上游设计冲突？方案 C 的 warn-only 是否更稳妥？  
4. **#2747+#2746 同分支**是否合理？  
5. **先文档 PR、后代码** 的节奏是否合适？  
6. **版本 tag 粒度**（fix-core.N / fix-scale.N）是否够用？  
7. 是否应 **fork omnigent-ai 再开 upstream PR**，而不是只在 zh-cn 长期 diverged 补丁？  
8. 验收矩阵是否应先写成 **可运行的最小复现** 再动代码？  

**期望审查输出格式（建议）：**

```markdown
## 审查结论
- 总体：approve / approve-with-changes / request-changes
- 优先级异议：...
- 方案异议：...
- 版本管理异议：...
- 建议下一步（最多 3 条）：...
```

---

## 9. 上游 Issue 快速链接

| # | URL |
|---|-----|
| 3016 | https://github.com/omnigent-ai/omnigent/issues/3016 |
| 3012 | https://github.com/omnigent-ai/omnigent/issues/3012 |
| 2967 | https://github.com/omnigent-ai/omnigent/issues/2967 |
| 2853 | https://github.com/omnigent-ai/omnigent/issues/2853 |
| 2854 | https://github.com/omnigent-ai/omnigent/issues/2854 |
| 2747 | https://github.com/omnigent-ai/omnigent/issues/2747 |
| 2746 | https://github.com/omnigent-ai/omnigent/issues/2746 |
| 2575 | https://github.com/omnigent-ai/omnigent/issues/2575 |
| 2539 | https://github.com/omnigent-ai/omnigent/issues/2539 |
| 3003 | https://github.com/omnigent-ai/omnigent/issues/3003 |
| 3004 | https://github.com/omnigent-ai/omnigent/issues/3004 |
| 2702 | https://github.com/omnigent-ai/omnigent/issues/2702 |
| 3001 | https://github.com/omnigent-ai/omnigent/issues/3001 |
| 2904 | https://github.com/omnigent-ai/omnigent/issues/2904 |

---

## 10. 给「执行 agent」的下一步（审查通过后）

**推荐默认路径（审查可改）：**

1. 合并 PR #2（文档进 main）  
2. 实现 `scripts/repro` 最小自动化或手测记录（至少 C-2853、C-3016、C-2539）  
3. 开 `fix/core-2853-native-prompt` 或 `fix/core-workspace-3016` 做 **方案 B**  
4. 合入后打 `v0.6.0-zhcn.fix-core.1`  
5. 并行：`ops/host-jwt-relogin` 落地 #3012 L0  

---

*本文是交接与审查包，不是已修复证明。一切「已修复」结论必须以测试矩阵 + tag 为准。*
