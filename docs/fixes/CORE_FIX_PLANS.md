# 核心问题修复方案（正确性）

> 目标：让 AgentCenter / agentpeihe 的 **角色身份、路由、隔离、子会话、长会话** 功能可信。  
> 每个 issue 给 **方案 A（止血）/ B（功能修复）/ C（上游级完整）**，并标明 Git 落点。

通用代码锚点基于上游 issue 描述（`omnigent 0.5.x–0.6.x` 系），落地时以当前 `main` 路径为准。

---

## 总原则

1. **修功能，不修表象**：验收标准是「角色/目录/子会话/模型」行为正确，不是「issue 被关掉」。  
2. **同功能簇同分支**：#2747+#2746 一起；#2853 单独但测矩阵共享。  
3. **先测后补丁**：每个 fix 分支必须带 `tests/` 或 `scripts/repro/` 可失败用例。  
4. **版本**：核心补丁合入后打 `v*-zhcn.fix-core.N`。

---

## #2853 Native harness 静默丢弃 `prompt:`

### 功能目标
Native harness（claude-native / codex-native / cursor-native / hermes-native / opencode-native 等）运行时，**必须**把 agent spec 的 `prompt:` / `system_prompt` 送进会话；做不到则必须 **显式告警**，禁止静默丢。

### 根因（功能层）
多个 `*_native_executor.py` / `native_server_harness.py` 在启动时 `del system_prompt`；只有 SDK / pi 路径会下发。

### 方案 A — 止血（L0，不改 harness 内核）
| 项 | 内容 |
|----|------|
| 做法 | 关键角色（Controller/Executor/Reviewer）改用 `claude-sdk` / 非 native；或把角色纪律写进 **第一条用户消息 / gate 协议文件**（repo 内 `AGENTS.md` 强制读取） |
| 改哪些功能面 | agent YAML、`examples/` 角色定义、部署文档 |
| 效果 | 身份可用；native 工具面能力仍受限 |
| 分支 | `ops/role-prompt-workaround` |
| 验收 | 提交 commit 时能看到角色要求的 trailer/约束 |

### 方案 B — 功能修复（L1，推荐）
| 项 | 内容 |
|----|------|
| 做法 | 按 harness 能力注入 prompt：① Claude Code：`--append-system-prompt` 拼上 spec prompt（不仅是 rename 指令）；② Codex/Cursor 等：在 session create / app-server launch 把 prompt 写入其 system/instructions API；③ 暂不支持的 harness：session create **WARNING** + 可选 `strict_prompt: true` 直接 fail-fast |
| 改点 | `omnigent/inner/*_native_executor.py`、`omnigent/claude_native.py`、`omnigent/native_server_harness.py` |
| 测试 | 单测：native executor 收到非空 system_prompt 时，launch argv/config 含该文本；回归 polly 子 agent commit trailer |
| 分支 | `fix/core-2853-native-prompt` |
| Tag | 合入后 `v*-zhcn.fix-core.1` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 统一 `HarnessPromptDelivery` 接口：`apply \| warn \| error`；文档写清各 native 的 prompt 语义；polly 示例改为「全 harness 一致」 |
| PR 标题 | `fix(harnesses): deliver agent spec prompt on native path (#2853)` |
| 同步 | 上游 merge 后 `upstream/sync-*` 去掉 zh-cn 重复补丁，保留测试 |

---

## #2747 + #2746 单文件 YAML：harness / model 解析不一致

### 功能目标
单文件 agent YAML 里声明的 `executor.type` / `executor.config.harness` / `executor.model`（及 config 内 model）**按文档优先级生效**，禁止被模型前缀静默改写。

### 根因
- #2747：harness 被 `_HARNESS_FOR_MODEL_PREFIX` 推断覆盖，忽略 YAML nesting。  
- #2746：codex-native 读 `executor.config.model` 而非 `executor.model`，默认模型顶掉声明。

### 方案 A — 止血（L0）
| 项 | 内容 |
|----|------|
| 做法 | 避免单文件歧义写法：用目录式 agent（`agents/<role>/config.yaml`）+ 明确 `executor.type`；模型名与 harness 前缀一致（临时） |
| 分支 | `ops/agent-yaml-conventions` |
| 验收 | `omnigent run` 日志里 harness/model 与预期一致（人工看 launch 行） |

### 方案 B — 功能修复（L1，推荐，同分支）
| 项 | 内容 |
|----|------|
| 做法 | 统一 **spec 解析优先级**：`executor.config.harness` > `executor.type` > model-prefix 推断；model：`executor.model` 与 `executor.config.model` 规范化为同一字段（config 覆盖或显式 merge，二选一并写死） |
| 改点 | `omnigent` 内 agent repr / single-file loader（`comp:repr` 相关）、native launch 读 model 路径 |
| 测试 | YAML fixture：声明 kimi-native + 明确 model → 不得落到 openai-agents/claude-sdk；codex-native 必须用声明 model |
| 分支 | `fix/core-spec-parse-2746-2747` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 更新 `docs/AGENT_YAML_SPEC.md` 优先级表；加载时若发生推断覆盖则 **log warning** 带上最终 harness/model |
| PR | `fix(repr): honor single-file executor harness/model (#2747 #2746)` |

---

## #2854 `harness_override` 在 kickoff turn 被忽略

### 功能目标
创建 session 时若同时带 `harness_override` + `initial_items`，**第一 turn 与后续 turn 使用同一 override harness**。

### 方案 A — 止血（L0）
| 项 | 内容 |
|----|------|
| 做法 | 先建空 session，再发第一条消息并带 override（issue 已有 workaround） |
| 封装 | 在编排层（agentpeihe / 脚本）提供 `create_session_then_kickoff()`，禁止业务代码直调「带 initial_items 的 create」 |
| 分支 | `ops/session-kickoff-helper` |

### 方案 B — 功能修复（L1，推荐）
| 项 | 内容 |
|----|------|
| 做法 | kickoff 路径在选择 harness 时 **先读 override**，再跑 initial_items；保证 snapshot 与 turn 0 同源 |
| 改点 | server/runner 创建 session + 首 turn 路由（issue 标 `comp:server`/`comp:runner`） |
| 测试 | API 测试：create + override + initial_items → turn0 harness == override |
| 分支 | `fix/core-harness-override-2854` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 明确 API 契约：override 作用于整个 session 生命周期；加 OpenAPI 说明 |
| PR | `fix(runner): apply harness_override on initial_items kickoff (#2854)` |

---

## #3016 snapshot 失败后工作区永久钉死全局 cwd

### 功能目标
snapshot/workspace 解析失败时 **不缓存成功结果**；后续重试可恢复到正确 worktree。agent reset 应清投影缓存。

### 根因
`_session_workspace_cache` 在 fallback/`workspace=None` 时仍写入；仅 `delete_session` 会 pop。

### 方案 A — 止血（L0）
| 项 | 内容 |
|----|------|
| 做法 | 运维：发现 cwd 异常 → **删除 session 重建**；避免在 server 抖动时狂刷 filesystem API |
| 监控 | 日志告警：`workspace=None` 或 cwd == runner global |
| 分支 | `ops/workspace-poison-runbook` |

### 方案 B — 功能修复（L1，推荐，高优先）
| 项 | 内容 |
|----|------|
| 做法 | ① 仅当 snapshot 成功且 workspace 非空时写入 `_session_workspace_cache`；② reset-agent-cache 同步驱逐 workspace 投影缓存；③ filesystem 路径先 resolve spec 再 register（修正 #3016 描述的调用顺序） |
| 改点 | `omnigent/runner/app.py`（`_session_workspace_value` / `_ensure_session_registered` / reset 路径） |
| 测试 | 扩展已有 `test_failed_session_snapshot_is_not_cached_and_retries`：覆盖 workspace 投影层 |
| 分支 | `fix/core-workspace-3016` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 缓存分层：snapshot cache / workspace projection / env bake 统一 invalidation 策略文档 |
| PR | `fix(runner): do not cache failed session workspace projection (#3016)` |

---

## #2539 named `sys_session_send` 第二子会话 404

### 功能目标
同一 parent、bundled session-scoped agent 下，可连续创建 **多个** named 子会话。

### 根因
`SqlAlchemyAgentStore._session_id_for_agent()` 使用无序 `LIMIT 1`，破坏单所有者假设。

### 方案 A — 止血（L0）
| 项 | 内容 |
|----|------|
| 做法 | 编排层少用 named send；或每个角色独立顶层 session，用外部协议拼结果（牺牲紧耦合 fan-out） |
| 分支 | `ops/child-session-topology` |

### 方案 B — 功能修复（L1，推荐）
| 项 | 内容 |
|----|------|
| 做法 | `_session_id_for_agent` 按稳定键解析（owner session id + agent name），禁止无序 LIMIT 1；创建子 session 时写入明确归属 |
| 改点 | agent store / runner session 路由（issue `comp:runner`/`comp:server`） |
| 测试 | 同 parent 连续 3 次 named `sys_session_send` 均 201/200 |
| 分支 | `fix/core-child-session-2539` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 数据模型明确 session↔agent 1:1 或 1:N 约束 + 迁移 |
| PR | `fix(runner): stable session lookup for named sys_session_send (#2539)` |

---

## #2967 上下文满后 session 砖死（无 auto-compact）

### 功能目标
上下文接近上限时，harness turn 路径 **主动 compact 或截断**，避免永久 `Prompt is too long`。

### 方案 A — 止血（L0）
| 项 | 内容 |
|----|------|
| 做法 | gate 协议：N 轮后强制新 session + 交接摘要；大任务拆关卡；优先大窗口模型 |
| 脚本 | `scripts/repro/long_session_guard.sh` 检测错误后重建 |
| 分支 | `ops/session-rotation-policy` |

### 方案 B — 功能修复（L1，推荐）
| 项 | 内容 |
|----|------|
| 做法 | turn 前估算 token；超阈值触发 compact（复用 SDK/claude 已有 compact 能力，接到 harness turn path）；失败则返回可恢复错误码而非死循环同错误 |
| 改点 | runner harness turn 路径、`comp:harnesses` 相关 |
| 测试 | 模拟超长 history → 下一 turn 不 brick，或明确 `needs_compact` 状态 |
| 分支 | `fix/core-compact-2967` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 可配置 `compaction: {mode: proactive\|on_error\|off, threshold}`；Web UI 显示 compact 事件 |
| PR | `fix(runner): proactive compaction on harness turn path (#2967)` |

---

## 核心修复的 Git 落地清单（复制即用）

```bash
# 0. 基线
git checkout main
git pull origin main

# 1. 文档已在 docs/fix-plans-core-secondary
# 2. 按波次开分支（示例：第 1 波 prompt）
git checkout -b fix/core-2853-native-prompt
# ... 开发 + 测试 ...
git commit -m "fix(harnesses): deliver agent spec prompt on native path (#2853)"
gh pr create --base main --title "fix(harnesses): native prompt delivery (#2853)" --body-file docs/fixes/tickets/2853.md

# 3. 合入后打 tag
git checkout main && git pull
git tag -a v0.6.0-zhcn.fix-core.1 -m "core fixes wave1: #2853"
git push origin v0.6.0-zhcn.fix-core.1

# 4. 上游贡献（干净提交）
git checkout -b upstream-pr/2853-native-prompt main
git cherry-pick <clean-sha>
# fork omnigent-ai/omnigent 后 push + gh pr create
```

---

## 验收矩阵（核心）

| ID | 操作 | 期望 |
|----|------|------|
| C-2853 | native + 独特 prompt 让其 commit | commit 含 prompt 要求 |
| C-2747 | 单文件 YAML 声明 kimi-native | 实际 harness = kimi-native |
| C-2746 | 单文件声明非默认 model | launch 使用声明 model |
| C-2854 | create+override+initial_items | turn0 harness = override |
| C-3016 | 注入 snapshot 失败后再恢复 | cwd 恢复为 session worktree |
| C-2539 | 连续 2+ named 子会话 | 均成功 |
| C-2967 | 超长 history 再 turn | 不永久 brick / 有 compact |
