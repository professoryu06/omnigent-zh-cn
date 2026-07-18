[CmdletBinding()]
param(
    [Parameter()]
    [string]$RepositoryPath
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryPath)) {
    $RepositoryPath = Split-Path -Parent $PSScriptRoot
}
$repository = (Resolve-Path -LiteralPath $RepositoryPath).Path

function Require-Command {
    param([string]$Name, [string]$Hint)
    if ($null -eq (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is required. $Hint"
    }
}

Require-Command 'uv' 'Install uv from https://docs.astral.sh/uv/.'
Require-Command 'node' 'Install Node.js 22 LTS or newer from https://nodejs.org/.'
Require-Command 'npm' 'Install Node.js 22 LTS or newer from https://nodejs.org/.'

$nodeVersion = ((& node --version).Trim()).TrimStart('v').Split('.')[0]
if ([int]$nodeVersion -lt 22) {
    throw 'Node.js 22 or newer is required.'
}

if ($env:OS -eq 'Windows_NT') {
    Write-Host 'Windows native mode supports the server, web UI, and SDK harnesses.'
    Write-Host 'For Claude/Kimi/Qwen/Hermes native tmux workflows, run this installer inside WSL2.'
} elseif ($null -eq (Get-Command 'tmux' -ErrorAction SilentlyContinue)) {
    Write-Warning 'tmux is missing. Native CLI harnesses require tmux.'
}

Push-Location (Join-Path $repository 'web')
try {
    if (Test-Path 'package-lock.json') { & npm ci } else { & npm install }
    if ($LASTEXITCODE -ne 0) { throw 'Web dependency installation failed.' }
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Web UI build failed.' }
} finally {
    Pop-Location
}

& uv tool install --force --python 3.12 $repository
if ($LASTEXITCODE -ne 0) { throw 'omnigent-zh-cn installation failed.' }

Write-Host 'Installed. Run: omnigent-zh platform-info'
Write-Host 'Then configure providers with: omnigent-zh setup'
