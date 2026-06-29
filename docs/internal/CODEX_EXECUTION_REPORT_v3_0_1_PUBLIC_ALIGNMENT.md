# Codex Execution Report: v3.0.1 Public Alignment & P98 Track Separation

Date: 2026-06-29

## Scope

This pass did not add new diagnosis capability. It aligned the public repository entry points around the current v3 line and separated stable, P95, and P98 validation tracks so the project does not imply a final P98 master-gate pass.

## Version Strategy

Adopted strategy: v3.0 is the current public line, with v3.0.1 as the alignment patch.

- `pyproject.toml`: `3.0.1`
- README current milestone: `Agent Failure Doctor v3.0.1 Public Alignment & P98 Track Separation Pack`
- P98 development track: in progress, not a final passed master gate

## Public Entry Alignment

- README top section now presents Agent Failure Doctor as a local-first failure diagnosis, repair planning, and fix verification tool.
- README and README.zh-CN both identify v3.0.1 as the current milestone.
- README keeps the quick-start command near the top and links to validation and safety boundary documents.
- Changelog now includes v3.0.1.

## Release Notes

Release-note coverage is present for:

- `docs/RELEASE_NOTES_v2.4.1.md`
- `docs/RELEASE_NOTES_v2.5.0.md`
- `docs/RELEASE_NOTES_v2.6.0.md`
- `docs/RELEASE_NOTES_v3.0.0.md`
- `docs/RELEASE_NOTES_v3.0.1.md`

`docs/GITHUB_RELEASE_TODO.md` records the publication checklist. Historical GitHub releases were not created automatically because tags and release boundaries should be confirmed before publishing them.

## Validation Dashboard

`validation/dashboard.md` is now split into:

- Stable Core Tracks
- P95 Completed Gates
- P98 Development Tracks

`validation/p98_master_gate.json` was added with `overall_status: in_progress` and `final_p98_gate: false`.

## Verification

Commands run locally:

```powershell
python -m unittest tests.test_version_alignment tests.test_dashboard_sections tests.test_release_notes_presence tests.test_p98_track_not_fake_pass tests.test_release_alignment_pack tests.test_batch_diagnosis_fleet_mode tests.test_release_trust_pack tests.test_public_release_cleanup tests.test_validation_hardening_v1_3
python -m unittest discover -s tests -p "test_*.py"
python -m tools.validation.run_p95_core_triage_gate
python -m tools.knowledge_base.validate_patterns
python -m tools.validation.run_crawler_failure_coverage_matrix
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

Results:

- Targeted alignment tests: 33 passed
- Full unittest suite: 319 passed
- P95 core triage gate: pass
- Knowledge-base validation: 140 patterns, forbidden output count 0
- Crawler failure coverage matrix: 20 categories, 200 mapped cases, forbidden output count 0
- Smoke test: pass
- Local safety scan: pass

## Remaining Boundaries

- P98 is a development track and is not represented as a final master-gate pass.
- Real external releases should be created only from confirmed tags and intended release commits.
- No new diagnosis subtype, crawler bypass behavior, CAPTCHA bypass, signature cracking, fingerprint spoofing, or bot-evasion logic was added in this pass.
