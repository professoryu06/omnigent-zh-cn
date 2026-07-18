#!/usr/bin/env bash
# Handles `/merge` slash commands. Tries `gh pr merge --auto` first
# (queues until protection passes); falls back to a direct merge when
# `--auto` is rejected because the PR is already in `clean status` or
# the base moved underneath us. Always posts a reply comment.
#
# Env in: GH_TOKEN, REPO, PR, AUTHOR, GATE

set -euo pipefail

set +e
MERGE_OUT=$(gh pr merge "$PR" --repo "$REPO" --squash --auto --delete-branch 2>&1)
MERGE_RC=$?
MODE="auto-merge enabled (squash, delete branch)"

if [[ $MERGE_RC -ne 0 ]] \
   && echo "$MERGE_OUT" | grep -qE "clean status|Base branch was modified"; then
  echo "::notice::--auto rejected ($MERGE_OUT); retrying direct merge."
  MERGE_OUT=$(gh pr merge "$PR" --repo "$REPO" --squash --delete-branch 2>&1)
  MERGE_RC=$?
  MODE="merged directly (squash, delete branch)"
fi
set -e
echo "$MERGE_OUT"

if [[ $MERGE_RC -eq 0 ]]; then
  BODY=":robot: \`/merge\` from @$AUTHOR, $MODE. $GATE"
else
  # Race: an earlier auto-merge may have fired between the /merge
  # command and our attempt. Confirm friendlier.
  PR_STATE=$(gh pr view "$PR" --repo "$REPO" --json state --jq '.state' 2>/dev/null || echo "")
  if [[ "$PR_STATE" == "MERGED" ]]; then
    BODY=":white_check_mark: \`/merge\` from @$AUTHOR -- PR is already merged."
  else
    BODY=$(printf ':warning: `/merge` from @%s, could not enable auto-merge. `gh pr merge` output:\n```\n%s\n```' "$AUTHOR" "$MERGE_OUT")
  fi
fi
gh pr comment "$PR" --repo "$REPO" --body "$BODY"
