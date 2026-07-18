#!/usr/bin/env bash
# Enables GitHub auto-merge when the `automerge` label is added.
# Queues until branch protection (the Merge Ready status) goes green;
# GitHub fires the merge automatically once it does, so a single call
# is sufficient.
#
# Env in: GH_TOKEN, REPO, PR

set -euo pipefail

set +e
MERGE_OUT=$(gh pr merge "$PR" --repo "$REPO" --squash --auto --delete-branch 2>&1)
MERGE_RC=$?
set -e
echo "$MERGE_OUT"

if [[ $MERGE_RC -eq 0 ]]; then
  echo "::notice::Auto-merge enabled via 'automerge' label."
else
  echo "::warning::Could not enable auto-merge via 'automerge' label: $MERGE_OUT"
fi
