#!/usr/bin/env sh
set -eu

repository="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf '%s\n' "$1 is required. $2" >&2
    exit 1
  fi
}

require_command uv 'Install uv from https://docs.astral.sh/uv/.'
require_command node 'Install Node.js 22 LTS or newer from https://nodejs.org/.'
require_command npm 'Install Node.js 22 LTS or newer from https://nodejs.org/.'

node_major="$(node --version | sed 's/^v//' | cut -d. -f1)"
if [ "$node_major" -lt 22 ]; then
  printf '%s\n' 'Node.js 22 or newer is required.' >&2
  exit 1
fi

case "$(uname -s)" in
  Linux)
    command -v tmux >/dev/null 2>&1 || printf '%s\n' 'WARNING: tmux is required for native CLI harnesses.' >&2
    command -v bwrap >/dev/null 2>&1 || printf '%s\n' 'WARNING: bubblewrap is required for sandboxed native CLI harnesses on Linux/WSL2.' >&2
    ;;
  Darwin)
    command -v tmux >/dev/null 2>&1 || printf '%s\n' 'WARNING: tmux is required for native CLI harnesses. Install it with: brew install tmux' >&2
    ;;
  *)
    printf '%s\n' 'This installer supports Linux, WSL2, and macOS. Use install-zh.ps1 on Windows.' >&2
    exit 1
    ;;
esac

cd "$repository/web"
if [ -f package-lock.json ]; then npm ci; else npm install; fi
npm run build

uv tool install --force --python 3.12 "$repository"
printf '%s\n' 'Installed. Run: omnigent-zh platform-info'
printf '%s\n' 'Then configure providers with: omnigent-zh setup'
