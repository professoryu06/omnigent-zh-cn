# P4C-R2: P4C 新增翻译的定向验收测试

## R1 复核结论

R1 实际新增 5 条中文断言，低于至少 8 条的要求。且下列三条没有覆盖 P4C 新增翻译：

- `ForkSessionDialog` 的“克隆会话”；
- `NewChatDialog` 的“有什么可以帮你的？”；
- `Sidebar` 的“会话”。

它们是此前已有的翻译，不能作为本工作包验收证据。

## 目标

在现有 R1 测试基础上，新增 **至少 8 条** 针对 P4C 新增 key 的中文断言。可保留 R1
测试，但不能将其计入以下 8 条。只改测试；不改生产代码、字典、样式、接口或测试基础设施。

## 强制验收断言

以下 8 条都必须存在，在 `setLocale("zh-CN")` 下通过公开 UI 渲染或交互断言：

1. `MarkdownRichTextViewer`：只读按钮文本或 title 为“复制”。
2. `MarkdownRichTextViewer`：触发外部更新冲突后出现“保留我的版本”。
3. `MarkdownRichTextViewer`：同一冲突状态出现“加载最新版本”。
4. `FolderTree`：空工作区出现“工作区中没有文件”。
5. `Sidebar`：最后一条会话移出项目的确认弹窗标题为“从项目中移除会话？”。
6. `Sidebar`：同一弹窗的 destructive 操作按钮为“从项目中移除”。
7. `NewChatDialog`：受管沙箱关闭、且 docs 链接存在时，禁用项文字为“新建沙箱”。
8. `NewChatDialog`：同一状态的帮助按钮 aria-label 为“为什么新建沙箱不可用”。

再额外完成以下两项中的至少一项：

- `FolderTree` 搜索失败且错误不是 `Error` 实例时，显示中文未知错误回退；
- `ForkSessionDialog` 源 agent 缺失 display name、base name 与 name 时，选择器显示“原始 Agent”。

## 禁止计入

下列旧翻译可保留，但不得计入 R2 的断言数量：

- “克隆会话”
- “有什么可以帮你的？”
- “会话”

## 测试要求

- 新增用例均需 `afterEach(() => setLocale("en"))` 或复用已有等价清理。
- 断言通过 role、文本、title 或 aria-label 等可见行为完成，禁止读取字典对象、mock `t()` 或
  断言实现细节。
- 不翻译并且不把 URL、分支名、真实 agent 名、路径与命令作为中文化目标。

## 验收命令

在 `E:\agent team\Omnigent\source-zh-cn\web` 执行：

```powershell
npm.cmd run test -- --run src/shell/Sidebar.test.tsx src/shell/MarkdownRichTextViewer.test.tsx src/shell/FolderTree.test.tsx src/shell/ForkSessionDialog.test.tsx src/shell/NewChatDialog.test.tsx
npm.cmd run build
npm.cmd run test -- --run
```

全量测试仅允许既有 `AgentInfo.test.tsx` 的 `1K` 基线失败，不能有新增失败。

## 交付

完成报告必须写入：
`ops/handoffs/p4c-test-coverage-correction-v2-deepseek-completion.md`

报告逐条列出上述 8 个强制断言的测试文件、测试名、断言文本；不要用汇总数字替代明细。
