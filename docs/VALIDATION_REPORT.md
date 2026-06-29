# Agent Failure Doctor Validation Report

## Scope

Agent Failure Doctor is validated with three evidence tiers:

1. Sanitized template fixtures for broad regression coverage.
2. Traceable public-source ledger records for credibility and category grounding.
3. Native Playwright-generated `trace.zip` fixtures for adapter semantics.

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
