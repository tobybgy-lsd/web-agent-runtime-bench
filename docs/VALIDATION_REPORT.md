# Agent Failure Doctor Validation Report

## Scope

Agent Failure Doctor is validated with three evidence tiers:

1. Sanitized template fixtures for broad regression coverage.
2. Traceable public-source ledger records for credibility and category grounding.
3. Native Playwright-generated `trace.zip` fixtures for adapter semantics.
4. External public reference seeds for post-release source grounding and held-out validation.
5. Local-only applied scenario demos for business automation style failure diagnosis.

The project does not claim that all validation samples are raw real-world private failure packages. Sanitized and public-inspired records are labeled separately from real public issue URLs. Older template records are best described as public-inspired, sanitized records.

Source families: GitHub Issues / Stack Overflow / browser-use / Playwright.

Supported input families:

- `trace.zip`
- `error.log` / `console.txt`
- `network.json`
- `user_description.txt`
- screenshot metadata

## Source Ledger

`validation/source_ledger_real_failures.json` contains 131 source records.

| Source Type | Count | Use |
|---|---:|---|
| `real_public_issue` | 50 | Traceable public issue URLs for real symptoms |
| `official_doc_pattern` | 10 | Official behavior boundaries from Playwright and related docs |
| `public_inspired_sanitized` | 71 | Sanitized validation records inspired by public failure patterns |

Ledger rules:

- public-inspired records must not pretend to be GitHub issue URLs
- source URLs must not use fake example issue IDs
- every record must include source type, category, symptom, raw excerpt, and expected diagnosis
- no secrets, cookies, tokens, authorization headers, or private customer data are stored

## Template Validation Ledger

The main sanitized ledger remains `validation/public_failure_validation_150.json`.

| Metric | Result |
|---|---:|
| Sample count | 150 |
| Reasonable classifications | 146 |
| Reasonable classification rate | 97.3% |
| Actionable next actions | 142 |
| Actionable next action rate | 94.7% |
| Severe misclassifications | 4 |
| Insufficient evidence cases | 21 |
| Codex fix prompt generated | 150/150 |

## Public-Inspired Independent Validation

The independent validation track is intentionally more conservative than the template ledger.

| Metric | Result |
|---|---:|
| Sample count | 50 |
| Reasonable classification rate | 78.0% |
| Actionable next action rate | 90.0% |
| Severe misclassifications | 4 |
| Insufficient evidence cases | 7 |

## v0.8 Real Playwright Trace Semantic Validation

The v0.8 trace track generates native Playwright `trace.zip` files with `context.tracing.start(...)` and validates the adapter against raw Playwright trace records. The fixture generator uses a local-only HTTP server and does not contact third-party sites.

Artifacts:

- `examples/realistic_playwright_traces/*/trace.zip`
- `examples/realistic_playwright_traces/*/expected_diagnosis.json`
- `examples/realistic_playwright_traces/*/source.json`
- `validation/real_trace_validation_30.json`

Reproduce:

```powershell
python -m tools.real_trace_generation.generate_real_trace_fixtures --out .\examples\realistic_playwright_traces --count 30 --clean
python -m tools.validation.run_real_trace_validation
```

Current result:

| Metric | Result |
|---|---:|
| Native Playwright trace fixtures | 30 |
| Reasonable classifications | 30 |
| Reasonable classification rate | 100.0% |
| Exact subtype matches | 30 |
| Exact subtype match rate | 100.0% |
| Actionable next actions | 30 |
| Severe misclassifications | 0 |
| Insufficient evidence cases | 0 |
| Forbidden outputs | 0 |
| Custom classifier fields in raw traces | 0 |

Covered paths:

- storage-state/context login redirect, 401, session expiry
- route timing, route pattern mismatch, HAR missing, HAR fallback network leak
- shadow DOM boundary, custom element not upgraded, host-vs-inner target
- selector drift, strict mode, navigation timeout, execution-context race
- download, popup-style next-step failure, service-worker cache
- browser executable missing, CDP disconnect, agent repetition loop
- website response/API/login/download changes
- rate limit, challenge page, dynamic signature risk

## v0.8 External Held-Out Validation

The held-out track is intentionally small. It uses 10 public-source records that were not used to tune rules in this pass. Inputs are sanitized summaries derived from public issue symptoms; they are not copied private traces.

Artifacts:

- `validation/external_heldout_10_cases.json`
- `validation/external_heldout_10.json`
- `scripts/validate_external_heldout.py`

Reproduce:

```powershell
python scripts\validate_external_heldout.py
```

Current result:

| Metric | Result |
|---|---:|
| Held-out records | 10 |
| Reasonable classifications | 9 |
| Reasonable classification rate | 90.0% |
| Actionable next actions | 10 |
| Actionable next action rate | 100.0% |
| Severe misclassifications | 0 |
| Insufficient evidence cases | 2 |
| Forbidden outputs | 0 |

The non-reasonable held-out case is retained to show a real current limit: a mixed route-interception + cookie-store symptom does not yet produce a confident route/storage diagnosis from a short log-only summary.

## v0.9 External Public Reference Validation

The v0.9 external public reference pack starts from 62 traceable public sources and official documentation patterns. These are not external user submissions to this repository. They are public references used to seed a validation ledger and create a reproducible held-out set.

Artifacts:

- `validation/source_ledger_external_seed_v0_9.json`
- `validation/source_ledger_external_seed_v0_9.csv`
- `validation/external_public_reference_ledger.json`
- `validation/external_heldout_20_cases.json`
- `validation/external_heldout_20.json`
- `docs/EXTERNAL_DATA_SOURCES.md`
- `tools/validation/run_external_public_reference_validation.py`

Reproduce:

```powershell
python -m tools.validation.run_external_public_reference_validation
```

Current result:

| Metric | Result |
|---|---:|
| External public reference seeds | 62 |
| Official doc patterns | 5 |
| Real public issues | 43 |
| Real public Q&A records | 14 |
| Held-out records | 20 |
| Reasonable classifications | 20 |
| Reasonable classification rate | 100.0% |
| Exact category matches | 20 |
| Exact subtype matches | n/a |
| Actionable next actions | 20 |
| Forbidden outputs | 0 |

Exact subtype matching is not claimed for this track because the seed pack provides category-level expected diagnoses, not authoritative subtype labels.

## v1.0 Failure Resolution Loop Validation

The v1.0 resolution track validates the loop after diagnosis: fix plan generation, before/after verification, and regression case creation. Fixtures are local-only, sanitized before/after input packs.

Artifacts:

- `schemas/fix_plan.schema.json`
- `schemas/verification_report.schema.json`
- `examples/resolution_validation_cases/`
- `validation/resolution_validation_12.json`
- `tools/validation/run_resolution_validation.py`

Reproduce:

```powershell
failure-doctor diagnose examples/resolution_validation_cases/01_selector_drift_resolved/before --out tmp_report
failure-doctor plan tmp_report --out tmp_fix_plan
failure-doctor verify --before examples/resolution_validation_cases/01_selector_drift_resolved/before --after examples/resolution_validation_cases/01_selector_drift_resolved/after --out tmp_verification --create-regression
python -m tools.validation.run_resolution_validation
```

Current result:

| Metric | Result |
|---|---:|
| Resolution validation cases | 12 |
| Correct verification status | 12 |
| Actionable next steps | 12 |
| Forbidden outputs | 0 |

Anti-bot cases are not marked resolved through access-control defeat. They can only resolve through compliant path evidence such as official API use, authorized export, manual review, or stopping unclear automation.

## v1.1 Applied Scenario Demo Pack Validation

The v1.1 applied scenario track demonstrates how the same diagnosis, fix planning, and verification loop behaves on local-only mock business automation failures. These are not production business systems and do not connect to real commerce, live, content, GUI, or ERP platforms.

Artifacts:

- `examples/applied_scenarios/`
- `validation/applied_scenario_validation.json`
- `tools/validation/run_applied_scenario_validation.py`
- `docs/APPLIED_SCENARIO_DEMOS.md`

Reproduce:

```powershell
python -m tools.validation.run_applied_scenario_validation
```

Current result:

| Metric | Result |
|---|---:|
| Scenario families | 6 |
| Before/after cases | 18 |
| Reasonable classifications | 18 |
| Valid fix plans | 18 |
| Correct verification statuses | 18 |
| Forbidden outputs | 0 |

Covered scenario families:

- hot product collection
- live commerce monitoring
- ecommerce listing automation
- authorized content publishing workflow
- GUI / RPA data bridge
- ERP-to-ecommerce sync

## Website Change + Anti-Bot Risk Addendum

The v0.6 addendum is tracked separately in `validation/website_antibot_validation_50.json`.

| Metric | Result |
|---|---:|
| Sample count | 50 |
| Website Change records | 25 |
| Anti-Bot Risk records | 25 |
| Reasonable classifications | 50 |
| Safe next actions | 50 |
| Forbidden outputs | 0 |
| Insufficient evidence cases | 0 |
| Severe misclassifications | 0 |

Reproduce:

```bash
python scripts/validate_website_antibot.py
```

## Safety Boundary

`anti_bot_risk` is identification and compliant routing only. Safe actions include confirming authorization, using official APIs or authorized exports, reducing request volume where appropriate, manual review, contacting the platform owner, or stopping unclear runs.

The tool must not provide:

- challenge-solving instructions
- access-control circumvention
- credential extraction
- account rotation
- network rotation
- private signature defeat guidance
- unauthorized collection guidance

## Current Limits

- Screenshot input is metadata-only; there is no image understanding yet.
- Public-inspired records are sanitized summaries, not raw private evidence bundles.
- The real trace fixture server is local-only; it validates adapter semantics, not live third-party website drift.
- Low-evidence inputs should downgrade to `insufficient_evidence` instead of forcing a specific diagnosis.
- The validation corpus should keep growing from externally submitted sanitized cases.
