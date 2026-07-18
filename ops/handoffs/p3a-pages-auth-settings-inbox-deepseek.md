# P3A: Settings, Inbox, and Auth Page Chinese Localization

You are the constrained implementation agent for the Omnigent Web UI Simplified Chinese localization. Complete only this work package. Do not expand its scope.

## Goal

Localize the remaining user-visible static copy in the primary settings, inbox, approval, and authentication page flows. The default `zh-CN` experience must be Chinese, while the `en` locale must preserve the existing English copy and behavior.

This package also includes `ComposerMicButton.tsx`, because its visible `aria-label` and tooltip remain English on the otherwise localized new-session page.

## Context

- Workspace: `E:\agent team\Omnigent\source-zh-cn\web`
- Dictionaries: `src/i18n/locales/en.ts`, `src/i18n/locales/zh-CN.ts`
- Default locale is `zh-CN`; legacy test setup pins English.
- Previous packages P2A-P2H cover the core shell, new sessions, chat, files, terminals, review/editor, agents, and navigation.
- Acceptance found that the live Chinese root page works, but Settings and Inbox still render English. Do not change server code, API behavior, or routes.

## Allowed Source Files

- `src/pages/SettingsPage.tsx`
- `src/pages/InboxPage.tsx`
- `src/pages/ApprovePage.tsx`
- `src/pages/LoginPage.tsx`
- `src/pages/RegisterPage.tsx`
- `src/pages/SetupPage.tsx`
- `src/pages/NotFoundPage.tsx`
- `src/components/ComposerMicButton.tsx`
- `src/i18n/locales/en.ts`
- `src/i18n/locales/zh-CN.ts`
- Existing adjacent test files for the source files above.

## Explicitly Out of Scope

Do not modify any of these in this package:

- Backend, API clients, stores, hooks, routing, persistence, WebSocket/SSE behavior, authentication behavior, permission behavior, or `data-testid` values.
- `MembersPage.tsx`, `PoliciesPage.tsx`, `SharingPage.tsx`.
- `AgentInfo.tsx`, `PermissionsModal.tsx`, chat system/status cards, PWA components, keyboard shortcuts, image lightbox, or terminal blocks.
- Any CSS/layout, request payload, validation, button enablement, loading conditions, or error handling behavior.
- Product names, CLI commands, CLI model names, paths, account/user names, emails, usernames, dynamic error text from a server, session titles, project names, `data-testid` values, and code literals.

## Required Coverage

### Settings

Translate every static user-visible label, heading, description, button, tooltip, placeholder, loading/empty/error state, confirmation dialog, and `aria-label` in `SettingsPage.tsx`.

Keep technical values such as Git branch names, paths, CLI names, model IDs, account identifiers, and data returned by the server unchanged.

### Inbox

Translate title, loading state, empty state, filters/actions, and accessible labels in `InboxPage.tsx`.

### Approval and authentication

Translate static UI in `ApprovePage.tsx`, `LoginPage.tsx`, `RegisterPage.tsx`, `SetupPage.tsx`, and `NotFoundPage.tsx`.

Do not translate user input, server-provided errors, the literal `whoami` command, routes, or identity values.

### Composer microphone

Translate the static visible/accessible `Voice dictation` copy in `ComposerMicButton.tsx` using i18n. Preserve browser API checks and all recording behavior.

## i18n Rules

1. Add matching English and Simplified Chinese entries to both dictionaries. Prefer these namespaces: `settings`, `inbox`, `approval`, `auth`, `notFound`, and `common`.
2. Use `const { t } = useTranslation()` in React components. Do not call `translate()` at module load time or save rendered strings in module-level constants.
3. Dynamic sentences must use a complete translation key with named variables. Do not concatenate Chinese fragments around variables.
4. Translate `aria-label`, `title`, `placeholder`, toast messages, dialog text, empty/loading/error states, and button text whenever they are static UI copy.
5. Do not duplicate a key if an existing key has the same semantics and wording.

## Tests

Before changing production code, add or update tests that explicitly render under `I18nProvider` with `zh-CN` and assert Chinese output.

Add at least six focused Chinese assertions across these areas:

1. Settings heading plus one setting label or dialog action.
2. Inbox title or empty state.
3. Approval loading/resolved/error/close state.
4. Login, registration, setup, or 404 page.
5. Composer microphone accessible label.
6. One runtime locale-switch test for an already mounted page/component. It must prove that switching from English to Chinese updates rendered copy without remounting.

Run the relevant adjacent test files first, then:

```powershell
npm.cmd run build
```

Do not claim a clean full-suite or lint result unless you run it. Existing repository-wide failures must be reported separately with exact file and line evidence.

## Delivery

Create `ops/handoffs/p3a-pages-auth-settings-inbox-deepseek-completion.md` containing:

1. Modified files and the added i18n key groups.
2. Static English intentionally retained and why.
3. Exact test/build commands and results.
4. Any unlocalized visible strings found in allowed files, with reasons.
5. Any unrelated lint/test failures encountered, including exact file and line.
