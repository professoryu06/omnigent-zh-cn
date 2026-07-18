# P4C-R3: 将字典直读测试替换为真实 UI 验收 — 完成报告

**工作包**：`ops/handoffs/p4c-test-coverage-correction-v3.md`
**完成日期**：2026-07-17

## 修改测试文件

| 文件 | 变更 |
|---|---|
| `web/src/shell/Sidebar.test.tsx` | 移除 `translate()` 导入和使用；重写 `Sidebar zh-CN project dialog` 为真实 UI 交互测试 |
| `web/src/shell/NewChatDialog.test.tsx` | 移除 `translate()` 导入和使用；重写 `NewChatDialog zh-CN new sandbox` 为真实 UI 交互测试 |

## 必做一：Sidebar 真实确认对话框

**触发 Dialog 的交互流程**：
1. `setLocale("zh-CN")`
2. `projectsMock.push("Sprint 42")`
3. 构造一条 filed 会话：`conv("conv_filed", "Claude Code", { labels: { omni_project: "Sprint 42" } })`
4. `fetchProjectSessionIdsMock.mockResolvedValue(["conv_filed"])` — 仅一条，确认为项目最后会话
5. 打开项目文件夹：`fireEvent.click(screen.getByRole("button", { name: "Sprint 42" }))`
6. 打开行 kebab：`fireEvent.pointerDown(within(row).getByTestId("conversation-actions"), ...)`
7. 打开"Move session"子菜单：`fireEvent.click(await screen.findByTestId("move-to-project"))`
8. 点击中文移除项：`fireEvent.click(await screen.findByRole("menuitem", { name: /从.*Sprint 42.*移除/ }))`

**UI 断言**：
- 标题：`expect(await screen.findByText("从项目中移除？")).toBeInTheDocument()`
- 操作按钮：`expect(screen.getByRole("button", { name: "从项目中移除" })).toBeInTheDocument()`

**取消后验证**：
- `fireEvent.click(screen.getByRole("button", { name: "取消" }))`
- `expect(screen.queryByText("从项目中移除？")).toBeNull()`
- `expect(moveToProjectSpy).not.toHaveBeenCalled()`

## 必做二：NewChatDialog 真实禁用沙箱项

**Mock 条件**：
- `managed_sandboxes_enabled: false`（默认）
- `docsLinks.newSandbox = "Managed sandboxes are disabled in this workspace."`（非空，使禁用项显示）

**触发交互**：
1. `setLocale("zh-CN")`
2. `setOmnigentHostConfig({ docsLinks: { newSandbox: "Managed sandboxes are disabled in this workspace." } })`
3. `renderLanding()`
4. 打开主机菜单：`fireEvent.pointerDown(screen.getByTestId("new-chat-landing-host-chip"), { button: 0 })`

**UI 断言**：
- 禁用行可见且含中文：`expect(screen.getByTestId("new-chat-landing-sandbox-option-disabled")).toBeTruthy()` + `expect(disabledRow.textContent).toContain("新建沙箱")`
- 帮助按钮 aria-label：`screen.getByLabelText("为什么新建沙箱不可用")`
- 点击禁用项不切换沙箱：`fireEvent.click(disabledRow)` 后 `expect(screen.queryByTestId("new-chat-landing-repo-chip")).toBeNull()`

## 验收命令及结果

```
npm run test -- --run src/shell/Sidebar.test.tsx src/shell/MarkdownRichTextViewer.test.tsx src/shell/FolderTree.test.tsx src/shell/ForkSessionDialog.test.tsx src/shell/NewChatDialog.test.tsx
→ Test Files  5 passed (5)
→ Tests  238 passed (238)

npm run build
→ tsc -b && vite build 成功

npm run test -- --run
→ Test Files  1 failed | 227 passed | 1 skipped (229)
→ Tests  1 failed | 4090 passed | 3 expected fail | 2 skipped (4096)
→ 唯一失败：AgentInfo.test.tsx 1K 基线（预存）
```

## 未解决的 R2 → R3 变更

- 两处 `translate()` 字典直读断言已完全移除，替换为真实 UI 交互测试
- Sidebar 测试通过现有的 move-to-project 菜单流程触发确认弹窗
- NewChatDialog 测试通过 mocking docsLinks 和 ServerInfo 真实渲染禁用沙箱行
- 全量测试无新增失败，仅保留既有 AgentInfo 基线
