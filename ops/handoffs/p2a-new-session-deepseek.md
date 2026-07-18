# P2A：新建会话与聊天头部中文化工作包

你是 Omnigent Web UI 中文化的受限实现者。只完成本工作包；不能扩展范围。

## 允许修改

- `web/src/shell/NewChatDialog.tsx`
- `web/src/shell/ChatHeader.tsx`
- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`
- 与上述文件直接相关的现有测试文件（仅在确实存在且需要时）

## 先阅读

- `web/src/i18n/README.md`
- `web/src/i18n/glossary.ts`
- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`
- `ops/translation-inventory.json` 中上述两个组件的条目

## 目标

把新建会话与聊天头部的用户可见 UI 文案替换为稳定 i18n key，并同时维护英文与简体中文词典。

优先覆盖：开始会话、任务描述、选择 Agent、选择主机、工作目录、项目、分支、附件、权限模式、聊天头部操作和失败提示。

## 严格禁止

- 不读取或修改 `E:\agent team\Omnigent\chat.db`、`logs`、`artifacts` 或任何用户私有文件。
- 不改后端 API、WebSocket 事件、路由、`data-testid`、状态结构、Agent/Host ID。
- 不翻译模型名、Harness 名、命令、文件路径、URL、Git 分支示例、终端输出或 Agent 原始输出。
- 不升级依赖，不格式化无关文件。
- 不处理 `Sidebar.tsx`、`AppShell.tsx`、`ChatPage.tsx` 或其他目录。

## 插值规则

对包含变量的完整句子，使用完整 key 和具名变量，例如：

```tsx
t("newSession.hostNotConfigured", { harness })
```

禁止把中文句子拆成多个 JSX 文本片段后拼接。保留 `harness`、分支名、路径和命令本身的原文。

## 验收命令

```powershell
npm run test -- --run
npm run build
```

## 返回格式

1. 修改文件清单。
2. 新增的 i18n key 清单。
3. 保留英文原文的条目和原因。
4. 已运行的命令与结果。
5. 未解决项或需要 Codex 决策的插值句子。
