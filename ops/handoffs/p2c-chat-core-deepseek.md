# P2C：聊天核心界面中文化工作包

你是 Omnigent Web UI 中文化的受限实现者。只完成本工作包；不能扩展范围。

## 前置状态

- P2A 已完成新建会话与聊天头部中文化。
- P2B 已完成侧边栏和设置侧栏导航中文化，且全量测试仅保留一个与本包无关的 `AgentInfo.test.tsx` 基线失败。
- i18n 规则见 `web/src/i18n/README.md`；默认语言是 `zh-CN`，测试环境默认英文。

## 只允许修改

- `web/src/pages/ChatPage.tsx`
- `web/src/pages/QueuedMessagesStrip.tsx`
- `web/src/components/UserMessageNav.tsx`
- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`
- `web/src/pages/ChatPage*.test.tsx`
- `web/src/pages/ChatPage*.test.ts`
- `web/src/pages/QueuedMessagesStrip.test.tsx`
- `web/src/components/UserMessageNav.test.tsx`

## 明确不允许修改

- 任何后端、WebSocket、聊天状态机、`chatStore`、消息协议、路由、`data-testid`、Agent/Host/Session ID。
- `NewChatDialog.tsx`、`ChatHeader.tsx`、`Sidebar.tsx`、`settingsNav.tsx`、`AppShell.tsx`。
- `BlockRenderer.tsx`、工具卡、审批卡、模型路由、文件提及菜单、终端面板、原始 CLI/Agent 输出。
- `E:\agent team\Omnigent\chat.db`、日志、制品、密钥或任何用户项目文件。
- 依赖升级、全仓格式化或批量修改测试断言。

## 目标

将下列面向用户的可见文案改为 i18n key，并同步维护 `en.ts` 与 `zh-CN.ts`：

1. 聊天输入框：任务输入占位、发送、停止生成、附件校验错误、无法发送的原因、连接/重连提示。
2. 聊天内容区：空状态、加载历史、历史加载失败、会话不存在或 Runner 离线的说明、回到底部、复制用户消息、分支/继续对话等 ChatPage 本地操作。
3. 排队消息：排队中、发送中、取消排队、重试等 `QueuedMessagesStrip` 中的用户可见文案。
4. 用户消息跳转：上一条用户消息、下一条用户消息，以及相应 tooltip/aria-label。

## 不翻译规则

- 不翻译用户输入、Agent 原始输出、CLI 命令、终端输出、代码、文件路径、URL、模型名、Harness 名、Session ID、Git 分支名。
- 保留所有 `data-testid` 值和键盘快捷键值；可翻译它们周围的说明文字。
- 状态枚举值只能映射为显示文本，不得改写传输值或条件分支。

## 实施规则

1. 只使用 `chat.*`、`queue.*`、`userMessageNav.*` 命名空间；不要复用不相干的 Sidebar key。
2. 每个动态句子使用完整 key 和具名变量，例如 `t("chat.sessionLoadFailed", { reason })`。禁止字符串拼接。
3. `ChatPage.tsx` 很大。不要重排、重格式化或移动无关代码；只做最小文案替换。
4. 新增或更新测试必须保留英文默认断言，并至少增加一个显式选择 `zh-CN` 的测试，覆盖输入框或错误状态中的一个关键中文文案。

## 验收命令

```powershell
npm.cmd run test -- --run src/pages/ChatPage.test.ts src/pages/ChatPage.composer.test.tsx src/pages/ChatPage.statusLine.test.tsx src/pages/ChatPage.historyLoad.test.tsx src/pages/QueuedMessagesStrip.test.tsx src/components/UserMessageNav.test.tsx
npm.cmd run build
```

## 完成报告

写入 `ops/handoffs/p2c-chat-core-deepseek-completion.md`，内容必须包括：

1. 修改文件和每个文件的具体文案范围。
2. 新增 i18n key 列表。
3. 保留英文原文的条目和理由。
4. 运行过的命令与完整结果。
5. 未解决项、发现但未改动的文件，及任何可能影响发送/流式语义的风险。
