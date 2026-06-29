# Codex Execution Report: v2.6.0 Batch Diagnosis / Fleet Mode

## Scope

Implemented `failure-doctor batch <runs_dir> --out <batch_report>` to summarize multiple local failed runs into a fleet-level report.

## Added

- `failure_doctor.batch`
- `failure-doctor batch`
- `tests/test_batch_diagnosis_fleet_mode.py`
- `docs/RELEASE_NOTES_v2.6.0.md`

## Outputs

```text
batch_report/
|-- summary.json
|-- summary.md
|-- failures_by_type.csv
|-- top_root_causes.md
|-- repeated_failures.md
|-- suggested_regression_cases.md
|-- repair_priority.md
`-- reports/
```

## Safety

Batch mode only diagnoses local, user-provided failed-run folders. It does not access external platforms, edit source files, apply patches, open pull requests, or provide bypass-oriented guidance.

## Verification

```powershell
python -m unittest tests.test_batch_diagnosis_fleet_mode
```

Result: 2 tests passed.
