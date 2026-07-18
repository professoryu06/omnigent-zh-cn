# P2E：终端与 Shell 中文化 — 完成报告

**工作包**：`ops/handoffs/p2e-terminals-deepseek.md`
**完成日期**：2026-07-16

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 14 个 `terminal.*` 英文 i18n key |
| `web/src/i18n/locales/zh-CN.ts` | 新增 14 个 `terminal.*` 简体中文 i18n key |
| `web/src/shell/terminalStatus.tsx` | `STATUS_CONFIG` 重构为存储 i18n key 而非硬编码英文标签；`TerminalStatusBadge` 接入 `useTranslation()`，在渲染期调用 `t()` 确保语言切换实时响应 |
| `web/src/shell/NewTerminalButton.tsx` | 组件接入 `useTranslation()`；6 处文案替换为 `t()` 调用（新建 Shell、选择 Shell、默认标记、创建失败错误） |
| `web/src/shell/TerminalsPanel.tsx` | 组件接入 `useTranslation()`；"Shells" 标题和 "Close" aria-label 替换 |
| `web/src/shell/MainTerminalView.tsx` | 组件接入 `useTranslation()`；"No terminals available." 空状态和 "Close shell" aria-label 替换 |
| `web/src/shell/terminalStatus.test.tsx` | 新增中文静态断言（5 种终端状态标签）；新增 `I18nProvider` 包裹的语言切换实时响应测试（`LocaleSwitch` 交互后验证标签即时更新为中文） |

## 新增 i18n Key 清单

### terminal 命名空间（14 个）

| Key | 英文 | 简体中文 |
|---|---|---|
| `terminal.shells` | Shells | 终端 |
| `terminal.close` | Close | 关闭 |
| `terminal.closeShell` | Close shell | 关闭 Shell |
| `terminal.noneAvailable` | No terminals available. | 无可用终端。 |
| `terminal.newShell` | New shell | 新建 Shell |
| `terminal.chooseShell` | Choose shell | 选择 Shell |
| `terminal.defaultShellSuffix` | ` (default)` | （默认） |
| `terminal.createFailed` | Failed: {{message}} | 失败：{{message}} |
| `terminal.statusActive` | Active | 活跃 |
| `terminal.statusIdle` | Idle | 空闲 |
| `terminal.statusConnecting` | Connecting | 连接中 |
| `terminal.statusError` | Error | 错误 |
| `terminal.statusClosed` | Closed | 已关闭 |

## 关键架构决策

### STATUS_CONFIG 重构

按手off 规则第 4 条要求，`STATUS_CONFIG` 不得保存已翻译的 `label`。变更如下：

**改动前**（模块级常量持有英文文案）：
```ts
export const STATUS_CONFIG: Record<TerminalStatus, { label: string; className: string }> = {
  active: { label: "Active", className: "bg-emerald-500" },
  // ...
};
```

**改动后**（存储 key，渲染期翻译）：
```ts
export const STATUS_CONFIG: Record<TerminalStatus, { key: string; className: string }> = {
  active: { key: "terminal.statusActive", className: "bg-emerald-500" },
  // ...
};

export function TerminalStatusBadge({ status }: { status: TerminalStatus }) {
  const { t } = useTranslation();
  const { key, className } = STATUS_CONFIG[status];
  const label = t(key);
  // label 用于 aria-label、title 和可见文本
}
```

语言切换后 `TerminalStatusBadge` 随 React 重渲染自动更新标签为当前语言文案，不会停留在模块加载时的语言。

### 语言切换实时响应测试

测试文件包含一个 `LocaleSwitch` 组件，通过 `I18nProvider` 包裹后，验证点击切换按钮时 `TerminalStatusBadge` 的 `aria-label` 从 `"Active"` 实时变为 `"活跃"`，确认组件完全响应 React context 语言变更。

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| Shell 名称（`bash`、`zsh`、`fish` 等） | 服务端返回的 Shell 名称，不翻译 |
| 会话名称（`s1` 等） | 服务端数据 |
| `$SHELL` | Shell 环境变量名 |
| `PTY` | 技术缩写 |
| `TerminalView` | 组件名 |
| 终端内容/输出 | Agent 原始输出 |

## 验收命令及结果

```
npm run test -- --run src/shell/MainTerminalView.test.tsx src/shell/TerminalsPanel.test.tsx src/shell/NewTerminalButton.test.tsx src/shell/terminalStatus.test.tsx src/shell/InlineTerminalsSection.test.tsx
→ Test Files  5 passed (5)
→ Tests  34 passed (34)

npm run test -- --run
→ Test Files  1 failed | 226 passed | 1 skipped (228)
→ Tests  1 failed | 4008 passed | 3 expected fail | 2 skipped (4014)
→ 1 个失败为预存问题（AgentInfo.test.tsx，P2A/P2B/P2C/P2D 已确认）

npm run build
→ tsc -b && vite build 成功
```

## 未处理项

无。本包覆盖范围较小（终端状态标签 + Shell 按钮 + 面板标题/关闭），所有已发现英文文案均已接入 `terminal.*` key。

## 超出范围的发现

- `InlineTerminalsSection.tsx` 无需修改：纯渲染 `TerminalStatusBadge`（已 i18n 化）和 `NewTerminalButton`（已 i18n 化），自身无额外硬编码英文文案
- `useTerminalStatuses.ts` / `useTerminalSplit.ts` / `useTerminals.ts` 为 hooks 层，不含用户可见文案
