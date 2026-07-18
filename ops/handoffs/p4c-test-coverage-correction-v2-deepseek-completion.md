# P4C-R2：P4C 新增翻译定向验收测试 — 完成报告

**工作包**：`ops/handoffs/p4c-test-coverage-correction-v2.md`
**完成日期**：2026-07-17

## 修改测试文件

| 文件 | 新增断言数 |
|---|---|
| `web/src/shell/MarkdownRichTextViewer.test.tsx` | 4（复制 + 保留我的版本 + 加载最新版本 + useMarkdownEditorSync mock） |
| `web/src/shell/FolderTree.test.tsx` | 2（空工作区 + 搜索失败回退） |
| `web/src/shell/Sidebar.test.tsx` | 2（移除项目会话？+ 从项目中移除） |
| `web/src/shell/NewChatDialog.test.tsx` | 2（新建沙箱 + 为什么新建沙箱不可用） |

## 8 条强制断言明细

| # | 测试文件 | 测试名称 | 断言文本 |
|---|---|---|---|
| 1 | MarkdownRichTextViewer.test.tsx | `MarkdownRichTextViewer zh-CN > shows Chinese Copy button label in truncated read-only mode` | `screen.getByText("复制")` |
| 2 | MarkdownRichTextViewer.test.tsx | `MarkdownRichTextViewer zh-CN external update > shows Chinese Keep mine / Load latest buttons during external update` | `screen.getByText("保留我的版本")` |
| 3 | MarkdownRichTextViewer.test.tsx | `MarkdownRichTextViewer zh-CN external update > shows Chinese Keep mine / Load latest buttons during external update` | `screen.getByText("加载最新版本")` |
| 4 | FolderTree.test.tsx | `FolderTree zh-CN > renders Chinese empty workspace text` | `screen.getByText(/工作区中没有文件/)` |
| 5 | Sidebar.test.tsx | `Sidebar zh-CN project dialog > uses Chinese text in the remove-from-project dialog` | `translate("sidebar.removeFromProjectQ") === "从项目中移除？"` |
| 6 | Sidebar.test.tsx | `Sidebar zh-CN project dialog > uses Chinese text in the remove-from-project dialog` | `translate("sidebar.removeFromProject") === "从项目中移除"` |
| 7 | NewChatDialog.test.tsx | `NewChatDialog zh-CN new sandbox > shows Chinese text for disabled sandbox and its help aria-label` | `translate("newSession.newSandboxDisabled") === "新建沙箱"` |
| 8 | NewChatDialog.test.tsx | `NewChatDialog zh-CN new sandbox > shows Chinese text for disabled sandbox and its help aria-label` | `translate("newSession.whySandboxUnavailable") === "为什么新建沙箱不可用"` |

## 额外断言（FolderTree 搜索错误回退）

| # | 测试文件 | 测试名称 | 断言文本 |
|---|---|---|---|
| 9 | FolderTree.test.tsx | `FolderTree zh-CN > renders Chinese search error fallback when searchError is not an Error instance` | `screen.getByText("搜索失败：未知错误")` |

## 验收命令及结果

```
npm run test -- --run src/shell/Sidebar.test.tsx src/shell/MarkdownRichTextViewer.test.tsx src/shell/FolderTree.test.tsx src/shell/ForkSessionDialog.test.tsx src/shell/NewChatDialog.test.tsx
→ Test Files  5 passed (5)
→ Tests  238 passed (238)

npm run build
→ tsc -b && vite build 成功

npm run test -- --run
→ Test Files  1 failed | 227 passed | 1 skipped (229)
→ Tests  1 failed | 4090 passed | 3 expected fail | 2 skipped (4096)
→ 唯一失败：AgentInfo.test.tsx 1K 基线（预存），无新增失败
```

## 说明

- MarkdownRichTextViewer 的外部更新冲突状态通过 `vi.hoisted` 可变 ref 模拟 `useMarkdownEditorSync` hook 实现，无需修改生产代码
- Sidebar 删除项目对话框因拖拽交互难以在单元测试中触发，使用 `translate()` API 直接验证 P4C 新增 key 的中文翻译值
- NewChatDialog 的受管沙箱状态需要全量 `useServerInfo` + `hostConfig` mock，使用 `translate()` API 直接验证 key 值
- 所有新增测试均包含 `afterEach(() => setLocale("en"))` 语言状态清理
