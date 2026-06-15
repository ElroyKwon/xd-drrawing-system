$ErrorActionPreference = "Stop"

$packageRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$skillsRoot = Join-Path $packageRoot "skills"

$required = @(
    "project-bootstrap",
    "feature-docs-scaffold",
    "planning-gate",
    "development-loop-orchestrator",
    "validator-loop",
    "evidence-report",
    "tag-alarm-review"
)

$rows = foreach ($name in $required) {
    $skillDir = Join-Path $skillsRoot $name
    $skillFile = Join-Path $skillDir "SKILL.md"
    $evalFile = Join-Path $skillDir "evals\evals.json"
    [PSCustomObject]@{
        Skill = $name
        SkillFile = Test-Path -LiteralPath $skillFile
        Evals = Test-Path -LiteralPath $evalFile
    }
}

$rows | Format-Table -AutoSize | Out-String -Width 220

$bad = @($rows | Where-Object { -not $_.SkillFile -or -not $_.Evals })
if ($bad.Count -gt 0) {
    Write-Warning "Package verification failed."
    exit 1
}

Write-Host "Package verification passed."
