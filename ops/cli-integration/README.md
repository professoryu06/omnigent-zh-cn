# Omnigent WSL Native CLI Integration

## Scope

This integration uses Omnigent's built-in native harnesses. No custom bridge is
needed:

| CLI | Omnigent harness | Launch command |
| --- | --- | --- |
| Claude Code | `claude-native` | `omnigent claude` |
| Kimi Code | `kimi-native` | `omnigent kimi` |
| Hermes Agent | `hermes-native` | `omnigent hermes` |
| Qwen Code | `qwen-native` | `omnigent qwen` |

Each harness owns a resident CLI process in a tmux terminal and mirrors its
conversation into the Omnigent web UI. Credentials stay owned by the vendor
CLI; Omnigent does not receive or store provider API keys for these four native
integrations.

## Current Blocker

The WSL runner is currently unable to create any VM and returns
`Wsl/Service/CreateInstance/CreateVm/HCS/0x800705aa`, including for
`wsl --system`. This is below Omnigent and below individual CLIs. Do not install
or configure the backends from Windows PowerShell: Omnigent's native terminal
bridge requires Linux tmux.

After restarting Windows, verify the runner first:

```powershell
wsl --shutdown
wsl -d Ubuntu-24.04 -- bash -lc "echo WSL_READY; tmux -V; bwrap --version; omnigent --version"
```

Continue only after this prints `WSL_READY`.

## Installation

From the WSL shell, go to the cloned source tree and run the installer:

```bash
cd "/mnt/e/agent team/Omnigent/source-zh-cn"
bash ops/cli-integration/install-wsl-cli-backends.sh
exec bash
bash ops/cli-integration/verify-wsl-cli-backends.sh
```

The installer fetches only the vendors' official installers/packages and does
not touch credentials. Review its source before running it if needed.

## Authentication and Model Setup

Complete one backend at a time. Never copy Windows credential files into WSL.

1. **Claude Code**: configure its WSL-local authentication or the same
   CC Switch-compatible provider route used by the WSL process, then run
   `claude` and send a read-only prompt. Do not assume Windows CC Switch settings
   automatically flow into WSL; verify from the WSL process.
2. **Kimi Code**: run `kimi login`. Kimi writes its own configuration under
   `~/.kimi`; it also supports provider configuration inside Kimi.
3. **Hermes Agent**: run `hermes model`, select the desired provider and model,
   then use a read-only prompt. Hermes stores secrets in `~/.hermes/.env` and
   non-secret settings in `~/.hermes/config.yaml`.
4. **Qwen Code**: run `qwen`, then `/auth`. Qwen no longer has a `qwen login`
   command. Use a Model Studio API key or Coding Plan, or configure a supported
   OpenAI-compatible provider.

### CC Switch bridge used on this machine

CC Switch listens on Windows loopback (`127.0.0.1:15721`), which is not the
same loopback interface seen by WSL. The WSL Claude configuration therefore
uses `http://172.31.80.1:15721`, with a Windows `netsh interface portproxy`
rule forwarding that address back to `127.0.0.1:15721`. The rule binds only to
the WSL virtual adapter, not to the LAN. If CC Switch changes its listening
port, update both the portproxy rule and the WSL-local `ANTHROPIC_BASE_URL`.

## Acceptance Sequence

Run this sequence for each backend, in order: Claude, Kimi, Hermes, Qwen.

1. CLI version and authentication/model selection works directly in the WSL
   terminal.
2. Start it through `omnigent <backend>` in a test workspace.
3. In the Omnigent web UI, send `Only run pwd and return its output. Do not edit files.`
4. Confirm the response is mirrored to the web UI, the command executes in the
   expected workspace, and the tmux session can reconnect after a browser refresh.
5. Only then enable file writes and tool approvals for that backend.

## Implementation Boundary

The first version keeps approvals inside each vendor's TUI where Omnigent's
native adapter cannot safely intercept them. Omnigent may mirror or deny some
events, but no backend is granted unattended write/delete/network permissions
until the above read-only acceptance is complete.
