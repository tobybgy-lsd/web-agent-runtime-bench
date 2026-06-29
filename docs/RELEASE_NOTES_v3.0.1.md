# Agent Failure Doctor v3.0.1

v3.0.1 is a P98 development-track record, not the current packaged stable release. It does not add new diagnosis categories; it documents the P98 track separation work while the package stable line remains v2.4.1.

## What changed

- Package stable line remains `2.4.1`.
- README and README.zh-CN present v2.4.1 as the current stable milestone and v3.0.x as the P98 development track.
- Validation dashboard is split into:
  - Stable Core Tracks
  - P95 Completed Gates
  - P98 Development Tracks
- Added `validation/p98_master_gate.json` with `overall_status=in_progress`.
- Added tests that prevent README, pyproject, dashboard, release notes, and P98 gate status from drifting apart.

## Validation metrics

```text
P95 core triad gate: pass
Real Playwright trace semantic fixtures: 30/30 reasonable, 30/30 exact, 0 forbidden outputs
External public reference validation: 20/20 reasonable, 20/20 actionable, 0 forbidden outputs
External held-out public-source set: 9/10 reasonable, 10/10 actionable, 0 forbidden outputs
P98 development track: 140 knowledge patterns, 20 crawler categories, 200 mapped cases, 0 forbidden outputs
```

## Safety boundary

This release remains local-first and diagnostic-only. It does not provide CAPTCHA bypass, bot evasion, fingerprint spoofing, protected-signature cracking, credential extraction, private challenge solution logic, or real-platform collection workflows.

## Known limits

- `validation/p98_master_gate.json` is intentionally `in_progress`; it is not a final P98 pass.
- GitHub Releases should publish v2.4.1 as the latest stable release first.
- v3.0.1 should not be published as the latest stable release while `validation/p98_master_gate.json` remains `in_progress`.
- P98 completion requires a later master gate with larger case counts and counterfactual coverage.

## Reproduce commands

```powershell
python -m unittest discover -s tests -p "test_*.py"
python -m tools.validation.run_p95_core_triage_gate
python -m tools.knowledge_base.validate_patterns
python -m tools.validation.run_crawler_failure_coverage_matrix
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```
