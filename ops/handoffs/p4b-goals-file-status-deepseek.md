# P4B 工作包：目标、文件提及与会话状态中文化

## 项目与目标

- 工作目录：`E:\agent team\Omnigent\source-zh-cn`
- 目标：完成 Codex Goal 控件、文件提及菜单和会话状态徽章的静态 UI 中文化，保持目标 API、文件选择和状态映射行为不变。

## 允许修改

- `web/src/components/codex/CodexGoalControl.tsx`
- `web/src/components/codex/CodexGoalDialog.tsx`
- `web/src/components/FileMentionMenu.tsx`
- `web/src/components/SessionStateBadge.tsx`
- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`
- `web/src/components/codex/CodexGoalControl.test.tsx`
- `web/src/components/codex/CodexGoalDialog.test.tsx`
- `web/src/components/SessionStateBadge.test.tsx`
- 可新建且仅新建：`web/src/components/FileMentionMenu.test.tsx`

## 禁止修改

- 不改 Codex Goal API、hooks、请求参数、状态机、store、文件搜索/选择逻辑、路由、CSS、DOM 结构、`data-testid`。
- 不改工作区或聊天页其它组件。
- 不翻译文件名、目录名、路径、用户输入的目标文本、Goal ID、状态/错误原文、模型名与技术标识。

## 必须覆盖

1. Goal 控件：查看/设置目标的 aria-label、标题、按钮、加载状态、模式、保留当前、进行中、暂停、目标、可选项等静态文本。
2. Goal 状态：只翻译 UI 对状态的展示标签；API 传递的稳定 status 值不得变化。
3. 文件提及：加载、打开文件夹、附加文件、附加整个文件夹等静态 title/aria-label；条目的 `entry.name` 保持原样，仅翻译前缀。
4. 会话状态徽章：如“Needs response”及所有 `Visual` 映射的静态 label/aria-label。映射不能在模块加载时保存翻译结果，应保存 key 并在组件渲染期 `t()`。

## 实施规则

1. 通过 `useTranslation()` 和 `t()` 翻译；新增 key 必须双词典严格对齐。
2. 模块级状态映射、选项数组只能保存 key/原始数据，不得模块加载期调用 `t()` 或缓存翻译结果。
3. 保持所有事件、API 负载、状态条件、键盘交互不变。

## 测试要求

1. 新增至少 10 条 zh-CN 断言，覆盖四个组件。
2. 新建 FileMentionMenu 测试时只 mock 必要数据层，验证加载、文件附加和文件夹附加的中文无障碍标签。
3. 至少添加一条 I18nProvider 运行时语言切换测试，优先覆盖 SessionStateBadge 或 Goal 控件。
4. 不删除、不放宽既有测试。

## 验收命令

在 `web` 目录执行：

```powershell
npm.cmd run test -- --run src/components/codex/CodexGoalControl.test.tsx src/components/codex/CodexGoalDialog.test.tsx src/components/FileMentionMenu.test.tsx src/components/SessionStateBadge.test.tsx
npm.cmd run build
```

全量测试中 `AgentInfo.test.tsx:383` 的 `1K` 断言是既有基线失败，不在 P4B 范围内。

## 完成报告

完成后创建：

`ops/handoffs/p4b-goals-file-status-deepseek-completion.md`

报告列出修改文件、key 数、中文覆盖点、目标测试、构建、全量测试结果和遗留项。
