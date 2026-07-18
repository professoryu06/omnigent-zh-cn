# P4A：聊天卡片与系统状态中文化 — 完成报告

**工作包**：`ops/handoffs/p4a-chat-cards-status-deepseek.md`
**完成日期**：2026-07-16

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 approval（30）、slashCommand（4）、routing（20）、status（5）、systemMessage（1）、terminal（9）、reasoning（3）共 72 个英文 i18n key |
| `web/src/i18n/locales/zh-CN.ts` | 对应 72 个简体中文 i18n key |
| `web/src/components/blocks/ApprovalCard.tsx` | 组件接入 `useTranslation()`；全部标题/按钮/药丸标签/工具提示/描述替换 |
| `web/src/components/blocks/SlashCommandCard.tsx` | `KIND_STYLES` 重构为 `labelKey`；"Arguments"/"Output" 面板标题替换 |
| `web/src/components/blocks/SmartRoutingCard.tsx` | 组件接入 `useTranslation()`；路由状态/称重/评估/展开标签替换 |
| `web/src/components/blocks/StatusBlocks.tsx` | `ErrorBanner`/`PolicyDeniedBanner`/`RetryIndicator`/`CompactionMarker`/`RoutingDecisionChip`/`RoutingDecisionCard` 接入 i18n；模块级 shimmer 动词改为渲染期 t() 解析 |
| `web/src/components/blocks/SystemMessage.tsx` | "System:" 替换为 `t("systemMessage.system")` |
| `web/src/components/blocks/TerminalView.tsx` | 组件接入 `useTranslation()`；`selectionHintText`/`resumeErrorText` 使用 `translate()`；连接/重连/桥接状态替换 |
| `web/src/components/ai-elements/reasoning.tsx` | `defaultGetThinkingMessage` 重构为柯里化函数接收 t 参数；思考状态标签替换 |
| 测试文件 7 个 | 16+ 条 zh-CN 断言覆盖全部 7 组件 + StatusBlocks I18nProvider 运行时切换测试 |

## 新增 i18n Key 清单

### approval 命名空间（30 个）

`antigravityNeedsInput`, `codexNeedsInput`, `cursorHasQuestions`, `claudeHasQuestions`, `planRejected`, `rejected`, `resolvedElsewhere`, `submitted`, `selected`, `approvedRemembered`, `planApprovedAutoMode`, `approvedAutoAccepting`, `approvedWontAskFor`, `approvedWontAsk`, `planApproved`, `approved`, `cwd`, `wontAskHost`, `wontAskTool`, `acceptAllowAllEdits`, `approveDontAsk`, `reject`, `approveAndRemember`, `commandApproval`, `planReview`, `chooseOption`, `approvalRequired`, `finishedPlanning`, `codexWantsToRun`, `openApprovalPage`

### slashCommand 命名空间（4 个）

`skill`, `command`, `arguments`, `output`

### routing 命名空间（20 个）

`weighing`, `matching`, `tuning`, `sizingUp`, `weighingTasks`, `task`, `tasks`, `intelligentRouting`, `unavailable`, `sizedTasks`, `showRawResponse`, `noDecision`, `response`, `modelRouter`, `modelRouterTitle`, `wouldHavePicked`, `session`, `applied`, `advisory`, `showRawVerdict`, `verdict`

### status 命名空间（5 个）

`unknownError`, `error`, `blockedByPolicy`, `retrying`, `compacted`

### systemMessage 命名空间（1 个）

`system`

### terminal 命名空间（9 个，复用 P2E 的 14 个）

`macHint`, `winHint`, `connecting`, `reconnecting`, `bridgeClosed`, `resumeSession`, `resuming`, `bridgeError`, `couldntResume`, `couldntResumeFallback`

### reasoning 命名空间（3 个）

`thinking`, `thoughtFewSeconds`, `thoughtForSeconds`

## 关键架构决策

### SlashCommandCard KIND_STYLES 重构

```ts
// Before: { label: "Skill", ... } → rendered as-is
// After:  { labelKey: "slashCommand.skill", ... } → {t(style.labelKey)}
```

### reasoning defaultGetThinkingMessage 柯里化

```ts
// Before: hardcoded strings
// After: defaultGetThinkingMessage(t) returns a function using t()
```

### 重复 key 处理

`approval.rejected`/`approval.reject`/`approval.approved` 在 P4A 新 key 块中与 P3C 的老 key 重复——P3C 的 `approval.reject` = "Reject"（审批卡拒绝按钮）与 P4A 的 `approval.rejected` = "Rejected"（已拒绝药丸）是不同的 key。删除了 P4A 块中与已有 key 完全相同的重复 key。

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| `cwd:` 技术标签 | 文件系统路径前缀 |
| `" · "` 中间点分隔符 | 标点符号 |
| `"—"` 破折号占位符 | 标点符号 |
| 动态审批内容、命令文本、服务端错误 | 用户/系统数据 |
| 模型名称、策略名称 | 系统数据 |

## 验收命令及结果

```
npm run test -- --run src/components/blocks/ApprovalCard.test.tsx src/components/blocks/SlashCommandCard.test.tsx src/components/blocks/SmartRoutingCard.test.tsx src/components/blocks/StatusBlocks.test.tsx src/components/blocks/SystemMessage.test.tsx src/components/blocks/TerminalView.test.tsx src/components/ai-elements/reasoning.test.tsx
→ Test Files  7 passed (7)
→ Tests  107 passed (107)

npm run test -- --run
→ Test Files  1 failed | 226 passed | 1 skipped (228)
→ Tests  1 failed | 4072 passed | 3 expected fail | 2 skipped (4078)
→ 1 个失败为预存基线问题（AgentInfo.test.tsx "1K"，P2A-P3D 已确认）

npm run build
→ tsc -b && vite build 成功
```

## zh-CN 测试覆盖（16+ 条，覆盖全部 7 组件）

| # | 组件 | 断言内容 |
|---|---|---|
| 1 | ApprovalCard | 审批/拒绝按钮 → "批准"/"拒绝" |
| 2 | ApprovalCard | 已审批/已拒绝药丸 → "已批准"/"已拒绝" |
| 3 | SlashCommandCard | 技能标签 → "技能" |
| 4 | SlashCommandCard | 参数/输出面板 → "参数"/"输出" |
| 5 | SmartRoutingCard | 路由标题 → "智能路由" |
| 6 | SmartRoutingCard | 称重名词 → "任务" |
| 7 | StatusBlocks | Chip/Card → 含"智能模型路由器"和"智能路由" |
| 8 | StatusBlocks | ErrorBanner/Compaction/Policy → "未知错误"/"会话已压缩"/"被策略阻止" |
| 9 | StatusBlocks | **I18nProvider 运行时切换**：英文→中文不重新挂载 |
| 10 | SystemMessage | "系统：" |
| 11 | TerminalView | macOS 提示栏 → "按住 ⌥ 并拖拽以选择 · ⌘C 复制" |
| 12 | TerminalView | Windows 提示栏 → "按住 Shift 并拖拽以选择 · 右键复制" |
| 13 | reasoning | 流式思考 → "思考中..." |
| 14 | reasoning | 思考结束 → "思考了几秒钟" |

## 未解决项

1. `AgentInfo.test.tsx` "1K" token 格式化基线失败——预存问题，P2A 起已确认
