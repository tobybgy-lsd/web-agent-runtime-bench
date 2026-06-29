# Project Positioning

Recommended GitHub About text:

> Local-first failure diagnosis, repair planning, fix verification, auto-capture, and sanitized sharing for AI browser automation, Playwright, crawler, and RPA runs.

Agent Failure Doctor is a local-first failure lifecycle tool. It helps developers and automation users collect failed-run evidence, diagnose likely causes, generate repair plans, verify before/after results, and prepare sanitized failure packs for review.

## It Is

- a local-first failure diagnosis tool
- a repair planning tool
- a before/after verification tool
- a command auto-capture tool
- a shareable failure pack generator
- a validation and regression case workflow

## It Is Not

- not a crawler execution framework
- not a CAPTCHA bypass tool
- not a bot evasion tool
- not an ecommerce system
- not an ERP system
- not a credential extractor
- not a real-platform collection service

## Core Lifecycle

```text
failure-doctor run
  -> failure pack
  -> failure-doctor diagnose
  -> failure-doctor plan
  -> failure-doctor verify
  -> failure-doctor sanitize
  -> regression case or sanitized external report
```

## Applicable Scenarios

- Playwright / Browser Agent failure diagnosis
- crawler or RPA failure triage from local logs and traces
- ecommerce listing automation failure diagnosis
- live commerce monitoring failure diagnosis
- content publishing workflow failure diagnosis
- GUI bridge failure diagnosis
- ERP-to-ecommerce sync failure diagnosis

## Current Limits

- Playwright trace semantics are the deepest supported backend.
- Other frameworks are currently handled mainly through logs, collectors, and adapters.
- It does not automatically apply code changes.
- It does not prove a sanitized pack is public-safe; `safe_to_share=false` remains the default until manual review.
