# WebAgentRuntimeBench Adapter Smoke Test
# Tests warb adapter CLI on synthetic local fixtures.

param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $RepoRoot
$FixtureDir = Join-Path $RepoRoot "examples\playwright_trace_cli"
$OutDir = Join-Path $RepoRoot "outputs\adapt_playwright_trace"
$TempDir = Join-Path $RepoRoot "outputs\adapt_playwright_trace_tmp"
$TraceZip = Join-Path $TempDir "trace.zip"

Write-Host "=== Adapter CLI Smoke Test ===" -ForegroundColor Cyan

try { & "$Python" --version 2>&1 | Out-Null; Write-Host "[OK] Python" -ForegroundColor Green } catch { Write-Host "[FAIL] Python" -ForegroundColor Red; exit 1 }

if (Test-Path $TempDir) { Remove-Item -Recurse -Force $TempDir }
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
if (Test-Path $OutDir) { Remove-Item -Recurse -Force $OutDir }

Compress-Archive -Path (Join-Path $FixtureDir "trace.trace"), (Join-Path $FixtureDir "page.html") -DestinationPath $TraceZip -Force

Write-Host ""
Write-Host "--- Playwright trace adapter ---" -ForegroundColor Yellow
Push-Location $RepoRoot
$result = & "$Python" tools\warb.py adapt playwright-trace $TraceZip --out $OutDir --run-id pw_cli_fixture 2>&1
$ok = ($LASTEXITCODE -eq 0 -and ($result -join "`n") -match "Initial diagnosis: selector_drift")
Pop-Location
if (-not $ok) { Write-Host "[FAIL] playwright-trace adapter" -ForegroundColor Red; exit 1 }

$Artifact = Join-Path $OutDir "failure_artifact.json"
if (-not (Test-Path $Artifact)) { Write-Host "[FAIL] failure_artifact.json missing" -ForegroundColor Red; exit 1 }

$json = Get-Content $Artifact -Raw | ConvertFrom-Json
if ($json.labels.failure_type -ne "selector_drift") { Write-Host "[FAIL] expected selector_drift" -ForegroundColor Red; exit 1 }
if ($json.error.status_code -ne 200) { Write-Host "[FAIL] expected status_code=200" -ForegroundColor Red; exit 1 }
if ($json.safety.external_network_required -ne $false) { Write-Host "[FAIL] expected local-only artifact" -ForegroundColor Red; exit 1 }

Write-Host "[OK] playwright-trace adapter PASS" -ForegroundColor Green
Write-Host ""
Write-Host "=== ADAPTER SMOKE TEST: PASS ===" -ForegroundColor Green
