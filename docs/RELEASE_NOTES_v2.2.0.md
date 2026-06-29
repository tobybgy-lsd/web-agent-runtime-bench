# Agent Failure Doctor v2.2.0

## Cross-Framework Adapter Pack

v2.2 adds `failure-doctor adapt`, a local-only adapter layer for non-Playwright automation logs.

```powershell
failure-doctor adapt .\my_failed_run --framework selenium --out .\failure_pack
failure-doctor diagnose .\failure_pack --out .\report
failure-doctor plan .\report --out .\fix_plan
```

Supported frameworks:

```text
selenium | puppeteer | cypress | scrapy | requests | httpx | auto
```

## What Changed

- Added `integrations.cross_framework`.
- Added `schemas/framework_failure_pack.schema.json`.
- Added 42 sanitized fixtures across Selenium, Puppeteer, Cypress, Scrapy, requests, and httpx.
- Added `tools.validation.run_cross_framework_validation`.
- Added an adapter hint bridge so normalized framework packs enter the existing diagnosis, report, fix plan, and safety lifecycle.

## Validation

```text
42/42 reasonable classifications
42/42 actionable next actions
42/42 valid fix plans
0 severe misclassifications
0 forbidden outputs
```

## Boundary

Playwright remains the deepest native trace backend. Cross-framework adapters only normalize local logs and metadata. They do not run external frameworks, access real platforms, call external LLMs, upload artifacts, or provide access-control defeat guidance.
