# P3C：共享交互与会话分享中文化 — 完成报告

**工作包**：`ops/handoffs/p3c-shared-interactions-deepseek-completion.md`（用户指定）
**完成日期**：2026-07-16

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 permissions（25）、shortcuts（27）、lightbox（7）、pwa（3）共 62 个英文 i18n key |
| `web/src/i18n/locales/zh-CN.ts` | 新增 permissions（25）、shortcuts（27）、lightbox（7）、pwa（3）共 62 个简体中文 i18n key |
| `web/src/components/PermissionsModal.tsx` | 6 个组件接入 `useTranslation()`；`LEVEL_LABELS` 重构为仅存储翻译 key；全部对话框标题/描述/标签/按钮/placeholder/aria-label/空状态/列标题替换 |
| `web/src/components/KeyboardShortcutsDialog.tsx` | 组件接入 `useTranslation()`；**`SHORTCUT_GROUPS` 重构**为 `buildShortcutGroups()` 函数，所有 `title`/`note`/`label` 存储为 key，渲染期 `t()` 解析；`Ctrl`/`Alt`/`Esc`/`Tab` 键名翻译化 |
| `web/src/components/ImageLightbox.tsx` | 3 个组件接入 `useTranslation()`；缩放/重置/关闭/图片预览所有 aria-label 和 sr-only 文案替换 |
| `web/src/components/pwa/PWAUpdateBanner.tsx` | 组件接入 `useTranslation()`；版本更新提示/重新加载/忽略文案替换 |
| `web/src/components/PermissionsModal.test.tsx` | 新增 5 条 zh-CN 断言（共享标题、公开访问、授权、撤销、I18nProvider） |
| `web/src/components/KeyboardShortcutsDialog.test.tsx` | 新增 3 条 zh-CN 断言（标题、发送消息标签）+ **I18nProvider 运行时切换测试**（英文→中文不重新挂载） |
| `web/src/components/ImageLightbox.test.tsx` | 新增 5 条 zh-CN 断言（放大、重置缩放、缩放图片、关闭、I18nProvider） |
| `web/src/components/pwa/PWAUpdateBanner.test.tsx` | 新增 4 条 zh-CN 断言（新版本提示、重新加载按钮、忽略按钮、I18nProvider） |

## 新增 i18n Key 清单

### permissions 命名空间（25 个）

`sharingUnavailable`, `sharingDisabled`, `done`, `shareThisSession`, `readOnlyDescription`, `fullDescription`, `publicAccess`, `publicAccessDesc`, `loading`, `noGrants`, `name`, `permission`, `userId`, `level`, `read`, `edit`, `manage`, `owner`, `grant`, `searching`, `noMatches`, `copied`, `copyLink`, `permissionLevelFor`, `revoke`

### shortcuts 命名空间（27 个）

`title`, `description`, `ctrl`, `alt`, `esc`, `tab`, `general`, `openCommandPalette`, `showKeyboardShortcuts`, `inChats`, `sendMessage`, `newLineInMessage`, `recallPreviousPrompt`, `recallNextPrompt`, `acceptApproval`, `stopResponse`, `navigation`, `previousSession`, `nextSession`, `view`, `toggleConversationsSidebar`, `toggleWorkspaceSidebar`, `slashCommands`, `whileMenuOpen`, `navigateSuggestions`, `applyHighlightedCommand`, `dismissMenu`, `jumpToPinned`

### lightbox 命名空间（7 个）

`zoomIn`, `zoomOut`, `resetZoom`, `close`, `imagePreview`, `zoomImage`, `zoomImageAlt`

### pwa 命名空间（3 个）

`newVersionAvailable`, `reload`, `dismiss`

## 关键架构决策

### KeyboardShortcutsDialog SHORTCUT_GROUPS 重构

**改动前**（模块级常量存储英文文案）：
```ts
const SHORTCUT_GROUPS = [
  { title: "General", items: [{ label: "Open command palette", keys: [...] }] },
  ...
];
```

**改动后**（`buildShortcutGroups()` 函数返回 key-only 配置，渲染期 `t()` 解析）：
```ts
function buildShortcutGroups(ctrl: string, alt: string, esc: string, tab: string) {
  return [
    { titleKey: "shortcuts.general", items: [{ labelKey: "shortcuts.openCommandPalette", keys: [ctrl, "K"] }] },
    ...
  ];
}
```

按键符号（`⌘`/`↵`/`⇧`/`⌥`/`↑`/`↓`/`K`/`/`/`[`/`]`/`1…0`）保留原样不翻译。

### PermissionsModal LEVEL_LABELS 重构

```ts
// 改动前：{ 1: "Read", 2: "Edit", 3: "Manage", 4: "Owner" }
// 改动后：{ 1: "permissions.read", 2: "permissions.edit", 3: "permissions.manage", 4: "permissions.owner" }
```

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| `alice@example.com` 占位符 | 示例邮箱，不翻译 |
| 按键符号 `⌘`/`↵`/`⇧`/`⌥`/`↑`/`↓`/`K`/`/`/`[`/`]`/`1…0` | 键盘符号，不翻译 |
| 用户 ID、邮箱、服务端错误 | 动态/系统数据 |
| 图片 alt 文本 | 用户内容 |
| `Omnigent` 品牌名称 | 产品名 |
| `data-testid` 值 | 非用户可见 |

## 验收命令及结果

```
npm run test -- --run src/components/PermissionsModal.test.tsx src/components/KeyboardShortcutsDialog.test.tsx src/components/ImageLightbox.test.tsx src/components/pwa/PWAUpdateBanner.test.tsx
→ Test Files  4 passed (4)
→ Tests  55 passed (55)

npm run test -- --run
→ Test Files  1 failed | 226 passed | 1 skipped (228)
→ Tests  1 failed | 4048 passed | 3 expected fail | 2 skipped (4054)
→ 1 个失败为预存问题（AgentInfo.test.tsx，P2A-P3B 已确认）

npm run build
→ tsc -b && vite build 成功
```

## zh-CN 测试覆盖（15 条断言，远超 6 条要求）

| # | 测试文件 | 覆盖场景 |
|---|---|---|
| 1 | PermissionsModal | 标题"共享此会话" |
| 2 | PermissionsModal | 标签"公开访问" |
| 3 | PermissionsModal | 动作"授权" |
| 4 | PermissionsModal | 动作"撤销" |
| 5 | PermissionsModal | I18nProvider 集成 |
| 6 | KeyboardShortcutsDialog | 标题"键盘快捷键" |
| 7 | KeyboardShortcutsDialog | 标签"发送消息" |
| 8 | KeyboardShortcutsDialog | **运行时切换**：I18nProvider 包裹，英文→中文不重新挂载 |
| 9 | ImageLightbox | "放大" |
| 10 | ImageLightbox | "重置缩放" |
| 11 | ImageLightbox | "缩放图片" |
| 12 | ImageLightbox | "关闭" |
| 13 | ImageLightbox | I18nProvider 集成 |
| 14 | PWAUpdateBanner | "有新版本可用。" |
| 15 | PWAUpdateBanner | "重新加载"按钮 |
| 16 | PWAUpdateBanner | "忽略"按钮 |
| 17 | PWAUpdateBanner | I18nProvider 集成 |

## 未解决项

无。所有四个组件中已发现的静态英文文案均已接入 `t()` 调用。
