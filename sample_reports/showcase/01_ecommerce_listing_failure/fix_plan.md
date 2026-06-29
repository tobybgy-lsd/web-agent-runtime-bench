# Fix Plan

## Root Cause

The browser runtime dependency is missing or mismatched.

## Recommended Change

- Pin the browser runtime used by the automation command.
- Add a preflight check for browser executable availability.
- Capture stdout, stderr, and environment metadata on failure.

## Verification

```powershell
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\verification
```

## Boundaries

- Do not change business listing logic.
- Do not add credentials or private platform data.
