# Agent Failure Doctor Credibility Validation Report

## Scope

Agent Failure Doctor is validated against public-inspired, sanitized records. These records are useful for regression and routing checks, but they are not claimed to be complete real-world failure packages with private traces, screenshots, cookies, tokens, or authorization headers.

Supported input families:

- `trace.zip`
- `error.log` / `console.txt`
- `network.json`
- `user_description.txt`
- screenshot metadata

## Main Public Validation Ledger

The main ledger is `validation/public_failure_validation_150.json`.

Source families: GitHub Issues / Stack Overflow / browser-use / Playwright.

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

## v0.6 Website Change + Anti-Bot Risk Addendum

The v0.6 addendum is tracked separately in `validation/website_antibot_validation_50.json`.

| Metric | Result |
|---|---:|
| Sample count | 50 |
| Website Change records | 25 |
| Anti-Bot Risk records | 25 |
| Reasonable classifications | 50 |
| Reasonable classification rate | 100.0% |
| Safe next actions | 50 |
| Safe next action rate | 100.0% |
| Forbidden outputs | 0 |
| Insufficient evidence cases | 0 |
| Severe misclassifications | 0 |

Reproduce the v0.6 addendum:

```bash
python scripts/validate_website_antibot.py
```

## v0.7.1 Real Playwright Trace Semantic Validation

The real trace semantic validation track is implemented in `tests/test_real_trace_semantic_validation.py`. These fixtures use native Playwright-style trace records such as `before`, `after`, `event`, `Network.requestWillBeSent`, `Network.responseReceived`, `Page.frameNavigated`, `Runtime.consoleAPICalled`, and `Runtime.exceptionThrown`.

They intentionally do not include custom classifier fields such as `storageStateExpected`, `routeRegistered`, `shadowHost`, or `elementExistsInShadowDom`.

| Metric | Result |
|---|---:|
| Fixture count | 20 |
| Diagnosable fixtures | 20 |
| Severe misclassifications | 0 |
| Custom classifier fields in raw traces | 0 |

Covered paths:

- login redirect / 401 / session expired
- route timing / route pattern / HAR missing / HAR fallback
- shadow DOM boundary / custom element not upgraded / host-vs-inner target
- strict mode / popup / download / service-worker cache
- execution-context navigation race / navigation timeout
- proxy / DNS
- response shape changed / selector drift

## Combined v0.6 Dashboard View

| Metric | Result |
|---|---:|
| Combined records | 200 |
| Reasonable classifications | 196 |
| Reasonable classification rate | 98.0% |
| Actionable or safe next actions | 192 |
| Actionable or safe next action rate | 96.0% |
| Severe misclassifications | 4 |
| Insufficient evidence cases | 21 |

## Website Change Boundary

`website_change` is repair-oriented. It can recommend refreshing DOM/network evidence, updating selectors, endpoints, JSON paths, GraphQL queries, pagination, login-flow handling, or download-flow handling.

## Anti-Bot Risk Boundary

`anti_bot_risk` is identification and compliant routing only. Safe actions include confirming authorization, using official APIs or authorized exports, reducing request volume where appropriate, manual review, contacting the platform owner, or stopping unclear runs.

The tool must not provide:

- CAPTCHA bypass
- bot evasion
- credential extraction
- account rotation
- network rotation
- private signature bypass
- unauthorized collection guidance

## Current Limits

- Screenshot input is metadata-only; there is no image understanding yet.
- Public-inspired records are sanitized summaries, not full private evidence bundles.
- Low-evidence inputs should downgrade to `insufficient_evidence` instead of forcing a specific diagnosis.
- The validation corpus should keep growing from externally submitted sanitized cases.
