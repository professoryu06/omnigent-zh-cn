# P4D-R: P4D 可见中文的真实 UI 验收补齐 — 完成报告

**工作包**：`ops/handoffs/p4d-test-coverage-correction.md`
**完成日期**：2026-07-17

## 修改测试文件

| 文件 | 变更 |
|---|---|
| `web/src/pages/ChatPage.indicators.test.tsx` | 新增移动端 Chat/Terminal 中文 + 英文回退 (3条)、复制 toast 中文 (1条) |
| `web/src/pages/ChatPage.composer.test.tsx` | 新增拖放覆盖层中文 (1条)、AgentPicker 分组标题中文 (1条) |
| `web/src/components/ui/dialog.test.tsx` | 新增 DialogFooter Close 按钮关闭断言 (1条) |

**所有新增测试均仅使用 `screen` / DOM 文本、role、aria-label 和实际交互断言。**
**禁止 `translate()` 字典直读、mock `t()`、源码字符串检查或仅断言 test id。**
**每个 zh-CN 测试结束后恢复 `setLocale("en")`。**

## 必做 A — ChatPage（6 条独立中文断言）

### 测试 1：移动端切换控制中可见"聊天"
- **测试文件**：`ChatPage.indicators.test.tsx`
- **测试名**：`ConnectionIndicator zh-CN — terminal-first Chat/Terminal toggle > renders the Chat toggle button with Chinese label when locale is zh-CN`
- **触发交互**：`setLocale("zh-CN")` → 通过 `TerminalFirstContextProvider` 注入 `view: "chat"` 的 context → 渲染 `ConnectionIndicator`
- **断言**：`expect(screen.getByText("聊天")).toBeInTheDocument()`

### 测试 2：同一控制中可见"终端"
- **测试文件**：`ChatPage.indicators.test.tsx`
- **测试名**：`ConnectionIndicator zh-CN — terminal-first Chat/Terminal toggle > renders the Terminal toggle button with Chinese label when locale is zh-CN`
- **触发交互**：`setLocale("zh-CN")` → 通过 `TerminalFirstContextProvider` 注入 `view: "terminal"` 的 context → 渲染 `ConnectionIndicator`
- **断言**：`expect(screen.getByText("终端")).toBeInTheDocument()`

### 测试 3：英文标签回退
- **测试文件**：`ChatPage.indicators.test.tsx`
- **测试名**：`ConnectionIndicator zh-CN — terminal-first Chat/Terminal toggle > renders the Chat toggle button with English label when locale is en`
- **触发交互**：`setLocale("en")` → 同上的 context → 渲染 `ConnectionIndicator`
- **断言**：`expect(screen.getByText("Chat"))` + `expect(screen.getByText("Terminal"))`

### 测试 4：复制消息的移动端 toast 包含"已复制到剪贴板"
- **测试文件**：`ChatPage.indicators.test.tsx`
- **测试名**：`AssistantBubble zh-CN — copy toast > shows Chinese toast after copy on mobile viewport`
- **触发交互**：`setLocale("zh-CN")` → mock `window.matchMedia` 返回移动端 → mock `navigator.clipboard.writeText` → 渲染 `TooltipProvider` + `Toaster` + `BubbleView` → 点击 aria-label="复制" 的 Copy 按钮 → `await screen.findByRole("status")`
- **断言**：`expect(toast).toHaveTextContent("已复制到剪贴板")`

### 测试 5：拖放覆盖层显示"拖放文件到此处"
- **测试文件**：`ChatPage.composer.test.tsx`
- **测试名**：`Composer zh-CN > shows Chinese Drag-and-drop overlay when dragging a file over the composer`
- **触发交互**：`setLocale("zh-CN")` → 渲染 `Composer` → 定位 `div[class*="rounded-2xl"]`（Composer 的拖放接收容器）→ 构造带 `dataTransfer.types: ["Files"]` 的 `DragEvent` → `fireEvent(dropZone, event)` 触发 `handleDragEnter`
- **断言**：`expect(screen.getByText("拖放文件到此处")).toBeInTheDocument()`

### 测试 6：AgentPicker 分组标题中文"模型"和"推理强度"
- **测试文件**：`ChatPage.composer.test.tsx`
- **测试名**：`Composer zh-CN > opens the AgentPicker and shows Chinese section headers`
- **触发交互**：`setLocale("zh-CN")` → 渲染带 `modelPickerKind: "claude"` + `showEffort: true` 的 `Composer` → 在 textarea 输入 `/model ` 并回车（触发 `setPickerOpenNonce`）→ 等待 model-picker-item 出现（Picker 已打开）→ 直接断言文本
- **断言**：
  - `expect(screen.getByText("模型")).toBeInTheDocument()`
  - `expect(screen.getByText("推理强度")).toBeInTheDocument()`

## 必做 B — Dialog Footer

### 测试 7：role=button 的名称"关闭"，点击后 Dialog 关闭
- **测试文件**：`components/ui/dialog.test.tsx`
- **测试名**：`DialogFooter zh-CN > renders Chinese Close button in DialogFooter and clicking it closes the Dialog`
- **触发交互**：`setLocale("zh-CN")` → 渲染带 `<DialogFooter showCloseButton>` 的 `<Dialog>` → 获取 `screen.getAllByRole("button", { name: "关闭" })[1]`（footer Close 按钮，index 1，排除 X 按钮）→ `fireEvent.click(closeBtn)`
- **断言**：
  - `expect(closeBtn).toBeInTheDocument()`
  - `expect(onOpenChange).toHaveBeenCalledWith(false)`（Dialog 关闭）

## 验收命令及结果

```
npm run test -- --run src/pages/ChatPage.composer.test.tsx src/pages/ChatPage.indicators.test.tsx src/components/ui/dialog.test.tsx src/shell/ForkSessionDialog.test.tsx
→ Test Files  4 passed (4)
→ Tests  130 passed (130)

npm run build
→ ✓ built in 2.83s

npm run test -- --run
→ Test Files  1 failed | 227 passed | 1 skipped (229)
→ Tests  1 failed | 4107 passed | 3 expected fail | 2 skipped (4113)
→ 唯一失败：AgentInfo.test.tsx 1K 基线（预存），无新增失败
```

## 新增测试断言统计

| 来源 | 新增断言数 |
|---|---|
| ChatPage.indicators.test.tsx | 4（聊天 + 终端 + 英文回退 + 复制 toast） |
| ChatPage.composer.test.tsx | 2（拖放覆盖层 + Picker 分组标题） |
| dialog.test.tsx | 1（DialogFooter Close 按钮 + 关闭验证） |
| **合计** | **7 条新测试（含 10+ 条独立断言）** |
