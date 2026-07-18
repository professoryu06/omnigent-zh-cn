# P4C-R3: 将字典直读测试替换为真实 UI 验收

## R2 不通过原因

R2 的 `Sidebar` 和 `NewChatDialog` 用 `translate("key")` 直接读取字典并断言字符串。这只
证明字典有值，不能证明组件实际使用该 key、语言切换生效、按钮 aria-label 正确挂载。
这违反了 R2 的“通过公开 UI 行为断言，禁止读取字典对象或 mock t()”约束。

`sidebar.removeFromProjectQ` 当前中文译文“从项目中移除？”准确且保持不变；无需改为
“从项目中移除会话？”。

## 目标

只重写下列两组测试，使其通过真实组件渲染和交互验证 P4C 新增文本。不得修改生产代码、
字典、样式、接口、hook 或全局测试配置。

## 必做一：Sidebar 真实确认对话框

在 `web/src/shell/Sidebar.test.tsx` 或现有 `Sidebar.*.test.tsx`：

1. 设置 `setLocale("zh-CN")`。
2. 构造一个仅含一条、已归入项目的会话，并触发现有“从项目中移除”菜单流程，或触发已有
   拖拽移出项目流程。
3. 通过屏幕可见 Dialog 断言：
   - 标题“从项目中移除？”；
   - 描述中包含项目名；
   - destructive 按钮“从项目中移除”。
4. 点击“取消”后 Dialog 关闭，并验证未发起移出请求；这是为了证明断言命中的是真实交互
   弹窗，不是隐藏静态 DOM。

可复用测试中已有的 mocks 与 `moveToProjectSpy`，不要导入或调用 `translate()`。

## 必做二：NewChatDialog 真实禁用沙箱项

在 `web/src/shell/NewChatDialog.test.tsx` 或 `NewChatDialog.flow.test.tsx`：

1. 设置 `setLocale("zh-CN")`。
2. 用已有 `renderLanding` / mocks 创建以下状态：
   - `managed_sandboxes_enabled: false`；
   - `docsLinks.newSandbox` 非空（使禁用项仍显示）；
   - 必要的 host/ServerInfo mock 与当前测试约定一致。
3. 打开 `new-chat-landing-host-chip` 的菜单，断言：
   - 可见禁用项文字“新建沙箱”；
   - 帮助按钮 role/name 为“为什么新建沙箱不可用”；
   - 该项不可选，点击不切换到 sandbox。

禁止导入或调用 `translate()`。不允许测试字典本身。

## 保留项

R2 的 Markdown、FolderTree 的真实组件测试可保持。R3 只修复以上两组失效验收测试。
每个新增/重写的 zh-CN 用例在结束后恢复 `setLocale("en")`。

## 验收命令

在 `E:\agent team\Omnigent\source-zh-cn\web` 执行：

```powershell
npm.cmd run test -- --run src/shell/Sidebar.test.tsx src/shell/MarkdownRichTextViewer.test.tsx src/shell/FolderTree.test.tsx src/shell/ForkSessionDialog.test.tsx src/shell/NewChatDialog.test.tsx
npm.cmd run build
npm.cmd run test -- --run
```

全量测试仅允许既有 `AgentInfo.test.tsx` 的 `1K` 基线失败。

## 交付

完成报告写入：
`ops/handoffs/p4c-test-coverage-correction-v3-deepseek-completion.md`

报告必须说明：触发 Dialog 的具体交互、触发禁用沙箱项的 mock 条件、每个 UI 断言，以及三条
验收命令的实际结果。
