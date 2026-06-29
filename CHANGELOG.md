# Changelog

## v2.4.1

- Aligned package, README, dashboard, release notes, and machine-readable validation status around the P95 gate.
- Added Playwright Trace Doctor P95 validation ledger with 100 local native-trace/semantic fixture records and 0 forbidden outputs.
- Added Cross-Framework P95 validation ledger with 100 local sanitized framework log fixtures across Selenium, Puppeteer, Cypress, Scrapy, requests, httpx, browser-use, and generic RPA.
- Added Training Challenge P95 validation ledger with 40 local-only challenge-inspired fixtures, 0 forbidden outputs, and 0 private solution leaks.
- Added `validation/p95_core_triage_gate.json` and `tools.validation.run_p95_core_triage_gate` as the machine-readable P95 summary gate.
- Added three composite showcase sample reports under `sample_reports/composite_showcase/`.

## v2.4.0

- Added Composite Diagnosis P95 Strict Gate Pack.
- Added candidate-based diagnosis, evidence node extraction, evidence graph generation, causal policy, and composite diagnosis output while preserving legacy `failure_type`, `technical_category`, `subtype`, and `confidence` fields.
- Added composite schema files: `schemas/composite_diagnosis.schema.json`, `schemas/evidence_graph.schema.json`, and `schemas/composite_validation_result.schema.json`.
- Added strict local-only composite validation fixtures and `tools.validation.run_composite_diagnosis_p95_strict_validation`.
- Validation result: 160/160 primary classifications, 160/160 repair-order checks, 160/160 evidence graphs, 0 forbidden outputs.
- `failure-doctor diagnose` now writes primary, secondary, blocking, downstream, evidence graph, and repair order fields to `diagnosis.json`.
- `failure-doctor plan` preserves composite repair order, and `failure-doctor verify` can report `partially_resolved` when the primary failure is fixed but a known secondary failure remains.
- No external AI calls, no uploads, no bypass guidance, and no private challenge solutions were added.

## v2.3.0

- Added Spiderbuf-Inspired Challenge Validation Pack.
- Added `examples/spiderbuf_inspired_challenges/` with 10 local-only mock failure packs inspired by public crawler-training challenge categories.
- Added `tools.validation.run_spiderbuf_inspired_validation`.
- Added `validation/spiderbuf_inspired_validation.json`.
- Validation result: 10/10 reasonable classifications, 10/10 valid fix plans, 10/10 correct verification statuses, 0 forbidden outputs.
- Public artifacts are diagnosis-only and do not include private solutions, access-control defeat steps, or real-site collection logic.

## v2.2.0

- Added Cross-Framework Adapter Pack.
- Added `failure-doctor adapt <input> --framework <framework> --out <failure_pack>`.
- Supports `selenium`, `puppeteer`, `cypress`, `scrapy`, `requests`, `httpx`, and `auto`.
- Added `integrations.cross_framework` with local-only log normalization, redaction status, framework metadata, and standard failure pack output.
- Added `schemas/framework_failure_pack.schema.json`.
- Added 42 sanitized cross-framework fixtures and `tools.validation.run_cross_framework_validation`.
- Validation result: 42/42 reasonable classifications, 42/42 actionable next actions, 42/42 valid fix plans, 0 forbidden outputs.
- Playwright remains the native trace backend; cross-framework adapters do not run external frameworks or access external platforms.

## v2.1.1

- Release Alignment & Showcase Pack.
- Updated README and README.zh-CN to present v2.1 as the current stable milestone.
- Added project positioning, FAQ, and v2.1.0 release notes.
- Added sanitized showcase sample reports for ecommerce listing, real trace login redirect, and sanitize/share pack flows.
- Clarified the failure lifecycle: diagnose, plan, verify, run, and sanitize.
- No new diagnosis categories or framework adapters were added in this patch.

## v2.1.0

- Added Sanitize & Share Pack.
- Added `failure-doctor sanitize <failed_run> --out <shareable_failure_pack>`.
- Generates `sanitized_error.log`, `sanitized_network.json`, `sanitized_trace_metadata.json`, `redaction_report.json`, `safe_to_share.json`, `README_FOR_REVIEWER.md`, and `shareable_failure_pack.zip`.
- Redacts common authorization headers, cookies, bearer tokens, API keys, emails, phone numbers, ID numbers, order ids, customer names, and internal/private URLs.
- Raw `trace.zip` archives are not copied into the shareable pack; only metadata is exported.
- `safe_to_share=false` remains the default until a human reviews the pack.

## v2.0.0

- Added Auto Capture Pack.
- Added `failure-doctor run -- <command>` to execute a local command and capture stdout, stderr, exit code, environment, detected artifacts, and input summary.
- Failed wrapped commands automatically generate `diagnosis/`, `fix_plan/`, `verification_hint.md`, and `shareable_failure_pack.zip`.
- Added basic local redaction for bearer tokens, API keys, and common token/password query forms.
- Shareable packs default to `safe_to_share=false` and require manual review before external submission.
- No real-platform access, no automatic code modification, no CAPTCHA bypass, no bot evasion, no credential extraction.

## v1.3.0

- Added Validation Hardening Pack.
- Added `tools.validation.run_validation_hardening`.
- Added `validation/v1_3_validation_hardening.json` as a multi-track validation gate.
- Kept validation lanes separate by evidence tier instead of averaging synthetic, public-inspired, native-trace, resolution, applied-scenario, and integration results into one score.
- Added regression backlog extraction with `safe_to_publish=false` by default.
- Safety boundary remains unchanged: no access-control circumvention, no CAPTCHA bypass, no bot evasion, no fingerprint spoofing, no signature cracking, no account/IP pool guidance.

## v1.2.0

- Added Integration Pack:
  - `failure-doctor collect-playwright`
  - `failure-doctor pack-logs`
  - Playwright test-results collector
  - generic log folder packer
  - browser-use / browser-agent log adapter
  - GitHub Actions usage documentation
- Added local mock integration fixtures:
  - `examples/mock_playwright_test_results`
  - `examples/mock_raw_logs`
- Added integration safety tests.
- No real-platform access and no anti-bot bypass guidance.

## v1.1.0

- Added Applied Scenario Demo Pack.
- Added six local-only business automation failure demo families:
  - hot product collection
  - live commerce monitoring
  - ecommerce listing automation
  - authorized content publishing workflow
  - GUI / RPA data bridge
  - ERP-to-ecommerce sync
- Added 18 before/after applied scenario cases.
- Added `tools.validation.run_applied_scenario_validation`.
- Added applied scenario validation dashboard output:
  - 18/18 reasonable classifications
  - 18/18 valid fix plans
  - 18/18 correct verification statuses
  - 0 forbidden outputs
- Added resume/interview notes for positioning the project as a failure diagnosis and repair verification layer.
- No real-platform scraping, no automated posting to real platforms, no anti-bot bypass.

## v1.0.0

- Added Failure Resolution Loop:
  - `failure-doctor plan`
  - `failure-doctor verify`
  - fix plan generation
  - before/after resolution verification
  - regression case generation
- Added `fix_plan/v1` and `verification_report/v1` schemas.
- Added 12 local resolution validation cases.
- Resolution validation:
  - 12/12 correct verification statuses
  - 12/12 actionable next steps
  - 0 forbidden outputs
- Anti-bot risk remains identification and compliant routing only.

## v0.8.0

- Added a 131-record source ledger:
  - 50 `real_public_issue`
  - 10 `official_doc_pattern`
  - 71 `public_inspired_sanitized`
- Added 30 native Playwright-generated `trace.zip` fixtures.
- Added real trace semantic validation runner.
- Added native-trace validation coverage for storage/context, route/HAR, shadow DOM, website-change, environment, and anti-bot risk routing.
- Real trace validation:
  - 30/30 reasonable classification
  - 30/30 exact subtype match
  - 0 forbidden outputs
- Added external held-out validation:
  - 10 public-source held-out records
  - 9/10 reasonable classification
  - 10/10 actionable next action
  - 0 forbidden outputs
- GitHub Actions:
  - Ubuntu / macOS / Windows unit tests
  - Windows benchmark / smoke / safety

## v0.6.0

- Added Website Change diagnosis layer.
- Added Anti-Bot Risk identification and compliant routing layer.
- Added 50 public-inspired sanitized Website Change / Anti-Bot Risk corpus records.
- Added independent v0.6 routing validation ledger: 50/50 reasonable classifications, 50/50 safe next actions, 0 forbidden outputs.
- Added `failure_layer` and `safe_next_action` fields to Agent Failure Doctor output.
- Added safety tests to ensure anti-bot risk prompts do not provide bypass guidance.

## v0.4.0

- 150 public-inspired / sanitized validation records with traceable public URLs
- 97.3% reasonable classification
- 94.7% actionable next_action
- 170 tests
- local-first diagnosis
- safety scan
- no CAPTCHA bypass / no bot evasion boundary

## v0.3.0

- Real User Input Pack
- Actionable Report
- Codex fix prompt
- input_summary.json
- missing_evidence
- evidence_priority
