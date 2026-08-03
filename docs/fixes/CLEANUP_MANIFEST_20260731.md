# Cleanup manifest — 2026-07-31

This manifest was captured after `PROJECT_PROGRESS_20260731.md` and before any cleanup action.

## Preserved evidence

- Evidence root: `C:\Users\Administrator\omnigent-diagnostics\`
- No child evidence root is in the deletion set.
- Ubuntu source VHDX is preserved until its backup is verified.

## Verified WSL backup

- Source: `C:\Users\Administrator\AppData\Local\wsl\{d970ed06-a30a-4c14-ae28-e59df08f1542}\ext4.vhdx`
- Backup: `C:\Users\Administrator\omnigent-diagnostics\backups\20260731-Ubuntu-24.04-ext4.vhdx`
- Source SHA-256: `8883480DD079355BCA71272CAC8BB1727E7D2B7E6AACB230D11913F7F230F30C`
- Backup SHA-256: `8883480DD079355BCA71272CAC8BB1727E7D2B7E6AACB230D11913F7F230F30C`
- The source VHDX has not been deleted or modified.

## Orphan host processes eligible for exact cleanup

These processes all target the dead local server `http://127.0.0.1:54721`; their parent processes are absent. They are the only process cleanup targets in this manifest:

- PID `24844`: `.venv\Scripts\python.exe -m omnigent.host._daemon_entry --server http://127.0.0.1:54721`
- PID `25252`: uv Python child of PID `24844`, same server target
- PID `20556`: `.venv\Scripts\python.exe -m omnigent.host._daemon_entry --server http://127.0.0.1:54721`
- PID `2272`: uv Python child of PID `20556`, same server target
- Absent parents verified: `8288`, `25820`

No process-name-wide kill is permitted.

## Completed, unused temporary run directories eligible for cleanup

All were checked as not referenced by a live non-PowerShell process:

- `C:\Users\Administrator\AppData\Local\Temp\omnigent-appserver-426-20260730-155325-dc83140-grok-appserver-426-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-d2-c-cli0146-20260730-185043-dc83140-grok-d2-c-cli0146-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-d2-c-cli0146-20260730-185106-dc83140-grok-d2-c-cli0146-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-d2-c-cli0146-20260730-185128-dc83140-grok-d2-c-cli0146-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-task18-manual-data`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-task18-manual-data3`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-d2-c-cli0146-20260730-185515-dc83140-grok-d2-c-cli0146-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-d2-c-cli0146-20260730-185707-dc83140-grok-d2-c-cli0146-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-task18-hostprobe-data`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-d2-c-cli0146-20260730-185922-dc83140-grok-d2-c-cli0146-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-d2-c-cli0146-20260730-190114-dc83140-grok-d2-c-cli0146-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-d2-c-cli0146-20260730-190428-dc83140-grok-d2-c-cli0146-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-task18-driver`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-d2-run-20260730-172454-dc83140-hermes-d2-run-cli0146-r2`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-e7d3e769f3f5`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-isolation-20260731-060535-dc83140-hermes-isolation-fullrun-cli0146-r2`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-isolation-20260731-152542-dc83140-codex-proxy-fullrun-r1`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-isolation-20260731-153045-dc83140-codex-proxy-fullrun-r2`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-isolation-20260731-153704-dc83140-codex-proxy-fullrun-r3`
- `C:\Users\Administrator\AppData\Local\Temp\omnigent-isolation-20260731-154130-dc83140-codex-proxy-fullrun-r4`

The generic `C:\Users\Administrator\AppData\Local\Temp\omnigent` directory is not in the deletion set because its ownership/purpose was not established.

## Other residue

- Untracked `F:\codex-ai\git项目部署\tmp\omnigent-review\nul` is eligible for exact deletion after this manifest is committed to the working tree.
- `C:\Users\Administrator\AppData\Local\Temp\pytest-of-Administrator` is not recursively deleted in this pass; it requires per-child age/ownership verification.

