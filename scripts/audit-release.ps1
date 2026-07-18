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

& git -C $repository rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Not a Git repository: $repository"
}

$blockedPathPatterns = @(
    '(^|/)\.env$',
    '(^|/)\.venv(/|$)',
    '(^|/)node_modules(/|$)',
    '(^|/)\.pytest_cache(/|$)',
    '(^|/)test-results(/|$)',
    '(^|/)build(/|$)',
    '(^|/)dist(/|$)',
    '(^|/)omnigent\.egg-info(/|$)',
    '(^|/)omnigent/server/static/web-ui(/|$)',
    '\.(db|db-wal|db-shm|log)$',
    '(^|/)\.p[0-9].*\.(html|txt|png)$'
)
$secretPatterns = @(
    '(?i)\b(?:sk|ghp)-[A-Za-z0-9_-]{20,}\b',
    '(?i)\bgithub_pat_[A-Za-z0-9_]{20,}\b',
    '(?i)\bAKIA[0-9A-Z]{16}\b'
)
$allowlistPath = Join-Path $repository 'scripts/release-audit-allowlist.txt'
$secretAllowlist = [System.Collections.Generic.HashSet[string]]::new()
if (Test-Path -LiteralPath $allowlistPath) {
    foreach ($line in Get-Content -LiteralPath $allowlistPath) {
        if ($line -and -not $line.TrimStart().StartsWith('#')) {
            [void]$secretAllowlist.Add($line.Trim())
        }
    }
}

function Test-BlockedPath {
    param([string]$Path)
    $normalized = $Path.Replace('\', '/')
    return $blockedPathPatterns | Where-Object { $normalized -match $_ } | Select-Object -First 1
}

function Test-SecretContent {
    param([string]$Content)
    return $secretPatterns | Where-Object { $Content -match $_ } | Select-Object -First 1
}

function Test-SecretAllowlisted {
    param([string]$Path, [string]$BlobId)
    return $secretAllowlist.Contains("$Path|$BlobId")
}

function Get-CurrentPaths {
    & git -C $repository ls-files -co --exclude-standard
    if ($LASTEXITCODE -ne 0) { throw 'Unable to read Git file list.' }
}

function Get-HistoricalSecretPaths {
    param([string]$Commit)

    # Let Git search only text blobs in the commit. Reading every historical
    # file with `git show` makes a full-source release audit unnecessarily
    # slow, especially for the bundled web application and binary assets.
    $matches = @(& git -C $repository grep -I -l -E -i `
        -e '\b(sk|ghp)-[A-Za-z0-9_-]{20,}\b' `
        -e '\bgithub_pat_[A-Za-z0-9_]{20,}\b' `
        -e '\bAKIA[0-9A-Z]{16}\b' `
        $Commit --)
    if ($LASTEXITCODE -notin @(0, 1)) {
        throw "Unable to scan historical commit $Commit for secrets."
    }
    return @($matches | ForEach-Object { $_ -replace '^[^:]+:', '' })
}

$findings = [System.Collections.Generic.List[string]]::new()
$currentPaths = @(Get-CurrentPaths)

foreach ($path in $currentPaths) {
    if (Test-BlockedPath $path) {
        $findings.Add("Blocked path: $path")
        continue
    }

    $fullPath = Join-Path $repository $path
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { continue }
    if ((Get-Item -LiteralPath $fullPath).Length -gt 2MB) { continue }
    try {
        $content = [System.IO.File]::ReadAllText($fullPath)
    } catch {
        continue
    }
    if (Test-SecretContent $content) {
        $blobId = (& git -C $repository hash-object -- $fullPath).Trim()
        if (-not (Test-SecretAllowlisted $path $blobId)) {
            $findings.Add("Possible secret content: $path")
        }
    }
}

$commits = @(& git -C $repository rev-list --all)
foreach ($commit in $commits) {
    $paths = @(& git -C $repository ls-tree -r --name-only $commit)
    foreach ($path in $paths) {
        if (Test-BlockedPath $path) {
            $findings.Add("Historical blocked path: $commit $path")
        }
    }
    foreach ($path in Get-HistoricalSecretPaths $commit) {
        $content = & git -C $repository show "${commit}:$path" 2>$null | Out-String
        if (Test-SecretContent $content) {
            $blobId = (& git -C $repository rev-parse "${commit}:$path").Trim()
            if (-not (Test-SecretAllowlisted $path $blobId)) {
                $findings.Add("Historical possible secret: $commit $path")
            }
        }
    }
}

if ($findings.Count -gt 0) {
    Write-Output 'Release audit failed:'
    $findings | Sort-Object -Unique | ForEach-Object { Write-Output "- $_" }
    exit 1
}

Write-Output 'Release audit passed: no blocked paths or possible secrets found.'
