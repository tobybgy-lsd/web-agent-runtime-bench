# Agent Failure Doctor v4.3.0 - Real User Case Program & Public Benchmark Pack

v4.3.0 adds the first stable public-case and benchmark layer on top of the
v4.2 Plugin SDK baseline.

## Install

```powershell
python -m pip install agent-failure-doctor==4.3.0
failure-doctor --help
```

## What changed

- Added `failure-doctor case intake/anonymize/validate/publish-check/export-public`.
- Added `failure-doctor issue-pack create/validate`.
- Added `failure-doctor benchmark run/compare/validate-suite`.
- Added public case manifest validation, local anonymization, publish checks,
  sanitized issue packs, public-safe benchmark reports, and regression compare.
- Added P98 pillars: `real_user_case_program` and `public_benchmark_pack`.

## Reproduce

```powershell
python -m tools.validation.run_real_user_case_program_validation
python -m tools.validation.run_public_benchmark_pack_validation
python -m tools.validation.run_p98_master_gate
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
python -m unittest discover -s tests -p "test_*.py" -b
```

## Safety

- Local-only by default.
- No external API calls by default.
- No telemetry.
- Public benchmark cases must be sanitized and diagnosis-only.
- Private local training artifacts remain outside the public package.
- Forbidden output count is required to stay at 0 across the v4.3 validation
  gates.

## Known limits

- Public benchmark suites are local synthetic and public-safe; they are not a
  claim of external ecosystem adoption.
- Case intake does not upload evidence or submit GitHub issues automatically.
- Issue packs are sanitized attachments for humans to review before sharing.
- Benchmark compare reports regressions; it does not automatically change user
  code or apply patches.
