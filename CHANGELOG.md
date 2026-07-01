# Changelog

> Current package stable line: v3.2.10.
> v3.1.0 remains the previous P98 stable release, and v2.4.1 remains the previous P95 stable release. Ecosystem maturity is tracked separately from P98 controlled maturity.

## v3.2.10

- Added data-engineering closed-loop triage for `schema_validation_failure`, `duplicate_submission`, `checkpoint_missing`, `dead_letter_overflow`, and `pagination_data_loss`.
- Added safe fix-plan coverage for `SchemaValidator`, `BloomDedupeChecker`, `CheckpointManager`, `RetryPolicy`, `DeadLetterQueue`, `FieldQualityReporter`, and `RunManifest`.
- Fixed pagination-vs-dedup precedence so adjacent-page duplicate records are classified as pagination boundary/data-loss evidence instead of duplicate submission.
- Kept the package diagnosis and repair-planning only: no private training solvers, flags, challenge defeat code, or access-control circumvention guidance.

## v3.2.9

- Added public-safe data engineering stability helpers for schema validation, deduplication, checkpointing, retry bookkeeping, dead-letter queues, run manifests, source hashes, field-quality reports, structured JSONL logging, and Bloom-filter dedupe.
- Added `failure-doctor visual-diagnose` for local screenshot/DOM/OCR/click-coordinate visual failure diagnosis.
- Added optional local-first VLM visual analyzer helpers with mock mode by default and no automatic network calls.
- Added precise public-safe subtypes for `audio_fingerprint_risk`, `tcp_ip_os_fingerprint_mismatch`, and `ast_dynamic_token_required`.
- Added `docs/VISUAL_DATA_QUALITY_BOUNDARY.md` to keep local challenge solvers, flags, anti-bot bypass instructions, and private training scripts out of the public package.
- Kept the package diagnosis-only: no solver code, no challenge defeat, no fingerprint spoofing instructions, no behavioral mimicry recipes, and no private solution leaks.

## v3.2.8

- Added public-safe deep runtime evidence subtypes for sanitized WebGL/WebRTC runtime evidence, browser global-scope leakage, runtime sandbox leakage, native reflection mismatch, and debugger timing anomalies.
- Added public-safe protocol and client-VM evidence subtypes for HTTP/2 SETTINGS mismatch, JA4/H2 mismatch, client VM integrity failures, and numeric-semantics mismatch.
- Added public-safe behavioral telemetry subtypes for pointer trajectory entropy anomalies and mathematical trajectory evidence.
- Extended offline `browser_runtime_report.json`, `probe_report.json`, `js_integrity_report.json`, and `input_timing_summary.json` handling for these sanitized evidence summaries.
- Added `docs/DEEP_RUNTIME_PROTOCOL_BEHAVIOR_BOUNDARY.md` to keep local challenge solvers, flags, browser runtime alteration recipes, protocol impersonation values, VMP reconstruction logic, and behavioral mimicry steps out of the public package.
- Kept the package diagnosis-only: no runtime alteration recipes, no protocol impersonation guidance, no behavioral bypass steps, no anti-bot evasion logic, and no private solution leaks.

## v3.2.7

- Added public-safe Canvas fingerprint evidence subtypes: `canvas_fingerprint_collision` and `browser_canvas_fingerprint_risk`.
- Extended `browser_runtime_report.json` handling so sanitized Canvas hash/session-count evidence can be supplied as offline runtime evidence.
- Added safe next-action guidance for Canvas hash/session-count evidence, browser/runtime metadata, HTTP rejection evidence, authorized APIs/SDKs/test hooks, and stopping automation when authorization is unclear.
- Added `docs/CANVAS_FINGERPRINT_BOUNDARY.md` to keep local Canvas challenge solvers, rendering-hook details, flags, and fingerprint-alteration techniques out of the public package.
- Kept the package diagnosis-only: no Canvas manipulation recipes, no fingerprint spoofing, no anti-bot evasion logic, and no private solution leaks.

## v3.2.6

- Added `js_integrity_report.json` as a recognized offline evidence input for sanitized JavaScript/request-integrity summaries.
- Added public-safe JavaScript integrity subtypes: `obfuscated_js_integrity_required`, `js_ast_obfuscation_detected`, `rotated_string_array_detected`, `client_generated_token_missing`, and `request_integrity_algorithm_changed`.
- Added safe next-action guidance for sanitized JS bundle metadata, function-name summaries, request-parameter diffs, HTTP rejection evidence, authorized APIs/SDKs/test hooks, and stopping automation when authorization is unclear.
- Added `docs/JS_INTEGRITY_BOUNDARY.md` to keep local AST recovery, signature formulas, constants, flags, and solver code out of the public package.
- Kept the package diagnosis-only: no deobfuscation recipes, no signature reconstruction, no anti-bot evasion logic, and no private solution leaks.

## v3.2.5

- Added `browser_runtime_report.json` and `input_timing_summary.json` as recognized offline evidence inputs.
- Added public-safe behavioral and Client Hints subtypes: `client_hints_platform_mismatch`, `browser_header_consistency_risk`, `keystroke_telemetry_anomaly`, `zero_interval_input_detected`, and `behavioral_input_risk`.
- Added safe next-action guidance for browser header/runtime consistency evidence, sanitized input-timing summaries, authorized APIs/SDKs/test hooks, compliant export paths, and stopping automation when authorization is unclear.
- Added `docs/BEHAVIORAL_CLIENT_HINTS_BOUNDARY.md` to keep local challenge solvers, timing mimicry, flags, and browser-stealth implementation details out of the public package.
- Kept the package diagnosis-only: no default active probes, no browser automation probes, no anti-bot evasion logic, and no private solution leaks.

## v3.2.4

- Added `probe_report.json` as a recognized offline evidence input for user-supplied active-probe summaries.
- Mapped sanitized TLS/ALPN/HTTP-version probe evidence into `tls_alpn_fingerprint_mismatch` and `transport_fingerprint_risk` without adding default network probing.
- Added `docs/ACTIVE_PROBE_BOUNDARY.md` to keep active probes opt-in, external, and diagnosis-only.
- Fixed the README language-switch link and documented `probe_report.json` in the accepted input list.
- Kept private local probe tools, flags, transport impersonation details, and solver code out of the public package and Git tracking boundary.

## v3.2.3

- Added public-safe transport-layer diagnostics for `tls_alpn_fingerprint_mismatch` and `transport_fingerprint_risk`.
- Added safe next-action guidance for TLS/ALPN/HTTP-version evidence collection, official API / SDK / compliant export checks, and stopping automation when authorization is unclear.
- Expanded the Spiderbuf-inspired public-safe validation pack from 25 to 27 local synthetic cases.
- Updated validation ledgers to 27/27 reasonable classification, 27/27 fix-plan validity, 27/27 verification correctness, and 0 forbidden outputs.
- Kept private local training helpers, flags, transport impersonation details, and solver code out of the public package and Git tracking boundary.

## v3.2.2

- Promoted the Spiderbuf-inspired public-safe validation pack from 10 to 17 local synthetic cases.
- Added safe diagnosis for HTTP 200 decoy/data-poisoning responses, header-normalization evidence gaps, and periodic 401/session lifecycle anomalies.
- Added public-safe regression cases for JA3/HTTP2/client hints fingerprint risk, HMAC signature triage, slider trajectory behavioral risk, and MFA risk-login redirects.
- Updated validation ledgers to 17/17 reasonable classification, 17/17 fix-plan validity, 17/17 verification correctness, and 0 forbidden outputs.
- Kept private local training helpers under `tools/spiderbuf/` out of the public package and Git tracking boundary.

## v3.2.1

- Added safe complex scraper diagnostic rules for Client Hints gaps, honeypot data mismatch, MFA/risk-login flows, Service Worker cache interference, SSE streams, and proxy header leakage.
- Improved MD5-vs-HMAC signature triage for timestamp/salt signature failures.
- Added regression tests for the Spiderbuf-inspired composite-risk cases while keeping public outputs diagnosis-only and safety-boundary aligned.
- Kept private local training helpers under `tools/spiderbuf/` out of the public package and Git tracking boundary.

## v3.2.0

- Completed the Auto Collector & One-Click Diagnosis Pack.
- Added `failure-doctor agent-bootstrap --target <agent> --project <dir>` for the Agent Frontend Invocation Pack.
- Added Codex, Cursor, Claude Code, VS Code/Copilot, Antigravity, OpenCode, Qoder, Trae, WorkBuddy, OpenClaw, Hermes, and generic agent invocation targets.
- Added `failure-doctor collect --project <dir> --preset auto --out <report> --auto-diagnose --auto-handoff --auto-sanitize`.
- Added `failure-doctor watch --project <dir> --out <reports> --once --auto-diagnose` for polling-based local failure capture.
- Added authorized project-scoped collection manifests, `open_this_first.md`, raw-local-only storage, sanitized packs, diagnosis reports, fix plans, and AI handoff packs.
- Added Windows one-click launchers under `scripts/windows/`.
- Added `tools.validation.run_auto_collector_validation` with 95 local fixture cases, 0 out-of-scope files collected, 0 browser profile files collected, 0 raw secrets in sanitized output, and 0 forbidden outputs.
- Added Auto Collector as a P98 master gate pillar.
- Kept collection local-only: no uploads, no whole-computer scan, no browser profiles, no credential stores, no dependency folders, and no Git internals.

## v3.1.0

- Completed the P98 Master Gate Completion Pack.
- Added P98 validation runners for Playwright trace, cross-framework adapters, training challenge sedimentation, composite/counterfactual diagnosis, AI handoff and patch proposal, batch/fleet diagnosis, and sanitize/share.
- Expanded the failure knowledge base to 210 local synthetic public-safe patterns.
- Expanded crawler coverage to 26 categories and 312 mapped local synthetic cases.
- Added `tools.validation.run_p98_master_gate` and promoted `validation/p98_master_gate.json` to `overall_status=pass`.
- Added v3.1.0 release notes and P98 limits/results documentation.
- Kept safety boundary strict: forbidden output count 0, private solution leaks 0, real platform access 0.

## v3.0.1

- Aligned public project positioning around Agent Failure Doctor v3.0.1.
- Separated stable validation tracks, completed P95 gates, and P98 development tracks in the validation dashboard.
- Added release-note drafts for v3.0.1 and a release publication checklist for historical v2.4.1, v2.5.0, v2.6.0, v3.0.0, and v3.0.1 milestones.
- Added `validation/p98_master_gate.json` as an explicit in-progress P98 master gate placeholder instead of claiming a final P98 pass.
- Added tests that lock version/readme/dashboard/release-note/P98-gate alignment.

## v3.0.0

- Started the P98 Controlled Maturity Pack.
- Added `docs/P98_CONTROLLED_MATURITY_SCORECARD.md` to separate controllable project maturity from ecosystem maturity.
- Added a structured failure knowledge base with 120+ local-only diagnostic patterns.
- Added knowledge-base validation and search tools.
- Added crawler failure coverage matrix documentation, JSON output, validation runner, and tests.
- Kept anti-bot content restricted to detection, safe routing, and compliance-oriented next actions.

## v2.6.0

- Added Batch Diagnosis / Fleet Mode.
- Added `failure-doctor batch <runs_dir> --out <batch_report>`.
- Batch reports generate `summary.json`, `summary.md`, `failures_by_type.csv`, `top_root_causes.md`, `repeated_failures.md`, `suggested_regression_cases.md`, `repair_priority.md`, and per-run reports under `reports/`.
- Fleet mode groups repeated failures, ranks repair priority, suggests regression cases, and keeps forbidden output count at 0.

## v2.5.0

- Added AI Handoff & Patch Proposal Pack.
- Added `failure-doctor handoff <report> --target codex|claude_code|cursor|all --out <ai_handoff>`.
- Added `failure-doctor propose-patch --repo <repo> --report <report> --out <patch_plan>`.
- Handoff packs generate Codex, Claude Code, and Cursor task files plus affected-file hints, validation commands, forbidden actions, token budget metadata, and a zip bundle.
- Patch proposals generate dry-run change steps, candidate affected areas, validation commands, and a risk assessment without editing source files.
- Added `validation/ai_handoff_validation.json` with 20 handoff cases, 18 patch proposals, 20/20 required sections present, and 0 forbidden outputs.
- The repair lifecycle is now `capture/adapt -> diagnose -> plan -> AI handoff / patch proposal -> verify -> sanitize/share`.
- Safety boundary remains unchanged: no automatic source modification, no challenge automation, no access-control defeat, no credential extraction, no bot evasion, and no unauthorized collection.

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
