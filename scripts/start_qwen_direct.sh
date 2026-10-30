#!/usr/bin/env bash
set -euo pipefail

# Qwen direct-to-Token-Plan route. Keep Qwen independent from Claude/CCSwitch,
# Codex/OpenCodex, and Grok. The existing ~/.qwen/.env supplies DASHSCOPE_API_KEY.
unset HTTPS_PROXY HTTP_PROXY ALL_PROXY https_proxy http_proxy
unset OPENAI_API_KEY OPENAI_BASE_URL OPENAI_MODEL
export DASHSCOPE_BASE_URL="https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"

cd /mnt/f/codex-ai/omnigent-zh-next
exec qwen "$@"
