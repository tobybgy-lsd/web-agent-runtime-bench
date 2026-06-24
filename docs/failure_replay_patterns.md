# Failure Replay Patterns

Failure replay turns raw errors into reproducible debugging workflows. All patterns are for **benchmark and debugging analysis**. Not for bypassing real websites.

## Why Failure Replay Matters

A stack trace tells you "what broke." A failure replay tells you:
- **What was the input** (compact observation, API payload)
- **What was expected** (classifier output, verification result)
- **What was the deviation** (wrong dependency, missing shim, signature mismatch)
- **How to reproduce** (re-run the case)
- **How to fix** (repair strategy)

## Replay Workflows

### 1. Runtime Failure Replay (A2)

```
Trace file: sample_run/a2/bundle_variant_trace.jsonl

Example steps:
  {"step": "case_signed", "case_name": "missing_navigator", "expected": "missing_navigator", "actual": "missing_navigator"}
  {"step": "dependencies_traced", ...}
  {"step": "mock_api_verified", "accepted": true}

Replay report: sample_run/a2/failure_replay.md
  → Table of 5 failures with error type, root cause, repair
```

### 2. Signed API Verification Replay (A3)

```
Trace file: sample_run/a3/signed_api_trace.jsonl

Steps per case:
  case_signed → dependencies_traced → mock_api_verified → negative_case_rejected

If mock_api_verified = false:
  → Check 1: Does signature computation match WARBDemoV2 on both Python and JS sides?
  → Check 2: Are dependency keys aligned (e.g., "salt_source" not "salt")?
  → Check 3: Is stable_json producing identical output in both languages?
```

### 3. Negative Case Not Rejected

```
Trace: negative_case_rejected step shows "rejected: false"

Debug:
  → The tampered payload hash matched the original? Check stable_json canonicalization.
  → The signature was computed from original payload not tampered? Check verification pipeline.
  → The verification function only checks path prefix? Ensure full signature verification.
```

## How to Read trace.jsonl

```powershell
# Find all failure steps
Select-String -Path sample_run\a3\signed_api_trace.jsonl -Pattern '"accepted": false'

# Filter by case
Select-String -Path sample_run\a3\signed_api_trace.jsonl -Pattern "user_agent_salt"
```

## Safety

- All traces are from synthetic/local benchmark runs
- No real platform data
- Replay is for debugging, not for production monitoring of real websites
