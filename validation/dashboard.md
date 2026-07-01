# Validation Dashboard

Agent Failure Doctor keeps validation lanes separate. Stable release, completed P95 gates, and the P98 master gate measure controlled project maturity. Ecosystem maturity is excluded.

## 1. Current Stable Release

Agent Failure Doctor v3.2.7 is the current controlled-maturity stable line.

| Release | Status | Notes |
|---|---|---|
| v3.2.7 Canvas Fingerprint Evidence Patch | pass | Current package stable line with sanitized Canvas fingerprint evidence, no rendering-hook recipes, and no bypass guidance. |
| v3.1.0 P98 Master Gate | previous stable | Previous P98 master gate completion line. |
| v2.4.1 P95 Alignment & Missing Tracks | previous P95 stable | Published GitHub Release and previous P95 stable line. |

## 2. P95 Completed Gates

| Track | Samples / Cases | Key Metric | Forbidden Output | Status | Reproduce |
|---|---:|---|---:|---|---|
| Playwright Trace P95 | 100 | 100/100 reasonable, 100/100 exact subtype, 100/100 actionable | 0 | pass | `python -m tools.validation.run_playwright_trace_p95_validation` |
| Cross-framework P95 | 100 | 100/100 reasonable, 100/100 actionable, 100/100 valid fix plans | 0 | pass | `python -m tools.validation.run_cross_framework_p95_validation` |
| Training Challenge P95 | 40 | 40/40 reasonable, 40/40 fix plan, 40/40 verification, 0 private leaks | 0 | pass | `python -m tools.validation.run_training_challenge_validation` |
| Composite P95 Strict | 160 | 160/160 primary, repair order, and evidence graph checks | 0 | pass | `python -m tools.validation.run_composite_diagnosis_p95_strict_validation` |
| P95 Core Triad Gate | 5 pillars | `overall_status=pass` | 0 | pass | `python -m tools.validation.run_p95_core_triage_gate` |

## 3. P98 Master Gate

| Pillar | Cases | Key Metric | Forbidden Output | Status | Reproduce |
|---|---:|---|---:|---|---|
| Knowledge Base P98 | 210 | 210 public-safe local synthetic patterns, schema valid | 0 | pass | `python -m tools.knowledge_base.validate_patterns` |
| Crawler Matrix P98 | 312 | 26 categories, 312 mapped local synthetic cases | 0 | pass | `python -m tools.validation.run_crawler_failure_coverage_matrix` |
| Playwright Trace P98 | 220 | 218/220 reasonable, 212/220 exact subtype, 219/220 actionable | 0 | pass | `python -m tools.validation.run_playwright_trace_p98_validation` |
| Cross-framework P98 | 240 | 238/240 reasonable, 240/240 actionable, 237/240 fix plans | 0 | pass | `python -m tools.validation.run_cross_framework_p98_validation` |
| Training Challenge P98 | 200 | 178 diagnosis reasonable threshold met, 0 private solution leaks | 0 | pass | `python -m tools.validation.run_training_challenge_p98_validation` |
| Composite + Counterfactual P98 | 280 | 276/280 primary correct, 69/70 counterfactual pairs correct | 0 | pass | `python -m tools.validation.run_composite_counterfactual_p98_validation` |
| AI Handoff P98 | 100 | 100/100 task packs, 92 patch proposals, proposal-only | 0 | pass | `python -m tools.validation.run_ai_handoff_p98_validation` |
| Batch / Fleet P98 | 30 batch sets | 30/30 processed, 200-run batch covered | 0 | pass | `python -m tools.validation.run_batch_diagnosis_p98_validation` |
| Sanitize / Share P98 | 120 | 100% secrets redacted, 0 raw secrets in output | 0 | pass | `python -m tools.validation.run_sanitize_share_p98_validation` |
| Auto Collector / One-Click P98 | 95 | 95/95 collected, 95/95 preset detected, 0 raw secrets in sanitized output | 0 | pass | `python -m tools.validation.run_auto_collector_validation` |
| Safety Boundary P98 | all pillars | global forbidden output 0, private leaks 0, real platform access 0 | 0 | pass | `powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1` |
| P98 Master Gate | 12 pillars | `overall_status=pass`, controlled maturity score 98 | 0 | pass | `python -m tools.validation.run_p98_master_gate` |

## 4. Limits

- P98 does not include ecosystem maturity: stars, forks, external PRs, external issues, PyPI downloads, or community adoption.
- P98 does not represent unknown business-logic omniscience.
- P98 does not represent bypass or evasion capability.
- P98 does not mean the tool automatically repairs every source-code failure.
- Anti-bot risk remains detection, compliant routing, and safe next action only.

## Machine-Readable Gates

- P95 gate: `validation/p95_core_triage_gate.json`
- P98 gate: `validation/p98_master_gate.json`
- P98 results: `docs/P98_CONTROLLED_MATURITY_RESULTS.md`
- P98 limits: `docs/P98_LIMITS.md`

## Completed Historical Validation Tracks

These tracks remain part of the public validation record. They are not the P98 master gate, but they still document earlier gates and can be reproduced independently.

| Track | Key Metric | Forbidden Output | Reproduce |
|---|---|---:|---|
| Template fixtures | 97.3% reasonable classification | 0 | `python -m tools.validation.run_template_fixture_validation` |
| Public-inspired independent set | 78.0% reasonable classification | 0 | `python -m tools.validation.run_public_failure_validation` |
| Real Playwright trace semantic fixtures | 90.0% semantic adapter coverage | 0 | `python -m tools.validation.run_real_trace_validation` |
| External held-out public-source set | held-out public-source results tracked separately | 0 | `python scripts/validate_external_heldout.py` |
| Website-change / anti-bot routing | safe routing without evasion guidance | 0 | `python -m tools.validation.run_v0_6_validation` |
| External public reference validation | 62 traceable public reference seeds | 0 | `python -m tools.validation.run_external_reference_validation` |
| Resolution validation | diagnosis to plan to verify lifecycle | 0 | `python -m tools.validation.run_resolution_validation` |
| Applied scenario validation | applied scenario reports and fix plans | 0 | `python -m tools.validation.run_applied_scenario_validation` |
| Cross-framework adapter validation | Selenium, Puppeteer, Cypress, Scrapy, requests/httpx adapters | 0 | `python -m tools.validation.run_cross_framework_p95_validation` |
| Spiderbuf-inspired validation | local-only inspired training pack, no real target access | 0 | `python -m tools.validation.run_spiderbuf_inspired_validation` |
| Training challenge P95 validation | P95 training challenge sedimentation | 0 | `python -m tools.validation.run_training_challenge_validation` |
| Playwright Trace Doctor P95 validation | native trace P95 validation | 0 | `python -m tools.validation.run_playwright_trace_p95_validation` |
| Composite Diagnosis P95 Strict | strict composite diagnosis gate | 0 | `python -m tools.validation.run_composite_diagnosis_p95_strict_validation` |
| v1.3 Validation Hardening Gate | no single averaged accuracy score; tiered validation tracks; `validation/v1_3_validation_hardening.json` | 0 | `python -m tools.validation.run_validation_hardening` |

## Source Ledger

`validation/source_ledger_real_failures.json` separates real public sources from sanitized validation records.
`validation/external_public_reference_ledger.json` adds 62 external public reference seeds from official docs, public issues, and Q&A sources. These are not external user submissions to this repository.
External held-out public-source set results are tracked separately from template and synthetic validation records.
`validation/external_heldout_10.json` and `validation/external_heldout_20.json` store held-out validation outputs.
