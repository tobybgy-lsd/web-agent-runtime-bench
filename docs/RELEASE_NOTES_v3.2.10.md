# Agent Failure Doctor v3.2.10 - Data Engineering Closed-Loop Triage Patch

v3.2.10 is a patch release for the v3.2 Auto Collector line. It turns the
public data-quality helpers from v3.2.9 into a closed diagnosis -> plan ->
verify workflow for common crawler/RPA data pipeline failures.

## What changed

- Added data-engineering failure classification for:
  - `schema_validation_failure`
  - `duplicate_submission`
  - `checkpoint_missing`
  - `dead_letter_overflow`
  - `pagination_data_loss`
- Added safe fix-plan coverage that points users to:
  - `SchemaValidator`
  - `BloomDedupeChecker` or `DedupeChecker`
  - `CheckpointManager`
  - `RetryPolicy`
  - `DeadLetterQueue`
  - `FieldQualityReporter`
  - `RunManifest`
- Fixed the pagination/dedup precedence issue: "duplicate records on pages 4-5"
  is now treated as adjacent-page pagination drift/data loss, not a duplicate
  submission bug.
- Added regression tests for the full public-safe data engineering triage path.

## Safety

- Forbidden outputs remain at 0 in the local safety scan.
- The package remains diagnosis, repair planning, verification, and sanitized
  sharing only.
- No local challenge solvers, flags, mock challenge servers, browser stealth
  recipes, fingerprint modification steps, behavioral mimicry steps, or private
  solution details are included.
- The data-engineering plan only references local validation, dedupe,
  checkpointing, retry, DLQ, and reporting helpers.

## Known limits

- These rules diagnose local pipeline quality failures. They do not infer target
  platform access-control behavior.
- Bloom-filter dedupe can have false positives by design.
- Data-quality helpers validate and isolate records; they do not rewrite business
  logic automatically.

## Reproduce

```powershell
python -m pip install agent-failure-doctor==3.2.10
failure-doctor --help
```

PyPI: <https://pypi.org/project/agent-failure-doctor/>

From source:

```powershell
python -m unittest tests.test_data_quality_and_visual_public_pack
python -m unittest discover -s tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
python -m tools.validation.run_p98_master_gate
```
