# Roadmap

Agent Failure Doctor is a local-first diagnostic tool for AI browser automation, Playwright, crawler, RPA, and business automation failures.

The current engine is a deterministic evidence-based diagnostic engine. It does not claim to solve arbitrary failures, but it provides explainable classification, evidence, fix plans, and before/after verification for known automation failure patterns.

## Current Strengths

- Explainable rule engine with evidence scoring.
- Multi-input CLI for trace/log/network/description/screenshot metadata.
- Auto capture with `failure-doctor run -- <command>`.
- Conservative sharing flow with `failure-doctor sanitize <failed_run> --out <shareable_failure_pack>`.
- Repair planning with `failure-doctor plan`.
- Before/after verification with `failure-doctor verify`.
- Real Playwright trace semantic validation.
- Validation dashboard, source ledger, held-out validation, and CI gates.
- Safety boundary: local sanitized evidence only, no credential extraction, no access-control circumvention, no unauthorized collection.

## Current Limits

- Complex composite failures can still exceed a single-label classifier.
- Framework coverage is deepest for Playwright; other frameworks are mostly log-pack or generic adapters.
- The primary interaction remains CLI plus Markdown/JSON reports.
- Optional reasoning assist is not yet implemented and must not replace the deterministic rule engine.
- community-submitted failure cases can expand the corpus over time, but real external adoption remains future work.

## v2.2 Composite Diagnosis Pack

Goal: make the rule system express multi-cause failures instead of forcing one label.

Planned output fields:

```json
{
  "primary_failure": {
    "technical_category": "playwright_storage_state_context",
    "subtype": "login_redirect_after_authenticated_action"
  },
  "secondary_failures": [
    {
      "technical_category": "selector_drift",
      "subtype": "missing_price_selector"
    }
  ],
  "blocking_failure": "playwright_storage_state_context",
  "downstream_failures": ["selector_drift"],
  "evidence_conflicts": [],
  "diagnosis_priority": ["auth", "navigation", "selector"]
}
```

Acceptance:

- Detect at least auth-redirect-then-selector-fail, proxy-fail-then-timeout, route-mock-leak-then-response-shape, and website-change-then-locator-fail cases.
- Add tests for primary failure, secondary failure, blocking failure, downstream failure, and confidence reason.
- Keep reports deterministic and evidence-grounded.

## v2.3 HTML Report Viewer

Goal: lower the CLI threshold without building a full web app.

Planned output:

```text
report_html/
|-- index.html
|-- evidence.html
|-- fix_plan.html
|-- verification.html
`-- assets/
```

Acceptance:

- Render diagnosis, evidence, next action, fix plan, and verification result as static HTML.
- Include the HTML report in downloadable report zips.
- No backend, no upload, no external network dependency.

## v2.4 Cross-Framework Adapter Pack

Goal: make Playwright the deepest supported backend while giving other automation frameworks useful log-pack adapters.

Planned adapters:

- `integrations/selenium/`
- `integrations/puppeteer/`
- `integrations/cypress/`
- `integrations/scrapy_requests/`

Initial coverage:

- Selenium: `NoSuchElementException`, `StaleElementReferenceException`, `ElementClickInterceptedException`, `TimeoutException`, `SessionNotCreatedException`, `WebDriverException`.
- Puppeteer: `TimeoutError`, `Execution context was destroyed`, `Target closed`, `net::ERR_NAME_NOT_RESOLVED`, `net::ERR_PROXY_CONNECTION_FAILED`, selector timeout, download failure.
- Cypress: selector timeout, intercept mismatch, fixture mismatch, command retry timeout, viewport mismatch.
- Scrapy / requests / httpx: 403, 429, redirect to login, empty response, proxy error, DNS/TLS error, response shape changed.

## v2.5 Reasoning Assist Layer

Goal: help users package evidence for AI review without turning the project into an online black-box judge.

Default mode:

- disabled
- offline prompt only
- no automatic external model call
- rule evidence remains the source of truth

Planned output:

```json
{
  "reasoning_assist": {
    "enabled": false,
    "mode": "offline_prompt_only",
    "candidate_hypotheses": [
      "auth redirect may be the blocking failure",
      "selector drift may be downstream"
    ],
    "questions_to_confirm": [
      "Was storageState expected for this run?",
      "Did the page redirect to login before the selector failed?"
    ]
  }
}
```

Also planned:

- `reasoning_assist_prompt.md`
- similar case retrieval from local corpus
- missing evidence questions

## v2.6 Patch Proposal Pack

Goal: generate safer edit instructions without automatically applying code changes.

Planned outputs:

- `proposed_changes.md`
- `codex_edit_prompt.md`
- `affected_files.json`
- optional `candidate.patch`

Default behavior:

- do not auto-apply patches
- keep changes scoped to the diagnosed failure
- include verification commands and forbidden edit scope

## v3.0 Local Web UI

Goal: provide a local upload-and-review experience after the static HTML report has proven useful.

Principles:

- local only
- no artifact upload
- same report schema as CLI
- share packs still require manual review

## Historical Milestones

- Phase 5.2-A3 Synthetic Signed API Benchmark: done.
- Phase 5.2-A4 Showcase Sync + Private Push: done.
- Developer Toolkit Polish v1: done.
- Benchmark Credibility Layer v1: done.
- Agent Failure Doctor v0.8 Real Data & Real Trace Validation: done.
- Agent Failure Doctor v1.0 Failure Resolution Loop: done.
- Agent Failure Doctor v1.2 Integration Pack: done.
- Agent Failure Doctor v1.3 Validation Hardening Pack: done.
- Agent Failure Doctor v2.0 Auto Capture Pack: done.
- Agent Failure Doctor v2.1 Sanitize & Share Pack: done.
