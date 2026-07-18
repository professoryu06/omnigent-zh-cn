# P5-R: 已修复可见文案的质量与真实 UI 验证

## P5 复核发现

P5 代码已修改 ChatPage、toast、spinner 与 SessionImage，但完成报告没有列出这些新增文本的真实
UI 测试；现有目标测试仍是 P4D 的四个文件。P5 还留下一个不符合全中文目标的译文：

- `chat.effortXHigh` 在 `zh-CN.ts` 中仍是 `xHigh`。

另外，P5 报告称有约 75 个 `must_translate` 残留，但没有给出每一项的文件、行号和原文，不能
作为安全批量改动的依据。这部分不在本修正包实施范围，交由 P6 审计。

## 允许修改

- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`
- `web/src/pages/ChatPage.tsx`（仅 P5 已改区域的确定修正）
- `web/src/components/ui/toast.tsx`
- `web/src/components/ui/spinner.tsx`
- `web/src/components/SessionImage.tsx`
- 对应的现有/新增测试。

禁止处理 P6 遗留组件，不改接口、业务逻辑、样式、全局测试配置。

## 必做修正

1. `chat.effortXHigh` 的简体中文改为自然用户文案，例如“极高”；保留底层 `xhigh` ID 不变。
2. `chat.chattingWithSubAgentPrefix` 译文应自然连接动态 agent 名称。推荐“正在与子智能体：”；
   不能把 agent 名翻译或硬编码。

## 必须新增的真实 UI 测试

在 `setLocale("zh-CN")` 下，通过真实组件渲染或用户交互，至少覆盖下列 10 项中的 8 项，且
必须覆盖每个源文件：

### ChatPage（至少 5 项）
- 沙箱启动失败（带与不带动态 error 至少一种）；
- MCP 启动失败/取消或溢出 “+N 个”；
- 正在压缩会话；
- 助手错误标签“错误”；
- 上下文占用 aria-label 或 tooltip；
- 推理强度“极高”；
- 子智能体兜底“子智能体”或“正在与子智能体：<动态名称>”；
- `/compact` 不支持错误；
- 匿名文件兜底“未知文件”。

### toast
- 关闭按钮的 aria-label 为“关闭”，点击后 toast 消失。

### spinner
- loading 状态的 aria-label 为“加载中...”。

### SessionImage
- 图像加载占位的 role=status / accessible name 为“加载图像中”。

## 测试约束

- 禁止导入或调用 `translate()` 直接读取字典，禁止 mock `t()`，禁止检查源代码字符串；
- 只能断言 screen/DOM 的文本、role、aria-label、title 或真实交互结果；
- 每个 zh-CN 测试结束后恢复 `setLocale("en")`；
- 动态 error、agent 名、文件名、URL、路径、模型 ID、命令与协议名须保留原样。

## P6 审计输入

另写：`ops/handoffs/p6-visible-english-inventory.md`。
该文件只记录尚未修复的每一个 `must_translate` 项，必须有文件、精确行号、原文、UI 上下文、建议
key；不要用“约 75 处”汇总替代明细。技术标识/动态数据要列出保留理由。

## 验收

运行受影响测试、构建和全量测试：

```powershell
npm.cmd run build
npm.cmd run test -- --run
```

全量仅允许已知 `AgentInfo.test.tsx` 的 `1K` 基线失败。

## 交付

完成报告：
`ops/handoffs/p5-implementation-verification-correction-completion.md`

必须列出每项真实 UI 测试、触发方式、断言内容，以及 P6 清单统计。
