# P4C：工作区与会话导航残留中文化 — 完成报告

**工作包**：`ops/handoffs/p4c-workspace-navigation-residual-deepseek.md`
**完成日期**：2026-07-16

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 9 个 markdown.* key、7 个新 key（sidebar.irreversible, newSession.*, session.originalAgent） |
| `web/src/i18n/locales/zh-CN.ts` | 对应中文翻译 |
| `web/src/shell/MarkdownRichTextViewer.tsx` | 组件接入 `useTranslation()`；9 处文案（复制/外部修改/保留/加载最新/执行器离线/保存状态）替换 |
| `web/src/shell/FolderTree.tsx` | 搜索错误回退 → `t("status.unknownError")`；文件空状态 → `t("file.noFilesInWorkspace")` |
| `web/src/shell/Sidebar.tsx` | 拖拽取消分组确认对话框 4 处 → `sidebar.*` key；`"irreversible"` → `t("sidebar.irreversible")` |
| `web/src/shell/NewChatDialog.tsx` | 9 处（Remove aria-label ×2、New Sandbox、Why/How/Databricks aria-label、Repository branch、Bypass、Base branch、bypass-confirmation）替换 |
| `web/src/shell/ForkSessionDialog.tsx` | 回退值 → `t("session.originalAgent")` |

## 新增 i18n Key

### markdown 命名空间（9 个）

`copy`, `copied`, `externallyModified`, `keepMine`, `loadLatest`, `runnerOffline`, `saving`, `unsavedChanges`, `commentingAvailable`

### sidebar 命名空间（1 个）

`irreversible`

### newSession 命名空间（5 个）

`newSandboxDisabled`, `whySandboxUnavailable`, `databricksGitCredentials`, `repositoryBranch`, `bypassConfirmationAriaLabel`

### session 命名空间（1 个）

`originalAgent`

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| `https://github.com/org/repo` | 示例 URL |
| `feature/my-branch` | 示例分支名 |
| `image.png` | 文件名回退值 |
| `bypass sandbox`（确认短语） | 必须逐字输入 |
| `host.status`（online/offline） | 服务端数据 |
| CLAUDE_NATIVE_MODELS 模型名 | 产品名称 |

## 验收命令及结果

```
npm run test -- --run src/shell/Sidebar.test.tsx src/shell/MarkdownRichTextViewer.test.tsx
→ Test Files  2 passed (2), Tests  65 passed (65)

npm run test -- --run
→ Test Files  1 failed | 227 passed | 1 skipped (229)
→ Tests  1 failed | 4081 passed | 3 expected fail | 2 skipped (4087)
→ 1 个失败为预存基线（AgentInfo.test.tsx 1K）

npm run build
→ tsc -b && vite build 成功
```

## 未解决项

1. `AgentInfo.test.tsx` 1K token 格式化基线失败——预存问题
2. NewChatDialog 中 CLAUDE_NATIVE_PERMISSION_MODES、CURSOR_NATIVE_EXEC_MODES、CODEX_NATIVE_APPROVAL_MODES 的 `label`/`description` 仍为模块级硬编码英文——这些是技术选项值，P2A 完成报告已标记为"保留英文原文"
3. `AGENT_PICKER_DESCRIPTIONS`（polly/debby 副标题）仍为模块级英文——P2A 已标记为保留
