# Codex Execution Report: v2.4.2 / v3.0.1 Public Consistency Patch

Date: 2026-06-29

## Scope

This pass fixes public consistency only. It does not add new diagnosis categories, new crawler behavior, or new bypass-oriented logic.

## Public Version Strategy

Adopted strategy:

- Current packaged stable line: `v2.4.1`
- P98 development track: `v3.0.x`
- `validation/p98_master_gate.json`: `overall_status=in_progress`
- `v3.0.1` is a development-track record and is not the current packaged stable release.

## Changes

- `pyproject.toml` now reports package version `2.4.1`.
- README and README.zh-CN now present `Agent Failure Doctor v2.4.1 P95 Alignment & Missing Tracks Pack` as the current stable milestone.
- README now presents `v3.0.x P98 Controlled Maturity Pack` as a development track.
- CHANGELOG now explains that v3.0.x entries document the in-progress P98 development track and are not the current packaged stable release.
- `validation/p98_master_gate.json` now includes:
  - `ecosystem_score_excluded: true`
  - `current_stable_line: v2.4.1`
  - `p98_track_status: development`
- `docs/GITHUB_RELEASE_TODO.md` now points release publication at `v2.4.1` as latest stable and keeps `v3.0.1` out of releases until the P98 master gate is final.
- Tests were updated to lock the stable/dev split.

## Verification

Commands run locally:

```powershell
python -m unittest tests.test_version_alignment tests.test_p98_track_not_fake_pass tests.test_release_notes_presence tests.test_release_alignment_pack tests.test_release_trust_pack tests.test_public_release_cleanup tests.test_batch_diagnosis_fleet_mode
python -m unittest discover -s tests -p "test_*.py"
python -m tools.validation.run_p95_core_triage_gate
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

Results:

- Targeted public-consistency tests: 28 passed
- Full unittest suite: 319 passed
- P95 core triage gate: pass
- Smoke test: pass
- Local safety scan: pass

## Release Publication

`v2.4.1` should be published as the latest stable GitHub Release with `docs/RELEASE_NOTES_v2.4.1.md`.

`v3.0.1` should not be published as a stable GitHub Release while `validation/p98_master_gate.json` remains `in_progress`.

## Safety Boundary

This pass keeps the project local-first and diagnostic-only. It does not provide CAPTCHA bypass, bot evasion, fingerprint spoofing, protected-signature cracking, credential extraction, private challenge solution logic, or real-platform collection workflows.
