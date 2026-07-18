# P4A 工作包：聊天卡片与系统状态中文化

## 项目与目标

- 工作目录：`E:\agent team\Omnigent\source-zh-cn`
- 目标：将聊天消息流中面向用户的静态英文卡片、系统状态与推理折叠区接入 i18n，使 `zh-CN` 下完整显示简体中文；不改变审批、命令、路由或终端行为。

## 允许修改

源码：

- `web/src/components/blocks/ApprovalCard.tsx`
- `web/src/components/blocks/SlashCommandCard.tsx`
- `web/src/components/blocks/SmartRoutingCard.tsx`
- `web/src/components/blocks/StatusBlocks.tsx`
- `web/src/components/blocks/SystemMessage.tsx`
- `web/src/components/blocks/TerminalView.tsx`
- `web/src/components/ai-elements/reasoning.tsx`
- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`

测试：仅修改对应已有测试：

- `ApprovalCard.test.tsx`
- `SlashCommandCard.test.tsx`
- `SmartRoutingCard.test.tsx`
- `StatusBlocks.test.tsx`
- `SystemMessage.test.tsx`
- `TerminalView.test.tsx`
- `reasoning.test.tsx`

## 禁止修改

- 不改后端、API、hooks、store、路由、审批提交、命令发送、智能路由决策、终端桥接、CSS、DOM 结构、`data-testid`。
- 不改其它组件、文件选择器、会话状态徽章、Codex Goal 组件。
- 不翻译用户消息、LLM 返回内容、命令文本、路径、文件名、模型/智能体名、错误原文、动态状态值、JSON 字段、工具输出和协议值。

## 覆盖范围

1. `ApprovalCard`：审批卡片标题、允许/拒绝/记住选择、输入提示、Claude/Codex 固定说明等静态提示。动态的请求内容、命令和服务端错误保持原样。
2. `SlashCommandCard`：参数、输出、复制/展开等静态标签和无障碍文本；命令名、参数值、输出原文保持原样。
3. `SmartRoutingCard` 与 `StatusBlocks`：智能路由、响应、裁决、原始路由结果、会话压缩等静态标签、tooltip、aria-label。
4. `SystemMessage`：固定的“System”前缀；`message.label` 是动态数据，不翻译。
5. `TerminalView`：桥接错误等固定状态文本；终端输出和错误详情保持原样。
6. `reasoning.tsx`：推理耗时/展开收起等静态文本；推理正文保持原样。

## 实施规则

1. 使用 `useTranslation()` 和 `t()`；新 key 必须在 `en.ts` 与 `zh-CN.ts` 一一对应。
2. 模块级常量、状态映射、选项数组只能保存稳定 key 或原始数据，禁止模块加载期调用 `t()`/`translate()`并缓存结果。
3. callback、tooltip、aria-label 与 toast 必须在执行/渲染时解析当前语言。
4. 不因翻译而修改条件分支、事件处理、审批默认值或终端/路由数据流。

## 测试要求

1. 现有测试中新增至少 12 条 `zh-CN` 断言，覆盖全部 7 个组件。
2. 至少一条运行时语言切换测试，验证不重新挂载时静态英文会切换为中文。
3. 保留所有既有断言，不降低覆盖率。

## 验收命令

在 `web` 目录执行：

```powershell
npm.cmd run test -- --run src/components/blocks/ApprovalCard.test.tsx src/components/blocks/SlashCommandCard.test.tsx src/components/blocks/SmartRoutingCard.test.tsx src/components/blocks/StatusBlocks.test.tsx src/components/blocks/SystemMessage.test.tsx src/components/blocks/TerminalView.test.tsx src/components/ai-elements/reasoning.test.tsx
npm.cmd run build
```

全量测试中的 `AgentInfo.test.tsx:383` 对 `1K` 的断言是既有失败，不能在本包修复或归因于 P4A。

## 完成报告

完成后创建：

`ops/handoffs/p4a-chat-cards-status-deepseek-completion.md`

报告列出修改文件、i18n key 数、每个组件的中文覆盖点、目标测试/构建/全量测试结果，以及遗留项。
