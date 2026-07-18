# P3D 工作包：AgentInfo 会话信息面板中文化

## 项目与目标

- 工作目录：`E:\agent team\Omnigent\source-zh-cn`
- 目标：将 `AgentInfo` 会话信息面板内所有面向用户的静态英文接入既有 i18n，使 `zh-CN` 下显示简体中文，同时保持 MCP、策略、会话权限、用量统计与复制行为完全不变。

## 允许修改

- `web/src/components/AgentInfo.tsx`
- `web/src/components/AgentInfo.test.tsx`
- `web/src/i18n/locales/en.ts`
- `web/src/i18n/locales/zh-CN.ts`

## 禁止修改

- 不改后端、API、hooks、store、路由、权限、MCP/策略提交逻辑、会话用量计算、CSS、DOM 结构、`data-testid`。
- 不改 `AgentInfo.test.tsx:382` 现有 `1K` token 格式化基线失败；该失败不属于本工作包。
- 不翻译用户输入、用户名、会话 ID、MCP 服务器名称、MCP 命令/URL/参数、模型名称、策略名称与描述、后端错误、协议值（如 `http`、`stdio`、`true`、`false`）。
- 不碰其它组件或测试文件，不做无关重构。

## 必须覆盖的静态 UI

1. 会话信息：所有者、当前用户标记、会话 ID、复制/已复制、会话成本、工具与策略区域、智能体工具与策略按钮/提示。
2. MCP 服务器：管理窗口标题、说明、服务器区、添加/编辑/删除、空状态、字段标签、保存/清空/取消、保存中、重启生效提示与 toast。
3. 会话策略：添加策略窗口、描述、筛选 placeholder、空状态、添加/移除动作。
4. 用量展示的静态标签：输入、输出、总计、成本等。模型名和数值本身必须保持原样。
5. 所有相关 tooltip、`title`、`aria-label`、按钮和可见文本。

## 实施规则

1. 使用 `useTranslation()` 与 `t()`；所有新 key 必须同时加入 `en.ts`、`zh-CN.ts`，两边严格一一对应。
2. 任何模块级常量、配置数组或辅助函数不得在模块加载时保存翻译结果。它们只能保存稳定 key/原始数据，并在组件渲染期调用 `t()`。
3. 对需要在 callback、toast、异步回调中显示的静态文案，保证当前语言可正确解析；不要为了翻译而改变请求时机或业务状态。
4. 保留技术占位示例（如 `github`、`https://example.com/sse`、`npx`）和协议选项原文；只翻译字段标签和说明。
5. 服务器返回的 `err.message` 及用户/服务器数据按原样显示。

## 测试要求

1. 在现有 `AgentInfo.test.tsx` 中新增至少 8 条 `zh-CN` 断言，覆盖：会话信息、复制状态、MCP 管理、MCP 空状态或重启提示、会话策略、添加策略弹窗、用量标签、无障碍标签/tooltip。
2. 至少新增一条 I18nProvider 运行时语言切换测试，验证组件不重新挂载时英文能切换为中文。
3. 不删除或放宽现有断言。

## 验收命令

在 `web` 目录执行：

```powershell
npm.cmd run test -- --run src/components/AgentInfo.test.tsx
npm.cmd run build
```

全量回归可运行，但预期保留 `AgentInfo.test.tsx:382` 的既有 token 格式化失败。不得将其归因于 P3D，除非本次改动改变了该失败行为。

## 完成报告

完成后创建：

`ops/handoffs/p3d-agent-info-deepseek-completion.md`

报告需列出修改文件、i18n key 数、中文覆盖点、目标测试结果、构建结果、全量测试结果和遗留项。
