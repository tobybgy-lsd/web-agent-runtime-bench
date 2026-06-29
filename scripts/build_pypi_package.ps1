param(
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

Write-Host "=== Agent Failure Doctor PyPI Build Check ==="

python -m pip install --upgrade build twine

if (Test-Path dist) {
    Remove-Item -Recurse -Force dist
}
if (Test-Path build) {
    Remove-Item -Recurse -Force build
}

python -m build
python -m twine check dist/*

if (-not $SkipTests) {
    python -m unittest discover -s tests -p "test_*.py"
    powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
}

Write-Host "=== PyPI Build Check: PASS ==="
