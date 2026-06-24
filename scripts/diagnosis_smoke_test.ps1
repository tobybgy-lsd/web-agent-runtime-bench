# WebAgentRuntimeBench Diagnosis Smoke Test
# Tests the Failure Diagnosis CLI on synthetic failure examples.

param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $RepoRoot
$DiagTool = Join-Path $RepoRoot "tools\diagnostics\diagnose_failure.py"
$ExDir = Join-Path $RepoRoot "examples\failure_diagnosis"

Write-Host "=== Diagnosis CLI Smoke Test ===" -ForegroundColor Cyan

# Check Python
try { & "$Python" --version 2>&1 | Out-Null; Write-Host "[OK] Python" -ForegroundColor Green } catch { Write-Host "[FAIL] Python" -ForegroundColor Red; exit 1 }

# Test 1: Missing runtime diagnosis
Write-Host ""
Write-Host "--- Missing Runtime Diagnosis ---" -ForegroundColor Yellow
$OutMR = Join-Path $RepoRoot "outputs\diagnosis_missing_runtime"
$rs = Join-Path $ExDir "missing_runtime_run_summary.json"
$tr = Join-Path $ExDir "missing_runtime_trace.jsonl"
$result = & "$Python" $DiagTool --run-summary $rs --trace $tr --out-dir $OutMR 2>&1; $ok1 = ($LASTEXITCODE -eq 0 -and ($result -join "`n") -match "failure_type.*missing_local_storage")
if (-not $ok1) { Write-Host "[FAIL] Missing runtime diagnosis" -ForegroundColor Red; exit 1 }
Write-Host "[OK] failure_type=missing_local_storage" -ForegroundColor Green

# Test 2: Signed API diagnosis
Write-Host ""
Write-Host "--- Signed API Failure Diagnosis ---" -ForegroundColor Yellow
$OutSA = Join-Path $RepoRoot "outputs\diagnosis_signed_api"
$rs2 = Join-Path $ExDir "signed_api_failure_run_summary.json"
$tr2 = Join-Path $ExDir "signed_api_failure_trace.jsonl"
$result = & "$Python" $DiagTool --run-summary $rs2 --trace $tr2 --out-dir $OutSA 2>&1; $ok2 = ($LASTEXITCODE -eq 0 -and ($result -join "`n") -match "failure_type.*negative_case_not_rejected")
if (-not $ok2) { Write-Host "[FAIL] Signed API diagnosis" -ForegroundColor Red; exit 1 }
Write-Host "[OK] failure_type=negative_case_not_rejected" -ForegroundColor Green

# Check output files
Write-Host ""
Write-Host "--- Checking Output Files ---" -ForegroundColor Yellow
$files = @(
    "$OutMR\diagnosis.json","$OutMR\diagnosis.md","$OutMR\codex_repair_prompt.md",
    "$OutSA\diagnosis.json","$OutSA\diagnosis.md","$OutSA\codex_repair_prompt.md"
)
$allOk = $true
foreach ($f in $files) {
    if (Test-Path $f) { Write-Host "  [OK] $f" -ForegroundColor Green } else { Write-Host "  [FAIL] $f missing" -ForegroundColor Red; $allOk = $false }
}
if (-not $allOk) { exit 1 }

Write-Host ""
Write-Host "=== DIAGNOSIS SMOKE TEST: PASS ===" -ForegroundColor Green
