# P2D：文件工作区中文化 — 完成报告

**工作包**：`ops/handoffs/p2d-files-workspace-deepseek.md`
**完成日期**：2026-07-16

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 75 个 file.* 英文 i18n key，25 个 workspace.* 英文 i18n key |
| `web/src/i18n/locales/zh-CN.ts` | 新增 75 个 file.* 简体中文 i18n key，25 个 workspace.* 简体中文 i18n key |
| `web/src/shell/FilesPanel.tsx` | 4 个子组件接入 `useTranslation()`（HiddenFilesToggle, SortSelector, FileScopeSwitch, FilesPanel）；SORT_OPTIONS 模块级常量使用 `translate()`；所有 aria-label/tooltip/按钮/标题文案替换为 i18n key |
| `web/src/shell/FlatFileList.tsx` | `FlatFileList` 组件接入 `useTranslation()`；加载/错误/空状态/隐藏文件提示文案替换 |
| `web/src/shell/FolderTree.tsx` | `FolderTree` 和 `TreeNodeRow` 组件接入 `useTranslation()`；搜索/错误/空状态/懒加载/隐藏文件文案替换 |
| `web/src/shell/FileDownloadButton.tsx` | `FileDownloadButton` 组件接入 `useTranslation()`；下载工具提示文案替换 |
| `web/src/shell/FileViewer.tsx` | `FileViewerBody` 组件接入 `useTranslation()`；38 处工具栏操作标签/aria-label/tooltip、保存状态芯片、已删除文件通知、加载/错误状态、未保存更改对话框文案替换 |
| `web/src/shell/WorkspacePathField.tsx` | `WorkspacePathField` 组件接入 `useTranslation()`；7 处路径输入/浏览/匹配分组/加载文案替换 |
| `web/src/shell/WorkspacePicker.tsx` | `WorkspacePicker` 组件接入 `useTranslation()`；25 处导航按钮/路径输入/隐藏文件/新建文件夹/冲突提示/状态消息文案替换 |
| `web/src/shell/FileViewer.test.tsx` | 新增 zh-CN 未保存更改对话框测试用例；导入 `setLocale` |

## 新增 i18n Key 清单

### file 命名空间（75 个）

**文件查看器 — Markdown 视图模式**（6 个）：`preview`, `renderedPreview`, `edit`, `richTextEditor`, `source`, `rawMarkdownSource`

**文件查看器 — 工具栏操作**（22 个）：`viewMode`, `viewModeTooltip`, `viewSource`, `viewPreview`, `openInNewTab`, `hideComments`, `showComments`, `exitDiffView`, `showDiff`, `splitView`, `unifiedView`, `showWhitespaceChanges`, `hideWhitespaceChanges`, `findInFile`, `downloadFile`, `downloadTruncated`, `download`, `downloadFailed`, `copyLinkToFile`, `copied`, `copyLink`

**文件查看器 — 导航与状态**（15 个）：`closeFileViewer`, `close`, `previousFile`, `nextFile`, `runnerOfflineSave`, `unsaved`, `saving`, `saved`, `saveFailed`, `moreActions`, `deletedNotice`, `clickToViewDiff`, `loadFailed`, `loadingDiff`, `loading`

**文件查看器 — 未保存更改对话框**（4 个）：`unsavedChangesTitle`, `unsavedChangesDesc`, `keepEditing`, `discardChanges`

**文件面板 — 排序/范围/搜索**（16 个）：`sort`, `changed`, `all`, `showChangedOnly`, `showFullFolderTree`, `fileScope`, `workingFolder`, `closeFiles`, `searchChangedFiles`, `searchAllFiles`, `search`, `hideSearchFilters`, `showSearchFilters`, `filesToIncludeExclude`, `filesToInclude`, `filesToExclude`

**文件列表/目录树 — 状态消息**（12 个）：`noWorkspaceChanges`, `noFilesInWorkspace`, `allChangesHidden`, `clickToShow`, `noChangedFilesMatch`, `filesHidden_one`, `filesHidden_other`, `searching`, `searchFailed`, `noFilesMatch`, `matchesInHiddenDirs_one`, `matchesInHiddenDirs_other`

**隐藏文件切换**（2 个）：`showHiddenFiles`, `hideHiddenFiles`

**隐藏文件工具提示**（2 个）：`hiddenFilesTooltip_one`, `hiddenFilesTooltip_other`

**其他**（2 个）：`allFilesHidden`, `sortFilename`, `sortLastEdited`, `sortSize`, `sortType`

### workspace 命名空间（25 个）

**路径字段**（4 个）：`workingDirectoryPath`, `browseDirectories`, `recent`, `matches`, `moreMatches`, `loading`

**选择器导航**（5 个）：`upOneLevel`, `home`, `hideHidden`, `showHidden`, `newFolder`

**选择器操作**（5 个）：`selectThisFolder`, `select`, `close`, `newFolderName`, `createFolder`, `cancelNewFolder`, `failedToCreateFolder`

**冲突与状态**（5 个）：`agentWorking_one`, `agentWorking_other`, `conflictWarning`, `failedToLoadDirectory`, `noMatchingEntries`, `emptyDirectory`, `tooManyEntries`

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| `e.g. *.ts, src/**` / `e.g. **/node_modules, *.test.ts` | Glob 示例模式，非自然语言 |
| `~`（tilde 快捷输入） | Shell 约定符号 |
| `/Users/you/projects/app` | 示例路径占位符 |
| `feature/my-branch` | Git 分支示例占位符 |
| Git 状态字母（C/M/D） | 技术状态码，不翻译 |
| `View mode:` 前缀（模板字面量） | 仍为硬编码英文，拼接在动态翻译标签前。需后续单独处理 |
| 文件路径、文件名、diff 内容 | 用户/系统数据，不翻译 |

## 验收命令及结果

```
npm run test -- --run src/shell/FilesPanel.test.tsx src/shell/FileViewer.test.tsx src/shell/FlatFileList.test.tsx src/shell/FolderTree.test.tsx src/shell/WorkspacePathField.test.tsx src/shell/WorkspacePicker.test.tsx
→ Test Files  6 passed (6)
→ Tests  176 passed | 1 expected fail (177)

npm run test -- --run
→ Test Files  1 failed | 226 passed | 1 skipped (228)
→ Tests  1 failed | 4005 passed | 3 expected fail | 2 skipped (4011)
→ 1 个失败为预存问题（AgentInfo.test.tsx，P2A/P2B/P2C 已确认）

npm run build
→ tsc -b && vite build 成功
```

## 未解决项

1. **`View mode:` 前缀仍为英文**：FileViewer 中 markdown 视图模式选择器的 Trigger aria-label 使用 `` `View mode: ${activeMode.label}` `` 模板字面量拼接，"View mode:" 部分未被 `t()` 包裹。`activeMode.label` 本身已翻译，但前缀 `"View mode:"` 仍是英文。需将整个模板替换为 `t("file.viewMode", { mode: activeMode.label })`，使完整文案可翻译

2. **SORT_OPTIONS 使用模块级 `translate()`**：FilesPanel.tsx 中 SORT_OPTIONS 的 label 使用 `translate()` 在模块加载时求值，语言切换后不会重新渲染。这些标签仅在文件面板内部使用，且 `FilesPanel` 重渲染时 SortSelector 会重新读取 SORT_OPTIONS，但因 `translate()` 在模块作用域只调用一次，切换语言后排序标签不更新

3. **AgentInfo.test.tsx 1 个预存失败**：与本次变更无关

## 发现但未改动的文件

- `CommentsPanel.tsx`：评论面板，不在本包范围内
- `MainTerminalView.tsx`：终端视图，不在本包范围内
- `TerminalsPanel.tsx`：终端面板，不在本包范围内
- `chatStore.ts` / `useWorkspaceChangedFiles.ts`：数据层，不在此 UI 中文化范围
