# Batch Diagnosis

Batch diagnosis analyzes folders of failed runs and reports repeated failures, root-cause groups, repair priority, suggested regression cases, and fleet health.

The P98 validation runner is:

```powershell
python -m tools.validation.run_batch_diagnosis_p98_validation
```

The runner writes `validation/batch_diagnosis_p98_validation.json`.
