# P2B：侧边栏与设置导航中文化工作包

你是 Omnigent Web UI 中文化的受限实现者。只完成本工作包；不能扩展范围。

## 前置状态

- P2A 已完成 `NewChatDialog.tsx` 与 `ChatHeader.tsx`。
- `web/src/i18n/index.ts` 已支持 `useTranslation()`；生产默认 `zh-CN`，测试环境默认 `en`。
- `Sidebar.tsx` 顶部的收件箱、新建会话、搜索、设置、我的会话、与我共享已接入 `sidebar.*` key。必须保留这些现有改动。

## 只允许修改

- `web/src/shell/Sidebar.tsx`
- `web/src/shell/settingsNav.tsx`
- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`
- `web/src/shell/Sidebar.test.tsx`
- `web/src/shell/AppShell.test.tsx`（仅当 SettingsSidebarBody 的现有断言确实需要调整）

## 先阅读

1. `web/src/i18n/README.md`
2. `web/src/i18n/glossary.ts`
3. P2A 完成报告：`ops/handoffs/p2a-new-session-deepseek-completion.md`
4. 本文件列出的源码与测试。

## 目标

将下列面向用户的文案接入稳定 i18n key，并同时补齐英语和简体中文词典：

- Sidebar：会话分组、项目分组、空状态、加载更多、收起/展开、选择会话、批量操作、固定/取消固定、重命名、归档、删除、停止、项目操作与失败提示。
- SettingsSidebarBody：返回 Omnigent、关闭/收起侧栏、桌面端、通用、管理、已归档、外观、Git、键盘快捷键、账户、成员、策略、共享、本地 CLI、已归档会话。

## 术语

- Session -> 会话
- Project -> 项目
- Conversations -> 会话
- Agent -> 智能体
- Host -> 主机
- Runner -> 执行器
- Policy -> 策略
- Approval -> 授权确认
- Shell、CLI、Git、Codex、Claude Code、Hermes、OpenCode 保留英文。

## 严格禁止

- 不修改后端 API、WebSocket、路由、状态结构、`data-testid`、Agent/Host ID、命令、模型名、文件路径和 Git 分支值。
- 不修改 `web/src/i18n/index.ts`、`web/src/test-setup.ts`、`NewChatDialog.tsx`、`ChatHeader.tsx`、`AppShell.tsx`（除非测试文件本身）。
- 不读取或修改 `E:\agent team\Omnigent\chat.db`、`logs`、`artifacts`、密钥或用户私有项目文件。
- 不升级依赖，不格式化无关文件，不处理 ChatPage、文件面板、终端面板或设置页正文。

## 实施规则

1. 每条用户可见字符串使用 `t("sidebar.*")` 或 `t("settingsNav.*")`，不得直接拼接中文文本。
2. 有变量的完整句子用具名插值，例如 `t("sidebar.deleteFailed", { name })`。
3. `settingsNavGroups()` 目前是普通函数。可以让它接收翻译函数或改为在组件层映射 label；不得改变其分组、权限或路由判断语义。
4. 测试中保留英文断言；新增至少一个显式选择 `zh-CN` 的用例，覆盖侧边栏核心入口及设置导航。

## 验收命令

```powershell
npm run test -- --run src/i18n/index.test.ts src/shell/Sidebar.test.tsx src/shell/AppShell.test.tsx
npm run build
```

## 完成报告格式

写入 `ops/handoffs/p2b-sidebar-settings-deepseek-completion.md`，包含：

1. 修改文件与每个文件的职责。
2. 新增 i18n key 清单。
3. 保留英文原文的条目和原因。
4. 验收命令及完整结果。
5. 未解决项、可能影响语义的文案，以及任何超出范围的发现。
