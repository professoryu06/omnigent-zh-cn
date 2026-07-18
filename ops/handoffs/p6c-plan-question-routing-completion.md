# P6C: Plan Mode Review, AskUserQuestionForm, CostRoutingControl i18n -- Completion Report

**Completed:** 2026-07-17

## Summary

All 15 hardcoded English strings across 3 source files have been replaced with `t("key")` calls, new i18n entries have been added to both locale files, zh-CN tests have been created/expanded, and all tests pass with no type errors attributable to these changes.

## Files Modified

### Source files
1. `web/src/components/blocks/ExitPlanModeReview.tsx`
2. `web/src/components/blocks/AskUserQuestionForm.tsx`
3. `web/src/components/CostRoutingControl.tsx`

### Locale files (new keys added)
4. `web/src/i18n/locales/en.ts`
5. `web/src/i18n/locales/zh-CN.ts`

### Test files
6. `web/src/components/blocks/ExitPlanModeReview.test.tsx` (NEW)
7. `web/src/components/blocks/AskUserQuestionForm.test.tsx` (NEW)
8. `web/src/components/CostRoutingControl.test.tsx` (updated with zh-CN describe block)

## String Inventory

### ExitPlanModeReview.tsx

| Line | Original | Key | English | Chinese |
|------|----------|-----|---------|---------|
| 61 | `"What should change about the plan? (optional)"` | `exitPlanMode.feedbackPlaceholder` | What should change about the plan? (optional) | 对计划有什么修改意见？（可选） |
| 69 | `"Reject plan"` | `exitPlanMode.rejectPlan` | Reject plan | 拒绝计划 |
| 72 | `"Cancel"` | `common.cancel` (reuse) | Cancel | 取消 |
| 80 | `"Yes, and use auto mode"` | `exitPlanMode.yesAutoMode` | Yes, and use auto mode | 是的，并使用自动模式 |
| 84 | `"Yes, manually approve edits"` | `exitPlanMode.yesManualApprove` | Yes, manually approve edits | 是的，手动批准编辑 |
| 88 | `"Reject with feedback"` | `exitPlanMode.rejectWithFeedback` | Reject with feedback | 拒绝并反馈 |

### AskUserQuestionForm.tsx

| Line | Original | Key | English | Chinese |
|------|----------|-----|---------|---------|
| 225 | `Question {n} of {total}:` | `askUserQuestion.questionProgress` | Question {{current}} of {{total}}: | 第 {{current}} 题，共 {{total}} 题： |
| 322 | `"Type something"` | `askUserQuestion.typeSomething` | Type something | 输入内容 |
| 353 | `"Prev"` | `askUserQuestion.prev` | Prev | 上一题 |
| 362 | `"Next"` | `askUserQuestion.next` | Next | 下一题 |
| 374 | `"Submit"` | `askUserQuestion.submit` | Submit | 提交 |
| 379 | `"Cancel"` | `common.cancel` (reuse) | Cancel | 取消 |

### CostRoutingControl.tsx

| Line | Original | Key | English | Chinese |
|------|----------|-----|---------|---------|
| 195 | `"Intelligent model router"` (aria-label) | `costRouting.intelligentModelRouter` | Intelligent model router | 智能模型路由器 |
| 225 | `"Intelligent model router"` (tooltip title) | `costRouting.intelligentModelRouterTitle` | Intelligent model router | 智能模型路由器 |
| 229 | `"Picked"` / `"Would pick"` | `costRouting.picked` / `costRouting.wouldPick` | Picked / Would pick | 已选择 / 将会选择 |

## Test Coverage

### ExitPlanModeReview.test.tsx (NEW)
- **renders all three plan-review action buttons in Chinese**: Asserts "是的，并使用自动模式", "是的，手动批准编辑", "拒绝并反馈" buttons are in the document in zh-CN locale.
- **shows reject form buttons in Chinese after clicking 'reject with feedback'**: Clicks "拒绝并反馈", then asserts "拒绝计划" button, "取消" button, and placeholder text "对计划有什么修改意见？（可选）" are visible.

### AskUserQuestionForm.test.tsx (NEW)
- **renders progress text in Chinese**: Asserts `"第 1 题，共 1 题："` for single-question form.
- **renders progress text for multi-question carousel in Chinese**: Asserts `"第 1 题，共 2 题："` then `"第 2 题，共 2 题："` after navigating.
- **renders navigation and action buttons in Chinese**: Asserts "上一题", "下一题", "取消", "提交" buttons.
- **renders the custom input placeholder in Chinese**: Asserts placeholder text "输入内容".

### CostRoutingControl.test.tsx (updated)
- **renders the aria-label in Chinese**: Asserts `aria-label="智能模型路由器"`.
- **renders the tooltip title in Chinese**: Asserts tooltip text "智能模型路由器".
- **renders '已选择 haiku · cheap' in Chinese when verdict is applied**: Full-line equality check.
- **renders '将会选择 haiku · cheap' in Chinese when verdict is advisory**: Full-line equality check.

All tests call `setLocale("zh-CN")` before render and restore `setLocale("en")` in afterEach.

## Build / Type-check

```
npx tsc -b
```

No type errors attributable to these changes. The only pre-existing error is:
- `src/shell/ExecutionLogsPanel.test.tsx(225,1): error TS1005: '}' expected.` (unrelated)

## Test Results

```
Test Files  3 passed (3)
     Tests  52 passed (52)
```

All 52 tests across the 3 test files pass, including 41 pre-existing CostRoutingControl tests that still pass with the i18n wrapper (the test setup pins default locale to "en" via `__pinDefaultLocale`).
