# P2D: 文件工作区中文化工作包

你是 Omnigent Web UI 中文化的受限实现者。只完成本工作包，不得扩展范围。

## 目标

将文件工作区中面向用户的静态文案改为 `file.*` 或 `workspace.*` i18n key。默认 `zh-CN` 时显示中文，切换到 `en` 时保持原英文。不得改变文件读取、保存、下载、导航、编辑、评论、路径选择或 API 的行为。

## 前置上下文

- 工作目录：`E:\agent team\Omnigent\source-zh-cn\web`
- 默认语言：`zh-CN`；旧测试环境通过 `src/test-setup.ts` 固定英文。
- 词典：`src/i18n/locales/en.ts`、`src/i18n/locales/zh-CN.ts`
- 使用方式：组件内使用 `const { t } = useTranslation()`；模块级纯函数使用 `translate()`，但不得在模块加载时把翻译结果写入常量。
- 已完成 P2A、P2B、P2C。不要修改其范围外的文件。

## 允许修改的文件

- `src/shell/FilesPanel.tsx`
- `src/shell/FlatFileList.tsx`
- `src/shell/FolderTree.tsx`
- `src/shell/FileDownloadButton.tsx`
- `src/shell/FileViewer.tsx`
- `src/shell/WorkspacePathField.tsx`
- `src/shell/WorkspacePicker.tsx`
- `src/i18n/locales/en.ts`
- `src/i18n/locales/zh-CN.ts`
- 上述源文件各自现有的 `*.test.tsx` / `*.test.ts`

## 明确禁止

- 不修改后端、API、WebSocket、hooks、store、路由、持久化、`data-testid`、模型/Harness 名称、路径值或文件内容。
- 不翻译用户文件名、文件路径、代码、diff 内容、Git 状态值、命令、错误原文或评论内容。
- 不修改 `CommentsPanel.tsx`、`MainTerminalView.tsx`、`TerminalsPanel.tsx`、`ChatPage.tsx`，也不修改任何其他目录。
- 不增加依赖，不做格式化或重构，不变更 CSS 布局和交互条件。

## 本批应覆盖的用户文案

### 文件列表与目录树

- 文件、文件夹、已更改、全部、搜索、排序、加载、空状态、刷新、显示/隐藏隐藏文件。
- 展开/折叠目录、上一层、返回、打开/关闭文件、下载及下载失败。

### 文件查看器

- 关闭查看器、上一/下一文件、更多操作、视图模式、行号、换行、只读、加载文件或 diff、加载失败。
- 保存状态：未保存、保存中、已保存、保存失败、Runner 离线时的保存说明。
- 已删除文件、查看 diff、未保存更改确认对话框、继续编辑、放弃更改。

### 工作目录选择

- 工作目录路径、浏览目录、最近使用、匹配项、加载、继续输入以缩小范围、新建目录、显示/隐藏隐藏文件、选择与取消。

## i18n 规则

1. 新增 key 只使用 `file.*`、`workspace.*` 命名空间；动态句子使用完整 key 加具名变量，例如 `t("file.loadFailed", { reason })`。
2. 英文词典必须保持现有英文含义；中文术语统一使用：File=文件，Folder=文件夹，Workspace=工作目录，Diff=差异，Unsaved=未保存，Runner=执行器。
3. `aria-label`、tooltip、按钮、空状态、确认对话框均属于可见/可访问文案，必须同样使用 key。
4. 不得将 `t()` 的返回值放在模块级常量中；语言切换后可见文案必须随 React 重渲染更新。

## 测试要求

1. 先在相邻测试中新增一个显式 `zh-CN` 断言，覆盖下列任一核心场景：文件下载、保存状态、未保存更改对话框或工作目录选择。
2. 先运行该测试并确认因缺少 key 或旧英文而失败。
3. 实施最小改动后，运行：

```powershell
npm.cmd run test -- --run src/shell/FilesPanel.test.tsx src/shell/FileViewer.test.tsx src/shell/FlatFileList.test.tsx src/shell/FolderTree.test.tsx src/shell/WorkspacePathField.test.tsx src/shell/WorkspacePicker.test.tsx
```

4. 再运行：

```powershell
npm.cmd run build
```

## 交付

完成后创建 `ops/handoffs/p2d-files-workspace-deepseek-completion.md`，必须列出：

1. 实际修改的文件和新增 key。
2. 保留英文原文的条目及理由。
3. 运行过的测试命令和完整统计结果。
4. 未处理的可见英文、原因及其所属后续批次。
