# Resume and Interview Notes

## One-Line Project Description

Agent Failure Doctor is a local-first failure diagnosis, repair planning, and fix verification tool for AI browser automation, Playwright, crawler, RPA, and business automation runs.

## How to Explain It

This project is not a crawler executor and not an anti-bot tool. It is a diagnostic and verification layer that reads sanitized failure evidence such as trace files, logs, network summaries, screenshots metadata, and user descriptions.

It answers:

- What likely failed?
- What evidence supports that diagnosis?
- What should be fixed next?
- What prompt can be handed to Codex or another coding assistant?
- Did the next run actually resolve the original failure?

## Roles Where It Fits

| Role | Emphasis |
|---|---|
| AI Agent / Browser Agent | Diagnosing tool-call and browser-run failures instead of only replaying them |
| Playwright / RPA / automation testing | Trace/log based failure classification, repair planning, and before/after verification |
| Crawler / data collection engineering | Distinguishing code bugs, website changes, environment problems, and platform-risk boundaries |
| Commerce automation | Diagnosing listing, upload, selector, login-state, and data-shape failures in authorized workflows |
| ERP / data sync | Diagnosing field mapping, permission, cursor, idempotency, and rate-limit failures with audit evidence |
| GUI automation | Diagnosing download, popup, iframe, and virtualized table failures |

## What to Demo

For a short demo, run:

```powershell
failure-doctor diagnose .\examples\applied_scenarios\03_ecommerce_listing_automation\failed_run --out .\tmp_listing_report
failure-doctor plan .\tmp_listing_report --out .\tmp_listing_plan
failure-doctor verify --before .\examples\applied_scenarios\03_ecommerce_listing_automation\failed_run --after .\examples\applied_scenarios\03_ecommerce_listing_automation\rerun_after_fix --out .\tmp_listing_verify
```

For release-level validation, run:

```powershell
python -m tools.validation.run_applied_scenario_validation
```

## Safety Boundary

Do not describe this project as a CAPTCHA solver, access-control bypass tool, fingerprint spoofing system, private signature tool, account automation system, or real-platform scraper.

The right framing is:

> It diagnoses automation failures and routes platform-risk cases to compliant next actions.
