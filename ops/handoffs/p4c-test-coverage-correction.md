# P4C-R: 工作区与会话导航中文化验收测试补齐

## 背景

P4C 的源代码和双词典已完成，且相关回归测试与构建通过；但完成报告只运行了
`Sidebar.test.tsx` 和 `MarkdownRichTextViewer.test.tsx`，没有新增本工作包要求的中文
验收断言。不能只以 `t("...")` 的静态替换作为验收依据。

## 目标

只增加或扩展测试，证明 P4C 新增的中文翻译会在真实组件渲染中出现。不要修改生产
组件、字典、样式、接口、hooks 或业务行为，除非测试揭示确定的生产缺陷。

## 允许修改

- `web/src/shell/MarkdownRichTextViewer.test.tsx`
- `web/src/shell/FolderTree.test.tsx`
- `web/src/shell/Sidebar.test.tsx` 或现有 `Sidebar.*.test.tsx`
- `web/src/shell/NewChatDialog.test.tsx` 或 `NewChatDialog.flow.test.tsx`
- `web/src/shell/ForkSessionDialog.test.tsx`
- 仅在确有必要时可修改对应组件和 `en.ts` / `zh-CN.ts`，并在报告中说明原因。

## 必须覆盖

每个区域至少一条 `setLocale("zh-CN")` 下的可见文本、role 名称或 aria-label 断言；
合计至少 8 条新增中文断言。

1. `MarkdownRichTextViewer`
   - 覆盖“复制”或“已复制”；以及“此文件在您编辑期间被外部修改。”、
     “保留我的版本”、“加载最新版本”、“执行器离线”中至少一个状态。
2. `FolderTree`
   - 覆盖空工作区“工作区中没有文件”，或搜索失败时中文回退错误文本。
3. `Sidebar`
   - 覆盖最后会话移出项目的确认对话框，至少断言“从项目中移除会话？”以及操作按钮。
   - 可额外覆盖“不可逆”。
4. `NewChatDialog`
   - 在可触发的受管沙箱禁用状态下，覆盖“新建沙箱”及“为什么新建沙箱不可用”的
     aria-label；或覆盖“仓库分支”。
5. `ForkSessionDialog`
   - 覆盖源 agent 缺少显示名时的“原始 Agent”回退值。

## 约束

- 保持 `setLocale("en")` 的 `beforeEach` / `afterEach` 清理，禁止让语言状态污染其他测试。
- 测试通过公开 UI 行为，不测试 `t()` 调用次数或私有实现细节。
- 真实路径、分支名、URL、agent 名称、CLI 命令等动态/技术数据不应被翻译；测试也不得要求
  翻译它们。
- 不新增快照大文件，不调整测试超时，不跳过失败测试。

## 验收命令

在 `E:\agent team\Omnigent\source-zh-cn\web` 执行：

```powershell
npm.cmd run test -- --run src/shell/Sidebar.test.tsx src/shell/MarkdownRichTextViewer.test.tsx src/shell/FolderTree.test.tsx src/shell/ForkSessionDialog.test.tsx src/shell/NewChatDialog.test.tsx
npm.cmd run build
npm.cmd run test -- --run
```

全量测试唯一允许的失败仍是既有 `AgentInfo.test.tsx` 中 `1K` 格式化基线失败；不得引入
新的失败。

## 交付

完成后写入：
`ops/handoffs/p4c-test-coverage-correction-deepseek-completion.md`

报告须列出：修改测试文件、每条新增中文断言、目标测试数、构建结果、全量测试结果，以及
是否出现任何非基线失败。
