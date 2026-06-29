# Agent Failure Doctor v2.1.0 - Auto Capture, Sanitize & Share, Failure Resolution Loop

Agent Failure Doctor v2.1.0 is the current stable release line for the local-first failure lifecycle workflow.

## Highlights

- `failure-doctor diagnose`: classify local failure inputs and produce evidence-backed reports.
- `failure-doctor plan`: generate a fix plan and Codex-ready repair prompt.
- `failure-doctor verify`: compare before/after runs and report whether the original failure was resolved.
- `failure-doctor run`: auto-capture local command stdout, stderr, exit code, environment, detected artifacts, diagnosis, and fix plan.
- `failure-doctor sanitize`: create a redacted shareable failure pack with `safe_to_share=false` by default.

## Milestone Summary

- v1.0 Failure Resolution Loop: diagnose, plan, verify, and regression case generation.
- v1.1 Applied Scenario Demos: six local-only business automation failure demo families.
- v1.2 Integration Adapters: Playwright collector, generic log packer, and browser-use style adapters.
- v1.3 Validation Hardening: multi-track validation gate and regression backlog.
- v2.0 Auto Capture: command wrapper and captured run folders.
- v2.1 Sanitize & Share: redacted failure packs and trace metadata-only sharing.

## Validation

Validation is tracked in separate lanes: synthetic fixtures, public-inspired cases, native Playwright traces, external public references, resolution validation, applied scenario validation, integration adapters, auto-capture, and sanitize/share checks.

See:

- [validation/dashboard.md](../validation/dashboard.md)
- [docs/VALIDATION_REPORT.md](VALIDATION_REPORT.md)

## Safety Boundary

- local-first
- no artifact upload
- no credential extraction
- no real-platform collection service
- suspected platform-risk cases produce identification and compliant routing only

## Known limits

- not a crawler execution framework
- not an anti-bot bypass tool
- deep trace semantics are strongest for Playwright
- other frameworks are currently handled mainly through logs, collectors, and adapters
- `safe_to_share=false` means a human should review any pack before external sharing
