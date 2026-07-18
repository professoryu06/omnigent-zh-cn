# Native CLI Backend Status

Updated: 2026-07-18

## Configured Backends

| Backend | Native harness | Model route | Direct smoke result | Status |
| --- | --- | --- | --- | --- |
| Claude Code | `claude-native` | CC Switch on the WSL-only bridge | Response received | Ready |
| Kimi Code | `kimi-native` | `kimi-code/k3` | Response received | Ready |
| Qwen Code | `qwen-native` | Alibaba ModelStudio `qwen3.6-plus` | Response received in safe mode | Ready with startup flag |
| Hermes Agent | `hermes-native` | DeepSeek `deepseek-v4-pro` through CC Switch | Response received | Ready |

No credentials are stored in this document. Vendor keys are held only in their
user-local files with mode `0600`.

## Required Launch Variant

Use Qwen safe mode for the first Omnigent acceptance session:

```bash
omnigent qwen -- --safe-mode
```

The user-level Qwen state previously caused a `tool_fetch` availability error
outside safe mode. The same API/model succeeds in safe mode, so this is not an
Alibaba authentication failure.

## Remaining Blocker

The original direct DeepSeek credential was rejected with HTTP 401. Hermes now
uses the existing CC Switch route through the WSL-only bridge instead; its
smoke test returned a model response. The direct DeepSeek credential is no
longer used by Hermes.

## Next Acceptance Steps

1. Start a Claude native session and send a read-only `pwd` request from the web UI.
2. Repeat for Kimi K3.
3. Repeat for Qwen in safe mode.
4. Repeat for Hermes through CC Switch.
5. Confirm session reattachment after browser refresh for every backend.
6. Configure per-project working directories and approval policies.
