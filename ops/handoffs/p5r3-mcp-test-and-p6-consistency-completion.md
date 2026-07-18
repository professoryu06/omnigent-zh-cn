# P5-R3: MCP 完整中文断言与 P6 分类一致性修正 — 完成报告

**工作包**：`ops/handoffs/p5r3-mcp-test-and-p6-consistency.md`
**完成日期**：2026-07-17

## 1. MCP 真实 UI 断言修正

- **文件**：`web/src/pages/ChatPage.indicators.test.tsx`
- **旧断言**：`expect(...textContent).toMatch(/\\+\\d/)` — 只匹配数字，不能证明中文
- **新断言**：`expect(screen.getByTestId("mcp-startup-indicator").textContent).toContain("+2 个")`
- **测试名**：`ChatPage P5-R zh-CN > renders Chinese +2 more text for MCP server overflow in the real McpStartupIndicator`
- **触发**：构造 10 个 `{ status: "failed" }` MCP 服务器 → `useChatStore.setState` → 真实渲染 `<McpStartupIndicator />`
- **禁止**：纯函数、`translate()` 直读、正则数字、仅 test-id 断言

## 2. P6 清单分类一致性修正

已重写：`ops/handoffs/p6-visible-english-inventory.md`

### 关键修正

| 问题 | 修正 |
|---|---|
| HTTP/stdio 同时出现在 must_translate 和 keep_technical | 从 must_translate 表移除，**仅保留 keep_technical T3** |
| `e.g. *.ts, src/**` 双重分类 | **拆分**：说明 `"e.g. "` → must_translate #53，glob 语法 `*.ts, src/**` → keep_technical T8 |
| `e.g. **/node_modules, *.test.ts` 双重分类 | **拆分**：说明 `"e.g. "` → must_translate #54，glob 语法 → keep_technical T9 |
| `command (e.g. npx)` 混合分类 | **拆分**：说明 `"command (e.g. "` → must_translate #55，工具名 `npx` → keep_dynamic D12 |
| `args (e.g. -y ...)` 混合分类 | **拆分**：说明 `"args (e.g. "` → must_translate #56，示例参数 → keep_dynamic D6 |
| `"main"` (ExecutionLogsPanel) | 保留 must_translate #52（非 git 分支，是用户可见日志条目名） |

### 最终分类统计

| 分类 | 数量 |
|---|---|
| `must_translate` | **56** |
| `keep_technical` | **9** |
| `keep_dynamic` | **13** |
| `ignore_non_ui` | **0** |
| **合计** | **78** |
| 明细校验 | 56 + 9 + 13 = 78 ✅ |

## 验收结果

```
npm run test -- --run src/pages/ChatPage.indicators.test.tsx src/pages/ChatPage.composer.test.tsx src/components/ui/dialog.test.tsx src/components/ui/toast.test.tsx src/components/SessionImage.test.tsx src/components/ui/spinner.test.tsx
→ Test Files  6 passed (6)
→ Tests  122 passed (122)

npm run build
→ ✓ built in 3.00s

npm run test -- --run
→ Test Files  1 failed | 228 passed | 1 skipped (230)
→ Tests  1 failed | 4119 passed | 3 expected fail | 2 skipped (4125)
→ 唯一失败：AgentInfo.test.tsx 1K 基线（预存）
```
