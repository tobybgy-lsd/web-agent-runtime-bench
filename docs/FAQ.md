# FAQ

## Is this a crawler?

No. Agent Failure Doctor is a failure diagnosis and repair workflow tool. It can analyze local crawler or RPA failure evidence, but it does not execute production crawling jobs.

## Is this a CAPTCHA bypass tool?

No. It does not provide challenge-solving, access-control circumvention, or bot-evasion instructions. Suspected platform-risk cases are routed to safe next actions such as confirming authorization, using official APIs, reducing request volume where appropriate, or stopping unclear runs.

## How is it different from Playwright Trace Viewer?

Playwright Trace Viewer is excellent for manually inspecting actions, snapshots, console output, network events, and errors. Agent Failure Doctor adds an automated diagnostic layer: failure classification, evidence summaries, repair suggestions, issue drafts, fix plans, before/after verification, and sanitized share packs.

## Can it modify code automatically?

No. It can generate fix plans, Codex prompts, and verification guidance, but it does not automatically apply code changes.

## How do I share a failure case safely?

Use:

```powershell
failure-doctor sanitize .\failed_run --out .\shareable_failure_pack
```

Then inspect `safe_to_share.json`, `redaction_report.json`, and the sanitized files before posting or sending anything. The default is `safe_to_share=false`.

## Which frameworks are deeply supported?

Playwright is the deepest supported backend, especially for native trace semantics. Browser-use style logs, generic logs, and Playwright test-results have adapters. Selenium, Puppeteer, Cypress, Scrapy, requests, and httpx are planned for broader log-pack support.

## What are the current limits?

- complex composite failures can exceed a single-label classifier
- screenshots are metadata-only
- non-Playwright frameworks are mostly log/adaptor based today
- automated redaction is not a guarantee that a report is public-safe
- external community-submitted cases depend on actual user adoption
