# Validation Dashboard

Agent Failure Doctor keeps validation lanes separate. Stable tracks, completed P95 gates, and P98 development tracks measure different levels of evidence, so there is no single averaged accuracy score.

## A. Stable Core Tracks

| Track | Samples / Cases | Key Metric | Forbidden Output | Status | Reproduce Command | Notes |
|---|---:|---|---:|---|---|---|
| Template fixtures | 150 | 97.3% reasonable, 94.7% actionable | 0 | pass | `python -m unittest tests.test_sanitized_failure_pack_templates` | Sanitized template coverage with 4 severe misclassifications and 21 insufficient-evidence cases tracked separately. |
| Public-inspired independent set | 50 | 78.0% reasonable, 90.0% actionable | 0 | pass | `python -m tools.validation.run_validation_hardening` | Public-inspired sanitized records, not raw public traces. |
| Real Playwright trace semantic fixtures | 30 | 30/30 reasonable, 30/30 exact subtype | 0 | pass | `python -m tools.validation.run_real_trace_validation` | Native local `trace.zip` fixtures without synthetic classifier-only fields. |
| Website-change / anti-bot routing | 50 | 50/50 reasonable, 50/50 safe next actions | 0 | pass | `python scripts/validate_website_antibot.py` | Anti-bot risk is detection, routing, and compliant next action only. |
| External public reference validation | 20 | 20/20 reasonable, 20/20 actionable | 0 | pass | `python -m tools.validation.run_external_public_reference_validation` | Traceable public reference records selected from the external source ledger. |
| External held-out public-source set | 10 | 9/10 reasonable, 10/10 actionable | 0 | pass | `python scripts/validate_external_heldout.py` | Held-out short records; remaining miss is kept visible instead of hidden. |
| Resolution validation | 12 | 12/12 verification statuses correct | 0 | pass | `python -m tools.validation.run_resolution_validation` | Before/after local fixtures for resolved, unresolved, partial, and changed-failure outcomes. |
| Applied scenario validation | 18 | 18/18 diagnosis, fix plan, and verification checks | 0 | pass | `python -m tools.validation.run_applied_scenario_validation` | Local-only applied automation scenarios; not real platform workflows. |
| Integration adapters | 4 adapters | Collector/packer/browser-agent adapters smoke-tested | 0 | pass | `python -m unittest tests.test_playwright_collector tests.test_generic_log_pack_adapter tests.test_browser_use_adapter` | Workflow entrypoint adapters produce diagnosable local failure packs. |
| Cross-framework adapter validation | 42 | 42/42 reasonable, 42/42 actionable, 42/42 fix plans | 0 | pass | `python -m tools.validation.run_cross_framework_validation` | Selenium, Puppeteer, Cypress, Scrapy, requests, httpx, browser-use, and generic RPA logs. |
| Spiderbuf-inspired validation | 10 | 10/10 reasonable, 10/10 fix plan, 10/10 verification | 0 | pass | `python -m tools.validation.run_spiderbuf_inspired_validation` | Local-only public-training-inspired mock failures; no real spiderbuf.cn access or private solution logic. |

## B. P95 Completed Gates

| Track | Samples / Cases | Key Metric | Forbidden Output | Status | Reproduce Command | Notes |
|---|---:|---|---:|---|---|---|
| Playwright Trace Doctor P95 validation | 100 | 100/100 reasonable, 100/100 exact subtype, 100/100 actionable | 0 | pass | `python -m tools.validation.run_playwright_trace_p95_validation` | Deepest native backend remains Playwright trace semantics. |
| Cross-framework P95 validation | 100 | 100/100 reasonable, 100/100 actionable, 100/100 valid fix plans | 0 | pass | `python -m tools.validation.run_cross_framework_p95_validation` | Broad adapter coverage through normalized logs/failure packs. |
| Training challenge P95 validation | 40 | 40/40 reasonable, 40/40 fix plan, 40/40 verification, 0 private leaks | 0 | pass | `python -m tools.validation.run_training_challenge_validation` | Training challenge sedimentation without publishing private solutions. |
| Composite Diagnosis P95 Strict | 160 | 160/160 primary, repair order, and evidence graph checks | 0 | pass | `python -m tools.validation.run_composite_diagnosis_p95_strict_validation` | Primary/secondary/blocking/downstream/evidence-graph validation. |
| P95 Core Triad Gate | 5 pillars | `overall_status=pass` | 0 | pass | `python -m tools.validation.run_p95_core_triage_gate` | Machine-readable P95 summary gate. |
| AI Handoff & Patch Proposal | 20 | 20/20 Codex tasks, 20/20 Claude Code tasks, 20/20 Cursor tasks, 18/20 patch proposals | 0 | pass | `python -m tools.validation.run_ai_handoff_validation` | Proposal-only AI coding assistant handoff; does not edit source files. |
| Batch Diagnosis / Fleet Mode | CLI fixture | repeated failures detected, regression suggestions, repair priority generated | 0 | pass | `python -m unittest tests.test_batch_diagnosis_fleet_mode` | Fleet summary for local folders of failed runs. |

## C. P98 Development Tracks

| Track | Samples / Cases | Key Metric | Forbidden Output | Status | Reproduce Command | Notes |
|---|---:|---|---:|---|---|---|
| P98 Controlled Maturity Skeleton | scorecard + KB + matrix | 140 knowledge patterns, 20 crawler categories, 200 mapped crawler cases | 0 | in_progress | `python -m unittest tests.test_p98_scorecard tests.test_knowledge_base_patterns tests.test_crawler_failure_coverage_matrix` | Development track only; not the final P98 master gate. |
| Failure Knowledge Base | 140 patterns | schema-valid, searchable, anti-bot safety declared | 0 | in_progress | `python -m tools.knowledge_base.validate_patterns` | Local-only diagnostic knowledge; no bypass or credential guidance. |
| Crawler Failure Coverage Matrix | 20 categories / 200 mapped cases | matrix generated and documented | 0 | in_progress | `python -m tools.validation.run_crawler_failure_coverage_matrix` | Coverage taxonomy, not a crawler execution system. |
| Future P98 Master Gate | pending | `overall_status=in_progress` | 0 | in_progress | `type validation\p98_master_gate.json` | Placeholder gate until the P98 completion pack produces final pass metrics. |

## Machine-Readable Gates

- v1.3 Validation Hardening Gate: `validation/v1_3_validation_hardening.json` keeps evidence tiers separate and does not publish a single averaged score.
- P95 gate: `validation/p95_core_triage_gate.json` currently has `overall_status=pass`.
- P98 gate: `validation/p98_master_gate.json` currently has `overall_status=in_progress`.

## Source Ledger

`validation/source_ledger_real_failures.json` separates real public sources from sanitized validation records.
`validation/external_public_reference_ledger.json` adds 62 external public reference seeds from official docs, public issues, and Q&A sources. These are not external user submissions to this repository.
`validation/external_heldout_10.json` and `validation/external_heldout_20.json` store the current held-out validation outputs.

| Source Type | Count | Meaning |
|---|---:|---|
| `real_public_issue` | 50 | Public GitHub issue URLs used as traceable symptoms and category evidence |
| `official_doc_pattern` | 10 | Official documentation URLs used as behavior boundaries |
| `public_inspired_sanitized` | 71 | Sanitized regression records inspired by public patterns, not claimed as raw public issues |
| Total | 131 | Mixed source ledger for evidence tracking |

## Release Notes

Prepared release-note drafts:

- `docs/RELEASE_NOTES_v2.4.1.md`
- `docs/RELEASE_NOTES_v2.5.0.md`
- `docs/RELEASE_NOTES_v2.6.0.md`
- `docs/RELEASE_NOTES_v3.0.0.md`
- `docs/RELEASE_NOTES_v3.0.1.md`

Manual publication steps are tracked in `docs/GITHUB_RELEASE_TODO.md`.
