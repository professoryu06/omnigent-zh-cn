# P2H：应用壳层、工作区与导航中文化 — 完成报告

**工作包**：`ops/handoffs/p2h-shell-workspace-navigation-deepseek.md`
**完成日期**：2026-07-16

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 app（4）、workspacePanel（6）、commandPalette（12）、rail（8）、server（2）共 32 个英文 i18n key |
| `web/src/i18n/locales/zh-CN.ts` | 新增 app（4）、workspacePanel（6）、commandPalette（12）、rail（8）、server（2）共 32 个简体中文 i18n key |
| `web/src/shell/AppShell.tsx` | 7 处文案替换（分享禁用提示 ×2、移动抽屉标题 ×3、智能体对话框 ×2） |
| `web/src/shell/MobilePanelDrawer.tsx` | 组件接入 `useTranslation()`；关闭按钮 aria-label 替换 |
| `web/src/shell/TitleBarServerPicker.tsx` | 组件接入 `useTranslation()`；切换服务器 tooltip 和菜单项替换 |
| `web/src/shell/WorkspacePanel.tsx` | `FileTabsStrip` 和 `WorkspacePanel` 接入 `useTranslation()`；8 处文案替换（工作区 aria-label、关闭文件 aria-label、5 个 rail 标签文本） |
| `web/src/shell/SessionRail.tsx` | `TerminalsCard` 和 `ExecutionLogsCard` 接入 `useTranslation()`；8 处文案替换（卡片标题 ×2、展开/收起 aria-label ×4、空状态、main 标签） |
| `web/src/shell/CommandPalette.tsx` | 组件接入 `useTranslation()`；12 处文案替换（对话框标题 ×2、搜索占位、加载/空状态、分组标题 ×2、操作标签 ×5）；搜索关键词保留英文 |
| `web/src/shell/CommandPalette.test.tsx` | 新增 zh-CN 搜索占位符断言 |

## 新增 i18n Key 清单

### app 命名空间（4 个）

`sharingUnavailableLocal`, `sharingDisabledServer`, `agent`, `agentDescription`

### workspacePanel 命名空间（6 个）

`workspace`, `closeFile`, `files`, `agents`, `shells`, `tasks`, `browser`

### commandPalette 命名空间（12 个）

`title`, `searchPlaceholder`, `searching`, `noResults`, `sessions`, `actions`, `newChat`, `goToInbox`, `goToSettings`, `toggleConversationsSidebar`, `toggleWorkspaceSidebar`

### rail 命名空间（8 个）

`terminals`, `expandTerminals`, `collapseTerminals`, `noOpenTerminals`, `executionLogs`, `expandExecutionLogs`, `collapseExecutionLogs`, `main`

### server 命名空间（2 个）

`switchServer`, `connectToNewServer`

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| `Omnigent`（品牌文字） | 产品名称，不翻译 |
| 命令面板搜索关键词数组（`["compose", "start", "new session"]` 等） | 仅用于客户端过滤匹配，非用户可见文案 |
| 文件路径 `title={path}` | 用户数据，不翻译 |
| `·` 分隔符（SessionRail 中） | 标点符号，不翻译 |
| 服务端返回的会话标题、项目名、智能体名 | 服务端数据，不翻译 |
| `data-testid`、CSS 类名 | 非用户可见 |

## 验收命令及结果

```
npm run test -- --run src/shell/AppShell.test.tsx src/shell/AppShell.subagent-nav.test.tsx src/shell/WorkspacePanel.test.tsx src/shell/TodoPanel.test.tsx src/shell/CommandPalette.test.tsx src/shell/sidebarNav.test.ts
→ Test Files  6 passed (6)
→ Tests  155 passed (155)

npm run test -- --run
→ Test Files  1 failed | 226 passed | 1 skipped (228)
→ Tests  1 failed | 4016 passed | 3 expected fail | 2 skipped (4022)
→ 1 个失败为预存问题（AgentInfo.test.tsx，P2A-P2G 已确认）

npm run build
→ tsc -b && vite build 成功
```

## 未处理项

1. `TodoPanel.tsx` 无硬编码用户可见英文文案——纯数据驱动，待办事项内容和状态来自 `useChatStore`
2. `railTabs.ts` 仅包含 TypeScript 类型定义和 CSS 常量，无用户可见文案
3. `sidebarNav.ts` 中的 `UNTITLED_CONVERSATION_LABEL = "New session"` 和 `CLAUDE_NATIVE_DEFAULT_LABEL = "Claude Code"` 等常量——这些是 P2B Sidebar 使用的数据标签，已在对应组件中通过 `t()` 处理。"New session" 已有 `sidebar.newSession` key。"Claude Code" 等为产品名称，不翻译
4. `WorkspacePanel.test.tsx` 的 zh-CN 测试因需要 mock `openFiles` store 状态而未添加（该组件有较多内部 hooks 依赖），由 `CommandPalette.test.tsx` 的 zh-CN 测试覆盖命令面板场景
