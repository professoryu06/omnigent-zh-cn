# P4D-R: P4D 可见中文的真实 UI 验收补齐

## 当前结论

P4D 生产代码已正确接入 i18n；但 P4D 完成报告中的测试没有满足原工作包的硬要求。
“生产代码已验证接入 `t()`”不能替代真实 UI 测试。

本包只增加或修改测试，禁止修改生产代码、字典、样式、hook、接口或全局测试配置。

## 现有已有效覆盖，不必重复

- `Connecting…` 中文及运行时英转中文；
- `Interrupted` 中文；
- Plan 按钮与 Plan mode 状态；
- Dialog X 按钮的隐藏“关闭”；
- ForkSessionDialog 的“主机”。

## 必须新增的真实 UI 覆盖

### A. ChatPage（至少 6 条独立中文断言）

必须在 `setLocale("zh-CN")` 下，以实际组件渲染与交互完成以下断言：

1. 移动端切换控制中可见“聊天”。
2. 同一控制中可见“终端”。
3. 复制消息的移动端真实 toast 包含“已复制到剪贴板”。
4. 将文件拖入 Composer 后，覆盖层显示“拖放文件到此处”。
5. 打开可用的模型/智能体选择器后，至少一个真实分组标题为“智能体”或“模型”。
6. 打开同一选择器后，推理强度分组标题为“推理强度”。

如果既有组件的测试工具或 mock 使分组难以展开，必须复用生产所需 provider/mock 后从用户入口
打开。不可改为 `translate()`、字典导入、源代码字符串检查或仅断言 test id。

### B. Dialog Footer

使用 `<DialogFooter showCloseButton>` 的真实渲染，断言 role=button 的名称为“关闭”；点击该
按钮后 Dialog 关闭。不得将 DialogContent 的 X 按钮测试算作这一条。

### C. 测试卫生

- 每个新 zh-CN 测试结束后恢复 `setLocale("en")`；
- 禁止导入或调用 `translate()`，禁止 mock `t()`；
- 不新增快照、不放宽超时、不跳过测试；
- 技术标识、动态路径、URL、模型 ID、分支名、命令均不翻译。

## 验收

在 `E:\agent team\Omnigent\source-zh-cn\web` 运行：

```powershell
npm.cmd run test -- --run src/pages/ChatPage.composer.test.tsx src/pages/ChatPage.indicators.test.tsx src/components/ui/dialog.test.tsx src/shell/ForkSessionDialog.test.tsx
npm.cmd run build
npm.cmd run test -- --run
```

全量测试只允许已知 `AgentInfo.test.tsx` 的 `1K` 基线失败。

## 交付

报告写入：
`ops/handoffs/p4d-test-coverage-correction-deepseek-completion.md`

逐条列出六个 Chat UI 断言与 Dialog Footer 断言的测试文件、测试名、触发交互和可见中文文本。
