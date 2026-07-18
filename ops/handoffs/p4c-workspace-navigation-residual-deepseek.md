# P4C 工作包：工作区与会话导航残留中文化

## 项目与目标

- 工作目录：`E:\agent team\Omnigent\source-zh-cn`
- 目标：处理全局审计发现的工作区与会话导航残余静态英文，保持新会话、分叉会话、项目移除和文件编辑行为不变。

## 允许修改

- `web/src/shell/ForkSessionDialog.tsx`
- `web/src/shell/MarkdownRichTextViewer.tsx`
- `web/src/shell/FolderTree.tsx`
- `web/src/shell/Sidebar.tsx`
- `web/src/shell/NewChatDialog.tsx`
- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`
- 上述组件已有对应测试文件；若没有对应测试，只能创建同名 `*.test.tsx` 测试文件。

## 禁止修改

- 不改 API、hooks、store、路由、新建会话参数、分叉/恢复逻辑、项目管理逻辑、文件保存逻辑、CSS、DOM 结构、`data-testid`。
- 不改其它组件，不做全局重构。
- 不翻译项目名、目录/文件路径、模型/执行器名、用户输入、后端错误、技术标识和动态文件内容。

## 已定位的最低覆盖项

1. `ForkSessionDialog`：Host 静态标签及相关无障碍文字。
2. `MarkdownRichTextViewer`：文件在编辑期间被外部修改的固定提示。
3. `FolderTree`：工作区无文件空状态。
4. `Sidebar`：从项目移除的确认对话框。
5. `NewChatDialog`：New Sandbox 及同一局部区域的其它静态 UI 文案、tooltip、aria-label、placeholder。

## 实施规则

1. 采用 `useTranslation()`/`t()`，双词典 key 必须一一对应。
2. 模块级数组、映射或配置只能保存稳定 key/原始数据；不得模块加载期缓存翻译结果。
3. 动态数据仅作为插值值传入，例如文件名、项目名、主机名；不得把数据本身翻译。
4. 不改变确认/取消、保存、创建沙箱、分叉会话等事件处理和条件分支。

## 测试要求

1. 增加至少 8 条 zh-CN 断言，五个组件均需覆盖。
2. 至少一条 I18nProvider 运行时切换测试，避免重新挂载。
3. 不删除或放宽既有测试。

## 验收命令

在 `web` 目录执行对应的测试文件，并执行：

```powershell
npm.cmd run build
```

全量测试中的 `AgentInfo.test.tsx:383` 的 `1K` 断言是既有基线失败，不属于 P4C。

## 完成报告

完成后创建：

`ops/handoffs/p4c-workspace-navigation-residual-deepseek-completion.md`

报告列出修改文件、key 数、中文覆盖点、目标测试、构建、全量回归及遗留项。
