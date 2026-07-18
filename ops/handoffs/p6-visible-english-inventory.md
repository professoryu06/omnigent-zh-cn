# P6: 未修复 must_translate 逐项清单（P5-R3 一致性修正版）

**审计日期**：2026-07-17
**修正日期**：2026-07-17 (P5-R3)

## 分类规则

| 分类 | 判定标准 |
|---|---|
| `must_translate` | 面向用户的固定 UI 文案（按钮文本、标签、占位符、提示语、说明文字） |
| `keep_technical` | 协议名、传输标识、产品名、模型 ID、代码标识、glob 语法、文件大小单位缩写、布尔字面量 |
| `keep_dynamic` | 示例 URL/路径/分支名/服务器名等仅作样例占位的字符串 |
| `ignore_non_ui` | 注释、类型定义 |

---

## must_translate（53 项）

### components/BrowserPane/BrowserPane.tsx

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 1 | 393 | `"Go back"` | 浏览器后退按钮 aria-label | must_translate | 新增 key `browser.goBack` |
| 2 | 394 | `"Back"` | 浏览器后退按钮 title | must_translate | 新增 key `browser.back` |
| 3 | 403 | `"Go forward"` | 浏览器前进按钮 aria-label | must_translate | 新增 key `browser.goForward` |
| 4 | 404 | `"Forward"` | 浏览器前进按钮 title | must_translate | 新增 key `browser.forward` |
| 5 | 413 | `"Reload"` | 浏览器刷新按钮 aria-label + title | must_translate | 新增 key `browser.reload` |
| 6 | 425 | `"Enter a URL"` | 地址栏 placeholder | must_translate | 新增 key `browser.enterUrl` |
| 7 | 426 | `"Address bar"` | 地址栏 aria-label | must_translate | 新增 key `browser.addressBar` |
| 8 | 447 | `"Toggle DevTools"` | DevTools 切换 aria-label + title | must_translate | 新增 key `browser.toggleDevTools` |
| 9 | 458 | `"Exit design mode"` / `"Enter design mode"` | 设计模式切换 aria-label | must_translate | 新增 key `browser.exitDesignMode` / `browser.enterDesignMode` |
| 10 | 461-462 | `"Click an element in the page, then describe what to change"` / `"Design mode: point at an element to prompt about it"` | 设计模式提示 title | must_translate | 新增 key `browser.designModeHint` / `browser.designModeActiveHint` |
| 11 | 480 | `"Enter a URL above to get started — the agent will open pages here too."` | 空状态 JSX 文本 | must_translate | 新增 key `browser.emptyStateHint` |

### components/ai-elements/message.tsx

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 12 | 242 | `"Previous branch"` | 分支导航按钮 aria-label | must_translate | 新增 key `message.branchPrevious` |
| 13 | 262 | `"Next branch"` | 分支导航按钮 aria-label | must_translate | 新增 key `message.branchNext` |
| 14 | 369 | `"Copy Code"` | 代码复制按钮 aria-label | must_translate | 新增 key `message.copyCode` |
| 15 | 373 | `"Copy Code"` | 代码复制按钮 title | must_translate | 复用 `message.copyCode` |
| 16 | 385 | `"Toggle word wrap"` | 自动换行切换 aria-label | must_translate | 新增 key `message.toggleWordWrap` |
| 17 | 391 | `"Disable word wrap"` / `"Enable word wrap"` | 自动换行切换 title | must_translate | 新增 key `message.disableWordWrap` / `message.enableWordWrap` |

### components/blocks/ToolCard.tsx

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 18 | 208 | `"Parameters"` | 工具参数面板 title | must_translate | 新增 key `tool.parameters` |
| 19 | 211 | `"Copy parameters"` | 复制参数按钮标签 | must_translate | 新增 key `tool.copyParameters` |
| 20 | 240 | `` `See ${n} step${n === 1 ? "" : "s"}` `` | 折叠工具组 JSX 文本 | must_translate | 新增 key `tool.seeSteps`（含单复数） |
| 21 | 429 | `"Output"` | 工具输出面板 title | must_translate | 新增 key `tool.output` |
| 22 | 429 | `"Copy output"` | 复制输出按钮标签 | must_translate | 新增 key `tool.copyOutput` |
| 23 | 437 | `"Showing full output"` / `"Previewing output"` | 输出预览 JSX 文本 | must_translate | 新增 key `tool.showingFullOutput` / `tool.previewingOutput` |
| 24 | 452 | `"Collapse"` / `"Expand"` | 展开/折叠按钮 JSX | must_translate | 新增 key `tool.collapse` / `tool.expand` |
| 25 | 466 | `"Waiting for output..."` | 等待输出 JSX | must_translate | 新增 key `tool.waitingForOutput` |
| 26 | 480 | `"Tool was cancelled before output arrived."` | 取消状态 JSX | must_translate | 新增 key `tool.cancelledBeforeOutput` |
| 27 | 482 | `"No output was recorded for this tool call."` | 无输出状态 JSX | must_translate | 新增 key `tool.noOutputRecorded` |
| 28 | 484 | `"Tool did not return output before the response failed."` | 失败状态 JSX | must_translate | 新增 key `tool.didNotReturnOutput` |
| 29 | 577-578 | `"line"`, `"char"` | 输出统计单位（用户可读标签） | must_translate | 新增 key `tool.lineUnit` / `tool.charUnit` |
| 30 | 583-586 | `" hidden"`, `" shown"` | 输出统计文本 | must_translate | 新增 key `tool.hidden` / `tool.shown` |

### components/blocks/ExitPlanModeReview.tsx

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 31 | 61 | `"What should change about the plan? (optional)"` | textarea placeholder | must_translate | 新增 key `exitPlanMode.feedbackPlaceholder` |
| 32 | 69 | `"Reject plan"` | 按钮 JSX 文本 | must_translate | 新增 key `exitPlanMode.rejectPlan` |
| 33 | 72 | `"Cancel"` | 按钮 JSX 文本 | must_translate | 复用 `common.cancel` |
| 34 | 80 | `"Yes, and use auto mode"` | 按钮 JSX 文本 | must_translate | 新增 key `exitPlanMode.yesAutoMode` |
| 35 | 84 | `"Yes, manually approve edits"` | 按钮 JSX 文本 | must_translate | 新增 key `exitPlanMode.yesManualApprove` |
| 36 | 88 | `"Reject with feedback"` | 按钮 JSX 文本 | must_translate | 新增 key `exitPlanMode.rejectWithFeedback` |

### components/blocks/AskUserQuestionForm.tsx

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 37 | 225 | `"Question {n} of {total}:"` | 进度 JSX 文本 | must_translate | 新增 key `askUserQuestion.questionProgress` |
| 38 | 322 | `"Type something"` | 自定义输入 placeholder | must_translate | 新增 key `askUserQuestion.typeSomething` |
| 39 | 353 | `"Prev"` | 按钮 JSX 文本 | must_translate | 新增 key `askUserQuestion.prev` |
| 40 | 362 | `"Next"` | 按钮 JSX 文本 | must_translate | 新增 key `askUserQuestion.next` |
| 41 | 374 | `"Submit"` | 按钮 JSX 文本 | must_translate | 新增 key `askUserQuestion.submit` |
| 42 | 379 | `"Cancel"` | 按钮 JSX 文本 | must_translate | 复用 `common.cancel` |

### components/CostRoutingControl.tsx

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 43 | 195 | `"Intelligent model router"` | 切换按钮 aria-label | must_translate | 新增 key `costRouting.intelligentModelRouter` |
| 44 | 225 | `"Intelligent model router"` | Tooltip title JSX | must_translate | 新增 key `costRouting.intelligentModelRouterTitle` |
| 45 | 229 | `"Picked"` / `"Would pick"` | Tooltip 条件 JSX | must_translate | 新增 key `costRouting.picked` / `costRouting.wouldPick` |

### shell/TruncatedBanner.tsx

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 46 | 16-17 | `"This file is too large to load fully — showing a truncated preview..."` | 截断文件提示 JSX | must_translate | 新增 key `editor.truncatedBanner` |

### shell/fileStatusUtils.ts

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 47 | 18 | `"Added"` | Git 状态标签（文件列表） | must_translate | 新增 key `file.statusAdded` |
| 48 | 20 | `"Deleted"` | Git 状态标签（文件列表） | must_translate | 新增 key `file.statusDeleted` |
| 49 | 22 | `"Modified"` | Git 状态标签（文件列表） | must_translate | 新增 key `file.statusModified` |

### shell/sidebarNav.ts

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 50 | 47 | `"New session"` | 无标题会话标签常量 | must_translate | 新增 key `session.newSession` |
| 51 | 72 | `"Other"` | 智能体类型兜底标签 | must_translate | 新增 key `session.otherAgentType` |

### shell/ExecutionLogsPanel.tsx

| # | 行号 | 原文 | UI 上下文 | 分类 | 建议处理 |
|---|---|---|---|---|---|
| 52 | 211 | `"main"` | 主执行日志条目标签（用户可见名） | must_translate | 新增 key `logs.mainEntry` |

### 外围说明文字（从包含技术样例的 placeholder 中拆分）

| # | 文件 | 行号 | 说明文字（must_translate） | 技术样例（保留原样） | 建议处理 |
|---|---|---|---|---|---|
| 53 | FilesPanel.tsx | 458 | `"e.g. "` | `*.ts, src/**` (glob 语法，keep_technical) | 新增 key `file.includePatternsPlaceholder` → zh-CN: "例如：\*.ts, src/\*\*" |
| 54 | FilesPanel.tsx | 464 | `"e.g. "` | `**/node_modules, *.test.ts` (glob 语法，keep_technical) | 新增 key `file.excludePatternsPlaceholder` → zh-CN: "例如：\*\*/node_modules, \*.test.ts" |
| 55 | CreateAgentDialog.tsx | 376 | `"command (e.g. "` → `")"` | `npx` (CLI 工具名，keep_technical) | 新增 key `agentInfo.commandPlaceholder` → zh-CN: "命令（例如：npx）" |
| 56 | CreateAgentDialog.tsx | 382 | `"args (e.g. "` → `")"` | `-y @modelcontextprotocol/server-github` (示例参数，keep_dynamic) | 新增 key `agentInfo.argsPlaceholder` → zh-CN: "参数（例如：-y @modelcontextprotocol/server-github）" |

**must_translate 合计：56**

---

## keep_technical（技术标识，保留原样）

| # | 文件 | 行号 | 原文 | 归类理由 |
|---|---|---|---|---|
| T1 | fileStatusUtils.ts | 31 | `"KB"`, `"MB"`, `"GB"`, `"TB"` | 国际标准文件大小单位缩写 |
| T2 | AgentInfo.tsx | 517-518 | `"true"`, `"false"` | 布尔字面量 |
| T3 | AgentInfo.tsx | 908 | `"HTTP"`, `"stdio"` | 网络传输协议标识 |
| T4 | OttoEyes.tsx | 387 | `"Omnigent"` | 产品名 |
| T5 | sidebarNav.ts | 26-28 | `"Claude Code"`, `"Codex"`, `"Pi"` | 产品名 |
| T6 | ChatPage.tsx | 3592-3596 | `"Claude"`, `"Codex"`, `"Cursor"`, `"Kiro"`, `"OpenCode"` | 产品名 |
| T7 | ChatPage.tsx | 5182-5185 | `"low"`, `"medium"`, `"high"`, `"xhigh"`, `"max"` | 推理级别代码标识 |
| T8 | FilesPanel.tsx | 458 | `\*.ts, src/\*\*` | glob 语法 |
| T9 | FilesPanel.tsx | 464 | `\*\*/node_modules, \*.test.ts` | glob 语法 |

**keep_technical 合计：9**

---

## keep_dynamic（示例数据/动态值，保留原样）

| # | 文件 | 行号 | 原文 | 归类理由 |
|---|---|---|---|---|
| D1 | NewChatDialog.tsx | 3372 | `"https://github.com/org/repo"` | 示例仓库 URL |
| D2 | ForkSessionDialog.tsx | 728 | `"feature/my-branch"` | 示例 Git 分支名 |
| D3 | ResumeWithDirectoryDialog.tsx | 385 | `"feature/my-branch"` | 示例 Git 分支名 |
| D4 | CreateAgentDialog.tsx | 207 | `"my-agent"` | 示例 Agent 名称 |
| D5 | CreateAgentDialog.tsx | 343 | `"server-name"` | 示例 MCP 服务器名 |
| D6 | CreateAgentDialog.tsx | 382 | `-y @modelcontextprotocol/server-github` | **仅参数样例**（外围说明 `args (e.g. ` 已拆分到 must_translate #56） |
| D7 | CreateAgentDialog.tsx | 398 | `"https://mcp.example.com/sse"` | 示例 URL |
| D8 | AgentInfo.tsx | 893 | `"github"` | 示例服务器名 |
| D9 | AgentInfo.tsx | 918 | `"https://example.com/sse"` | 示例 URL |
| D10 | AgentInfo.tsx | 928 | `"npx"` | CLI 工具名示例 |
| D11 | AgentInfo.tsx | 937 | `"-y\n@modelcontextprotocol/server-github"` | 示例 CLI 参数 |
| D12 | CreateAgentDialog.tsx | 376 | `npx` | **仅 CLI 工具名**（外围说明 `command (e.g. ` 已拆分到 must_translate #55） |
| D13 | CreateAgentDialog.tsx | 261 | `"claude-sonnet-4-20250514"` | 模型 ID 示例 |

**keep_dynamic 合计：13**

---

## 分类汇总

| 分类 | 数量 | 占比 |
|---|---|---|
| `must_translate` | **56** | 71.8% |
| `keep_technical` | **9** | 11.5% |
| `keep_dynamic` | **13** | 16.7% |
| `ignore_non_ui` | **0** | 0% |
| **合计** | **78** | 100% |

明细校验：56 + 9 + 13 = 78 ✅

---

## 分类变更速查（相对 P5-R2 → P5-R3）

| 变更项 | P5-R2 | P5-R3 | 原因 |
|---|---|---|---|
| HTTP/stdio (AgentInfo.tsx:908) | must_translate + 独立说明 | **仅 keep_technical T3** | 移除矛盾重复 |
| true/false (AgentInfo.tsx:517-518) | must_translate | keep_technical T2 | 布尔字面量 |
| `e.g. *.ts, src/**` 整体 (FilesPanel.tsx:458) | 混合（keep_technical + must_translate） | **拆分**：说明 must_translate #53 + glob keep_technical T8 | 一个主分类 |
| `e.g. **/node_modules, *.test.ts` 整体 (FilesPanel.tsx:464) | 同上混合 | **拆分**：说明 must_translate #54 + glob keep_technical T9 | 一个主分类 |
| `command (e.g. npx)` (CreateAgentDialog.tsx:376) | 混合（keep_dynamic + must_translate） | **拆分**：说明 must_translate #55 + npx keep_dynamic D12 | 一个主分类 |
| `args (e.g. -y ...)` (CreateAgentDialog.tsx:382) | 同上混合 | **拆分**：说明 must_translate #56 + 样例 keep_dynamic D6 | 一个主分类 |
