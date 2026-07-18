# P3B: Admin Members, Policies, and Sharing Chinese Localization

You are the constrained implementation agent for Omnigent Web UI Simplified Chinese localization. Complete only this work package. Do not expand its scope.

## Goal

Translate the remaining static user-facing copy in the three admin settings surfaces:

- Member management: `MembersPage.tsx`
- Global policies: `PoliciesPage.tsx`
- Server-wide session sharing: `SharingPage.tsx`

The default `zh-CN` UI must render Chinese. The `en` locale must retain the current English copy. Permission gates, admin checks, API calls, mutations, routes, sensitive-value handling, and UI behavior must remain exactly unchanged.

## Context

- Workspace: `E:\agent team\Omnigent\source-zh-cn\web`
- Dictionaries: `src/i18n/locales/en.ts`, `src/i18n/locales/zh-CN.ts`
- Existing test setup pins English unless a test intentionally renders `I18nProvider` under `zh-CN`.
- P3A is complete and localized Settings, Inbox, approval, auth, and landing microphone UI. Do not reopen those files.
- The user asked for full UI localization. This package is limited to these three admin pages; shared permission dialogs and agent/session cards are later packages.

## Allowed Files

- `src/pages/MembersPage.tsx`
- `src/pages/PoliciesPage.tsx`
- `src/pages/SharingPage.tsx`
- `src/i18n/locales/en.ts`
- `src/i18n/locales/zh-CN.ts`
- Existing adjacent tests only:
  - `src/pages/MembersPage.test.tsx`
  - `src/pages/PoliciesPage.test.tsx`
  - `src/pages/SharingPage.test.tsx`

## Explicitly Forbidden

- No backend, API client, hooks, store, router, persistence, WebSocket, capability, authentication, or permission changes.
- No changes to `SettingsPage.tsx`, `settingsNav.tsx`, `PermissionsModal.tsx`, `AgentInfo.tsx`, `ChatPage.tsx`, or any files outside the allowed list.
- No changes to API payloads, mutation execution, refresh timing, optimistic behavior, button enablement, access gates, sensitive-data visibility rules, table structure, CSS/layout, or `data-testid` values.
- Do not translate dynamic user/server data: account/user IDs, emails, passwords, invite URLs, policy names/body content, server errors (`result.error`, `err.message`), timestamps, routes, CLI commands, URLs, code identifiers, protocol values (`http`, `stdio`), or product names.

## Required UI Coverage

### MembersPage

Translate all static headings, descriptions, loading, permission, error-prefix text, table headers, badges, buttons, `title`, `aria-label`, empty states, invite/reset/delete dialogs, confirmation copy, checkbox text, sensitive-value instructions, copy feedback, and actions.

Keep generated invite URLs, generated passwords, username/account IDs, API errors, and time values unchanged.

### PoliciesPage

Translate all static headings, descriptions, loading/permission/empty/error states, policy type labels/descriptions, add/edit/remove controls, fields, dialog labels, validation copy, confirmation copy, placeholders, accessible labels, and toasts.

Preserve actual policy names, command/filter expressions, JSON/structured policy data, and server-returned errors unchanged.

### SharingPage

Translate all static headings, descriptions, loading/permission/managed notices, sharing tier names/descriptions, public-access section, labels, errors, and `aria-label` values.

`TIERS` currently stores user-facing English labels and descriptions at module level. Refactor it to store only stable IDs/non-copy data. Resolve label and description through `t()` at render time. Do not call `translate()` at module load time and do not cache rendered translations in constants.

## i18n Rules

1. Add matching English and Simplified Chinese keys to both dictionaries. Prefer namespaces `members.*`, `policies.*`, and `sharing.*`; reuse `common.*` only where wording is truly identical.
2. Components render dynamic UI text through `const { t } = useTranslation()`.
3. For complete sentences containing variables, use a single key with named variables. Do not concatenate Chinese fragments around variables. Variables remain raw values.
4. Translate every static `title`, `aria-label`, `placeholder`, dialog title/description, empty/loading/error state, button, tooltip, badge, and toast in scope.
5. Module-level arrays may hold translation keys and stable IDs only. Render-time `t()` is mandatory so the currently mounted UI updates on locale switch.

## Tests

Before changing production code, add or update focused tests with explicit `zh-CN` assertions. Add at least six Chinese assertions in total:

1. Members page heading plus one table header, empty state, or permission state.
2. Members invite, reset-password, or delete dialog/action.
3. Policies page heading plus an empty/permission/loading state.
4. Policies add/edit/remove dialog or action.
5. Sharing page heading plus one tier/managed state.
6. Sharing public-access label or accessible radio-group label.

Also add one `I18nProvider` runtime switch test for the already mounted Sharing page. It must prove an English tier or heading updates to Chinese without remounting.

Run the relevant tests and then:

```powershell
npm.cmd run test -- --run src/pages/MembersPage.test.tsx src/pages/PoliciesPage.test.tsx src/pages/SharingPage.test.tsx
npm.cmd run build
```

Do not claim repository-wide tests or lint are clean unless you run them. Report unrelated baseline failures precisely.

## Delivery

Create `ops/handoffs/p3b-admin-members-policies-sharing-deepseek-completion.md` with:

1. Modified files and added i18n key groups.
2. Static English deliberately retained and why.
3. Exact test/build commands and results.
4. Any visible untranslated text remaining in allowed files and why.
5. Any unrelated test/lint failures with file and line.
