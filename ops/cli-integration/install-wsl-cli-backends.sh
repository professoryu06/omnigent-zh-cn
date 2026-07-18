#!/usr/bin/env bash
# Install Omnigent's first four native CLI backends in WSL/Linux.
# This script intentionally never reads, copies, or writes provider credentials.

set -euo pipefail

selected=("${@:-claude kimi hermes qwen}")

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Run this script inside the Ubuntu WSL terminal, not PowerShell." >&2
  exit 1
fi

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

ensure_node() {
  if ! command -v node >/dev/null 2>&1; then
    echo "Node.js 22+ is required for $1. Install Node.js first, then rerun this script." >&2
    exit 1
  fi
}

ensure_login_path() {
  local directory="$1"
  local marker="# omnigent-native-cli-path: ${directory}"
  local profile="$HOME/.profile"

  if grep -Fqs "$marker" "$profile"; then
    return
  fi

  cat >>"$profile" <<EOF

$marker
if [ -d "$directory" ]; then
    PATH="$directory:\$PATH"
fi
EOF
}

install_claude() {
  ensure_node "Claude Code"
  npm install -g @anthropic-ai/claude-code@latest
}

install_kimi() {
  require_command curl
  curl -fsSL https://code.kimi.com/kimi-code/install.sh | KIMI_NO_MODIFY_PATH=1 bash
  ensure_login_path "$HOME/.kimi-code/bin"
}

install_hermes() {
  require_command uv
  uv tool install --force --python 3.12 "hermes-agent[cli]"
}

install_qwen() {
  ensure_node "Qwen Code"
  npm install -g @qwen-code/qwen-code@latest
  ensure_login_path "$(npm prefix -g)/bin"
}

for backend in "${selected[@]}"; do
  case "$backend" in
    claude) install_claude ;;
    kimi) install_kimi ;;
    hermes) install_hermes ;;
    qwen) install_qwen ;;
    *)
      echo "Unknown backend: $backend. Supported: claude kimi hermes qwen" >&2
      exit 2
      ;;
  esac
done

echo
echo "Installation step finished. Open a new WSL shell, then run:"
echo "  bash ops/cli-integration/verify-wsl-cli-backends.sh"
