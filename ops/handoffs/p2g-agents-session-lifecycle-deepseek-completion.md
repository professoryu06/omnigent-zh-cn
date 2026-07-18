# P2G：智能体管理与会话生命周期中文化 — 完成报告

**工作包**：`ops/handoffs/p2g-agents-session-lifecycle-deepseek.md`
**完成日期**：2026-07-16

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 agent（19）、subagent（8）、session（30+）、common（1）共 60+ 个英文 i18n key |
| `web/src/i18n/locales/zh-CN.ts` | 新增 agent（19）、subagent（8）、session（30+）、common（1）共 60+ 个简体中文 i18n key |
| `web/src/shell/AddAgentDialog.tsx` | 组件接入 `useTranslation()`；标题/标签/placeholder/按钮/错误文案替换 |
| `web/src/shell/CreateAgentDialog.tsx` | 组件接入 `useTranslation()`；标题/所有标签/placeholder/按钮文案替换；技术占位（`my-agent`、`claude-sonnet-4-20250514`、`server-name`等）保留英文 |
| `web/src/shell/SwitchAgentDialog.tsx` | 组件接入 `useTranslation()`；标题/描述/标签/placeholder/模型重置警告/错误/按钮文案替换 |
| `web/src/shell/SubagentsPanel.tsx` | 3 个子组件接入 `useTranslation()`；加载/错误状态、列表/图谱切换、状态指示器标签替换 |
| `web/src/shell/SubagentsGraphView.tsx` | `AgentNodeComponent` 接入 `useTranslation()`；子智能体状态标签翻译映射 |
| `web/src/shell/ForkSessionDialog.tsx` | `ForkSessionForm` 和 `ForkSessionDialog` 接入 `useTranslation()`；全部对话框标题/描述/标签/placeholder/按钮/冲突提示/风险警告文案替换 |
| `web/src/shell/ResumeWithDirectoryDialog.tsx` | 组件接入 `useTranslation()`；标题/描述/加载/目录/按钮/错误文案替换 |
| `web/src/shell/ReconnectSessionDialog.tsx` | 组件接入 `useTranslation()`；模块级描述常量移入组件渲染期求值；标题/标签/描述文案替换 |
| `web/src/shell/RunnerAsleepHint.tsx` | 组件接入 `useTranslation()`；休眠提示文案替换 |
| `web/src/shell/AddAgentDialog.test.tsx` | 新增 zh-CN 对话框标题断言 |
| `web/src/shell/SwitchAgentDialog.test.tsx` | 新增 zh-CN 对话框标题断言 |
| `web/src/shell/SubagentsPanel.test.tsx` | `Failed to load agents` 断言更新为 `Failed to load sub-agents` |

## 新增 i18n Key 清单

### agent 命名空间（19 个）

`addAgent`, `pickAnAgent`, `noAgentsAvailable`, `name`, `namePlaceholder`, `nameRequired`, `adding`, `add`, `create`, `description`, `summaryPlaceholder`, `systemInstructions`, `instructionsPlaceholder`, `mcpTools`, `addServer`, `harness`, `switchAgent`, `currentAgent`, `switchTo`, `switchDescription`, `switchReadOnly`, `switchResetsModel`, `couldntAdd`, `couldntSwitch`, `switching`, `agent`, `chooseAgent`

### subagent 命名空间（8 个）

`panelTitle`, `addAgent`, `list`, `graph`, `loading`, `loadingGraph`, `empty`, `failedToLoad`

### session 命名空间（30+ 个）

**重连**：`reconnect`, `clone`, `hostOffline`, `agentDisconnected`, `hostOwnerDescription`, `hostViewerDescription`, `runDescription`

**分支/克隆**：`forkSession`, `forkDescription`, `forkRiskLabel`, `cloneFailed`, `nameClonedSession`, `nameOptional`, `cloneReusesDirPrefix`, `cloneReusesDirSuffix`, `sameAsOriginal`, `cloneAndStart`, `forkFromResponse`, `cloneSession`, `whatIsCloning`, `cloneTruncatedDescription`, `cloneTruncatedCodingDescription`, `cloneFullDescription`, `cloneFullCodingDescription`

**目录与主机**：`workingDirectory`, `currentDirectory`, `newDirectory`, `directoryDiffers`, `directoryMismatchWarning`, `directoryConflictHintSingular`, `directoryConflictHintPlural`, `selectHostForDir`, `noHostsOnline`, `noHostsConnected`, `connectAnotherHost`

**Git 工作树**：`gitWorktreeOptional`, `gitWorktreeHelp`, `baseBranchPlaceholder`, `baseBranchAriaLabel`

**恢复**：`resumeWithDirectory`, `resumeThis`, `resumeDescription`, `resumeDirectoryDescription`, `loadingSourceDir`, `sourceHostOfflineResume`, `cannotResumeHostOffline`, `cannotResumeLocal`

**启动**：`startFailed`, `startSession`

**休眠**：`agentAsleep`, `sendToReconnect`, `continueSession`, `reconnecting`

**通用**：`common.starting`

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| `my-agent`、`server-name`、`claude-sonnet-4-20250514` | 技术示例/占位符值 |
| `command (e.g. npx)`、`args (e.g. -y @modelcontextprotocol/server-github)` | 命令行示例 |
| `https://mcp.example.com/sse` | 示例 URL |
| `KEY=VALUE`、`GITHUB_TOKEN=ghp_...` | 环境变量示例格式 |
| `stdio`、`http` | 技术传输协议名称 |
| 智能体名称、Harness 名称、模型名称 | 服务端数据，不翻译 |
| 主机名、会话 ID、分支名、文件路径 | 系统/用户数据，不翻译 |
| `data-testid`、CSS 类名 | 非用户可见 |

## 关键架构决策

### ReconnectSessionDialog 模块级常量移除

原文件在模块级定义了 `HOST_OWNER_DESCRIPTION`、`HOST_VIEWER_DESCRIPTION`、`RUN_DESCRIPTION` 三个字符串常量。由于 `translate()` 在模块加载时求值会冻结语言，改为在 `ReconnectSessionDialog` 组件渲染期内联调用 `t()`，确保语言切换后重新渲染。

### SubagentsPanel/SubagentsGraphView 状态标签翻译

子智能体状态指示器使用判别联合类型 `AgentActivity`，通过 `displayLabel` / `displayStatusLabel` 计算属性将活动类型映射到 `t("subagent.*")` 调用，保留 `"other"` 活动的原始服务端标签不做翻译。

## 验收命令及结果

```
npm run test -- --run src/shell/AddAgentDialog.test.tsx src/shell/SwitchAgentDialog.test.tsx src/shell/SubagentsPanel.test.tsx src/shell/SubagentsGraphView.test.tsx src/shell/ForkSessionDialog.test.tsx src/shell/ResumeWithDirectoryDialog.test.tsx src/shell/ReconnectSessionDialog.test.tsx
→ Test Files  7 passed (7)
→ Tests  155 passed | 1 expected fail (156)

npm run test -- --run
→ Test Files  1 failed | 226 passed | 1 skipped (228)
→ Tests  1 failed | 4014 passed | 3 expected fail | 2 skipped (4020)
→ 1 个失败为预存问题（AgentInfo.test.tsx，P2A-P2F 已确认）

npm run build
→ tsc -b && vite build 成功
```

## 未处理项

1. `CreateAgentDialog.tsx` 与 `RunnerAsleepHint.tsx` 无独立测试文件，由 TypeScript 编译覆盖验证
2. `AddAgentDialog.tsx` 中 `noAgentsAvailable` 文案包含 `<code>` 标签包裹的 `omnigent server --agent` 命令——翻译时通过 `indexOf` 查找命令名拆分插入标签，与 P2A 中的 harness 警告处理方法一致
3. `SubagentsPanel` 与 `SubagentsGraphView` 的状态标签翻译依赖 `AgentActivity` 判别联合类型，服务端返回的 `"other"` 活动保持原文不变
