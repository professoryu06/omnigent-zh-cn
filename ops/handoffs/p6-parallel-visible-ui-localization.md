# P6: 剩余 56 项可见 UI 文案并行中文化

## 前提

唯一实施依据是 `ops/handoffs/p6-visible-english-inventory.md` 中 56 条 `must_translate` 项。
不得翻译该清单中的 `keep_technical` 或 `keep_dynamic` 项。

本包采用并行车道，但 **只有主 Agent 可改**：

- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`

子 Agent 只能改各自被分配的源文件、对应测试和自己的 handoff 报告；在报告中列出新增 key
建议及中英文值。主 Agent 收到所有报告后，串行合并双词典并解决 key 重名。

## 共同规则

- 只改清单中 `must_translate` 的固定 UI 文案；
- 使用 `useTranslation()`，纯非 React 函数可在调用时使用项目现有 `translate()`；
- 禁止在模块加载时缓存翻译结果；
- 禁止 `translate()` 字典直读作为验收、禁止 mock `t()`、禁止源码字符串检查；
- 新增真实 UI 测试。每个涉及源文件至少一条中文 UI 断言，关键按钮/菜单/错误状态优先；
- 每个 zh-CN 测试后恢复 `setLocale("en")`；
- 技术值、动态值、URL、路径、分支、模型 ID、协议、命令、glob 与文件单位保持原样；
- 不重构、不改 API、行为、样式或测试全局配置。

## 子 Agent 车道

### P6A: 浏览器与消息控件

只可改：

- `web/src/components/BrowserPane/BrowserPane.tsx`
- `web/src/components/ai-elements/message.tsx`
- 对应测试

覆盖 inventory #1-17：浏览器前进/后退/刷新/地址栏/DevTools/设计模式/空状态；消息分支导航、
代码复制和自动换行。

报告：`ops/handoffs/p6a-browser-message-completion.md`

### P6B: 工具卡

只可改：

- `web/src/components/blocks/ToolCard.tsx`
- 对应测试

覆盖 inventory #18-30：参数、输出、复制、步骤数、预览、折叠、等待/取消/失败状态、行/字符/隐藏
统计。

报告：`ops/handoffs/p6b-tool-card-completion.md`

### P6C: 计划审核、用户问答、智能路由

只可改：

- `web/src/components/blocks/ExitPlanModeReview.tsx`
- `web/src/components/blocks/AskUserQuestionForm.tsx`
- `web/src/components/CostRoutingControl.tsx`
- 对应测试

覆盖 inventory #31-45。

报告：`ops/handoffs/p6c-plan-question-routing-completion.md`

### P6D: Shell 余项与本地化外围说明

只可改：

- `web/src/shell/TruncatedBanner.tsx`
- `web/src/shell/fileStatusUtils.ts`
- `web/src/shell/sidebarNav.ts`
- `web/src/shell/ExecutionLogsPanel.tsx`
- `web/src/shell/FilesPanel.tsx`
- `web/src/shell/CreateAgentDialog.tsx`
- 对应测试

覆盖 inventory #46-56。`FilesPanel` 的 glob、`CreateAgentDialog` 的 `npx` 与 MCP 参数样例必须保持
原样，只将外围“例如/命令/参数”等说明中文化。

报告：`ops/handoffs/p6d-shell-residuals-completion.md`

## 主 Agent 集成顺序

1. 等待 A-D 报告；审查每项建议 key，避免重复并复用已有 key。
2. 主 Agent 一次性合并 en/zh-CN 字典。中文须自然、简洁，保留插值变量和技术样例。
3. 逐车道运行目标测试，修复类型、行为或测试缺陷。
4. 运行：

```powershell
npm.cmd run build
npm.cmd run test -- --run
```

全量仅允许既有 `AgentInfo.test.tsx` 的 `1K` 基线失败。

5. 再次执行静态扫描，确认 inventory 内 56 项均不再保留硬编码英文，且没有误改技术/动态值。

## 交付

主 Agent 最终报告：
`ops/handoffs/p6-parallel-visible-ui-localization-completion.md`

报告列出每条 inventory 项的最终状态、合并 key、真实 UI 测试、构建和全量结果，以及残留英文分类。
