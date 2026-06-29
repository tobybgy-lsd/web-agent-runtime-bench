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

## Validation metrics

```text
CLI fixture diagnosed
Repeated failures detected
Repair priority generated
Suggested regression cases generated
0 forbidden outputs
```

## Known limits

- Batch mode summarizes local run folders; it does not schedule jobs or run automation fleets.
- Per-run diagnosis quality depends on the evidence captured in each failed-run folder.

## Reproduce commands

```powershell
python -m unittest tests.test_batch_diagnosis_fleet_mode
python -m unittest discover -s tests -p "test_*.py"
```

Expected result: batch tests pass and the full suite remains green.
