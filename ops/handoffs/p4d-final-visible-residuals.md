# P4D: 全局扫描发现的最后可见英文残留

## 背景

P4C 已通过真实 UI 验收。全局静态扫描发现少量用户可见英文仍在源代码中；本包仅处理
以下明确范围，不进行扩展重构。

## 允许修改

- `web/src/pages/ChatPage.tsx`
- `web/src/components/ui/dialog.tsx`
- `web/src/shell/ForkSessionDialog.tsx`
- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`
- 以上组件对应的现有测试；必要时新增同目录测试文件。

## 必须处理的可见字符串

### 1. `ChatPage.tsx`

将下列真正显示给用户的硬编码字符串接入 i18n。优先复用已有 `chat.*` key；不存在时新增
语义明确的 `chat.*` key，并同步双词典。

- 连接横幅：`Connecting…`
- 移动端视图切换：`Chat`、`Terminal`
- 移动端复制提示：`Copied to clipboard`
- 中断状态：`Interrupted`
- 计划模式状态/按钮：`Plan mode`、`Plan`
- 拖放覆盖层：`Drop files here`
- 模型选择器分组：`Agents`、`Models`、`Effort`

要求：组件内使用 `useTranslation()`；不得在模块加载期调用 `t()` 并把翻译结果写入常量。
对异步回调，使用现有项目中可支持语言切换的方式（例如调用时的 `translate()` 或 ref），不要
捕获过期语言。

### 2. `components/ui/dialog.tsx`

将两处通用 `Close`（隐藏的可访问文本与页脚关闭按钮）接入 i18n。此基础组件需要在运行时
响应语言切换；不要把翻译结果作为模块级常量。

### 3. `ForkSessionDialog.tsx`

将编码来源区域的静态 `Host` 标签接入 i18n。名称可为 `session.host` 或同等清晰的命名空间。

## 不在范围内

以下为技术标识或动态数据，必须保持原样：

- `HTTP`、`stdio`、MCP、Codex、Claude、模型 ID；
- URL、文件路径、分支名、命令、服务器返回的 host 状态与 agent 名；
- TypeScript 类型、注释、测试中的英文 fixture 数据；
- `BrowserPane.tsx` 里的接口方法、类型和桥接字段。

## 测试要求

新增至少 10 条 zh-CN 的真实 UI 断言，覆盖所有三个源文件：

- `ChatPage` 至少 6 条，必须含移动端 Chat/Terminal、复制 toast、拖放覆盖层和一个状态/分组；
- `dialog.tsx` 至少 2 条，验证隐藏 close 的可访问名称和 footer Close 按钮；
- `ForkSessionDialog` 至少 1 条，验证 Host 标签；
- 额外至少 1 条验证运行时由英文切至中文后，相关已挂载组件更新，不卸载重挂。

测试只能通过 `screen` / DOM 的文本、role、title、aria-label 和实际交互断言。禁止 `translate()`
字典直读、mock `t()` 或检查 locale 文件内容。每个 zh-CN 测试结束后恢复 `setLocale("en")`。

## 验收

在 `E:\agent team\Omnigent\source-zh-cn\web` 运行相关测试、构建和全量测试：

```powershell
npm.cmd run test -- --run src/pages/ChatPage.composer.test.tsx src/pages/ChatPage.indicators.test.tsx src/components/ui/dialog.test.tsx src/shell/ForkSessionDialog.test.tsx
npm.cmd run build
npm.cmd run test -- --run
```

全量仅允许已知的 `AgentInfo.test.tsx` `1K` 基线失败；不得新增失败。

## 交付

完成报告：
`ops/handoffs/p4d-final-visible-residuals-deepseek-completion.md`

报告逐条列出：每个替换的源字符串、所用 i18n key、中文文案、对应真实 UI 测试，以及三条验收
命令的结果。
