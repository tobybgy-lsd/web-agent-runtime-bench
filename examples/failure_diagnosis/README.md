# Failure Diagnosis Examples

Synthetic/local failure trace samples for testing the Failure Diagnosis CLI.

## Files

| File | Description |
|------|-------------|
| `missing_runtime_trace.jsonl` | Simulates a missing_local_storage runtime failure |
| `missing_runtime_run_summary.json` | Corresponding run summary with overall_status=FAIL |
| `signed_api_failure_trace.jsonl` | Simulates a negative case not rejected |
| `signed_api_failure_run_summary.json` | Corresponding run summary with negative_rejected < negative_cases |
| `expected_missing_runtime_diagnosis.md` | Expected diagnosis for missing_runtime case |
| `expected_signed_api_diagnosis.md` | Expected diagnosis for signed_api case |

## Usage

```powershell
python tools\diagnostics\diagnose_failure.py --input-dir examples\failure_diagnosis --out-dir outputs\diagnosis_missing_runtime
python tools\diagnostics\diagnose_failure.py --run-summary examples\failure_diagnosis\signed_api_failure_run_summary.json --trace examples\failure_diagnosis\signed_api_failure_trace.jsonl --out-dir outputs\diagnosis_signed_api
```

All data is synthetic/local mock. No real platforms.
