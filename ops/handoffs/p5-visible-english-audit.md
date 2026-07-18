# P5: 静态审计 — 用户可见英文残留报告

**审计日期**：2026-07-17
**审计范围**：`web/src/`（排除 `*.test.*`、`i18n/locales/`、注释、类型定义、构建产物）

## 分类统计

| 分类 | 数量 |
|---|---|
| `must_translate` | 14 |
| `keep_technical` | 已确认（见下列各表） |
| `keep_dynamic` | 已确认（见下列各表） |
| `ignore_non_ui` | 已确认（见下列各表） |

---

## must_translate — 面向用户的固定 UI 文案

### ChatPage.tsx

| # | 行号 | 源字符串 | 上下文 | 建议 key |
|---|---|---|---|---|
| 1 | 2531 | `Sandbox launch failed` | 沙箱启动失败错误横幅，含 `{error}` 后缀 | `chat.sandboxLaunchFailed` |
| 2 | 2778 | ` more`（在 `+12 more` 中） | MCP 服务器名溢出，如 `+2 more` | `chat.andNMore` |
| 3 | 2816-2823 | `failed:` / `cancelled:` 前缀 + `MCP startup incomplete` | MCP 启动失败的 banners | `chat.mcpStartupIncomplete` 等 |
| 4 | 2985 | `Compacting conversation…` | 对话压缩中 Shimmer 指示器 | `chat.compactingConversation` |
| 5 | 3307 | `Error:` 前缀 | 助手 bubble 失败状态 | `chat.errorLabel` |
| 6 | 3492/3517 | `% of context used` | ContextRing aria-label / tooltip | `chat.contextUsedPercent` |
| 7 | 3549 | `xHigh` | 推理强度标签特殊大小写 | `chat.effortXHigh` |
| 8 | 3742 | `sub-agent` | subAgentComposerLabel 兜底值 | `chat.subAgentFallback` |
| 9 | 3773 | `Chatting with sub-agent ` | ✅ 已在 P5 修复为 `t("chat.chattingWithSubAgentPrefix")` | — |
| 10 | 4178 | `/compact is not supported for this agent type` | 内联命令错误 | `chat.compactNotSupported` |
| 11a | 4219 | `(override)` | 模型显示后缀 | `chat.modelOverride`（已有 key） |
| 11b | 4220 | `agent default` | 无 llmModel 时的兜底 | `chat.agentDefaultModel` |
| 12 | 4246/4259 | `Model:` 前缀 + `(Context window size unknown)` | `/context` 命令输出 | `chat.contextModel` / `chat.contextWindowSizeUnknown` |
| 13 | 4824 | `image.png` | 匿名文件芯片兜底名 | `chat.unknownFilePath` |

### toast.tsx

| # | 行号 | 源字符串 | 上下文 | 建议 key |
|---|---|---|---|---|
| 14 | 83 | `aria-label="Dismiss"` | Toast 关闭按钮无障碍标签 | `common.dismiss` |

---

## keep_technical — 正确保留的英文

| 文件 | 内容 | 原因 |
|---|---|---|
| ChatPage.tsx:3592-3596 | `Claude`, `Codex`, `Cursor`, `Kiro`, `OpenCode` | 产品名 |
| ChatPage.tsx:2823 | `MCP` | 协议名 |
| ChatPage.tsx:953 | `Omnigent` | 产品名 |
| ChatPage.tsx:5182-5185 | `low`, `medium`, `high`, `xhigh`, `max` | 推理级别代码标识 |
| ChatPage.tsx:3549 | `xhigh` 比较 | 级别 ID 匹配 |
| ChatPage.tsx:5351-5353 | `formatEffortLabel` 函数 | 纯字符串转换，无英文词 |
| BrowserPane.tsx | 接口方法/类型/桥接字段 | WebView 桥接 API |
| CostRoutingControl.tsx | `weighing`, `matching`, `tuning` | 服务端路由状态 ID 映射（已通过 `routing.*` 翻译输出） |
| shell/Sidebar.tsx | 搜索/匹配文本 | 测试中的 fixture 数据 |
| shell/MonacoCodeEditor.tsx | Monaco 配置 | 编辑器内部配置 |

## keep_dynamic — 动态数据（正确保留）

| 文件 | 内容 | 原因 |
|---|---|---|
| ChatPage.tsx | `host.status`, `host.name` | 服务端返回 |
| ChatPage.tsx | `llmModel`, `gitBranch`, `conversationId` | 服务端/运行时值 |
| shell/*.tsx | 文件名、路径、URL、分支名 | 服务端或用户数据 |
| components/SessionImage.tsx | 图像 URL | 动态数据 |
| components/OttoEyes.tsx | SVG 路径 | 图形数据 |

## ignore_non_ui — 非用户可见

| 文件 | 内容 | 原因 |
|---|---|---|
| 全部 *.tsx | 注释中的英文 | 开发注释 |
| 全部 *.ts | 类型定义、接口 | TypeScript 类型 |
| ChatPage.tsx | `(a directly-opened /c/:id...)` | 代码注释 |

---

## 审计结论

- **14 个 `must_translate` 项** 需要修复（ChatPage.tsx 13 + toast.tsx 1）
- 其中第 9 项（Chatting with sub-agent）已在 P5 阶段 B 修复
- 其余 13 项按 P5 阶段 B 执行
- `keep_technical`、`keep_dynamic`、`ignore_non_ui` 分类均合理，无需额外处理
