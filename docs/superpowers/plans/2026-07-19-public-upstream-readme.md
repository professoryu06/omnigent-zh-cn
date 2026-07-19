# Public Chinese Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish Omnigent Chinese distribution as a public, self-contained repository with clear upstream tracking and a user-facing README.

**Architecture:** The repository remains a full source distribution, so installation never needs a second official Omnigent package. A read-only scheduled workflow compares the upstream default-branch SHA and creates a GitHub issue when it changes; it never merges upstream automatically. The root README becomes a concise Chinese entry page linked to detailed platform documents.

**Tech Stack:** GitHub Actions, GitHub CLI, Markdown, existing Omnigent screenshots, Python release-audit tests.

## Global Constraints

- Keep Apache-2.0 `LICENSE` and `NOTICE` unchanged.
- Do not commit API keys, local state, or generated Web UI output.
- Keep `omnigent-zh` and `omni-zh` as the only distribution console commands.
- Public installation must use the full `professoryu06/omnigent-zh-cn` source repository, not a patch package.
- Upstream monitoring may create an issue but must never auto-merge upstream changes.

---

### Task 1: Add upstream watch workflow

**Files:**
- Create: `.github/workflows/upstream-watch.yml`
- Modify: `UPSTREAM.md`
- Test: `tests/test_release_workflows.py`

- [ ] Add a test that requires an `upstream-watch.yml` workflow with a schedule, `workflow_dispatch`, `issues: write`, and `omnigent-ai/omnigent` reference.
- [ ] Run the test and observe failure because the workflow is absent.
- [ ] Add a read-only workflow that fetches the upstream default-branch SHA, compares it with a repository variable, and opens or updates a labeled issue on change.
- [ ] Document manual synchronization: fetch upstream, review diff, preserve Chinese locale work, test, then tag.
- [ ] Re-run release workflow tests and commit.

### Task 2: Replace root README with public project page

**Files:**
- Modify: `README.md`
- Modify: `docs/zh-CN/AGENT_INSTALL.md`
- Test: `tests/test_distribution_metadata.py`

- [ ] Add assertions that the README identifies the project as a complete distribution, contains the public installation URL, and links to upstream documentation.
- [ ] Run the test and observe failure against the private-install wording.
- [ ] Write the Chinese README with centered project identity, product screenshot, badges, one-line Agent installation block, capability sections, supported CLI table, quick start, platform boundary table, documentation links, upstream policy, FAQ, and license.
- [ ] Replace private-repository wording in Agent installation documentation with public access wording.
- [ ] Re-run the metadata tests and build the Web UI.
- [ ] Commit the public documentation.

### Task 3: Publish and verify public access

**Files:**
- Modify: GitHub repository metadata and visibility

- [ ] Confirm the working tree, release audit, targeted tests, and existing CI status are clean.
- [ ] Change `professoryu06/omnigent-zh-cn` visibility to public and update its description.
- [ ] Push the documentation and workflow commits.
- [ ] Query GitHub repository metadata to verify `isPrivate` is false.
- [ ] Verify the public README and final Actions runs.
