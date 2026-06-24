# WebAgentRuntimeBench Local Demo Runner
# Run all demos locally. No network, no API key, no real platforms.

param(
    [string]$Python = "python",
    [string]$Node = "node",
    [string]$OutDir = "..\sample_run"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RuntimeDir = Join-Path $ScriptDir "phase5_2_runtime"

Write-Host "=== WebAgentRuntimeBench Local Demo ===" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
try {
    & $Python --version 2>&1 | Out-Null
    Write-Host "[OK] Python available" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Python not found. Install Python 3.10+ or use -Python flag." -ForegroundColor Red
    exit 1
}

try {
    & $Node --version 2>&1 | Out-Null
    Write-Host "[OK] Node.js available" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Node.js not found. Install Node 18+ or use -Node flag." -ForegroundColor Red
    exit 1
}

# A0: Synthetic Dynamic Runtime MVP
Write-Host ""
Write-Host "--- A0: Synthetic Dynamic Runtime MVP ---" -ForegroundColor Yellow
$A0Out = Join-Path $ScriptDir $OutDir "a0"
New-Item -ItemType Directory -Force -Path $A0Out | Out-Null
Push-Location $RuntimeDir
try {
    & $Python run_synthetic_runtime_demo.py --out-dir $A0Out --node $Node
    Write-Host "[OK] A0 demo passed" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] A0 demo failed: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# A2: Bundle Variants
Write-Host ""
Write-Host "--- A2: Synthetic Bundle Variants ---" -ForegroundColor Yellow
$A2Out = Join-Path $ScriptDir $OutDir "a2"
New-Item -ItemType Directory -Force -Path $A2Out | Out-Null
Push-Location $RuntimeDir
try {
    & $Python run_bundle_variant_cases.py --out-dir $A2Out --node $Node
    Write-Host "[OK] A2 bundle variants passed" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] A2 bundle variants failed: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""
Write-Host "=== All demos passed ===" -ForegroundColor Green
Write-Host "Output: $(Join-Path $ScriptDir $OutDir)" -ForegroundColor Cyan
