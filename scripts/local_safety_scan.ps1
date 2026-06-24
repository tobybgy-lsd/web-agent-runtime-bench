# Local Safety Scanner for WebAgentRuntimeBench
# Scans the showcase directory for sensitive patterns.
# PS 5.1 compatible — uses Get-ChildItem instead of -Recurse on Select-String.

param(
    [string]$TargetDir = "."
)

$ErrorActionPreference = "Continue"
$Pass = $true
$TargetDir = Resolve-Path $TargetDir

Write-Host "=== WebAgentRuntimeBench Local Safety Scan ===" -ForegroundColor Cyan
Write-Host "Target: $TargetDir"
Write-Host ""

function Test-Pattern($Pattern, $Label, [string[]]$Paths) {
    Write-Host "--- Check: $Label ---" -ForegroundColor Yellow
    $found = @()
    foreach ($path in $Paths) {
        $fullPath = Join-Path $TargetDir $path
        if (Test-Path $fullPath) {
            $matches = Get-ChildItem -Path $fullPath -Recurse -File -ErrorAction SilentlyContinue |
                       Select-String -Pattern $Pattern -ErrorAction SilentlyContinue
            $found += $matches
        }
    }
    if ($found.Count -gt 0) {
        Write-Host "[FAIL] Found pattern '$Pattern':" -ForegroundColor Red
        $found | ForEach-Object { Write-Host "  $($_.Path):$($_.LineNumber)" -ForegroundColor Red }
        $script:Pass = $false
    } else {
        Write-Host "[OK] No matches" -ForegroundColor Green
    }
}

# 1. API Key leak
Test-Pattern -Pattern "sk-" -Label "API Key (sk-)" -Paths @(".")

# 2. Real platform sensitive words in code
Test-Pattern -Pattern "x-s-common|x-s[^-]|x-t[^-]" -Label "Signature fields (x-s/x-t)" -Paths @("demo", "scripts")
Test-Pattern -Pattern "real_signature|bypass_captcha|evade_antibot|real_platform_api" -Label "Real platform phrases" -Paths @("demo", "scripts")

# 3. Network patterns in code
Test-Pattern -Pattern "http://|https://|fetch\(|axios|XMLHttpRequest|WebSocket" -Label "Network patterns" -Paths @("demo", "scripts")

# 4. Credential patterns in code
Test-Pattern -Pattern "Cookie|Authorization|Bearer " -Label "Credential patterns" -Paths @("demo", "scripts")

Write-Host ""
if ($Pass) {
    Write-Host "=== SAFETY SCAN: PASS ===" -ForegroundColor Green
} else {
    Write-Host "=== SAFETY SCAN: FAIL ===" -ForegroundColor Red
}
exit $(if ($Pass) { 0 } else { 1 })
