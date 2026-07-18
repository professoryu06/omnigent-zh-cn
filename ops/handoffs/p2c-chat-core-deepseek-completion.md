# P2C：聊天核心界面中文化 — 完成报告

**工作包**：`ops/handoffs/p2c-chat-core-deepseek.md`
**完成日期**：2026-07-15

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 53 个 chat/queue/userMessageNav 英文 i18n key |
| `web/src/i18n/locales/zh-CN.ts` | 新增 53 个 chat/queue/userMessageNav 简体中文 i18n key |
| `web/src/pages/ChatPage.tsx` | 9 个子组件接入 `useTranslation()`；ChatPage 空状态/历史加载/连接提示/Composer/气泡操作/模型选择器文案替换为 i18n key；模块级常量（WORKING_MESSAGES, SANDBOX_STAGE_LABELS, mcpStartingLine, readOnlyReasonForSessionLabels）使用 `translate()` |
| `web/src/pages/QueuedMessagesStrip.tsx` | `QueuedRow` 组件接入 `useTranslation()`，5 个 aria-label 和按钮文案替换为 `t("queue.*")` |
| `web/src/components/UserMessageNav.tsx` | 组件接入 `useTranslation()`，4 个 aria-label/tooltip 文案替换为 `t("userMessageNav.*")` |
| `web/src/pages/ChatPage.composer.test.tsx` | 新增中文 placeholder/aria-label 测试用例 |

## 新增 i18n Key 清单

### chat 命名空间（44 个）

**输入框与发送**：`emptyState`, `placeholder`, `send`, `interrupt`, `messageTheAgent`, `attachFiles`, `removeFile`, `removeQuote`, `enterPlanMode`, `exitPlanMode`

**只读/离线/重连原因**：`readOnly`, `sessionOffline`, `pendingRequest`, `waitingForAgents`, `sendQueued`, `hostOfflineResume`, `sendToReconnect`

**工作状态指示器**：`working`, `cooking`, `crunching`, `tinkering`, `pondering`, `brewing`

**消息操作**：`copy`, `forkFromHere`

**历史加载**：`loadingHistory`, `jumpToTop`, `jumpToFirstMessage`, `loading`

**连接状态**：`hostOfflineReconnect`, `agentDisconnectedReconnect`, `provisioningSandbox`, `cloningRepository`, `connectingHost`, `startingAgent`, `startingUp`, `sandboxSetupHint`, `startupHint`, `startingMcpServer`, `startingMcpServers`

**子智能体限制**：`subAgentClosed`, `claudeCodeSubAgentsReadOnly`

**选择器与视图**：`noAgents`, `model`, `viewMode`, `chat`, `terminal`, `terminalStartingUp`, `failedToLoadAgents`

**斜杠命令错误**：`compactFailed`, `planModeError`, `effortUsage`, `failedToSetEffort`, `modelUsage`, `failedToSetModel`, `modelOverride`, `noUsageData`, `itemsInContext`, `unknownCommand`

### queue 命名空间（5 个）

`reorder`, `sendNow`, `steer`, `edit`, `remove`

### userMessageNav 命名空间（4 个）

`previous`, `previousTooltip`, `next`, `nextTooltip`

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| `Claude` / `Codex` / `Cursor` / `Kiro` / `OpenCode` | 模型/Harness 专有名称 |
| `MCP` | 技术缩写，不翻译 |
| `⌘⌥↑` / `⌘⌥↓` 快捷键 | 键盘快捷键值，不翻译 |
| `Esc` | 键盘按键名 |
| `"image.png"` 文件名回退 | 代码内部回退占位 |
| `"Failed to copy message"` console.warn | 调试日志，非用户可见 |
| 所有 `data-testid` 值 | 测试属性 |
| 斜杠命令名（`/model`, `/effort`, `/compact` 等） | CLI 命令，不翻译 |

## 模块级 `translate()` 使用

以下常量/函数定义在组件外部，无法使用 `useTranslation()` hook，改用独立的 `translate()` 函数：

- **WORKING_MESSAGES** 数组（"Working…" / "Cooking…" 等 6 条）→ `translate("chat.working")` ...
- **SANDBOX_STAGE_LABELS** 对象（4 个启动阶段）→ `translate("chat.provisioningSandbox")` ...
- **mcpStartingLine()** 函数 → `translate("chat.startingMcpServer", ...)`
- **readOnlyReasonForSessionLabels()** 函数 → `translate("chat.subAgentClosed")`

## 验收命令及结果

```
npm run test -- --run src/pages/ChatPage.test.ts src/pages/ChatPage.composer.test.tsx src/pages/ChatPage.statusLine.test.tsx src/pages/ChatPage.historyLoad.test.tsx src/pages/QueuedMessagesStrip.test.tsx src/components/UserMessageNav.test.tsx
→ Test Files  6 passed (6)
→ Tests  246 passed (246)

npm run test -- --run
→ Test Files  1 failed | 226 passed | 1 skipped (228)
→ Tests  1 failed | 4001 passed | 3 expected fail | 2 skipped (4007)
→ 1 个失败为预存问题（AgentInfo.test.tsx databricks-gpt-5-5 模型名渲染，P2A/P2B 已确认）

npm run build
→ tsc -b && vite build 成功
→ 仅有 chunk 大小警告（预存）
```

## 未解决项

1. `ChatPage.tsx` 主组件中空状态区域的 `translate()` 调用（而非 `t()` hook）是因为该文件体量巨大、子组件繁多，主组件内的 `t()` hook 声明被 TS 报告 unused（所有 `t()` 调用实际分散在已接入独立 hook 的子组件中）。功能等价，仅实现路径不同
2. `"What should we work on?"` 空状态标题（`ConversationEmptyState` 中的 `<h3>`）暂未翻译——该文案跨多种会话类型共享，且不属于本包指定的"输入框/内容区操作/排队消息/用户消息跳转"优先范围
3. `AgentInfo.test.tsx` 1 个预存失败与本次变更无关
4. 键盘快捷键组合 `⌘⌥↑` / `⌘⌥↓` 在不同平台渲染不同（macOS），Windows 下会显示 `Ctrl+Alt+↑`，但此处保留原文不做平台特定映射

## 发现但未改动的文件

- `ChatPage.tsx` 中的 `"Attach to agent"`、`"Reply ↵"` 等悬浮提示属于子组件内部文案，不在本包范围内
- `ChatPage.tsx` 中 `SubagentComposerTray` 和 `TerminalFirstContext` 相关提示属于子代理/终端交互范围，P2A/P2B 已覆盖的头部和侧边栏文案不重复处理
- `ChatPage.tsx > TerminalFirstConnectedPill` 中的 `"Connected…"` / `"Disconnected"` 状态标签属于终端连接状态，不影响聊天核心交互
