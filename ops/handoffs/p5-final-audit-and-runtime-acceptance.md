# P5: 最终英文残留审计与浏览器运行验收

## 前置状态

P2A-P4D 已完成，P4D-R 已通过定向真实 UI 测试。当前已知仍需审计的可见残留：

- `web/src/pages/ChatPage.tsx`：`Chatting with sub-agent …`（子智能体对话提示）。

不要基于猜测做全仓批量替换；本包先审计、分类、再对确认的用户可见文本做最小修复。

## 阶段 A：静态审计

扫描 `web/src`（排除 `*.test.*`、`i18n/locales`、注释、类型和构建产物），建立报告：

`ops/handoffs/p5-visible-english-audit.md`

每项包含：文件、行号、原字符串、是否真实用户可见、分类、修复建议。

分类只能是：

1. `must_translate`：面向用户的固定 UI 文案；
2. `keep_technical`：CLI、协议、模型 ID、产品名、命令、代码标识；
3. `keep_dynamic`：服务器返回的名称、路径、分支、URL、文件内容；
4. `ignore_non_ui`：注释、类型、测试 fixture、开发日志。

特别检查 JSX 文本、`aria-label`、`title`、`placeholder`、toast、dialog、tooltip、空状态、错误状态、
菜单项和状态标签。禁止把扫描得到的注释或技术标识误报为待翻译。

## 阶段 B：最小修复

只修复审计报告中的 `must_translate` 项。每个改动必须：

- 用 `useTranslation()` 或项目认可的调用时翻译机制；
- 双词典键完全同步；
- 不在模块加载时缓存 `t()` 的返回值；
- 保留动态值与技术标识原样；
- 为每个修复区域新增真实 UI 中文断言，不得 `translate()` 字典直读或 mock `t()`。

`Chatting with sub-agent …` 如仍为真实 UI 文案，必须译为自然中文，例如“正在与子智能体 {{agent}} 对话”，
并保持实际 agent 名称动态插值。

## 阶段 C：浏览器运行验收

构建后用本项目的隔离静态前端服务访问中文版本，完成并记录：

1. 新建会话页、聊天输入、会话列表和侧栏；
2. 文件、终端、智能体、设置、对话框与菜单；
3. 中英文运行时切换；
4. 窄屏/移动视口下聊天与终端切换；
5. 空状态、错误状态、禁用状态与 toast；
6. 页面控制台没有新增错误。

没有可用浏览器自动化能力时，必须明确写“未执行浏览器验收”及原因，不得伪称完成。

## 验收

在 `E:\agent team\Omnigent\source-zh-cn\web`：

```powershell
npm.cmd run build
npm.cmd run test -- --run
```

只允许已知 `AgentInfo.test.tsx` 的 `1K` 基线失败。所有其他失败必须修复。

## 交付

完成报告写入：
`ops/handoffs/p5-final-audit-and-runtime-acceptance-completion.md`

报告包含：审计分类统计、修复项、保留英文及理由、UI 测试、构建与全量测试结果、浏览器验收结果和
任何无法验证的限制。
