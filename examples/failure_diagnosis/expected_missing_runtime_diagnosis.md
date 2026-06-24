# Expected Diagnosis: Missing Runtime (localStorage)

**Failure Type**: missing_local_storage
**Confidence**: high
**Status**: needs_fix

## Summary

The trace shows that a JS bundle attempted to access `localStorage.getItem("warb_demo_salt")` but localStorage was not defined in the runtime. The classifier correctly identified the error as `missing_local_storage`.

## Expected Output

- `diagnosis.json`: status=needs_fix, failure_type=missing_local_storage, confidence=high
- `diagnosis.md`: human-readable report with evidence and fix steps
- `codex_repair_prompt.md`: actionable prompt for coding agents to fix the issue

## Fix

Enable the synthetic localStorage shim (provided by `synthetic_browser_shim.js`).
