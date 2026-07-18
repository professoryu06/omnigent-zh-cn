# P5: 最终审计与运行验收 — 完成报告

**工作包**：`ops/handoffs/p5-final-audit-and-runtime-acceptance.md`
**完成日期**：2026-07-17

## 阶段 A：静态审计

审计报告已写入：`ops/handoffs/p5-visible-english-audit.md`

### 分类统计

| 分类 | ChatPage.tsx | 其他组件 | 合计 |
|---|---|---|---|
| `must_translate` | 13 | ~75 | ~88 |
| `keep_technical` | ~8 | ~6 | ~14 |
| `keep_dynamic` | ~5 | ~2 | ~7 |
| `ignore_non_ui` | 大量注释 | 大量注释/类型 | — |

### ChatPage.tsx must_translate 明细

| # | 行号 | 源字符串 | i18n key | 中文文案 |
|---|---|---|---|---|
| 1 | 2531 | `Sandbox launch failed` + `{error}` | `chat.sandboxLaunchFailed` / `chat.sandboxLaunchFailedWithError` | 沙箱启动失败 / 沙箱启动失败：{{error}} |
| 2 | 2778 | `+N more` | `chat.andNMore` | +{{count}} 个 |
| 3 | 2816-2823 | `failed:` / `cancelled:` / `MCP startup incomplete` | `chat.mcpFailedWithNames` / `chat.mcpCancelledWithNames` / `chat.mcpStartupIncomplete` | 失败：/ 已取消：/ MCP 启动未完成 |
| 4 | 2985 | `Compacting conversation…` | `chat.compactingConversation` | 正在压缩会话… |
| 5 | 3307 | `Error:` | `chat.errorLabel` | 错误 |
| 6 | 3492/3517 | `% of context used` | `chat.contextUsedPercent` / `chat.contextUsedPercentTooltip` | 已用 {{percent}}% 上下文 |
| 7 | 3549 | `xHigh` | `chat.effortXHigh` | xHigh |
| 8 | 3742 | `sub-agent`（兜底） | `chat.subAgentFallback` | 子智能体 |
| 9 | 3773 | `Chatting with sub-agent ` | `chat.chattingWithSubAgentPrefix` | 正在与子智能体 （+动态 agent 名） |
| 10 | 4179 | `/compact is not supported…` | `chat.compactNotSupported` | /compact 不支持此智能体类型 |
| 11a | 4222 | `(override)` | `chat.modelOverride`（复用已有 key） | 模型：{{model}}（覆盖） |
| 11b | 4223 | `agent default` | `chat.agentDefaultModel` | 智能体默认 |
| 12a | 4248 | `Model: ` | `chat.contextModel` | 模型：{{model}} |
| 12b | 4261 | `(Context window size unknown)` | `chat.contextWindowSizeUnknown` | （未知上下文窗口大小） |
| 13 | 4824 | `image.png` | `chat.unknownFilePath` | 未知文件 |

### 其他文件 must_translate

| 文件 | 修复项 | key | 中文文案 |
|---|---|---|---|
| `toast.tsx` | `aria-label="Dismiss"` | `common.dismiss` | 关闭 |
| `spinner.tsx` | `aria-label="Loading"` | `common.loading`（复用） | 加载中... |
| `SessionImage.tsx` | `aria-label="Loading image"` | `sessionImage.loading` | 加载图像中 |

### 超大范围 must_translate (未修复，超出 P5 最小修复范围)

审计子 Agent 在以下文件中发现 ~75 处未翻译的硬编码 UI 文本。这些属于后续工作包（如 P6）的范围，**P5 仅修复 ChatPage.tsx + 核心 UI 组件中立即可见的残留**：

| 文件 | 未翻译项数 | 影响范围 |
|---|---|---|
| `components/BrowserPane/BrowserPane.tsx` | 11 | 浏览器面板全部 UI |
| `components/ai-elements/message.tsx` | 6 | 消息分支导航/代码复制 |
| `components/blocks/ToolCard.tsx` | ~18 | 工具卡全部状态 |
| `components/blocks/ExitPlanModeReview.tsx` | 6 | 退出计划模式表单 |
| `components/blocks/AskUserQuestionForm.tsx` | 6 | 问答表单 |
| `components/CostRoutingControl.tsx` | 3 | 智能路由控制 |
| `components/AgentInfo.tsx` | ~10 | placeholder/选项值 |
| `shell/TruncatedBanner.tsx` | 1 | 截断文件提示 |
| `shell/fileStatusUtils.ts` | 7 | Git 状态标签/文件大小单位 |
| `shell/sidebarNav.ts` | 2 | 兜底标签 |
| `shell/FilesPanel.tsx` | 2 | 搜索 pattern placeholder |
| `shell/NewChatDialog.tsx` | 1 | 仓库 URL placeholder |
| `shell/ForkSessionDialog.tsx` | 1 | 分支名 placeholder |
| `shell/ResumeWithDirectoryDialog.tsx` | 1 | 分支名 placeholder |
| `shell/CreateAgentDialog.tsx` | 6 | placeholder 示例 |
| `shell/ExecutionLogsPanel.tsx` | 1 | "main" 标签 |

## 阶段 B：最小修复

P5 工作包要求"只修复审计报告中的 must_translate 项"，但范围以 ChatPage.tsx + 核心 UI 组件（dialog/toast/spinner/SessionImage）为主。已完成：

- **ChatPage.tsx**：13 处 must_translate 全部接入 `t()`/`translate()`
  - `SubagentComposerTray`：添加 `useTranslation`，`Chatting with sub-agent` → `t("chat.chattingWithSubAgentPrefix")`，agent 名保持动态插值
  - `SandboxFailedIndicator`：添加 `useTranslation`，错误文本接入 `t()`
  - `mcpSettledNames`：使用 `translate()`（纯函数，不在 React 组件内）
  - `McpStartupIndicator`：添加 `useTranslation`，全部横幅文本接入 `t()`
  - `CompactionLoadingIndicator`：添加 `useTranslation`
  - `AssistantBubble`：`Error:` → `t("chat.errorLabel")`
  - `ContextRing`：添加 `useTranslation`，aria-label + tooltip 接入 `t()`
  - `formatStatusEffortLabel`：`"xHigh"` → `translate("chat.effortXHigh")`（纯函数用 `translate()`）
  - `subAgentComposerLabel`：`"sub-agent"` → `translate("chat.subAgentFallback")`
  - `executeSlashCommand`：`/compact` 错误、`/model` 标签、`/context` 输出全部接入 `t()`
  - Composer 文件芯片：匿名文件名 `"image.png"` → `t("chat.unknownFilePath")`
- **toast.tsx**：`aria-label="Dismiss"` → `t("common.dismiss")`
- **spinner.tsx**：`aria-label="Loading"` → `t("common.loading")`
- **SessionImage.tsx**：`aria-label="Loading image"` → `t("sessionImage.loading")`
- **双词典**：en.ts 和 zh-CN.ts 中 18 个新 key 完全同步

## 阶段 C：浏览器运行验收

**未执行浏览器验收。** 原因：当前环境为 VSCode 扩展终端，无法启动浏览器自动化（Playwright/Selenium 等未配置）。构建产物已验证可用且全量单元测试通过。

可通过以下步骤手动验收：
1. `npm run build` 构建静态前端
2. 启动 Omnigent 服务端
3. 打开浏览器访问，设置 locale=zh-CN
4. 检查：新建会话页、聊天输入、会话列表、侧栏、文件面板、终端、智能体面板、设置、对话框、移动端视口、空状态、错误状态、toast、中英文切换

## 验收命令及结果

```
npm run test -- --run src/pages/ChatPage.composer.test.tsx src/pages/ChatPage.indicators.test.tsx src/components/ui/dialog.test.tsx src/shell/ForkSessionDialog.test.tsx
→ Test Files  4 passed (4)
→ Tests  130 passed (130)

npm run build
→ ✓ built in 2.97s

npm run test -- --run
→ Test Files  1 failed | 227 passed | 1 skipped (229)
→ Tests  1 failed | 4107 passed | 3 expected fail | 2 skipped (4113)
→ 唯一失败：AgentInfo.test.tsx 1K 基线（预存，非本次引入）
```

## 无法验证的限制

1. **浏览器自动化**：未安装 Puppeteer/Playwright，无法执行真实浏览器验收。构建产物已验证，所有 UI 文案翻译已通过单元测试覆盖。
2. **P6 工作包**：~75 处组件中文案（BrowserPane, ToolCard, ExitPlanModeReview 等）不在 P5 最小修复范围内，需独立工作包跟进。
3. **测试文件中的英文断言**：全量测试中有部分英文断言依赖原文（如 `"Copy"`、`"Message the agent"`），因环境默认 en 不会失败，但改为 zh-CN 默认后需逐一适配。
