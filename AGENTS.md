# Agent guidance

Guidance for AI agents (Claude Code, Copilot, Cursor, etc.) working in this
repository. See `CONTRIBUTING.md` for the full contributor workflow.

## Committing

Run the `pre-commit` hook before committing (`pre-commit run --all-files`, or
let it run on staged files via `git commit`). Fix any issues it reports so the
commit lands clean — CI runs the same checks.

## Pull requests

When you open a pull request, fill in the repo's PR template at
`.github/pull_request_template.md` (case-sensitive on Linux — note the lowercase
filename). Keep every section and checkbox row so reviewers can skim them.

- **Summary** — what changed and why.
- **Test Plan** — how you verified it.
- **Demo** — a **video or images** showing the change. Expected on contributor
  PRs for UI / frontend changes (check the "UI / frontend change" box under
  *Type of change*) so reviewers can see the new behaviour without checking out
  the branch. Use `N/A` for non-visual changes.
- **Type of change** / **Test coverage** — check all that apply (at least one
  each).
- **Coverage notes** — required if you checked "Manual verification completed"
  or "Not applicable".

Generate the description from the actual diff and this session's context — lead
with the motivation, then the change. Don't pass a `--body` that skips these
sections.

## Task completion report (mandatory)

Every agent MUST deliver a structured report when finishing a task round.
Four dimensions, in this order:

1. **Completed tasks** — what was done this round, with evidence (test
   results, file paths, RUN_IDs). One bullet per deliverable.
2. **Handoff documents** — paths to every artifact the next agent needs
   (task cards, plans, evidence roots, diagnosis docs). Use absolute
   paths.
3. **Next-agent prompt** — a ready-to-paste prompt for the relay agent
   (Codex, Grok, or another Hermes session). Technical language, no
   fluff. Include: role, worktree, what to read first, what to do,
   constraints, success criteria, and what NOT to touch.
4. **Watch-outs** — known pitfalls, pre-existing failures, environment
   quirks, and anything that could trip up the next agent. Be specific
   (file:line, error codes, PID numbers).

Format: two-part report to the user (plain language), plus the
technical prompt block for the next agent (can be terse / jargon-heavy).

## Code comments

Keep comments short and focused on the code, not on the change history.

- **Keep them brief** — prefer one or two lines. Avoid comments longer than
  three lines; if you need more, the code likely needs refactoring or a doc
  string, not a wall of inline commentary.
- **Describe the scenario, not the PR** — explain *what* the code handles or
  *why* it exists, in terms a future reader needs. Don't reference PR numbers,
  issue numbers, or ticket IDs (e.g. `#1646`, `fixes JIRA-123`); the scenario
  should be clear without chasing external links.
