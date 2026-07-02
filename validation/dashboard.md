# Validation Dashboard

Agent Failure Doctor keeps validation lanes separate. Stable release, completed P95 gates, and the P98 master gate measure controlled project maturity. Ecosystem maturity is excluded.

## 1. Current Stable Release

Agent Failure Doctor v4.2.0 is the current controlled-maturity stable line.

| Release | Status | Notes |
|---|---|---|
| v4.2.0 Plugin SDK & Adapter Ecosystem Pack | pass | Current package stable line with local-only plugin scaffold, validation, registry, audit log, safe candidate runner, plugin-aware console/CI/agent-bootstrap integration, and network/shell/raw access blocked by default. |
| v4.1.0 Enterprise Governance & Role-Based Console Pack | pass | Current package stable line with local enterprise workspaces, RBAC, policy controls, approval workflow, append-only audit ledger, enterprise-aware console status, and no telemetry or external API calls by default. |
| v4.0.0 Hybrid Evidence Reasoning Pack | previous stable | Previous package stable line with local evidence bundles, evidence-bound claims, competing hypotheses, causal chains, root-cause graphs, and no external model calls by default. |
| v3.9.0 Local Failure Knowledge Base Pack | previous stable | Previous package stable line with local-only failure case storage, similarity matching, verified fix suggestions, sanitized export, and no external embedding API calls. |
| v3.8.0 CI/CD Integration Pack | previous stable | Previous package stable line with local CI gates, GitHub Actions/GitLab/Jenkins/PowerShell templates, sanitized report outputs, and no raw upload or external API calls. |
| v3.7.0 Local Web Console Pack | previous stable | Previous package stable line with a loopback-only local report console, bundled assets, token-protected POST routes, workspace-scoped report import, and no upload or telemetry. |
| v3.6.0 Regulated Industry & Pure Visual Agent Full-Chain Evaluation Pack | previous stable | Previous package stable line with regulated synthetic mock suites, pure visual runtime observability, full-chain evaluation, and no real regulated-system access. |
| v3.5.0 OCR & Document Evidence Adapter Pack | previous stable | Previous package stable line with local-first OCR/document evidence, DOM/VLM/schema/data-quality consistency checks, disabled-by-default cloud OCR, and no document upload by default. |
| v3.4.0 Visual Agent Runtime Observability Pack | previous stable | Previous package stable line with offline visual runtime diagnosis, screenshot cost, stale observation, coordinate/DPR/viewport drift, optional DOM conflict, local mock VLM support, and no upload or bypass guidance. |
| v3.3.0 Safety & Compliance Evaluation Pack | previous stable | Previous package stable line with local-only safety evaluation, shareability decisions, AI handoff and patch safety gates, DOM/exfiltration/cloud/regulated-workflow mock checks, and no bypass guidance. |
| v3.2.10 Data Engineering Closed-Loop Triage Patch | previous stable | Data-engineering stable line with visual failure diagnosis, data-quality helpers, data-engineering closed-loop triage, Bloom dedupe, optional mock VLM helpers, and no bypass guidance. |
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
| Regulated Industry Workflow P98 | 220 | synthetic finance/government/healthcare/common mock cases, 0 real platform access | 0 | pass | `python -m tools.validation.run_regulated_industry_validation` |
| Visual Agent Runtime P98 | 170 | offline visual-run cases, pure visual no-DOM supported, zero VLM upload | 0 | pass | `python -m tools.validation.run_visual_agent_runtime_validation` |
| OCR / Document Evidence P98 | 148 | local-only mock OCR/document cases, 100% sensitive blocking, zero cloud upload | 0 | pass | `python -m tools.validation.run_ocr_document_evidence_validation` |
| Full-Chain Agent Evaluation P98 | 60 | 60/60 reports, unsafe handoff/share blocked, zero external API calls | 0 | pass | `python -m tools.validation.run_full_chain_agent_evaluation` |
| Local Web Console P98 | 96 | loopback default, token-protected POST routes, local bundled assets, report readers | 0 | pass | `python -m tools.validation.run_local_web_console_validation` |
| CI/CD Integration P98 | 96 | local CI gates, templates, sanitized outputs, no upload | 0 | pass | `python -m tools.validation.run_ci_cd_integration_validation` |
| Local Failure Knowledge Base P98 | 160 | local sanitized cases, similarity matching, verified fix suggestions, sanitized export | 0 | pass | `python -m tools.validation.run_local_failure_kb_validation` |
| Hybrid Evidence Reasoning P98 | 224 | local sanitized evidence bundles, evidence-bound claims, provider fallback, rejected unsafe reasoning | 0 | pass | `python -m tools.validation.run_hybrid_evidence_reasoning_validation` |
| Root-Cause / Causal-Chain P98 | 224 | causal-chain and root-cause graph correctness above gate threshold | 0 | pass | `python -m tools.validation.run_hybrid_evidence_reasoning_validation` |
| Enterprise Governance P98 | 180 | local enterprise workspace, RBAC, policies, approvals, and sanitized defaults | 0 | pass | `python -m tools.validation.run_enterprise_governance_validation` |
| Role-Based Console P98 | 180 | enterprise-aware loopback console status and local auth policy | 0 | pass | `python -m tools.validation.run_enterprise_governance_validation` |
| Audit Ledger P98 | 180 | append-only audit events, export, and hash-chain validation | 0 | pass | `python -m tools.validation.run_enterprise_governance_validation` |
| Plugin SDK Ecosystem P98 | 235 | local-only plugin manifest, scaffold, validation, install/enable, and candidate runner cases | 0 | pass | `python -m tools.validation.run_plugin_sdk_ecosystem_validation` |
| Plugin Security Sandbox P98 | 235 | network/shell/raw/private/unsafe plugins blocked by default | 0 | pass | `python -m tools.validation.run_plugin_sdk_ecosystem_validation` |
| Adapter Extension API P98 | 235 | hook output schema valid and scaffold success above gate threshold | 0 | pass | `python -m tools.validation.run_plugin_sdk_ecosystem_validation` |
| Safety Boundary P98 | all pillars | global forbidden output 0, private leaks 0, real platform access 0 | 0 | pass | `powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1` |
| P98 Master Gate | 26 pillars | `overall_status=pass`, controlled maturity score 98 | 0 | pass | `python -m tools.validation.run_p98_master_gate` |

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
