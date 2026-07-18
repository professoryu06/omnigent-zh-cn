# P2H: 应用壳层、工作区与导航中文化工作包

你是 Omnigent Web UI 中文化的受限实现者。只完成本工作包，不得扩展范围。

## 目标

将应用壳层、工作区/项目面板、任务面板、命令面板、桌面与移动端抽屉、会话右侧导航中的静态用户文案接入 i18n。默认 `zh-CN` 时显示中文，切换到 `en` 时保持原英文；不得改变导航、项目操作、命令执行、任务状态、面板打开/关闭、拖拽、移动端交互或会话选择行为。

## 前置上下文

- 工作目录：`E:\agent team\Omnigent\source-zh-cn\web`
- 默认语言：`zh-CN`；旧测试环境通过 `src/test-setup.ts` 固定英文。
- 词典：`src/i18n/locales/en.ts`、`src/i18n/locales/zh-CN.ts`
- 组件内使用 `const { t } = useTranslation()`；模块级纯函数可使用 `translate()`，但禁止在模块加载时将翻译结果写入常量。
- 已完成 P2A 至 P2G。不要修改其范围外的文件。

## 允许修改的文件

- `src/shell/AppShell.tsx`
- `src/shell/WorkspacePanel.tsx`
- `src/shell/TodoPanel.tsx`
- `src/shell/CommandPalette.tsx`
- `src/shell/SessionRail.tsx`
- `src/shell/TitleBarServerPicker.tsx`
- `src/shell/MobilePanelDrawer.tsx`
- `src/shell/FilesPanelDrawer.tsx`
- `src/shell/railTabs.ts`
- `src/shell/sidebarNav.ts`
- `src/i18n/locales/en.ts`
- `src/i18n/locales/zh-CN.ts`
- 上述源文件各自现有的 `*.test.tsx` / `*.test.ts`

## 明确禁止

- 不修改后端、API、WebSocket、hooks、store、路由、持久化、`data-testid`、项目/会话/任务数据结构、命令行为、导航逻辑、面板状态、拖拽、快捷键或移动端手势。
- 不翻译项目名称、会话标题、文件名、路径、Git 分支/状态、智能体/模型/Harness 名称、服务器/主机名、任务内容、命令、快捷键字面值、错误原文或用户内容。
- 不修改 `Sidebar.tsx`、`settingsNav.tsx`、`ChatPage.tsx`、`NewChatDialog.tsx`、`FileViewer.tsx`、`FilesPanel.tsx`、终端、评论、编辑器、智能体/会话对话框相关文件、任意 CSS 或其他目录。
- 不增加依赖，不做格式化或结构性重构，不改变 CSS 布局、按钮显示条件、权限或交互条件。

## 本批应覆盖的用户文案

### 应用与导航壳层

- 打开/关闭/收起侧栏或右侧面板、文件/智能体/Shell/任务/日志等导航标签的 tooltip 和 `aria-label`。
- 服务端/主机选择器：连接、切换、加载、离线、错误和空状态。
- 桌面及移动端抽屉：打开/关闭、拖拽把手、标题和无内容提示。

### 工作区、项目与任务

- 工作区面板中的项目、会话、智能体、Shell、文件和相关空状态/操作。
- 项目创建、重命名、删除、归档、搜索、筛选、确认/取消、加载/错误提示。
- Todo 面板中的任务、完成/未完成、展开/收起、空状态、加载与状态提示。

### 命令面板与会话右侧导航

- 命令面板标题、搜索 placeholder、无匹配、分组标题、命令描述与关闭操作。
- 右侧会话导航中各 tab 的名称、tooltip、未读/数量提示与空状态。

## i18n 规则

1. 新增 key 仅使用 `app.*`、`workspacePanel.*`、`todo.*`、`commandPalette.*`、`rail.*`、`server.*` 命名空间。
2. 英文词典保持原英文含义。中文术语统一：Project=项目，Workspace=工作区，Task=任务，Command palette=命令面板，Rail=侧栏导航，Host=主机，Server=服务器，Shell=Shell。
3. 按钮、tooltip、`title`、`aria-label`、placeholder、空状态、确认对话框、加载/错误提示均必须使用 key。
4. 动态句子使用完整 key 加具名变量；禁止拆分拼接中文自然语言。保留变量中的项目名、路径、数量、快捷键、命令和服务器数据原样。
5. 模块级 tab/菜单/命令定义只能保存翻译 key 与非文案数据，渲染期调用 `t()`；语言切换必须更新当前打开的面板。

## 测试要求

1. 先在相邻测试中新增至少四个显式 `zh-CN` 断言，分别覆盖：
   - 工作区/项目面板的标题、空状态或一个操作；
   - Todo 面板；
   - 命令面板的标题、搜索 placeholder 或无匹配状态；
   - 会话导航/服务器选择器/移动抽屉之一的可访问文案。
2. 若修改模块级菜单、tab 或命令配置，至少增加一个 `I18nProvider` 下的中英运行时切换测试。
3. 先运行新增测试，确认改动前因旧英文或缺失 key 失败。
4. 实施最小改动后，运行：

```powershell
npm.cmd run test -- --run src/shell/AppShell.test.tsx src/shell/AppShell.subagent-nav.test.tsx src/shell/WorkspacePanel.test.tsx src/shell/TodoPanel.test.tsx src/shell/CommandPalette.test.tsx src/shell/sidebarNav.test.ts
```

5. 若为 `SessionRail.tsx`、`TitleBarServerPicker.tsx`、`MobilePanelDrawer.tsx`、`FilesPanelDrawer.tsx`、`railTabs.ts` 新增测试，追加对应测试文件；若没有相邻测试，至少确保 TypeScript 构建覆盖。
6. 再运行：

```powershell
npm.cmd run build
```

## 交付

完成后创建 `ops/handoffs/p2h-shell-workspace-navigation-deepseek-completion.md`，必须列出：

1. 实际修改文件和新增 key。
2. 保留英文原文的条目及理由。
3. 运行过的测试命令和完整统计结果。
4. 未处理的可见英文、原因及其所属最终验收阶段。
