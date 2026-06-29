param(
    [string]$Project = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Project)) {
    $Project = (Get-Location).Path
}

$resolvedProject = (Resolve-Path -LiteralPath $Project).Path
$outDir = Join-Path $resolvedProject "failure_doctor_auto_report"

Write-Host "Agent Failure Doctor will collect local evidence only from:"
Write-Host "  $resolvedProject"
Write-Host ""
Write-Host "It will not scan the whole computer, browser profiles, credential stores, dependency folders, or Git internals."
$answer = Read-Host "Continue? Type YES"
if ($answer -ne "YES") {
    Write-Host "Cancelled."
    exit 2
}

$command = Get-Command failure-doctor -ErrorAction SilentlyContinue
if (-not $command) {
    Write-Host "failure-doctor command was not found."
    Write-Host "Run: python -m pip install -e ."
    exit 1
}

& failure-doctor collect --project "$resolvedProject" --preset auto --out "$outDir" --auto-diagnose --auto-handoff --auto-sanitize --open-report
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Start-Process -FilePath (Join-Path $outDir "open_this_first.md")
$diagnosis = Join-Path $outDir "report\diagnosis.md"
if (Test-Path -LiteralPath $diagnosis) {
    Start-Process -FilePath $diagnosis
}
