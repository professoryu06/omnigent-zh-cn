# P2G: 智能体管理与会话生命周期中文化工作包

你是 Omnigent Web UI 中文化的受限实现者。只完成本工作包，不得扩展范围。

## 目标

将智能体管理、子智能体视图，以及会话分支、恢复、重连和执行器休眠提示中的静态用户文案接入 i18n。默认 `zh-CN` 时显示中文，切换到 `en` 时保持原英文；不得改变智能体配置、会话所有权、分支、工作目录、重连、执行器状态或请求行为。

## 前置上下文

- 工作目录：`E:\agent team\Omnigent\source-zh-cn\web`
- 默认语言：`zh-CN`；旧测试环境通过 `src/test-setup.ts` 固定英文。
- 词典：`src/i18n/locales/en.ts`、`src/i18n/locales/zh-CN.ts`
- 组件内使用 `const { t } = useTranslation()`；模块级纯函数可使用 `translate()`，但禁止在模块加载时把翻译结果写入常量。
- 已完成 P2A 至 P2F。不要修改其范围外的文件。

## 允许修改的文件

- `src/shell/AddAgentDialog.tsx`
- `src/shell/CreateAgentDialog.tsx`
- `src/shell/SwitchAgentDialog.tsx`
- `src/shell/SubagentsPanel.tsx`
- `src/shell/SubagentsGraphView.tsx`
- `src/shell/ForkSessionDialog.tsx`
- `src/shell/ResumeWithDirectoryDialog.tsx`
- `src/shell/ReconnectSessionDialog.tsx`
- `src/shell/RunnerAsleepHint.tsx`
- `src/i18n/locales/en.ts`
- `src/i18n/locales/zh-CN.ts`
- 上述源文件各自现有的 `*.test.tsx` / `*.test.ts`

## 明确禁止

- 不修改后端、API、WebSocket、hooks、store、路由、持久化、`data-testid`、智能体定义、模型/Harness 名称、权限、会话所有权、分支生成、目录选择、重连逻辑、图布局或轮询逻辑。
- 不翻译服务端返回的智能体名称、模型名称、Harness 名称、主机名、会话 ID、分支名、仓库 URL、文件路径、Git ref、命令、错误原文、用户输入或用户会话标题。
- 不修改 `NewChatDialog.tsx`、`ChatPage.tsx`、`Sidebar.tsx`、`AppShell.tsx`、`WorkspacePanel.tsx`、`CommandPalette.tsx`、终端/文件/评论相关文件、任何 CSS 或其他目录。
- 不增加依赖，不做格式化或结构性重构，不改变 CSS 布局、按钮显示条件、访问权限或交互条件。

## 本批应覆盖的用户文案

### 智能体管理

- 添加/创建智能体对话框：标题、字段标签、placeholder、保存/取消、错误、服务器/主机选择、名称/描述、工具和策略说明。
- 切换智能体对话框：当前智能体、选择智能体、切换说明、确认/取消、加载/错误和只读提示。
- 子智能体面板与图视图：智能体列表、添加智能体、状态、图/列表切换、加载/空状态、折叠/展开、失败提示。

### 会话生命周期

- 分支会话：标题、分支/工作树说明、目录/主机选择、确认/取消、加载/错误、只读与风险提示。
- 使用其他目录恢复会话：标题、当前/新工作目录说明、选择目录、继续/取消、离线主机或无法恢复的提示。
- 重连对话框与执行器休眠提示：重连、取消、正在重连、主机/执行器离线或休眠的解释和操作提示。

## i18n 规则

1. 新增 key 仅使用 `agent.*`、`subagent.*`、`session.*` 三个命名空间；动态句子使用完整 key 与具名变量，例如 `t("session.reconnectFailed", { message })`。
2. 英文词典保持原英文含义。中文术语统一：Agent=智能体，Sub-agent=子智能体，Harness=执行器，Session=会话，Fork=分支会话，Reconnect=重新连接，Runner=执行器，Worktree=Git 工作树。
3. 按钮、tooltip、`title`、`aria-label`、placeholder、空状态、确认对话框、错误与风险提示都必须使用 key。
4. 不得拆分和拼接中文自然语言句子；必须用一个完整 key 加具名变量。
5. 可见菜单或状态配置若位于模块级，只能保存翻译 key 与非文案数据，在组件/Hook 渲染期调用 `t()`。

## 测试要求

1. 先在相邻测试中新增至少三个显式 `zh-CN` 断言，分别覆盖：
   - 智能体添加、创建或切换对话框中的一个核心按钮/placeholder；
   - 子智能体面板或图视图的标题/空状态；
   - 分支、恢复或重连对话框中的一个确认操作/错误提示。
2. 若修改模块级菜单或状态配置，额外增加 `I18nProvider` 下的中英运行时切换测试。
3. 先运行新增测试，确认改动前因旧英文或缺失 key 失败。
4. 实施最小改动后，运行：

```powershell
npm.cmd run test -- --run src/shell/AddAgentDialog.test.tsx src/shell/SwitchAgentDialog.test.tsx src/shell/SubagentsPanel.test.tsx src/shell/SubagentsGraphView.test.tsx src/shell/ForkSessionDialog.test.tsx src/shell/ResumeWithDirectoryDialog.test.tsx src/shell/ReconnectSessionDialog.test.tsx
```

5. 若为 `CreateAgentDialog.tsx` 或 `RunnerAsleepHint.tsx` 新增测试，追加对应测试文件；若当前没有相邻测试，至少保证 TypeScript 编译覆盖。
6. 再运行：

```powershell
npm.cmd run build
```

## 交付

完成后创建 `ops/handoffs/p2g-agents-session-lifecycle-deepseek-completion.md`，必须列出：

1. 实际修改文件和新增 key。
2. 保留英文原文的条目及理由。
3. 运行过的测试命令和完整统计结果。
4. 未处理的可见英文、原因及其所属后续批次。
