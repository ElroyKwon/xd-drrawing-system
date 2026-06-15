param(
    [switch]$Apply,
    [switch]$ClaudeOnly,
    [switch]$CodexOnly
)

$ErrorActionPreference = "Stop"

$packageRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$skillsRoot = Join-Path $packageRoot "skills"

if (-not (Test-Path -LiteralPath $skillsRoot)) {
    throw "Missing skills directory: $skillsRoot"
}

$targets = @()
if ($ClaudeOnly) {
    $targets += Join-Path $env:USERPROFILE ".claude\skills"
}
elseif ($CodexOnly) {
    $targets += Join-Path $env:USERPROFILE ".agents\skills"
    $targets += Join-Path $env:USERPROFILE ".codex\skills"
}
else {
    $targets += Join-Path $env:USERPROFILE ".claude\skills"
    $targets += Join-Path $env:USERPROFILE ".agents\skills"
    $targets += Join-Path $env:USERPROFILE ".codex\skills"
}

Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'PREVIEW' })"

$skills = Get-ChildItem -LiteralPath $skillsRoot -Directory |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") }

foreach ($skill in $skills) {
    foreach ($targetRoot in $targets) {
        $target = Join-Path $targetRoot $skill.Name
        Write-Host "$($skill.FullName) -> $target"
        if ($Apply) {
            New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
            if (Test-Path -LiteralPath $target) {
                $backup = "$target.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                Move-Item -LiteralPath $target -Destination $backup
                Write-Host "Existing skill backed up to $backup"
            }
            Copy-Item -LiteralPath $skill.FullName -Destination $target -Recurse
        }
    }
}

if (-not $Apply) {
    Write-Host "Preview only. Re-run with -Apply to install."
}
