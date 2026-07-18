# P2F: 执行日志、评论与编辑器中文化工作包

你是 Omnigent Web UI 中文化的受限实现者。只完成本工作包，不得扩展范围。

## 目标

将执行日志、评论和代码/Markdown 编辑器工具区的静态用户文案接入 i18n。默认 `zh-CN` 时显示中文，切换到 `en` 时保持原英文；不得改变日志加载、评论创建/回复/解决、代码编辑、查找、Markdown 编辑、表格操作、保存、快捷键或访问控制行为。

## 前置上下文

- 工作目录：`E:\agent team\Omnigent\source-zh-cn\web`
- 默认语言：`zh-CN`；旧测试环境通过 `src/test-setup.ts` 固定英文。
- 词典：`src/i18n/locales/en.ts`、`src/i18n/locales/zh-CN.ts`
- 组件内使用 `const { t } = useTranslation()`；模块级纯函数可使用 `translate()`，但绝不能将翻译结果存到模块级常量。
- 已完成 P2A、P2B、P2C、P2D、P2E。不要修改其范围外的文件。

## 允许修改的文件

- `src/shell/ExecutionLogsPanel.tsx`
- `src/shell/CommentsPanel.tsx`
- `src/shell/CodeViewer.tsx`
- `src/shell/HtmlCommentViewer.tsx`
- `src/shell/MarkdownCommentPlugin.tsx`
- `src/shell/MarkdownEditorToolbar.tsx`
- `src/shell/TableBubbleMenu.tsx`
- `src/shell/useMonacoCommentLayer.tsx`
- `src/i18n/locales/en.ts`
- `src/i18n/locales/zh-CN.ts`
- 上述源文件各自现有的 `*.test.tsx` / `*.test.ts`

## 明确禁止

- 不修改后端、API、WebSocket、hooks、store、路由、持久化、`data-testid`、评论数据结构、编辑器扩展、Markdown/HTML 解析、表格编辑行为、保存行为或快捷键绑定。
- 不翻译用户评论正文、代码、Markdown 内容、HTML 内容、文件名、路径、Git 状态、终端/执行日志 JSON、错误原文、模型/智能体名称或命令。
- 不修改 `FileViewer.tsx`、`MonacoCodeEditor.tsx`、`WorkspacePanel.tsx`、`ChatPage.tsx`、`SessionRail.tsx`、`Sidebar.tsx`、终端相关文件、任意 CSS 或其他目录。
- 不增加依赖，不做格式化或结构性重构，不改变 CSS 布局、按钮显示条件、权限或交互条件。

## 本批应覆盖的用户文案

### 执行日志

- `Execution logs`、关闭、加载、加载更多、加载失败、无日志项、主会话标签。
- 子会话的服务端标题/工具名/ID 必须原样显示，不能翻译。

### 评论与代码查找

- 评论面板的评论列表状态、添加/回复/取消/提交/解决/重新打开/全部处理、删除、复制评论链接、加载/错误/空状态。
- 内嵌评论入口与“附加到智能体”类操作。
- 代码查看器的 HTML 预览、缩放、查找输入框、上一处/下一处匹配、关闭查找、未找到匹配项。

### Markdown 与表格工具栏

- 富文本/Markdown 工具栏的标题和 `aria-label`：插入表格、行列数、对齐、撤销/重做、段落/标题、引用、粗体/斜体/删除线、行内代码、列表、任务列表、复制和保存状态。
- 表格行/列操作按钮、菜单项与确认提示。
- 保留快捷键字面值（例如 `⌘Z`），只翻译命令描述；保留 Markdown、HTML、JSON、URL、代码和表格内容本身。

## i18n 规则

1. 新增 key 仅使用 `logs.*`、`comment.*`、`editor.*` 三个命名空间；动态句子使用完整 key 与具名变量，例如 `t("logs.loadFailed", { message })`。
2. 英文词典必须保持现有英文含义。中文术语统一：Execution logs=执行日志，Comment=评论，Resolve=标记为已解决，Reopen=重新打开，Find=查找，Markdown=Markdown，HTML=HTML，Table=表格。
3. 按钮、tooltip、`title`、`aria-label`、placeholder、空状态、确认/错误信息都必须使用 key。
4. 含插值的中文句子必须通过完整 key 实现；禁止将中文句子拆成字符串片段拼接。
5. 保存状态若来自模块级配置，配置只能保存 key 和非文案数据，渲染期调用 `t()`。

## 测试要求

1. 先在相邻测试中新增至少三个显式 `zh-CN` 断言，分别覆盖：
   - 执行日志的标题或加载/空状态；
   - 评论输入框 placeholder 或评论操作的可访问文案；
   - Markdown 工具栏或表格菜单的 tooltip/`aria-label`。
2. 如果修改了模块级菜单/状态配置，再增加一次 `I18nProvider` 下的运行时中英切换测试。
3. 先运行新增测试并确认改动前因旧英文或缺失 key 失败。
4. 实施最小改动后，运行：

```powershell
npm.cmd run test -- --run src/shell/ExecutionLogsPanel.test.tsx src/shell/CommentsPanel.test.tsx src/shell/CodeViewer.test.tsx src/shell/HtmlCommentViewer.test.tsx src/shell/MarkdownCommentPlugin.test.tsx src/shell/MarkdownEditorToolbar.test.tsx src/shell/MarkdownEditorToolbar.tableAlign.test.tsx src/shell/TableBubbleMenu.test.tsx src/shell/useMonacoCommentLayer.test.tsx
```

5. 再运行：

```powershell
npm.cmd run build
```

## 交付

完成后创建 `ops/handoffs/p2f-review-editor-deepseek-completion.md`，必须列出：

1. 实际修改文件和新增 key。
2. 保留英文原文的条目及理由。
3. 运行过的测试命令和完整统计结果。
4. 未处理的可见英文、原因及其所属后续批次。
