# P2E: 终端与 Shell 中文化工作包

你是 Omnigent Web UI 中文化的受限实现者。只完成本工作包，不得扩展范围。

## 目标

将终端和 Shell 区域中面向用户的静态文案改为 `terminal.*` i18n key。默认 `zh-CN` 时显示中文，切换到 `en` 时保持原英文。不得改变 PTY 连接、终端创建、关闭、选择、状态计算、权限、轮询或布局行为。

## 前置上下文

- 工作目录：`E:\agent team\Omnigent\source-zh-cn\web`
- 默认语言：`zh-CN`；旧测试环境通过 `src/test-setup.ts` 固定英文。
- 词典：`src/i18n/locales/en.ts`、`src/i18n/locales/zh-CN.ts`
- 使用方式：组件内使用 `const { t } = useTranslation()`；不得在模块加载时把 `t()` 或 `translate()` 的结果写入常量。
- 已完成 P2A（新建会话）、P2B（侧栏设置）、P2C（聊天）和 P2D（文件工作区）。不要修改这些批次范围内的文件。

## 允许修改的文件

- `src/shell/MainTerminalView.tsx`
- `src/shell/TerminalsPanel.tsx`
- `src/shell/NewTerminalButton.tsx`
- `src/shell/terminalStatus.tsx`
- `src/shell/InlineTerminalsSection.tsx`
- `src/i18n/locales/en.ts`
- `src/i18n/locales/zh-CN.ts`
- 上述源文件各自现有的 `*.test.tsx` / `*.test.ts`

## 明确禁止

- 不修改后端、API、WebSocket、hooks、store、路由、持久化、`data-testid`、终端 ID、终端名称、会话名称、Shell 名称、命令、路径或终端输出。
- 不翻译 `bash`、`zsh`、`fish`、`$SHELL`、`PTY`、`TerminalView`，也不翻译由服务端返回的名称、错误原文或终端内容。
- 不修改 `ExecutionLogsPanel.tsx`、`SessionRail.tsx`、`ChatPage.tsx`、`WorkspacePanel.tsx`、`CommentsPanel.tsx`、Markdown/代码编辑器、任何 CSS 或其他目录。
- 不增加依赖，不做格式化或重构，不改变 CSS 布局、访问权限、按钮显示条件或交互条件。

## 本批应覆盖的用户文案

### 终端主视图与终端面板

- `Shells`、关闭面板、关闭 Shell、无可用终端。
- 所有终端状态：`Active`、`Idle`、`Connecting`、`Error`、`Closed`，包括可见标签、`aria-label` 与 `title`。

### 新建 Shell 控件

- `New shell` 的按钮、tooltip、`aria-label`。
- 终端创建失败：`Failed: {{message}}`。
- Shell 选择器：`Choose shell`。
- 默认 Shell 后缀：`{{name}} (default)`。只翻译括号中的 `default`，不得改动 Shell 名称。

## i18n 规则

1. 新增 key 只使用 `terminal.*` 命名空间；动态句子使用完整 key 加具名变量，例如 `t("terminal.createFailed", { message })`。
2. 英文词典必须保持现有英文含义；中文术语统一：Terminal=终端，Shell=Shell，Active=活跃，Idle=空闲，Connecting=连接中，Closed=已关闭。
3. `aria-label`、`title`、tooltip、按钮、空状态均属于可见/可访问文案，必须同样使用 key。
4. `STATUS_CONFIG` 不得保存已翻译的 `label`。它可保存 key 和 CSS class，在 `TerminalStatusBadge` 的渲染期调用 `t()`，确保语言切换立刻更新。
5. Shell 名称、会话名称与服务端错误须作为变量原样保留；不得把中文拼接进变量本身。

## 建议 key

可按实际需要增减，但保持一致：

- `terminal.shells`
- `terminal.close`
- `terminal.closeShell`
- `terminal.noneAvailable`
- `terminal.newShell`
- `terminal.chooseShell`
- `terminal.defaultShell`
- `terminal.createFailed`
- `terminal.statusActive`
- `terminal.statusIdle`
- `terminal.statusConnecting`
- `terminal.statusError`
- `terminal.statusClosed`

## 测试要求

1. 先在相邻测试中新增至少两个显式 `zh-CN` 断言：
   - 终端状态标签在 `zh-CN` 为中文，并且语言切换后不会保留模块级英文；
   - 新建 Shell 控件或终端面板有一个中文可访问文案断言。
2. 先运行新增测试，并确认改动前因旧英文或缺失 key 失败。
3. 实施最小改动后，运行：

```powershell
npm.cmd run test -- --run src/shell/MainTerminalView.test.tsx src/shell/TerminalsPanel.test.tsx src/shell/NewTerminalButton.test.tsx src/shell/terminalStatus.test.tsx src/shell/InlineTerminalsSection.test.tsx
```

4. 再运行：

```powershell
npm.cmd run build
```

## 交付

完成后创建 `ops/handoffs/p2e-terminals-deepseek-completion.md`，必须列出：

1. 实际修改文件和新增 key。
2. 保留英文原文的条目及理由。
3. 运行过的测试命令和完整统计结果。
4. 未处理的可见英文、原因及其所属后续批次。
