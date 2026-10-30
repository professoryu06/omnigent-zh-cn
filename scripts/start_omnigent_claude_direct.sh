#!/usr/bin/env bash
set -euo pipefail

# Omnigent Claude direct-to-DeepSeek route. This scopes the proxy to the
# Omnigent host process and does not alter CCSwitch, Codex, or Grok settings.
export HTTPS_PROXY="http://172.31.80.1:17892"
export HTTP_PROXY="http://172.31.80.1:17892"
export ALL_PROXY="http://172.31.80.1:17892"
export NO_PROXY="127.0.0.1,localhost,172.31.80.1"
unset ANTHROPIC_AUTH_TOKEN ANTHROPIC_API_KEY

cd /mnt/f/codex-ai/omnigent-zh-next
exec .venv/bin/python -m omnigent.cli --debug --log-to-stderr host --server http://127.0.0.1:6767
