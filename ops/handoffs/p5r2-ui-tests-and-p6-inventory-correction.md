# P5-R2: 补齐真实 UI 验收并校正 P6 清单分类

## P5-R 未通过项

1. `spinner.tsx` 没有真实组件级中文可访问名称测试；`button.test.tsx` 与 SessionImage 对 spinner
   的间接/正则匹配不算验收。
2. MCP 溢出 `+N 个` 测试直接调用 `mcpSettledNames()` 纯函数，违反“只能通过真实组件渲染或用户
   交互”的约束。

## P6 清单误分类

下列项目默认属于技术样例或动态数据，不得作为普通中文文案翻译；审计必须重新分类并说明理由：

- URL/仓库/分支样例：`https://...`、`feature/my-branch`；
- 命令、模型、服务器名样例：`npx`、`github`、`my-agent`、`server-name`、模型 ID；
- 协议和传输标识：`HTTP`、`stdio`、MCP；
- 文件大小单位：KB、MB、GB、TB；
- 执行条目或 Git/分支技术名称：如 `main`；
- 文件 glob 语法本身：`*.ts`、`src/**`、`**/node_modules`。

若外围说明文字（如 `e.g.`、`command`、`args`）对用户可见，可只翻译说明文字，保留样例本体。

## 允许修改

- `web/src/components/ui/spinner.test.tsx`（可新建）及必要的现有 spinner 测试；
- `web/src/pages/ChatPage.indicators.test.tsx`；
- `ops/handoffs/p6-visible-english-inventory.md`；
- `ops/handoffs/p5-implementation-verification-correction-completion.md`（仅更正报告统计）。

禁止修改生产代码、双词典、样式、接口、hook、全局测试配置。

## 必做测试

### A. Spinner

在 `setLocale("zh-CN")` 下真实渲染 `Spinner`，断言其可访问名称/aria-label 是“加载中...”。
再验证英文 locale 是 `Loading`。禁止 mock `t()`、`translate()` 直读或仅检查 class/test id。

### B. MCP 溢出

构造足够多 MCP server 名称，真实渲染实际承载溢出文案的 ChatPage 组件（例如
`McpStartupIndicator` 或其真实父组件），断言可见文本含“+1 个”。不得调用
`mcpSettledNames()`、不得只测纯函数。

每个中文测试后恢复 `setLocale("en")`。

## P6 清单要求

重写 `ops/handoffs/p6-visible-english-inventory.md`：

1. 每项仍需文件、精确行号、原文、UI 上下文、分类、建议处理；
2. 分类必须是 `must_translate`、`keep_technical`、`keep_dynamic`、`ignore_non_ui` 四者之一；
3. 对上述误分类类别逐项纠正，不能简单删除；
4. 仅 `must_translate` 项进入后续 P6 实现范围；
5. 汇总每种分类的准确数量。

## 验收与交付

运行相关测试、构建和全量测试。仅允许既有 `AgentInfo.test.tsx` 的 `1K` 基线失败。

报告：`ops/handoffs/p5r2-ui-tests-and-p6-inventory-correction-completion.md`

报告应列出 Spinner 与 MCP 的真实组件测试证据、重新分类后的 P6 数量和所有保留类别的依据。
