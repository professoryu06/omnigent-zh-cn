#!/usr/bin/env bash
set -euo pipefail

project_dir="/mnt/f/codex-ai/omnigent-zh-next"
server_url="http://127.0.0.1:6767"

cd "$project_dir"

echo "[Omnigent] Ensuring the Chinese WSL server is running..."
uv run omnigent-zh server --background --no-open

host_status_json="$(uv run omnigent-zh host status --server "$server_url" --json 2>/dev/null || true)"
if printf '%s' "$host_status_json" | grep -Eq '"host_status"[[:space:]]*:[[:space:]]*"(online|connected)"'; then
  echo "[Omnigent] Host is already online; no duplicate host is started."
elif tmux has-session -t omnigent 2>/dev/null; then
  echo "[Omnigent] Existing tmux session 'omnigent' found; host is not duplicated."
elif tmux has-session -t omnigent-host 2>/dev/null; then
  echo "[Omnigent] Existing tmux session 'omnigent-host' found; host is not duplicated."
else
  echo "[Omnigent] Starting host in tmux session 'omnigent-host'..."
  tmux new-session -d -s omnigent-host \
    "cd '$project_dir' && exec uv run omnigent-zh host --server '$server_url'"
fi

echo "[Omnigent] Current server status:"
uv run omnigent-zh server status
echo
echo "[Omnigent] Web UI: $server_url"
echo "[Omnigent] This window can stay open; close it only when you want to stop viewing logs."
