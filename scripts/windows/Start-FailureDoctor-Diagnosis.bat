@echo off
setlocal

if "%~1"=="" (
  set "PROJECT_DIR=%CD%"
) else (
  set "PROJECT_DIR=%~1"
)

set "OUT_DIR=%PROJECT_DIR%\failure_doctor_auto_report"

where failure-doctor >nul 2>nul
if errorlevel 1 (
  echo failure-doctor command was not found.
  echo Run: python -m pip install -e .
  exit /b 1
)

failure-doctor collect --project "%PROJECT_DIR%" --preset auto --out "%OUT_DIR%" --auto-diagnose --auto-handoff --auto-sanitize --open-report
if errorlevel 1 exit /b %errorlevel%

start "" "%OUT_DIR%\open_this_first.md"
if exist "%OUT_DIR%\report\diagnosis.md" start "" "%OUT_DIR%\report\diagnosis.md"
exit /b 0
