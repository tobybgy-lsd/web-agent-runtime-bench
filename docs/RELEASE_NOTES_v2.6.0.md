# Agent Failure Doctor v2.6.0

v2.6.0 adds Batch Diagnosis / Fleet Mode. It turns a folder of failed runs into a fleet-level diagnosis report with repeated failures, top root causes, repair priority, suggested regression cases, and per-run reports.

## What changed

- Package version aligned to `2.6.0`.
- Added `failure-doctor batch <runs_dir> --out <batch_report>`.
- Added fleet report generation:
  - `summary.json`
  - `summary.md`
  - `failures_by_type.csv`
  - `top_root_causes.md`
  - `repeated_failures.md`
  - `suggested_regression_cases.md`
  - `repair_priority.md`
  - `reports/`

## Safety boundary

Batch mode only diagnoses local failed-run folders. It does not run crawlers, access external platforms, bypass controls, edit source code, or apply patches.

## Verification

```powershell
python -m unittest tests.test_batch_diagnosis_fleet_mode
python -m unittest discover -s tests -p "test_*.py"
```

Expected result: batch tests pass and the full suite remains green.
