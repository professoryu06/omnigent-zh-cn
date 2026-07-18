# P5-R3: MCP 中文断言与 P6 分类一致性修正

## 只做两件事

本包禁止修改生产代码、双词典、样式、接口、hooks 与全局测试配置。

### 1. MCP 真实 UI 断言收紧

当前 `ChatPage.indicators.test.tsx` 已真实渲染 `McpStartupIndicator`，但只断言 `/\+\d/`。
这不能证明中文翻译 `chat.andNMore` 的“个”实际显示。

保留当前 10 个 MCP server 的真实渲染路径，将断言改为完整、确定的可见文案：

```ts
expect(screen.getByTestId("mcp-startup-indicator").textContent).toContain("+2 个");
```

不能回退为纯函数测试、字典直读、正则数字匹配或 test-id 存在性断言。

### 2. P6 清单分类一致性

重写/修正 `ops/handoffs/p6-visible-english-inventory.md` 的汇总和明细：

- `HTTP`、`stdio` 只能出现在 `keep_technical`，不得同时留在 `must_translate` 表；
- 下列条目虽然包含技术样例，但**外围说明文字**仍是 `must_translate`，应作为独立条目记录，
  并注明技术样例保持不变：
  - `e.g. *.ts, src/**`；
  - `e.g. **/node_modules, *.test.ts`；
  - `command (e.g. npx)`；
  - `args (e.g. -y @modelcontextprotocol/server-github)`；
- 每个条目只能有一个主分类；混合字符串要拆成“需要本地化的外围文案”和“保留的技术样例”两条
  说明，不能写成矛盾的双重分类；
- 更新准确的分类汇总数量，并使其等于明细总数；
- URL、分支、模型 ID、CLI 命令本体、glob 语法、文件大小单位继续保留原样。

## 验收

运行受影响测试、构建和全量测试。全量只允许既有 `AgentInfo.test.tsx` 的 `1K` 基线失败。

## 交付

报告写入：
`ops/handoffs/p5r3-mcp-test-and-p6-consistency-completion.md`

报告必须列出 MCP 的完整中文断言、P6 分类变动和最终各分类数量。
