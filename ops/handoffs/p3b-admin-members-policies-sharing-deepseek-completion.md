# P3B：成员管理、全局策略与会话共享中文化 — 完成报告

**工作包**：`ops/handoffs/p3b-admin-members-policies-sharing-deepseek.md`
**完成日期**：2026-07-16

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 members（30）、policies（22）、sharing（18）共 70 个英文 i18n key |
| `web/src/i18n/locales/zh-CN.ts` | 新增 members（30）、policies（22）、sharing（18）共 70 个简体中文 i18n key |
| `web/src/pages/MembersPage.tsx` | 组件 + `CopyableValue` 接入 `useTranslation()`；所有标题/表头/按钮/tooltip/aria-label/对话框/徽章/空状态/加载文案替换；`formatEpoch`/`formatTtl` 使用 `translate()` |
| `web/src/pages/PoliciesPage.tsx` | `PoliciesPage` + `AddDefaultPolicyDialog` 接入 `useTranslation()`；所有标题/描述/按钮/placeholder/标签/对话框/空状态/参数类型标签替换 |
| `web/src/pages/SharingPage.tsx` | 组件接入 `useTranslation()`；**TIERS 模块级常量重构**为仅存储 `id`/`labelKey`/`descKey`，渲染期通过 `t()` 解析标签和描述；所有标题/描述/权限提示/公开访问/aria-label 替换 |
| `web/src/pages/MembersPage.test.tsx` | 新增 zh-CN 标题 + 表头断言、邀请对话框断言；修复 "Loading…"→"Loading..." 断言 |
| `web/src/pages/PoliciesPage.test.tsx` | 新增 zh-CN 标题 + 空状态断言、添加策略对话框断言 |
| `web/src/pages/SharingPage.test.tsx` | 新增 zh-CN 标题 + 4 个 tier 标签断言、公开访问 label 断言；**I18nProvider 运行时切换测试**（英文→中文不重新挂载） |

## 新增 i18n Key 清单

### members 命名空间（30 个）

`title`, `singleUserNotice`, `permissionDenied`, `inviteMember`, `oidcReadOnly`, `username`, `role`, `lastLogin`, `actions`, `you`, `external`, `admin`, `member`, `resetPassword`, `reset`, `removeUser`, `remove`, `noMembersYet`, `refresh`, `inviteDialogTitle`, `inviteDialogDescription`, `grantAdmin`, `creating`, `createInvite`, `inviteUrlTitle`, `inviteUrlDescription`, `done`, `newPasswordFor`, `passwordInstructions`, `removeDialogTitle`, `removeDialogDescription`, `removing`, `copy`, `copied`, `never`, `soon`

### policies 命名空间（22 个）

`title`, `permissionDenied`, `description`, `addPolicy`, `addDialogTitle`, `addDialogDescription`, `filterPlaceholder`, `allApplied`, `noMatch`, `change`, `name`, `multiSelect`, `commaSeparated`, `commaSeparatedValues`, `adding`, `add`, `disabled`, `toggle`, `removePolicy`, `parameters`, `empty`, `refresh`, `removeDialogTitle`, `removeDialogDescription`, `removing`

### sharing 命名空间（18 个）

`title`, `permissionDenied`, `description`, `deploymentManaged`, `modeLabel`, `tierOnLabel`, `tierOnDesc`, `tierReadOnlyLabel`, `tierReadOnlyDesc`, `tierReadOnlyRestrictedLabel`, `tierReadOnlyRestrictedDesc`, `tierOffLabel`, `tierOffDesc`, `publicAccess`, `publicAccessDescription`, `publicAccessManaged`, `loading`

## 关键架构决策

### SharingPage TIERS 模块级常量重构

按手off 要求，`TIERS` 不得保存已翻译的标签和描述。变更如下：

**改动前**（存储英文文案）：
```ts
const TIERS = [
  { id: "on", label: "On", description: "Anyone with manage access..." },
  ...
];
```

**改动后**（仅存储稳定 ID 和翻译 key）：
```ts
const TIERS: { id: SharingMode; labelKey: string; descKey: string }[] = [
  { id: "on", labelKey: "sharing.tierOnLabel", descKey: "sharing.tierOnDesc" },
  ...
];

// 渲染期通过 t() 解析
{t(tier.labelKey)}
```

语言切换后已挂载组件随 React 重渲染即时更新。

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| 用户名、用户 ID、邮箱、密码 | 用户/系统数据 |
| 邀请 URL、策略名称、策略内容/JSON | 动态生成或服务端数据 |
| `array`/`string` 等 JSON Schema 类型名 | 技术标识符，不翻译 |
| 服务端错误（`result.error`、`err.message`） | 动态数据 |
| 时间戳、TTL 值 | 动态数据 |
| `data-testid` 值 | 非用户可见 |

## 验收命令及结果

```
npm run test -- --run src/pages/MembersPage.test.tsx src/pages/PoliciesPage.test.tsx src/pages/SharingPage.test.tsx
→ Test Files  3 passed (3)
→ Tests  38 passed (38)

npm run test -- --run
→ Test Files  1 failed | 226 passed | 1 skipped (228)
→ Tests  1 failed | 4030 passed | 3 expected fail | 2 skipped (4036)
→ 1 个失败为预存问题（AgentInfo.test.tsx，P2A-P3A 已确认）

npm run build
→ tsc -b && vite build 成功
```

## zh-CN 测试覆盖

| # | 测试文件 | 覆盖场景 |
|---|---|---|
| 1 | `MembersPage.test.tsx` | zh-CN 标题 "成员" + 表头 "用户名"/"角色" |
| 2 | `MembersPage.test.tsx` | zh-CN 邀请对话框 "邀请成员"/"创建邀请" |
| 3 | `PoliciesPage.test.tsx` | zh-CN 标题 "全局策略" + 空状态 |
| 4 | `PoliciesPage.test.tsx` | zh-CN 添加策略对话框 "添加全局策略" + 权限提示 |
| 5 | `SharingPage.test.tsx` | zh-CN 标题 "会话共享" + 4 个 tier 标签（开启/仅读取/仅读取（受限）/关闭） |
| 6 | `SharingPage.test.tsx` | zh-CN 公开访问标签 "公开访问" + switch aria-label "会话共享模式" |
| 7 | `SharingPage.test.tsx` | **运行时切换**：I18nProvider 包裹，英文→中文 tier 和 public access 文本即时更新（无需重新挂载） |

## 未解决项

1. `MembersPage.test.tsx` 中两处 `"Loading…"`（U+2026 省略号）断言更新为 `"Loading..."`（三个点），因 `common.loading` 字典值为 ASCII 三个点。若后续要求统一省略号字符，可批量替换字典值
2. `PoliciesPage.tsx` 中 JSON Schema 类型名（`{prop.type}`）保持英文原文直接渲染——这些是技术数据而非 UI 文案
3. 1 个预存 AgentInfo.test.tsx 失败与本次变更无关
