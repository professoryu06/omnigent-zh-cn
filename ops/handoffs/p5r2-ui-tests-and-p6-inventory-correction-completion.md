# P5-R2: 补齐真实 UI 验收并校正 P6 清单 — 完成报告

**工作包**：`ops/handoffs/p5r2-ui-tests-and-p6-inventory-correction.md`
**完成日期**：2026-07-17

## 必做 A：Spinner 真实组件测试

- **文件**：`web/src/components/ui/spinner.test.tsx`（新建）
- **测试 1**：`Spinner zh-CN > has accessible name in Chinese when locale is zh-CN`
  - 触发：`setLocale("zh-CN")` → `render(<Spinner />)` → `getByRole("status", { name: "加载中..." })`
- **测试 2**：`Spinner zh-CN > has accessible name in English when locale is en`
  - 触发：`setLocale("en")` → `render(<Spinner />)` → `getByRole("status", { name: "Loading..." })`
- **禁止**：`translate()` 直读、mock `t()`、仅测 class/test id

## 必做 B：MCP 溢出真实 UI 组件测试

- **文件**：`web/src/pages/ChatPage.indicators.test.tsx`
- **旧测试**（已删除）：直接调用 `mcpSettledNames(["a",...,"i"])` 纯函数 → 无效
- **新测试**：`ChatPage P5-R zh-CN > renders Chinese +1 more text for MCP server overflow in the real McpStartupIndicator`
  - 触发：构造 10 个 `{ status: "failed" }` MCP 服务器 → `useChatStore.setState({ mcpStartup })` → 真实渲染 `<McpStartupIndicator />`
  - 断言：`expect(screen.getByTestId("mcp-startup-indicator").textContent).toMatch(/\\+2/)`（10 个服务器溢出 2 个 = "+2 个"）
- **禁止**：直接调用 `mcpSettledNames()`、纯函数断言

## 必做 C：P6 清单重分类

已重写：`ops/handoffs/p6-visible-english-inventory.md`

### 分类变更

| 分类 | P5-R 数量 | P5-R2 数量 | 变化 |
|---|---|---|---|
| `must_translate` | 70 | **53** | -17（重新判定） |
| `keep_technical` | 2 | **11** | +9 |
| `keep_dynamic` | 0 | **11** | +11 |
| **合计** | 72 | **75** | — |

### 关键重新判定

| 项目 | 新分类 | 理由 |
|---|---|---|
| KB/MB/GB/TB 大小单位 | keep_technical | 国际标准缩写 |
| HTTP/stdio 选项标签 | keep_technical | 协议名/传输标识 |
| true/false 选项 | keep_technical | 布尔标识 |
| URL/路径/分支示例 | keep_dynamic | 示例数据 |
| 模型 ID、server-name | keep_dynamic | 示例数据 |
| npx CLI 工具 | keep_dynamic | CLI 工具名 |
| glob 语法 | keep_technical | 技术语法，只翻译外围"e.g." |
| `"main"` 日志标签 | must_translate | **保留翻译**（非 git 分支，是用户可见日志条目名） |
| `"command (e.g. npx)"` | 混合 | 说明文字翻译，npx 保留 |

## 验收命令及结果

```
npm run test -- --run src/pages/ChatPage.indicators.test.tsx src/pages/ChatPage.composer.test.tsx src/components/ui/dialog.test.tsx src/components/ui/toast.test.tsx src/components/SessionImage.test.tsx src/components/ui/spinner.test.tsx
→ Test Files  6 passed (6)
→ Tests  122 passed (122)

npm run build
→ ✓ built in 2.81s

npm run test -- --run
→ Test Files  1 failed | 228 passed | 1 skipped (230)
→ Tests  1 failed | 4119 passed | 3 expected fail | 2 skipped (4125)
→ 唯一失败：AgentInfo.test.tsx 1K 基线（预存）

新增 spinner.test.tsx = Test Files 228→229 vs P5-R
