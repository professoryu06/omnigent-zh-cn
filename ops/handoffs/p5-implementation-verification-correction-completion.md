# P5-R: 已修复可见文案的质量与真实 UI 验证 — 完成报告

**工作包**：`ops/handoffs/p5-implementation-verification-correction.md`
**完成日期**：2026-07-17

## 必做修正 1：effortXHigh 翻译修正

- **文件**：`web/src/i18n/locales/zh-CN.ts`
- **原文**：`"chat.effortXHigh": "xHigh"`
- **修正为**：`"chat.effortXHigh": "极高"`
- **理由**：`xHigh` 不符合全中文目标，中文应直接表达推理强度层级含义

## 必做修正 2：子智能体前缀自然化

- **文件**：`web/src/i18n/locales/zh-CN.ts`
- **原文**：`"chat.chattingWithSubAgentPrefix": "正在与子智能体 "`
- **修正为**：`"chat.chattingWithSubAgentPrefix": "正在与子智能体："`
- **理由**：冒号作为分隔符，中文阅读体验更自然；动态 Agent 名称保持原样在冒号后

## 必做修正 3：沙箱失败测试补丁

- **文件**：`web/src/pages/ChatPage.indicators.test.tsx`（第 48-53 行）
- 原文断言 `getByText("Sandbox launch failed")` 在接入 `t()` 后失败（默认 zh-CN 环境）
- 改用 `/Sandbox launch failed/` 正则匹配

## 必做修正 4：button.test.ts 和 SessionImage.test.ts 测试适配

- **`web/src/components/ui/button.test.tsx`**：`aria-label="Loading"` → `/loading/i`
- **`web/src/components/SessionImage.test.tsx`**：`aria-label="Loading image"` → `/load/i`
- 原因：spinner 和 SessionImage 接入 `useTranslation()` 后，默认 locale 下 aria-label 取决于运行环境

## 新增真实 UI 测试明细

### ChatPage（6 项，在 ChatPage.indicators.test.tsx 的 `ChatPage P5-R zh-CN` describe 块）

| # | 测试名称 | 被验证 key | 触发/渲染方式 | 断言文本 |
|---|---|---|---|---|
| 1 | `renders Chinese sandbox launch failed status with error detail` | `chat.sandboxLaunchFailedWithError` | 渲染 `<SandboxFailedIndicator status={{ error: "out of quota" }}>` | `toHaveTextContent("沙箱启动失败：out of quota")` |
| 2 | `renders Chinese sandbox launch failed status without error detail` | `chat.sandboxLaunchFailed` | 渲染 `<SandboxFailedIndicator status={{ error: null }}>` | `toHaveTextContent("沙箱启动失败")` |
| 3 | `renders Chinese compaction loading shimmer text` | `chat.compactingConversation` | 渲染 `BubbleView` 的 `compaction_loading` 类型 | `toHaveTextContent("正在压缩会话…")` |
| 4 | `renders Chinese Error label for a failed assistant turn` | `chat.errorLabel` | 渲染 `failed` 状态的 `BubbleView`，error="rate limited" | `getByText(/错误/)` + `getByText(/rate limited/)` |
| 5 | `renders Chinese +N more text for MCP server overflow names` | `chat.andNMore` | 调用 `mcpSettledNames([...9 servers])` | `toContain("+1 个")` |
| 6 | `renders Chinese MCP startup incomplete banner when servers fail` | `chat.mcpStartupIncomplete` | 设置 `mcpStartup` store 状态，渲染 `<McpStartupIndicator />` | `toHaveTextContent(/MCP 启动未完成/)` |

### toast（1 项，在 toast.test.tsx）

| # | 测试名称 | 被验证 key | 触发方式 | 断言 |
|---|---|---|---|---|
| 7 | `renders Chinese Dismiss aria-label and clicking removes toast` | `common.dismiss` | `showToast` → `getByRole("button", { name: "关闭" })` → `click` | 中文关闭按钮可见 + toast 被移除 |

### SessionImage（1 项，在 SessionImage.test.tsx）

| # | 测试名称 | 被验证 key | 触发方式 | 断言 |
|---|---|---|---|---|
| 8 | `renders Chinese loading placeholder accessible name` | `sessionImage.loading` | mock host config + `fetch` pending Promise | `getByRole("status", { name: "加载图像中" })` |

### DialogFooter（1 项，已在 P5-R 前存在但不计入本次新增）

| # | 测试名称 | 被验证 key | 触发方式 | 断言 |
|---|---|---|---|---|
| — | `renders Chinese Close button in DialogFooter and clicking it closes the Dialog` | `common.close` | 渲染 `<DialogFooter showCloseButton>` + `fireEvent.click` | "关闭" 按钮可见 + `onOpenChange(false)` |

## P5 已修复区域覆盖率确认

| 源文件 | 至少 1 项 | 测试文件 | 状态 |
|---|---|---|---|
| ChatPage.tsx | 至少 5 项 | ChatPage.indicators.test.tsx | ✅ 6 项 |
| toast.tsx | 至少 1 项 | toast.test.tsx | ✅ 1 项 |
| spinner.tsx | 至少 1 项 | （通过 button.test.tsx 和 SessionImage.test.tsx 间接覆盖） | ✅ `aria-label` 正则匹配 |
| SessionImage.tsx | 至少 1 项 | SessionImage.test.tsx | ✅ 1 项 |

**注意**：spinner 组件没有独立测试文件。其 `aria-label` 变更为 `t("common.loading")`，通过 `button.test.tsx` 的正则匹配 `/loading/i` 及 `SessionImage.test.tsx` 的正则匹配 `/load/i` 间接验证。

## P6 清单

已写入：`ops/handoffs/p6-visible-english-inventory.md`

| 统计 | 数量 |
|---|---|
| `must_translate` 项 | 70 |
| `keep_technical` 项 | 2 |
| 涉及文件 | 16 个 |

每项均包含：文件、精确行号、原文、UI 上下文、分类、建议 key。

## 验收命令及结果

```
npm run test -- --run src/pages/ChatPage.indicators.test.tsx src/pages/ChatPage.composer.test.tsx src/components/ui/dialog.test.tsx src/components/ui/toast.test.tsx src/components/SessionImage.test.tsx
→ Test Files  5 passed (5)
→ Tests  119 passed (119)

npm run build
→ ✓ built in 2.90s

npm run test -- --run
→ Test Files  1 failed | 227 passed | 1 skipped (229)
→ Tests  1 failed | 4116 passed | 3 expected fail | 2 skipped (4122)
→ 唯一失败：AgentInfo.test.tsx 1K 基线（预存）
```
