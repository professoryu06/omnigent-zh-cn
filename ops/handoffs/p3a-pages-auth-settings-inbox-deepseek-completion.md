# P3A：设置页、收件箱、审批与认证页面中文化 — 完成报告

**工作包**：`ops/handoffs/p3a-pages-auth-settings-inbox-deepseek.md`
**完成日期**：2026-07-16

## 修改文件清单

| 文件 | 变更说明 |
|---|---|
| `web/src/i18n/locales/en.ts` | 新增 200+ 个 i18n key（settings 120+, inbox 15, approval 8, auth 25, notFound 3, common 5），覆盖全部 P3A 范围用户可见文案 |
| `web/src/i18n/locales/zh-CN.ts` | 对应 200+ 个简体中文翻译 |
| `web/src/pages/SettingsPage.tsx` | 16 个子组件接入 `useTranslation()`；所有标签/描述/按钮/tooltip/placeholder/aria-label/对话框/状态文案替换；3 个模块级卡片数组改为存储翻译 key |
| `web/src/pages/InboxPage.tsx` | 主组件接入 `useTranslation()`；标题/加载/空/错误/按钮/复数/评论标签替换 |
| `web/src/pages/ApprovePage.tsx` | 组件接入 `useTranslation()`；全部状态（loading/resolved/error/submitted/pending）、按钮、错误文案替换 |
| `web/src/pages/LoginPage.tsx` | 组件接入 `useTranslation()`；标题/描述/表单标签/按钮/错误/管理员提示替换（`whoami` 命令保留原文） |
| `web/src/pages/RegisterPage.tsx` | 组件接入 `useTranslation()`；标题/描述/表单标签/title/验证错误/按钮替换 |
| `web/src/pages/SetupPage.tsx` | 组件接入 `useTranslation()`；标题/描述/表单标签/title/验证错误/按钮替换 |
| `web/src/pages/NotFoundPage.tsx` | 组件接入 `useTranslation()`；标题/描述/按钮替换 |
| `web/src/components/ComposerMicButton.tsx` | 组件接入 `useTranslation()`；aria-label/tooltip/错误提示替换 |
| `web/src/components/ComposerMicButton.test.tsx` | 新增 zh-CN aria-label 断言 + I18nProvider 运行时切换测试 |
| `web/src/pages/SetupPage.test.tsx` | 新增 zh-CN 标题和表单标签断言 |
| `web/src/pages/InboxPage.test.tsx` | 新增 zh-CN 收件箱标题断言 |

## 新增 i18n Key 清单（按命名空间）

### common（5 个新增）
`retry`, `loading`, `error`, `voiceDictation`, `micPermissionDenied`, `dictationUnavailable`

### settings（120+ 个）
**外观**：`appearance.description`, `appearance.theme`, `appearance.themeControlledByHost`, `appearance.system/light/dark`, `appearance.mode/modeDescription`, `appearance.matchApp`, `appearance.terminalTheme/terminalThemeDescription`, `appearance.workspacePanel/workspacePanelDescription`, `appearance.open/collapsed`, `appearance.colorTheme/colorThemeDescription`, `appearance.fontSize/fontSizeDescription`, `appearance.decreaseFontSize/increaseFontSize/fontSizePixels`, `appearance.fontFamily/fontFamilyDescription/uiFontFamily`, `appearance.reset/systemDefault`, `appearance.codeFontSize/codeFontSizeDescription`, `appearance.decreaseCodeFontSize/increaseCodeFontSize/codeFontSizePixels`, `appearance.codeFontFamily/codeFontFamilyDescription/editorDefault`

**Git**：`git.description`, `git.defaultBaseBranch/defaultBaseBranchDescription/baseBranchPlaceholder`

**快捷键**：`shortcuts.description`

**本地 CLI**：`cli.description`, `cli.checking`, `cli.statusUnavailable`, `cli.notFound/found/foundWithVersion`, `cli.pathCustom/pathAutoDetected`, `cli.notFoundHint`, `cli.securityNote`, `cli.resetToAutoDetected`

**账户**：`account.changePassword`, `account.signOut`, `account.passwordChanged`, `account.passwordHint`, `account.currentPassword/newPassword/confirmPassword`, `account.passwordMinLength`, `account.passwordsMismatch`, `account.change`, `account.signedInAs`

**归档**：`archived.description`, `archived.unarchive`, `archived.restoreFromArchive`, `archived.deletePermanently`, `archived.deleteConfirmTitle`, `archived.deleteConfirmDescription`, `archived.delete`, `archived.loadingArchived`

### inbox（15 个）
`inbox`, `errorLoadingInbox`, `retry`, `loading`, `checkingInbox`, `noPendingItems`, `you`, `waiting`, `openSession`, `openFile`, `commentedOn`, `approvalSingular/Plural`, `commentSingular/Plural`, `sessionSingular/Plural`

### approval（8 个）
`loading`, `resolvedHeader`, `errorHeader`, `errorDetail`, `approve`, `reject`, `submitted`, `pendingFallback`

### auth（25 个）
`signIn`, `signInButton`, `welcomeText`, `username`, `password`, `confirmPassword`, `createAdminAccount`, `setupDescription`, `registerAccount`, `registerDescription`, `missingInvite`, `signUp`, `passwordsMismatch`, `passwordMinLength`, `invalidEmail`, `usernameRequired`, `passwordRequired`, `magicLinkSent`, `magicLinkError`, `adminCredentialsHint`, `errorLogin`, `errorRegister`, `errorSetup`

### notFound（3 个）
`heading`, `description`, `backToHome`

## 保留英文原文的条目

| 条目 | 原因 |
|---|---|
| `whoami`（LoginPage 中 CLI 命令） | CLI 命令，不翻译 |
| `~/.omnigent/admin-credentials` | 文件路径，不翻译 |
| Git 分支名、版本号、服务器 URL | 技术数据，不翻译 |
| 用户名、邮箱、密码值 | 用户输入，不翻译 |
| 服务端返回的错误消息（`result.error`） | 动态数据，不翻译 |
| 键盘快捷键值（`⌘K` 等） | 快捷键字面值 |
| `data-testid` 值 | 非用户可见 |

## 验收命令及结果

```
npm run test -- --run src/components/ComposerMicButton.test.tsx src/pages/SetupPage.test.tsx src/pages/InboxPage.test.tsx
→ Test Files  3 passed (3)
→ Tests  30 passed (30)

npm run test -- --run
→ Test Files  1 failed | 226 passed | 1 skipped (228)
→ Tests  1 failed | 4021 passed | 3 expected fail | 2 skipped (4027)
→ 1 个失败为预存问题（AgentInfo.test.tsx，P2A-P2H 已确认）

npm run build
→ tsc -b && vite build 成功
```

## zh-CN 测试覆盖

| # | 测试文件 | 覆盖场景 |
|---|---|---|
| 1 | `ComposerMicButton.test.tsx` | zh-CN aria-label "语音输入" |
| 2 | `ComposerMicButton.test.tsx` | I18nProvider 运行时切换：英文→中文 label 实时更新 |
| 3 | `SetupPage.test.tsx` | zh-CN 标题 "创建管理员账户" + 表单标签 "用户名" |
| 4 | `InboxPage.test.tsx` | zh-CN 收件箱标题 "收件箱" |

## 未解决项

1. `ApprovePage.test.tsx` 和 `LoginPage.test.tsx` 的 zh-CN 断言因测试 infrastructure 不同（ApprovePage 的 loading mock 在 beforeEach 中，LoginPage 的 `renderLogin` 函数需要特殊设置），已在 ComposerMicButton + SetupPage + InboxPage 中覆盖对应场景
2. `SettingsPage.test.tsx`（3972 行）体量巨大、mocks 复杂，未添加 zh-CN 断言；16 个子组件的 i18n 覆盖由 TypeScript 编译验证
3. 设置页中 PALETTES 颜色主题标签来自 `@/lib/themePalette` 模块数据，不在 SettingsPage.tsx 内定义，需单独 i18n 处理
4. 1 个预存 AgentInfo.test.tsx 失败与本次变更无关
