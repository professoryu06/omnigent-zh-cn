#!/usr/bin/env bash
# Read-only readiness check for Omnigent's native CLI backends in WSL/Linux.

set -u

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Run this script inside the Ubuntu WSL terminal, not PowerShell." >&2
  exit 1
fi

check_command() {
  local name="$1"
  shift
  if ! command -v "$name" >/dev/null 2>&1; then
    printf '%-10s MISSING\n' "$name"
    return
  fi

  local version
  version=$("$@" 2>&1 | head -n 1 || true)
  printf '%-10s READY   %s\n' "$name" "${version:-version command returned no text}"
}

echo "Omnigent native CLI readiness"
echo "=============================="
check_command tmux tmux -V
check_command bwrap bwrap --version
check_command omnigent omnigent --version
check_command claude claude --version
check_command kimi kimi --version
check_command hermes hermes --version
check_command qwen qwen --version

echo
echo "Authentication is intentionally not checked here because each CLI owns its credentials."
echo "Use the onboarding steps in ops/cli-integration/README.md."
